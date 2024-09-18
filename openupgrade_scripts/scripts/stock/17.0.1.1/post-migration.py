# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _stock_scrap_convert_move_id_m2o_to_o2m(env):
    """
    Convert m2o to o2m in 'stock.scrap'
    """
    openupgrade.m2o_to_x2m(
        env.cr, env["stock.scrap"], "stock_scrap", "move_ids", "move_id"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "stock", "17.0.1.1/noupdate_changes.xml")
    _stock_scrap_convert_move_id_m2o_to_o2m(env)
