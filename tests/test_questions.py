from flask import Response
from flask.testing import FlaskClient, TestResponse
from app.common import models as m
from tests.utils import login
from app.database import db


def test_CRUD_questions(client: FlaskClient):
    login(client)
    response: TestResponse = client.post(
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
    create_action_log: m.Action = db.session.get(m.Action, 1)
    assert create_action_log
    assert create_action_log.action == m.ActionsType.CREATE
    res: TestResponse = client.post(
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
    assert res
    edited_question: m.Question = db.session.query(m.Question).first()
    assert edited_question
    assert edited_question.text == "Test question!!!"
    assert edited_question.correct_answer_mark == 2
    action_log: m.Action = db.session.get(m.Action, 2)
    assert action_log
    assert action_log.action == m.ActionsType.EDIT
    res_quiz: TestResponse = client.delete(
        "/quiz/delete/1",
        follow_redirects=True,
    )
    assert res_quiz
    assert res_quiz.status_code == 200
    deleted_question: m.Question = db.session.query(m.Question).first()
    assert deleted_question.is_deleted
    delete_action_log: m.Action = db.session.get(m.Action, 3)
    assert delete_action_log
    assert delete_action_log.action == m.ActionsType.DELETE
