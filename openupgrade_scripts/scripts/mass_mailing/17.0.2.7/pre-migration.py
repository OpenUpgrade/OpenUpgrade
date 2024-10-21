# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(
        env,
        "mass_mailing",
        "mailing_contact_list_rel",
        "unique_contact_list",
    )
