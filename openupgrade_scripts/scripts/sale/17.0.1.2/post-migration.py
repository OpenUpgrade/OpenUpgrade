# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _sale_order_populate_locked_field(env):
    """
    Set state of sale orders in state 'done' to 'sale'
    Lock them if the the group sale.group_auto_done_setting
    is inherited by the user group
    """
    auto_done_group = env.ref("sale.group_auto_done_setting")
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order
        SET locked = locked or create_uid = ANY (%s), state = 'sale'
        WHERE state = 'done'
        """,
        (auto_done_group.users.ids,),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale", "17.0.1.2/noupdate_changes.xml")
    _sale_order_populate_locked_field(env)
