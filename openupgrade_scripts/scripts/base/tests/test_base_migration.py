from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestBaseMigration(TransactionCase):
    def test_property_conversion(self):
        """
        Test that the partner's barcode was migrated correctly
        """
        self.assertTrue(
            self.env["res.partner"]
            .with_company(self.env.ref("base.main_company"))
            .search([("barcode", "=", "barcode main company")]),
        )
