import sqlalchemy as sa
from app.common import models as m
from app import db
from tests.utils import login


def test_crud_feedback(client):
    login(client)
    fds = db.session.scalars(sa.select(m.FeedBack)).all()
    assert not fds

    res  = client.get("/feedbacks/get_add_form")
    assert res.status_code == 200
    assert "Add feedback" in res.data.decode()

    feedback = {
        "client_name": "test client",
        "project_name": "test project",
        "link": "https://test.com",
        "language": m.Languages.ENGLISH.value,
    }
    res = client.post("/feedbacks/add", data=feedback)
    assert res.status_code == 200
    feedback = db.session.get(m.FeedBack, 1)
    assert feedback
    assert feedback.client_name == "test client"
    assert feedback.project_name == "test project"
    assert feedback.link == "https://test.com"
    assert feedback.language == m.Languages.ENGLISH.value

    res = client.get("/feedbacks/")
    assert res.status_code == 200
    html = res.data.decode()
    assert feedback.client_name in html


    res = client.get(f"/feedback/get_edit_form/{feedback.uuid}")
    assert res.status_code == 200
    assert "Edit feedback" in res.data.decode()

    feedback['uuid'] = feedback.uuid
    feedback['client_name'] = "updated client"


    res = client.post("/feedback/edit", data=feedback)
    assert res.status_code == 200
    feedback = db.session.get(m.FeedBack, 1)
    assert feedback
    assert feedback.client_name == "updated client"

    res = client.delete(f"/feedback/delete/{feedback.id}")
    assert res.status_code == 200
    feedback = db.session.get(m.FeedBack, 1)
    assert not feedback