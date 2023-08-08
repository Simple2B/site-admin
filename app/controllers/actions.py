from flask_login import current_user

from app.common import models as m
from app.database import db

from app.logger import log


def create_action_log(
    entity: m.Action.Entity,
    entity_id: int,
    action: m.Action.ActionsType,
    user_id: int,
    text: str,
):
    action = m.Action(
        text=text,
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
    )
    db.session.add(action)
    db.session.commit()
    log(
        log.INFO,
        "Create action_log for user with id [%s]",
        user_id,
    )


def case_action_log(action: m.Action.ActionsType, entity_id: int, user_id: int):
    text = None
    case: m.Case = db.session.get(m.Case, entity_id)
    match action:
        case m.Action.ActionsType.CREATE:
            text = f"{current_user.username} create a new case {case.title}"

        case m.Action.ActionsType.DELETE:
            text = f"{current_user.username} delete case {case.title}"

    create_action_log(m.Action.Entity.CASE, entity_id, action, user_id, text)


def candidate_action_log(action: m.Action.ActionsType, entity_id: int, user_id: int):
    text = None
    candidate: m.Candidate = db.session.get(m.Candidate, entity_id)
    match action:
        case m.Action.ActionsType.DELETE:
            text = f"{current_user.username} delete candidate {candidate.username}"

    create_action_log(m.Action.Entity.CANDIDATE, entity_id, action, user_id, text)


def admin_action_log(action: m.Action.ActionsType, entity_id: int, user_id: int):
    text = None
    admin: m.Case = db.session.get(m.SuperUser, entity_id)
    match action:
        case m.Action.ActionsType.DELETE:
            text = f"{current_user.username.upper() } delete admin {admin.username.upper() }"

        case m.Action.ActionsType.CREATE:
            text = f"{current_user.username.upper() } create a new admin {admin.username.upper() }"

    create_action_log(m.Action.Entity.ADMIN, entity_id, action, user_id, text)


def question_action_log(action: m.Action.ActionsType, entity_id: int, user_id: int):
    text = None
    question: m.Case = db.session.get(m.Question, entity_id)
    match action:
        case m.Action.ActionsType.DELETE:
            text = f"{current_user.username.upper() } delete question '{question.text}'"

        case m.Action.ActionsType.CREATE:
            text = (
                f"{current_user.username.upper() } create a new question {question.id }"
            )
        case m.Action.ActionsType.EDIT:
            text = f"{current_user.username.upper() } changed a question {question.id }"

    create_action_log(m.Action.Entity.QUESTION, entity_id, action, user_id, text)
