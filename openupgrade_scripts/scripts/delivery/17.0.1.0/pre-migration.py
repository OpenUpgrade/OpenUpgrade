from openupgradelib import openupgrade

_new_fields = [
    (
        "carrier_id",  # Field name
        "stock.move.line",  # Model name
        "stock_move_line",  # Table name
        "many2one",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "delivery",  # Module name
        False,  # [Optional] Default value
    )
]

_xmlids_renames = [
    (
        "delivery.act_delivery_trackers_url",
        "stock_delivery.act_delivery_trackers_url",
    ),
    (
        "delivery.access_choose_delivery_package",
        "stock_delivery.access_choose_delivery_package",
    ),
    (
        "delivery.access_delivery_carrier_stock_user",
        "stock_delivery.access_delivery_carrier_stock_user",
    ),
    (
        "delivery.access_delivery_carrier_stock_manager",
        "stock_delivery.access_delivery_carrier_stock_manager",
    ),
    (
        "delivery.access_delivery_price_rule_stock_manager",
        "stock_delivery.access_delivery_price_rule_stock_manager",
    ),
    (
        "delivery.access_delivery_zip_prefix_stock_manager",
        "stock_delivery.access_delivery_zip_prefix_stock_manager",
    ),
    (
        "delivery.menu_action_delivery_carrier_form",
        "stock_delivery.menu_action_delivery_carrier_form",
    ),
    (
        "delivery.menu_delivery_zip_prefix",
        "stock_delivery.menu_delivery_zip_prefix",
    ),
]


def _delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "delivery", "delivery_carrier", "margin_not_under_100_percent"
    )


def _fill_stock_move_line_carrier_id(env):
    """Field `carrier_id` on stock.move.line is now a stored field."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET carrier_id = sp.carrier_id
        FROM stock_picking sp
        WHERE sml.picking_id = sp.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.add_fields(env, _new_fields)
    _delete_sql_constraints(env)
    _fill_stock_move_line_carrier_id(env)
