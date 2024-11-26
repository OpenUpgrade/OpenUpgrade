# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "website_event_questions.constraint_event_registration_answer_value_check",
        "website_event.constraint_event_registration_answer_value_check",
    ),
    (
        "website_event_questions.ir_rule_event_question_answer_event_user",
        "website_event.ir_rule_event_question_answer_event_user",
    ),
    (
        "website_event_questions.ir_rule_event_question_answer_published",
        "website_event.ir_rule_event_question_answer_published",
    ),
    (
        "website_event_questions.ir_rule_event_question_event_user",
        "website_event.ir_rule_event_question_event_user",
    ),
    (
        "website_event_questions.ir_rule_event_question_published",
        "website_event.ir_rule_event_question_published",
    ),
]


def migrate(cr, version):
    openupgrade.rename_xmlids(cr, _xmlids_renames)
