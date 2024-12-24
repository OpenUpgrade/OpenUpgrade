# Copyright 2024- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _leave_type_responsible_convert_field_m2o_to_m2m(env):
    # Convert m2o to m2m in 'onboarding.onboarding.step'
    openupgrade.m2o_to_x2m(
        env.cr,
        env["hr.leave.type"],
        "hr_leave_type",
        "responsible_ids",
        "responsible_id",
    )


def _compute_already_accrued(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET already_accrued = True
        WHERE allocation_type = 'accrual'
              AND state = 'validate'
              AND accrual_plan_id IS NOT NULL
              AND employee_id IS NOT NULL
              AND number_of_days > 0;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_holidays", "17.0.1.6/noupdate_changes.xml")
    _leave_type_responsible_convert_field_m2o_to_m2m(env)
    _compute_already_accrued(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "hr_holidays.mail_act_leave_allocation_second_approval",
            "hr_holidays.hr_leave_stress_day_rule_multi_company",
        ],
    )
