from app.common import models as m
from app import db
from tests.utils import login


add_stacks = {
    "stacks": "JS,Python,TS, Flask",
}

delete_stack = {
    "stacks": "Flask",
}


def test_create_delete(client):
    login(client)
    res = client.post("/stack/create", data=add_stacks)
    assert res.status_code == 200
    count = db.session.query(m.Stack).count()
    assert count == 4
    res = client.delete(f"/stack/delete/{4}", data=delete_stack)
    assert res.status_code == 200
    assert db.session.query(m.Stack).count() == 3
