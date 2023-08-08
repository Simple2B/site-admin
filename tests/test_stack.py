from app.common import models as m
from app import db
from tests.utils import login


add_stacks = {
    "stacks": "JS,Python,TS, Flask",
}

delete_stack = {
    "stacks": "Flask",
}


def test_create(client):
    login(client)
    res = client.post("/stack/create", data=add_stacks)
    assert res.status_code == 200
    assert db.session.query(m.Stack).count() == 4


def test_delete(client):
    login(client)
    res = client.delete("/stack/delete", data=delete_stack)
    assert res.status_code == 200
