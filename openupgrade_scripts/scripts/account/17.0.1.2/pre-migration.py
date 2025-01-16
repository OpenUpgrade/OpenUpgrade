# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools.sql import convert_column_translatable

_fields_renames = [
    (
        "res.company",
        "res_company",
        "invoice_is_print",
        "invoice_is_download",
    ),
]

_l10n_generic_coa_tax_group_xmlid = [
    "l10n_generic_coa.tax_group_15",
]

_l10n_generic_coa_tax_xmlid = [
    "l10n_generic_coa.sale_tax_template",
    "l10n_generic_coa.purchase_tax_template",
]


def _map_account_report_filter_account_type(env):
    openupgrade.rename_columns(
        env.cr, {"account_report": [("filter_account_type", None)]}
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_report
        ADD COLUMN filter_account_type character varying;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE account_report
        SET filter_account_type = CASE
            WHEN {openupgrade.get_legacy_name('filter_account_type')} THEN 'both'
            ELSE 'disabled'
            END
        """,
    )


def _generic_coa_rename_xml_id(env):
    """
    Since the removal of account.chart.template
    we need to rename some xml_id like tax or tax.group
    in order to avoid duplication
    """
    _dummy, template_id = env["ir.model.data"]._xmlid_to_res_model_res_id(
        "l10n_generic_coa.configurable_chart_template",
    )
    if not template_id:
        return
    env.cr.execute(
        f"""
        SELECT id FROM res_company
        WHERE chart_template_id={template_id}
        """
    )
    xmlids_renames = []
    for (company_id,) in env.cr.fetchall():
        for tax_group_xmlid in _l10n_generic_coa_tax_group_xmlid:
            new_xmlid = f"account.{company_id}_" + tax_group_xmlid.split(".")[1]
            xmlids_renames.append((tax_group_xmlid, new_xmlid))
        for tax_xmlid in _l10n_generic_coa_tax_xmlid:
            old_xmlid = f"l10n_generic_coa.{company_id}_" + tax_xmlid.split(".")[1]
            new_xmlid = f"account.{company_id}_" + tax_xmlid.split(".")[1]
            xmlids_renames.append((old_xmlid, new_xmlid))
    openupgrade.rename_xmlids(env.cr, xmlids_renames)


def _convert_account_tax_description(env):
    openupgrade.copy_columns(env.cr, {"account_tax": [("description", None, None)]})
    openupgrade.rename_columns(
        env.cr, {"account_tax": [("description", "invoice_label")]}
    )
    convert_column_translatable(env.cr, "account_tax", "invoice_label", "jsonb")


def _am_create_delivery_date_column(env):
    """
    Create column then in module need them like l10n_de and sale_stock will fill value,
    https://github.com/odoo/odoo/pull/116643
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS delivery_date DATE
        """,
    )


def _am_create_incoterm_location_column(env):
    """
    Create column then in sale_stock, purchase_stock will fill it in pre,
    pr: https://github.com/odoo/odoo/pull/118954
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS incoterm_location CHARACTER VARYING
        """,
    )


def _am_uniquify_name(env):
    """
    Make move names unique per journal to satisfy the constraint v17 creates
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move SET name=name || ' [' || id || ']'
        FROM (
            SElECT array_agg(id) ids FROM account_move
            GROUP BY journal_id, name HAVING COUNT(id)>1
        ) duplicate_names
        WHERE account_move.id=ANY(duplicate_names.ids);
        """,
    )


def _account_report_update_figure_type(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "account_report_column": [("figure_type", None, None)],
            "account_report_expression": [("figure_type", None, None)],
        },
    )
    old_column = openupgrade.get_legacy_name("figure_type")
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        [("none", "string")],
        False,
        "account_report_column",
    )
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        [("none", "string")],
        False,
        "account_report_expression",
    )


def _account_tax_repartition_line_merge_repartition_lines_m2o(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax_repartition_line
            ADD COLUMN IF NOT EXISTS document_type VARCHAR,
            ADD COLUMN IF NOT EXISTS tax_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax_repartition_line
            SET document_type = CASE
                WHEN invoice_tax_id IS NOT NULL THEN 'invoice'
                WHEN refund_tax_id IS NOT NULL THEN 'refund'
            END,
                tax_id = CASE
                WHEN invoice_tax_id IS NOT NULL THEN invoice_tax_id
                WHEN refund_tax_id IS NOT NULL THEN refund_tax_id
            END
        """,
    )


def _pre_create_early_pay_discount_computation(env):
    """Avoid triggering the computed method and fill the corresponding value from
    companies.
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment_term
            ADD COLUMN IF NOT EXISTS early_pay_discount_computation VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term apt
        SET early_pay_discount_computation = rc.early_pay_discount_computation
        FROM res_company rc
        WHERE apt.company_id = rc.id
        AND apt.early_pay_discount_computation IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_account_report_filter_account_type(env)
    _generic_coa_rename_xml_id(env)
    # Drop triagram index on name column of account.account
    # to avoid error when loading registry, it will be recreated
    openupgrade.logged_query(
        env.cr,
        """
        DROP INDEX IF EXISTS account_account_name_index;
        """,
    )
    openupgrade.rename_fields(env, _fields_renames)
    _convert_account_tax_description(env)
    _am_create_delivery_date_column(env)
    _am_create_incoterm_location_column(env)
    _am_uniquify_name(env)
    _account_report_update_figure_type(env)
    _account_tax_repartition_line_merge_repartition_lines_m2o(env)
    _pre_create_early_pay_discount_computation(env)
