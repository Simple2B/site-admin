from flask import current_app as app
from flask.testing import FlaskClient
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
        m.SuperUser.select().order_by(m.SuperUser.id).limit(10)
    ).all()
    assert len(users) == 10
    for user in users[:DEFAULT_PAGE_SIZE]:
        assert user.username in html
    assert users[9].username not in html

    populate.application.config["PAGE_LINKS_NUMBER"] = 6
    response = populate.get("/admin/?page=6")
    assert response
    assert response.status_code == 200


def test_delete_user(populate: FlaskClient):
    login(populate)
    response = populate.delete("/admin/delete/1")
    deleted_admin = db.session.query(m.SuperUser).filter_by(id=1)
    assert deleted_admin
    assert deleted_admin[0].is_deleted
    action_log: m.Action = db.session.get(m.Action, 1)
    assert action_log.action == m.ActionsType.DELETE
    assert response.status_code == 200
