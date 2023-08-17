from flask import Response
from flask.testing import FlaskClient
from app.common import models as m
from tests.utils import login
from app.database import db


def test_CRUD_questions(client: FlaskClient):
    login(client)
    response: Response = client.post(
        "/quiz/create",
        data=dict(
            text="Test question",
            correct_answer_mark="1",
            variant_1="Variant 1",
            variant_2="Variant 2",
            variant_3="Variant 3",
            variant_4="Variant 4",
        ),
        follow_redirects=True,
    )
    assert response
    assert response.status_code == 200
    question: m.Question = db.session.query(m.Question).first()
    assert question
    assert question.text == "Test question"
    assert question.correct_answer_mark == 1
    action_log: m.Action = db.session.get(m.Action, 1)
    assert action_log
    assert action_log.action == m.ActionsType.CREATE
    response: Response = client.post(
        "/quiz/save",
        json=dict(
            id=question.id,
            uuid=question.uid,
            text="Test question!!!",
            correct_answer_mark="2",
            variant_1="Variant 1",
            variant_2="Variant 2",
            variant_3="Variant 3",
            variant_4="Variant 4",
        ),
        follow_redirects=True,
    )
    assert response
    edited_question: m.Question = db.session.query(m.Question).first()
    assert edited_question
    assert edited_question.text == "Test question!!!"
    assert edited_question.correct_answer_mark == 2
    action_log: m.Action = db.session.get(m.Action, 2)
    assert action_log
    assert action_log.action == m.ActionsType.EDIT
    response: Response = client.delete(
        "/quiz/delete/1",
        follow_redirects=True,
    )
    assert response
    assert response.status_code == 200
    deleted_question: m.Question = db.session.query(m.Question).first()
    assert deleted_question.is_deleted
    action_log: m.Action = db.session.get(m.Action, 3)
    assert action_log
    assert action_log.action == m.ActionsType.DELETE
