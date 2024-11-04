# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.addons.base.models.ir_property import TYPE2FIELD as ir_property_TYPE2FIELD

_deleted_xml_records = [
    "account.tax_group_taxes",
    "account.account_invoice_send_rule_group_invoice",
    "account.sequence_reconcile_seq",
]


def _am_update_invoice_pdf_report_file(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment ia
        SET res_field = 'invoice_pdf_report_file',
            res_id = am.id
        FROM account_move am
        WHERE am.message_main_attachment_id = ia.id
        """,
    )


def _onboarding_state_migration(env):
    """
    Following pr: https://github.com/odoo/odoo/pull/104223/
    """
    env.cr.execute(
        """
        SELECT id, account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state, account_setup_bank_data_state,
        account_setup_bill_state, account_setup_coa_state, account_setup_fy_data_state,
        account_setup_taxes_state FROM res_company
        """
    )
    for (
        company_id,
        account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state,
        account_setup_bank_data_state,
        account_setup_bill_state,
        account_setup_coa_state,
        account_setup_fy_data_state,
        account_setup_taxes_state,
    ) in env.cr.fetchall():
        OnboardingStep = env["onboarding.onboarding.step"].with_company(company_id)
        company = env["res.company"].browse(company_id)
        if company.street and company.street.strip():
            # Same behaviour for this base setup company data in v16
            # Check method 'action_save_onboarding_company_step' in v16
            # Note in v17 you only need to save it then it will be done
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_company_data"
            )
        if account_onboarding_create_invoice_state_flag:
            step = env.ref(
                "account.onboarding_onboarding_step_create_invoice",
                raise_if_not_found=False,
            )
            if step and step.current_step_state == "not_done":
                if env["account.move"].search(
                    [
                        ("company_id", "=", company_id),
                        ("move_type", "=", "out_invoice"),
                    ],
                    limit=1,
                ):
                    step.action_set_just_done()
        if account_onboarding_invoice_layout_state in ("just_done", "done"):
            step = env.ref(
                "account.onboarding_onboarding_step_base_document_layout",
                raise_if_not_found=False,
            )
            if step:
                step.with_company(company_id).action_set_just_done()
        if account_onboarding_sale_tax_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_sales_tax"
            )
        if account_setup_bank_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_bank_account"
            )
        if account_setup_bill_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_setup_bill"
            )
        if account_setup_coa_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_chart_of_accounts"
            )
        if account_setup_fy_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_fiscal_year"
            )
        if account_setup_taxes_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_default_taxes"
            )


def _account_payment_term_migration(env):
    """
    In post we will update the value_amount field
    to respect v17 to ensure total percentage will not
    exceed 100% of not <100%
    In v16, the payment term might have some cases like
    -Case 1
        line 1: value - balance, value_amount - 0.0
        line 2: value - percent, value_amount - 50
        line 3: value - percent, value_amount - 45
    -Case 2
        line 1: value - balance, value_amount - 0.0
        line 2: value - percent, value_amount - 100
    NOTE: in pre we already convert value_amount of balance to 100.0 %
    AFTER migration: line 1 of case 1 will have 'value_amount' is 5%
    line 2 of case 2 will have 'value_amount' is 100% while line 2 is 0.0%
    """
    payment_terms = (
        env["account.payment.term"].with_context(active_test=False).search([])
    )
    for term in payment_terms:
        term_lines = term.line_ids.filtered(lambda line: line.value == "percent")
        value_amount_total = sum(term_lines.mapped("value_amount"))
        if value_amount_total and value_amount_total > 100.0:
            term_lines_with_100_percentage = term_lines.filtered(
                lambda line: line.value_amount == 100
            )
            term_lines_below_100_percentage = term_lines.filtered(
                lambda line: line.value_amount < 100
            )
            if len(term_lines_with_100_percentage) > 1:
                (
                    term_lines_with_100_percentage - term_lines_with_100_percentage[0]
                ).write(
                    {
                        "value_amount": 0.0,
                    }
                )
            if term_lines_below_100_percentage:
                remaining_line = term_lines - term_lines_below_100_percentage
                if remaining_line:
                    remaining_line.write(
                        {
                            "value_amount": 100
                            - sum(
                                term_lines_below_100_percentage.mapped("value_amount")
                            )
                        }
                    )


def convert_from_company_dependent(
    env,
    model_name,
    origin_field_name,
    destination_field_name,
    origin_id_column_name,
    model_table_name=None,
):
    """
    Move a company-dependent field back to the model table.

    The usual setting is: A model didn't have a company_id field in version
    (n-1), but got company-aware in version (n). Then company-dependent fields
    don't make sense, and are replaced with plain database columns.

    You're responsible for duplicating records for all companies in whatever way
    makes sense for the model before calling this function, and link the
    duplicate to the original record in column `origin_id_column_name`, which
    you have to create yourself beforehand.

    :param model_name: Name of the model.
    :param origin_field_name: Name of the company-dependent field
    :param destination_field_name: Name of plain field
    :param origin_id_column_name: Name of the column you created to link record
      duplicates to the record they were duplicated from
    :param model_table_name: Name of the table. Optional. If not provided
      the table name is taken from the model (so the model must be
      registered previously).
    """
    # If you want to recycle this function for your own migration, better
    # add it to openupgradelib
    table_name = model_table_name or env[model_name]._table

    env.cr.execute(
        "SELECT id, ttype FROM ir_model_fields "
        f"WHERE model='{model_name}' AND name='{origin_field_name}'"
    )
    field_id, field_type = env.cr.fetchone()

    value_expression = ir_property_TYPE2FIELD.get(field_type)
    if value_expression == "value_reference":
        value_expression = "SPLIT_PART(ip.value_reference, ',', 2)::integer"

    return openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table_name}
        SET {destination_field_name} = (
            SELECT {value_expression}
            FROM ir_property ip
            WHERE ip.fields_id={field_id} --- {origin_field_name}
            AND (
                ip.res_id = '{model_name}.' || COALESCE(
                    {table_name}.{origin_id_column_name}, {table_name}.id
                )
                OR ip.res_id IS NULL
            )
            AND (
                ip.company_id = {table_name}.company_id
                OR ip.company_id IS NULL
            )
            ORDER BY ip.company_id NULLS LAST, ip.res_id NULLS LAST
            LIMIT 1
        )
        """,
    )


def _account_tax_group_migration(env):
    """
    In v17 tax groups are company-aware (company_id added):

    - Find which tax groups have accounts with different companies,
      duplicate them for each of that company
    - Update accounts to point to the newly created groups for their
      companies
    - Rename ir model data (xml_id), the format will be
      "{module_name}.{company_id}_xml_id"
    - Fill new fields tax_receivable_account_id, tax_payable_account_id,
      advance_tax_payment_account_id with the value of the properties
      they replace

    Example in v16:
    2 VN CoA company: tax 0, tax 5, tax 10
    2 Generic CoA company tax 15
    1 Belgium CoA company tax 6, 12, 21

    -> After migration we will have 2 tax 0, 2 tax 5, 2 tax 10
    and 2 tax 15 of course with only different company_id
    Also the new one will have their own xml_id using create method
    of ir.model.data
    And then in each l10n module, only need to perform rename xml_id like
    https://github.com/Viindoo/OpenUpgrade/pull/655
    """
    origin_id_column = openupgrade.get_legacy_name("origin_id")
    openupgrade.logged_query(
        env.cr,
        f"""
        ALTER TABLE account_tax_group
            ADD COLUMN IF NOT EXISTS {origin_id_column} INTEGER;
        """,
    )

    env.cr.execute(
        """
        SELECT tax_group_id, array_agg(DISTINCT(company_id))
            FROM account_tax
        GROUP BY tax_group_id
        HAVING COUNT(DISTINCT company_id) > 1
        """
    )

    for tax_group_id, company_ids in env.cr.fetchall():
        tax_group = env["account.tax.group"].browse(tax_group_id)
        first_company_id = min(company_ids)
        tax_group.company_id = first_company_id

        imd = env["ir.model.data"].search(
            [("res_id", "=", tax_group.id), ("model", "=", "account.tax.group")],
            limit=1,
        )
        tax_group_name = imd.name
        imd.write({"name": f"{first_company_id}_{imd.name}"})

        for company_id in company_ids:
            if company_id == first_company_id:
                continue
            new_tax_group = tax_group.copy({"company_id": company_id})

            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE account_tax_group
                SET {origin_id_column} = {tax_group.id}
                WHERE id = {new_tax_group.id}
                """,
            )

            if tax_group_name:
                new_imd = imd.copy(
                    {
                        "res_id": new_tax_group.id,
                    }
                )
                new_imd.write(
                    {
                        "name": f"{company_id}_{tax_group_name}",
                    }
                )

            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE account_tax
                SET tax_group_id = {new_tax_group.id}
                WHERE tax_group_id = {tax_group.id} AND company_id = {company_id}
                """,
            )

    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_tax_receivable_account_id",
        "tax_receivable_account_id",
        origin_id_column,
    )
    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_tax_payable_account_id",
        "tax_payable_account_id",
        origin_id_column,
    )
    convert_from_company_dependent(
        env,
        "account.tax.group",
        "property_advance_tax_payment_account_id",
        "advance_tax_payment_account_id",
        origin_id_column,
    )


def _account_payment_term_migration(env):
    """
    https://github.com/odoo/odoo/pull/110274
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term_line
        SET value = 'percent',
            value_amount = 100.0 - COALESCE(percentages.percentage, 0)
        FROM (
            SELECT
                payment_id,
                SUM(
                    CASE WHEN l.value='percent' THEN l.value_amount
                    ELSE 0 END
                ) percentage
            FROM account_payment_term_line l
            GROUP BY payment_id
        ) percentages
        WHERE
        value = 'balance' AND
        percentages.payment_id = account_payment_term_line.payment_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term_line
        SET delay_type = CASE
                WHEN end_month = true AND COALESCE(months, 0) = 0
                  AND COALESCE(days, 0) = 0
                    THEN 'days_after_end_of_month'
                WHEN end_month = true AND months = 1 AND COALESCE(days, 0) = 0
                    THEN 'days_after_end_of_next_month'
                WHEN end_month = true AND COALESCE(months, 0) <= 1 AND days > 0
                    THEN 'days_end_of_month_on_the'
                ELSE 'days_after'
            END,
            nb_days = CASE
                WHEN end_month = true AND months <= 1
                    THEN COALESCE(days, 0) + COALESCE(days_after, 0)
                ELSE
                    COALESCE(months, 0)*30 + COALESCE(days, 0) +
                    COALESCE(days_after, 0)
            END
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term term
        SET early_pay_discount_computation = com.early_pay_discount_computation
        FROM res_company com
        WHERE term.company_id = com.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term term
            SET early_discount = true
            WHERE EXISTS (
                SELECT 1
                    FROM account_payment_term_line t1
                    WHERE t1.payment_id = term.id
                    AND t1.discount_days IS NOT NULL
                    AND t1.discount_percentage IS NOT NULL
                    AND t1.discount_percentage > 0.0
            );
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH tmp as(
            SELECT payment_id, MAX(discount_days) discount_days,
            sum(discount_percentage) discount_percentage
            FROM account_payment_term_line
            WHERE discount_days IS NOT NULL AND discount_percentage IS NOT NULL
            AND discount_percentage > 0.0
            GROUP BY payment_id
        )
        UPDATE account_payment_term term
            SET discount_days = tmp.discount_days,
                discount_percentage = tmp.discount_percentage
        FROM tmp
        WHERE tmp.payment_id = term.id
        """,
    )


def _force_install_account_payment_term_module_module(env):
    """
    Force install account_payment_term if we need
    key 'days_end_of_month_on_the' of it
    it has already merged in odoo master
    """
    account_payment_term_module = env["ir.module.module"].search(
        [("name", "=", "account_payment_term")]
    )
    needs_account_payment_term = bool(
        env["account.payment.term.line"].search(
            [("delay_type", "=", "days_end_of_month_on_the")], limit=1
        )
    )
    if needs_account_payment_term and account_payment_term_module:
        account_payment_term_module.button_install()
        openupgrade.copy_columns(
            env.cr,
            {
                "account_payment_term_line": [
                    ("days_after", "days_next_month", "CHARACTER VARYING")
                ]
            },
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_payment_term_line
            SET
            nb_days = nb_days - days_after,
            days_next_month = days_after
            WHERE delay_type = 'days_end_of_month_on_the'
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _account_payment_term_migration(env)
    _force_install_account_payment_term_module_module(env)
    openupgrade.load_data(env, "account", "17.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _am_update_invoice_pdf_report_file(env)
    _onboarding_state_migration(env)
    _account_tax_group_migration(env)
