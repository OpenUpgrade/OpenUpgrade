# Copyright 2024- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_model_renames = [
    ("hr.leave.stress.day", "hr.leave.mandatory.day"),
]

_table_renames = [
    ("hr_leave_stress_day", "hr_leave_mandatory_day"),
]


def _map_leave_accrual_level_action(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET action_with_unused_accruals = 'all'
        WHERE action_with_unused_accruals = 'postponed';
        """,
    )


def _map_leave_accrual_level_added_value_type(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET added_value_type = 'day'
        WHERE added_value_type = 'days';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET added_value_type = 'hour'
        WHERE added_value_type = 'hours';
        """,
    )


def _map_leave_allocation_state(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_allocation
        SET state = 'confirm'
        WHERE state = 'draft';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_allocation
        SET state = 'refuse'
        WHERE state = 'cancel';
        """,
    )


def _set_is_based_on_worked_time(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE hr_leave_accrual_plan
            ADD COLUMN IF NOT EXISTS is_based_on_worked_time BOOLEAN;
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_plan plan
        SET is_based_on_worked_time = level.is_based_on_worked_time
        FROM  hr_leave_accrual_level level
        WHERE level.accrual_plan_id = plan.id;
        """,
    )


def _delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_accrual_level", "check_dates"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    _map_leave_accrual_level_action(env.cr)
    _map_leave_accrual_level_added_value_type(env.cr)
    _map_leave_allocation_state(env.cr)
    _set_is_based_on_worked_time(env.cr)
    _delete_sql_constraints(env)
