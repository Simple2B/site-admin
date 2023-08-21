import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app, db
from app.common import models as m
from tests.utils import register


@pytest.fixture()
def app():
    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app: Flask, mocker):
    mocker.patch("app.views.case.notify_case_created", return_value=None)

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()

        db.drop_all()
        db.create_all()
        register()

        yield client
        db.drop_all()
        app_ctx.pop()


@pytest.fixture()
def runner(app, client):
    from app import commands

    commands.init(app)

    yield app.test_cli_runner()


@pytest.fixture
def populate(client: FlaskClient):
    NUM_TEST_USERS = 15
    with db.begin() as session:
        for i in range(NUM_TEST_USERS):
            user = m.SuperUser(
                username=f"user{i+1}",
                email=f"user{i+1}@mail.com",
                password="password",
            )
            session.add(user)
    yield client
