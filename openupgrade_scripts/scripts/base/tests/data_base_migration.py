env = locals().get("env")
# partner with specific barcode
env["res.partner"].with_company(env.ref("base.main_company")).create(
    {
        "name": "partner with barcode",
        "barcode": "barcode main company",
    }
)
env.cr.commit()
