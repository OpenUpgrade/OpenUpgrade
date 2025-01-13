# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _convert_company_dependent(
    env, model_name, field_name, value_expression=None, old_field_id=None
):
    """
    Company dependent fields used to live in ir.property, in v18 they are jsonb
    dictionaries with company id as key and the company specific value as value
    Default values live in ir.default
    """
    Model = env[model_name]
    Field = (
        env["ir.model.fields"]._get(model_name, field_name)
        if not old_field_id else env["ir.model.fields"].browse(old_field_id)
    )
    value_expression = value_expression or (
        "value_%s"
        % {
            "float": "float",
            "boolean": "integer",
            "integer": "integer",
            "date": "datetime",
            "datetime": "datetime",
        }.get(Field.ttype, "text")
        if Field.ttype != "many2one"
        else "SPLIT_PART(value_reference, ',', 2)"
    )

    openupgrade.logged_query(
        env.cr,
        f"ALTER TABLE {Model._table} ADD COLUMN IF NOT EXISTS {field_name} jsonb",
    )

    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {Model._table} SET {field_name}=ir_property_by_company.value
        FROM (
            SELECT
            SPLIT_PART(res_id, ',', 2)::integer res_id,
            JSON_OBJECT_AGG(company_id, {value_expression}) value
            FROM ir_property
            WHERE
            fields_id={old_field_id or Field.id} AND res_id IS NOT NULL
            AND company_id IS NOT NULL
            GROUP BY res_id
        ) ir_property_by_company
        WHERE {Model._table}.id=ir_property_by_company.res_id
        """,
    )

    env.cr.execute(
        f"""
        SELECT company_id, {value_expression} FROM ir_property
        WHERE
        fields_id={old_field_id or Field.id} AND res_id IS NULL
        """
    )
    for company_id, value in env.cr.fetchall():
        env["ir.default"].set(model_name, field_name, value, company_id=company_id)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "base", "18.0.1.3/noupdate_changes.xml")
    _convert_company_dependent(env, "res.partner", "barcode")
