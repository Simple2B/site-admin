from flask_login import current_user

from app.common import models as m
from app.database import db

from app.logger import log


class ActionLogs:
    @classmethod
    def _create(
        cls,
        entity: m.Entity,
        entity_id: int,
        action: m.ActionsType,
        text: str,
    ):
        action = m.Action(
            text=text,
            user_id=current_user.id,
            action=action,
            entity=entity,
            entity_id=entity_id,
        )
        db.session.add(action)
        db.session.commit()
        log(
            log.INFO,
            "Create action_log for user with id [%s]",
            current_user.id,
        )

    @classmethod
    def create_case_log(self, action: m.ActionsType, entity_id: int):
        text = None
        case: m.Case = db.session.get(m.Case, entity_id)
        match action:
            case m.ActionsType.CREATE:
                text = f"{current_user.username} create a new case {case.title}"

            case m.ActionsType.DELETE:
                text = f"{current_user.username} delete case {case.title}"

        ActionLogs._create(m.Entity.CASE, entity_id, action, text)

    @classmethod
    def create_candidate_log(
        cls,
        action: m.ActionsType,
        entity_id: int,
    ):
        text = None
        candidate: m.Candidate = db.session.get(m.Candidate, entity_id)
        match action:
            case m.ActionsType.DELETE:
                text = f"{current_user.username} delete candidate {candidate.username}"

        ActionLogs._create(m.Entity.CANDIDATE, entity_id, action, text)

    @classmethod
    def create_admin_log(
        cls,
        action: m.ActionsType,
        entity_id: int,
    ):
        text = None
        admin: m.Case = db.session.get(m.SuperUser, entity_id)
        match action:
            case m.ActionsType.DELETE:
                text = f"{current_user.username.upper() } delete admin {admin.username.upper() }"

            case m.ActionsType.CREATE:
                text = f"{current_user.username.upper() } create a new admin {admin.username.upper() }"

        ActionLogs._create(m.Entity.ADMIN, entity_id, action, text)

    @classmethod
    def create_question_log(
        cls,
        action: m.ActionsType,
        entity_id: int,
    ):
        text = None
        question: m.Case = db.session.get(m.Question, entity_id)
        match action:
            case m.ActionsType.DELETE:
                text = f"{current_user.username.upper() } delete question '{question.text}'"

            case m.ActionsType.CREATE:
                text = f"{current_user.username.upper() } create a new question {question.id }"
            case m.ActionsType.EDIT:
                text = f"{current_user.username.upper() } changed a question {question.id }"

        ActionLogs._create(m.Entity.QUESTION, entity_id, action, text)
