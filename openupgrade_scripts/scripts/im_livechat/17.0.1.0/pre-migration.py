# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _discuss_channel_create_column(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE discuss_channel
            ADD COLUMN IF NOT EXISTS rating_last_value FLOAT;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _discuss_channel_create_column(env)
