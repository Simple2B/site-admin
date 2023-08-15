import filetype
from app.common import models as m
from app import db
import io
from tests.utils import login
from app import s3bucket

test_case = {
    "title": "test title",
    "case_id": "1",
    "type_of_image": "case_main_image",
    "sub_title": "test sub title",
    "title_image": (io.BytesIO(b"title"), "test.jpg"),
    "sub_title_image": (io.BytesIO(b"sub_title"), "test.jpg"),
    "description": "test description",
    "is_active": True,
    "project_link": "https://test.com",
    "role": "test role",
    "sub_images": [(io.BytesIO(b"sub_images"), "sub_images.jpg")],
}


def test_crud_case(client, mocker):
    login(client)
    # create
    mocker.patch.object(s3bucket, "upload_cases_imgs", return_value="https://test.com")
    mocker.patch.object(filetype, "is_image", return_value=True)
    mocker.patch.object(filetype, "guess", return_value=True)
    res = client.post(
        "/case/create", data=test_case, content_type="multipart/form-data"
    )
    assert res.status_code == 302
    case: m.Case = db.session.get(m.Case, 1)
    assert case
    action_log: m.Action = db.session.get(m.Action, 1)
    assert action_log.action == m.ActionsType.CREATE

    # read
    res = client.get("/case/")
    assert res.status_code == 200
    html = res.data.decode()
    assert test_case["title"] in html

    # update active and main
    case: m.Case = db.session.get(m.Case, 1)
    assert case.is_active == test_case["is_active"]
    res = client.patch(f"/case/update-status/{case.id}", data={"field": "is_active"})
    assert res.status_code == 200
    action_log: m.Action = db.session.get(m.Action, 2)
    assert action_log.action == m.ActionsType.EDIT
    assert not case.is_active

    # get case by id
    res = client.get(f"/case/{case.id}")
    assert res.status_code == 200

    # delete
    assert not case.is_deleted
    res = client.delete(f"/case/delete/{case.id}")
    assert case.is_deleted
    action_log: m.Action = db.session.get(m.Action, 3)
    assert action_log.action == m.ActionsType.DELETE
