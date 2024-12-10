# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_fields_renames = [
    (
        "hr.attendance",
        "hr_attendance",
        "check_in_latitude",
        "in_latitude",
    ),
    (
        "hr.attendance",
        "hr_attendance",
        "check_in_longitude",
        "in_longitude",
    ),
    (
        "hr.attendance",
        "hr_attendance",
        "check_out_latitude",
        "out_latitude",
    ),
    (
        "hr.attendance",
        "hr_attendance",
        "check_out_longitude",
        "out_longitude",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
