from flask import current_app as app, Response
from flask.testing import FlaskClient, FlaskCliRunner
from click.testing import Result
from app.common import models as m
from tests.utils import login
from app.database import db


def test_list(populate: FlaskClient):
    login(populate)
    DEFAULT_PAGE_SIZE = app.config["DEFAULT_PAGE_SIZE"]
    response = populate.get("/admin/")
    assert response
    assert response.status_code == 200
    html = response.data.decode()
    users = db.session.scalars(
        m.SuperUser.select().order_by(m.SuperUser.id).limit(11)
    ).all()
    assert len(users) == 11
    for user in users[:DEFAULT_PAGE_SIZE]:
        assert user.username in html
    assert users[10].username not in html

    populate.application.config["PAGE_LINKS_NUMBER"] = 6
    response = populate.get("/admin/?page=6")
    assert response
    assert response.status_code == 200
    html = response.data.decode()
    assert "/admin/?page=6" in html
    assert "/admin/?page=3" in html
    assert "/admin/?page=8" in html
    assert "/admin/?page=10" not in html
    assert "/admin/?page=2" not in html


def test_create_admin(runner: FlaskCliRunner, client: FlaskClient):
    res: Result = runner.invoke(args=["create-admin"])
    assert "admin created" in res.output
    query = m.SuperUser.select().where(
        m.SuperUser.username == app.config["ADMIN_USERNAME"]
    )
    assert db.session.scalar(query)
    login(client)
    response: Response = client.post(
        "/admin/create",
        data=dict(
            username="admin_2",
            email="admin_2@gmail.com",
            password="123456",
            password_confirmation="123456",
        ),
        follow_redirects=True,
    )
    assert response
    assert response.status_code == 200
    action_log: m.Action = db.session.get(m.Action, 1)
    assert action_log.action == m.ActionsType.CREATE


def test_delete_user(populate: FlaskClient):
    login(populate)
    response = populate.delete("/admin/delete/1")
    deleted_admin = db.session.query(m.SuperUser).filter_by(id=1)
    assert deleted_admin
    assert deleted_admin[0].is_deleted
    action_log: m.Action = db.session.get(m.Action, 1)
    assert action_log.action == m.ActionsType.DELETE
    assert response.status_code == 200
