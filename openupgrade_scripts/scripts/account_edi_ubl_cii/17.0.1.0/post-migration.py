# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _res_partner_compute_fields_values(env):
    res_partner = env["res.partner"].with_context(active_test=False).search([])
    res_partner._compute_ubl_cii_format()
    res_partner._compute_peppol_endpoint()
    res_partner._compute_peppol_eas()


@openupgrade.migrate()
def migrate(env, version):
    _res_partner_compute_fields_values(env)
