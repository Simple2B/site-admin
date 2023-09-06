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
    "germany_title": "test title",
    "germany_sub_title": "test sub title",
    "germany_description": "test description",
    "germany_role": "test role",
}


stack = {"name": "django"}


def test_crud_case(client, mocker):
    login(client)
    # create
    stack = m.Stack(name="django")
    db.session.add(stack)
    db.session.commit()
    test_case.update({"stacks": [stack.id]})
    mocker.patch.object(s3bucket, "upload_cases_imgs", return_value="https://test.com")
    mocker.patch.object(s3bucket, "delete_cases_imgs", return_value="https://test.com")
    mocker.patch.object(filetype, "is_image", return_value=True)
    mocker.patch.object(filetype, "guess", return_value=True)
    res = client.post(
        "/case/create", data=test_case, content_type="multipart/form-data"
    )

    assert res.status_code == 302
    case: m.Case | None = db.session.get(m.Case, 1)
    assert case
    assert case.germany_translation

    case_translation: m.CaseTranslation | None = db.session.get(m.CaseTranslation, 1)
    assert case_translation
    assert case_translation.case_id == case.id

    # case: m.Case | None = db.session.get(m.Case, case.id)
    # assert case.stacks_names == ["django"]

    action_log_count = db.session.query(m.Action).count()
    assert action_log_count == 1

    # read
    res = client.get("/case/")
    assert res.status_code == 200
    html = res.data.decode()
    assert test_case["title"] in html

    # update active and main
    case: m.Case | None = db.session.get(m.Case, 1)
    assert case.is_active == test_case["is_active"]
    res = client.patch(f"/case/update-status/{case.id}", data={"field": "is_active"})
    assert res.status_code == 200
    new_action_log_count = db.session.query(m.Action).count()
    assert new_action_log_count == action_log_count + 1
    assert not case.is_active

    # update full case
    res = client.post(
        "/case/update",
        data={
            "is_active": True,
            "title": "new title",
            "case_id": case.id,
            "role": "test role",
            "sub_title": "test sub title",
            "description": "test description",
            "project_link": "https://test.com",
            "stacks": [stack.id],
            "germany_title": "test germany title",
            "germany_sub_title": "test germany sub title",
            "germany_description": "test germany description",
            "germany_role": "test germany role",
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 302
    assert case.title == "new title"
    assert case.is_active
    # get case by id
    res = client.get(f"/case/{case.id}")
    assert res.status_code == 200
    case_translation: m.CaseTranslation | None = db.session.get(m.CaseTranslation, 1)
    assert case_translation.title == "test germany title"

    # test delete case screenshot
    assert case.screenshots
    res = client.delete(f"/case/delete/{case.screenshots[0].id}/screenshot")
    assert res.status_code == 200
    assert not case.screenshots

    # delete
    assert not case.is_deleted
    res = client.delete(f"/case/delete/{case.id}")
    assert case.is_deleted
    delete_action_log: m.Action | None = db.session.get(
        m.Action, new_action_log_count + 3
    )
    assert delete_action_log.action == m.ActionsType.DELETE
