# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools.sql import convert_column_translatable

_fields_renames = [
    (
        "res.company",
        "res_company",
        "invoice_is_print",
        "invoice_is_download",
    ),
]

COA_MAPPING = {
    "l10n_ae.uae_chart_template_standard": "ae",
    "l10n_ar.l10nar_base_chart_template": "ar_base",
    "l10n_ar.l10nar_ex_chart_template": "ar_ex",
    "l10n_ar.l10nar_ri_chart_template": "ar_ri",
    "l10n_at.l10n_at_chart_template": "at",
    "l10n_au.l10n_au_chart_template": "au",
    "l10n_be.l10nbe_chart_template": "be_comp",
    "l10n_bg.l10n_bg_chart_template": "bg",
    "l10n_bo.bo_chart_template": "bo",
    "l10n_br.l10n_br_account_chart_template": "br",
    "l10n_ca.ca_en_chart_template_en": "ca_2023",
    "l10n_ch.l10nch_chart_template": "ch",
    "l10n_cl.cl_chart_template": "cl",
    "l10n_cn.l10n_chart_china_small_business": "cn",
    "l10n_co.l10n_co_chart_template_generic": "co",
    "l10n_cr.account_chart_template_0": "cr",
    "l10n_cz.cz_chart_template": "cz",
    "l10n_de.l10n_de_chart_template": "de_skr03",
    "l10n_de.l10n_chart_de_skr04": "de_skr04",
    "l10n_de_skr03.l10n_de_chart_template": "de_skr03",
    "l10n_de_skr04.l10n_chart_de_skr04": "de_skr04",
    "l10n_dk.dk_chart_template": "dk",
    "l10n_do.do_chart_template": "do",
    "l10n_dz.l10n_dz_pcg_chart_template": "dz",
    "l10n_ec.l10n_ec_ifrs": "ec",
    "l10n_ee.l10nee_chart_template": "ee",
    "l10n_eg.egypt_chart_template_standard": "eg",
    "l10n_es.account_chart_template_assoc": "es_assec",
    "l10n_es.account_chart_template_common": "es_common",
    "l10n_es.account_chart_template_full": "es_full",
    "l10n_es.account_chart_template_pymes": "es_pymes",
    "l10n_et.l10n_et": "et",
    "l10n_fi.fi_chart_template": "fi",
    "l10n_fr.l10n_fr_pcg_chart_template": "fr",
    "l10n_generic_coa.configurable_chart_template": "generic_coa",
    "l10n_gr.l10n_gr_chart_template": "gr",
    "l10n_gt.cuentas_plantilla": "gt",
    "l10n_hk.l10n_hk_chart_template": "hk",
    "l10n_hn.cuentas_plantilla": "hn",
    "l10n_hr.l10n_hr_chart_template_rrif": "hr",
    "l10n_hr.l10n_hr_euro_chart_template": "hr",
    "l10n_hr_kuna.l10n_hr_kuna_chart_template_rrif": "hr_kuna",
    "l10n_hu.hungarian_chart_template": "hu",
    "l10n_id.l10n_id_chart": "id",
    "l10n_ie.l10n_ie": "ie",
    "l10n_il.il_chart_template": "il",
    "l10n_in.indian_chart_template_standard": "in",
    "l10n_it.l10n_it_chart_template_generic": "it",
    "l10n_jp.l10n_jp1": "jp",
    "l10n_jp.l10n_jp_chart_template": "jp",
    "l10n_ke.l10nke_chart_template": "ke",
    "l10n_kz.l10nkz_chart_template": "kz",
    "l10n_lt.account_chart_template_lithuania": "lt",
    "l10n_lu.lu_2011_chart_1": "lu",
    "l10n_lv.chart_template_latvia": "lv",
    "l10n_ma.l10n_ma_chart_template": "ma",
    "l10n_mn.mn_chart_1": "mn",
    "l10n_mx.mx_coa": "mx",
    "l10n_my.l10n_my_chart_template": "my",
    "l10n_mz.l10n_mz_chart_template": "mz",
    "l10n_nl.l10nnl_chart_template": "nl",
    "l10n_no.no_chart_template": "no",
    "l10n_nz.l10n_nz_chart_template": "nz",
    "l10n_pa.l10npa_chart_template": "pa",
    "l10n_pe.pe_chart_template": "pe",
    "l10n_ph.l10n_ph_chart_template": "ph",
    "l10n_pk.l10n_pk_chart_template": "pk",
    "l10n_pl.pl_chart_template": "pl",
    "l10n_pt.pt_chart_template": "pt",
    "l10n_ro.ro_chart_template": "ro",
    "l10n_rs.l10n_rs_chart_template": "rs",
    "l10n_sa.sa_chart_template_standard": "sa",
    "l10n_se.l10nse_chart_template": "se",
    "l10n_se.l10nse_chart_template_K2": "se_K2",
    "l10n_se.l10nse_chart_template_K3": "se_K3",
    "l10n_sg.sg_chart_template": "sg",
    "l10n_si.gd_chart": "si",
    "l10n_sk.sk_chart_template": "sk",
    "l10n_syscohada.syscohada_chart_template": "syscohada",
    "l10n_th.chart": "th",
    "l10n_tr.chart_template_common": "tr",
    "l10n_tr.l10n_tr_chart_template": "tr",
    "l10n_tw.l10n_tw_chart_template": "tw",
    "l10n_ua.l10n_ua_ias_chart_template": "ua_ias",
    "l10n_ua.l10n_ua_psbo_chart_template": "ua_psbo",
    "l10n_uk.l10n_uk": "uk",
    "l10n_uy.uy_chart_template": "uy",
    "l10n_ve.ve_chart_template_amd": "ve",
    "l10n_vn.vn_template": "vn",
    "l10n_za.default_chart_template": "za",
}

_l10n_generic_coa_tax_group_xmlid = [
    "l10n_generic_coa.tax_group_15",
]

_l10n_generic_coa_tax_xmlid = [
    "l10n_generic_coa.sale_tax_template",
    "l10n_generic_coa.purchase_tax_template",
]


def _map_account_report_filter_account_type(env):
    openupgrade.rename_columns(
        env.cr, {"account_report": [("filter_account_type", None)]}
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_report
        ADD COLUMN filter_account_type character varying;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE account_report
        SET filter_account_type = CASE
            WHEN {openupgrade.get_legacy_name('filter_account_type')} THEN 'both'
            ELSE 'disabled'
            END
        """,
    )


def _map_chart_template_id_to_chart_template(
    env, model, coa_m2o="chart_template_id", coa_str="chart_template"
):
    openupgrade.logged_query(
        env.cr,
        f"""
        ALTER TABLE {model}
        ADD COLUMN {coa_str} character varying;
        """,
    )
    env.cr.execute(
        f"""SELECT m.id AS m_id, CONCAT(imd.module, '.', imd.name) AS coa_xml_id
            FROM {model} m
                JOIN ir_model_data imd
                    ON imd.model='account.chart.template'
                        AND m.{coa_m2o} = imd.res_id
            WHERE m.{coa_m2o} IS NOT NULL
        """
    )
    for line in env.cr.dictfetchall():
        if line["coa_xml_id"] in COA_MAPPING:
            openupgrade.logged_query(
                env.cr,
                f"""
                UPDATE {model}
                SET {coa_str} = '{COA_MAPPING[line['coa_xml_id']]}'
                WHERE id = {line['m_id']}
                """,
            )


def _generic_coa_rename_xml_id(env):
    """
    Since the removal of account.chart.template
    we need to rename some xml_id like tax or tax.group
    in order to avoid duplication
    """
    env.cr.execute(
        """SELECT id, name FROM res_company WHERE chart_template = 'generic_coa'"""
    )
    xmlids_renames = []
    for company_id, _ in env.cr.fetchall():
        if company_id == env.company.id:
            for tax_group_xmlid in _l10n_generic_coa_tax_group_xmlid:
                new_xmlid = f"account.{company_id}_" + tax_group_xmlid.split(".")[1]
                xmlids_renames.append((tax_group_xmlid, new_xmlid))
        for tax_xmlid in _l10n_generic_coa_tax_xmlid:
            old_xmlid = f"l10n_generic_coa.{company_id}_" + tax_xmlid.split(".")[1]
            new_xmlid = f"account.{company_id}_" + tax_xmlid.split(".")[1]
            xmlids_renames.append((old_xmlid, new_xmlid))
    openupgrade.rename_xmlids(env.cr, xmlids_renames)


def _convert_account_tax_description(env):
    openupgrade.rename_columns(env.cr, {"account_tax": [("description", None)]})
    openupgrade.logged_query(env.cr, "ALTER TABLE account_tax ADD description JSONB")
    openupgrade.logged_query(
        env.cr,
        f"""UPDATE account_tax
        SET description = {'en_US': {openupgrade.get_legacy_name('description')}}
        """,
    )


def _am_create_delivery_date_column(env):
    """
    Create column then in module need them like l10n_de and sale_stock will fill value,
    https://github.com/odoo/odoo/pull/116643
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS delivery_date DATE
        """,
    )


def _am_create_incoterm_location_column(env):
    """
    Create column then in sale_stock, purchase_stock will fill it in pre,
    pr: https://github.com/odoo/odoo/pull/118954
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS incoterm_location CHARACTER VARYING
        """,
    )


def _am_uniquify_name(env):
    """
    Make move names unique per journal to satisfy the constraint v17 creates
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move SET name=name || ' [' || id || ']'
        FROM (
            SElECT array_agg(id) ids FROM account_move
            GROUP BY journal_id, name HAVING COUNT(id)>1
        ) duplicate_names
        WHERE account_move.id=ANY(duplicate_names.ids);
        """,
    )


def _account_report_update_figure_type(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "account_report_column": [("figure_type", None, None)],
            "account_report_expression": [("figure_type", None, None)],
        },
    )
    old_column = openupgrade.get_legacy_name("figure_type")
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        {"none": "string"},
        False,
        "account_report_column",
    )
    openupgrade.map_values(
        env.cr,
        old_column,
        "figure_type",
        {"none": "string"},
        False,
        "account_report_expression",
    )


def _account_tax_repartition_line_merge_repartition_lines_m2o(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax_repartition_line
            ADD COLUMN IF NOT EXISTS document_type VARCHAR,
            ADD COLUMN IF NOT EXISTS tax_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax_repartition_line
            SET document_type = CASE
                WHEN invoice_tax_id IS NOT NULL THEN 'invoice'
                WHEN refund_tax_id IS NOT NULL THEN 'refund'
            END,
                tax_id = CASE
                WHEN invoice_tax_id IS NOT NULL THEN invoice_tax_id
                WHEN refund_tax_id IS NOT NULL THEN refund_tax_id
            END
        """,
    )


def _res_partner_bank_create_column(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_partner_bank
            ADD COLUMN IF NOT EXISTS has_iban_warning BOOLEAN,
            ADD COLUMN IF NOT EXISTS has_money_transfer_warning BOOLEAN;
        """,
    )


def _pre_create_early_pay_discount_computation(env):
    """Avoid triggering the computed method and fill the corresponding value from
    companies.
    """
    openupgrade.logged_query(
        env.cr, "ALTER TABLE res_company ADD early_pay_discount_computation VARCHAR"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment_term apt
        SET early_pay_discount_computation = com.early_pay_discount_computation
        FROM res_company rc
        WHERE apt.company_id = rc.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_account_report_filter_account_type(env)
    _map_chart_template_id_to_chart_template(env, "res_company")
    _map_chart_template_id_to_chart_template(env, "account_report")
    _generic_coa_rename_xml_id(env)
    # Drop triagram index on name column of account.account
    # to avoid error when loading registry, it will be recreated
    openupgrade.logged_query(
        env.cr,
        """
        DROP INDEX IF EXISTS account_account_name_index;
        """,
    )
    openupgrade.rename_fields(env, _fields_renames)
    convert_column_translatable(env.cr, "account_tax", "description", "jsonb")
    _convert_account_tax_description(env)
    _am_create_delivery_date_column(env)
    _am_create_incoterm_location_column(env)
    _am_uniquify_name(env)
    _account_report_update_figure_type(env)
    _account_tax_repartition_line_merge_repartition_lines_m2o(env)
    _res_partner_bank_create_column(env)
    _pre_create_early_pay_discount_computation(env)
