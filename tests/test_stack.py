from app.common import models as m
from app import db
from tests.utils import login


test_stacks = {
    "stacks": "JS,Python,TS, Flask",
}


def test_create(client):
    login(client)
    res = client.post('/stack/create', data=test_stacks)
    assert res.status_code == 200
    assert db.session.query(m.Stack).count() == 4
