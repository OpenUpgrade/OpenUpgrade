# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _stock_move_convert_analytic_account_line_id_m2o_to_m2m(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["stock.move"],
        "stock_move",
        "analytic_account_line_ids",
        "analytic_account_line_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _stock_move_convert_analytic_account_line_id_m2o_to_m2m(env)
