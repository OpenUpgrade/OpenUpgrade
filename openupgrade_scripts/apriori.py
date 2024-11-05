""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_audit_trail": "account",
    "account_payment_term": "account",
    "l10n_br_pix": "l10n_br",
    "l10n_es_edi_facturae_adm_centers": "l10n_es_edi_facturae",
    "l10n_es_edi_facturae_invoice_period": "l10n_es_edi_facturae",
    "l10n_fr_invoice_addr": "l10n_fr_account",
    "l10n_ro_efactura": "l10n_ro_edi",
    "payment_sips": "payment_worldline",
    "sale_product_configurator": "sale",
    "website_sale_picking": "website_sale_collect",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
}
