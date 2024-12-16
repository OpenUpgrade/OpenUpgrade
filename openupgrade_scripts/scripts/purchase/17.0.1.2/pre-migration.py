from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    if not openupgrade.column_exists(env.cr, "purchase_order_line", "discount"):
        openupgrade.logged_query(
            env.cr, "ALTER TABLE purchase_order_line ADD COLUMN discount FLOAT"
        )
        openupgrade.logged_query(env.cr, "UPDATE purchase_order_line SET discount=0")
