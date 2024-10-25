# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _purchase_stock_convert_created_purchase_line_id_m2o_to_m2m(env):
    """
    Convert m2o to m2m in 'purchase.stock'
    """
    openupgrade.m2o_to_x2m(
        env.cr,
        env["stock.move"],
        "stock_move",
        "created_purchase_line_ids",
        "created_purchase_line_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _purchase_stock_convert_created_purchase_line_id_m2o_to_m2m(env)
