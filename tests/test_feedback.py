import sqlalchemy as sa
from app.common import models as m
from app import db
from tests.utils import login


def test_crud_feedback(client):
    login(client)
    fds = db.session.scalars(sa.select(m.FeedBack)).all()
    assert not fds

    res  = client.get("/feedbacks/add")
    assert res.status_code == 200
    assert "Add feedback" in res.data.decode()

    feedback_data = {
        "client_name": "test client",
        "project_name": "test project",
        "link": "https://test.com",
        "language": m.Languages.ENGLISH.value,
        'comment': 'test comment',
    }
    res = client.post("/feedbacks/add", data=feedback_data, follow_redirects=True)
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


    res = client.get(f"/feedbacks/edit/{feedback.uuid}")
    assert res.status_code == 200
    assert "Edit feedback" in res.data.decode()

    feedback_data['uuid'] = feedback.uuid
    feedback_data['client_name'] = "updated client"


    res = client.post("/feedbacks/edit", data=feedback_data, follow_redirects=True)
    assert res.status_code == 200
    feedback = db.session.get(m.FeedBack, 1)
    assert feedback
    assert feedback.client_name == "updated client"

    res = client.delete(f"/feedbacks/delete/{feedback.uuid}")
    assert res.status_code == 200
    feedback = db.session.get(m.FeedBack, 1)
    assert not feedback