from flask import Response, current_app as app
from flask.testing import FlaskClient, FlaskCliRunner
from click.testing import Result
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
    response: Response = client.post(
        "/quiz/save",
        data=dict(
            id=question.id,
            uid=question.uid,
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


# def test_delete_user(populate: FlaskClient):
#     login(populate)
#     uc = db.session.query(m.SuperUser).count()
#     response = populate.delete("/user/delete/1")
#     assert db.session.query(m.SuperUser).count() < uc
#     assert response.status_code == 200
