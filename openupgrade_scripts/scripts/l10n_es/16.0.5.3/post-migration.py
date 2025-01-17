from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "l10n_es", "16.0.5.3/noupdate_changes.xml")
