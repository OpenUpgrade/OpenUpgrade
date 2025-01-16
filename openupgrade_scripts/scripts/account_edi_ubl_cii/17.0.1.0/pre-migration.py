# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _res_partner_create_columns(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS peppol_eas VARCHAR,
        ADD COLUMN IF NOT EXISTS peppol_endpoint VARCHAR,
        ADD COLUMN IF NOT EXISTS ubl_cii_format VARCHAR
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _res_partner_create_columns(env)
