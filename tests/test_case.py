import filetype
from app.common import models as m
from app import db
import io
from tests.utils import login
from app import s3bucket

test_case = {
    "title": "test title",
    "case_id": "1",
    "type_of_image": "main_image",
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

    # read
    res = client.get("/case/")
    assert res.status_code == 200
    html = res.data.decode()
    assert test_case["title"] in html

    # update
    case: m.Case = db.session.query(m.Case).get(1)
    assert case.is_active == test_case["is_active"]
    res = client.patch(f"/case/update/{case.id}", data={"field": "is_active"})
    assert not case.is_active

    # delete
    assert not case.is_deleted
    res = client.delete(f"/case/delete/{case.id}")
    assert case.is_deleted
