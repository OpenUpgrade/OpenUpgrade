# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.addons.openupgrade_scripts.apriori import merged_modules, renamed_modules

_renamed_xmlids = [
    (
        "base.lang_sr_RS",
        "base.lang_sr@Cyrl",
    ),
]


def _fix_list_view_type(cr):
    """
    Former tree views have view type list now.

    It's not strictly necessary to change this, but squelches a lot of warnings
    in the log
    """
    openupgrade.logged_query(cr, "UPDATE ir_ui_view SET type='list' WHERE type='tree'")


def _fix_serbian_res_lang_record(cr):
    """
    ISO code of Serbian (Cyrillic) has been changed
    """
    openupgrade.logged_query(
        cr, "UPDATE res_lang SET code='sr@Cyrl', iso_code='sr@Cyrl' WHERE code='sr_RS'"
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.update_module_names(cr, renamed_modules.items())
    openupgrade.update_module_names(cr, merged_modules.items(), merge_modules=True)
    openupgrade.clean_transient_models(cr)
    openupgrade.rename_xmlids(cr, _renamed_xmlids)

    _fix_list_view_type(cr)
    _fix_serbian_res_lang_record(cr)
