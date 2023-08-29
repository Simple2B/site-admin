# flake8: noqa E712
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
import sqlalchemy as sa
from werkzeug.datastructures import FileStorage
import botocore

from app.common.models.case_image import EnumCaseImageType
from app.controllers import create_pagination

from app.common import models as m
from app import schema as s
from app import forms as f
from app.controllers import notify_case_created
from app.logger import log
from app.database import db
from app import s3bucket
from app.controllers import ActionLogs


bp = Blueprint("case", __name__, url_prefix="/case")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    form = f.NewCaseForm()
    form.stacks.choices = [(str(s.id), s.name) for s in db.session.query(m.Stack).all()]
    q = request.args.get("q", type=str, default=None)
    query = m.Case.select().where(m.Case.is_deleted == False).order_by(m.Case.id)
    count_query = (
        sa.select(sa.func.count()).where(m.Case.is_deleted == False).select_from(m.Case)
    )

    if q:
        query = (
            m.Case.select()
            .where(sa.and_(m.Case.title.ilike(f"%{q}%"), m.Case.is_deleted == False))
            .order_by(m.Case.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(sa.and_(m.Case.title.ilike(f"%{q}%"), m.Case.is_deleted == False))
            .select_from(m.Case)
        )

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "case/cases.html",
        cases=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
        form=form,
    )


@bp.route("/<int:id>", methods=["GET"])
@login_required
def get_case(id: int):
    case: m.Case = db.session.scalar(m.Case.select().where(m.Case.id == id))
    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    return s.CaseOut.from_orm(case).json(by_alias=True)


@bp.route("/create", methods=["POST"])
@login_required
def create():
    form = f.NewCaseForm()
    form.stacks.choices = [(str(s.id), s.name) for s in db.session.query(m.Stack).all()]
    if form.validate_on_submit():
        log(log.INFO, "Form submitted. Case: [%s]", form)
        session = db.session

        title: str = form.title.data
        main_image_obj: FileStorage = form.title_image.data
        preview_image_obj: FileStorage = form.sub_title_image.data
        case_screenshots: list[FileStorage] = form.sub_images.data

        try:
            main_image_url = s3bucket.upload_cases_imgs(
                file=main_image_obj,
                file_name=main_image_obj.filename,
                case_name=title,
                img_type=EnumCaseImageType.case_main_image.value,
            )
            preview_image_url = s3bucket.upload_cases_imgs(
                file=preview_image_obj,
                file_name=preview_image_obj.filename,
                case_name=title,
                img_type=EnumCaseImageType.case_preview_image.value,
            )

            screenshots_urls: list[str] = []

            for screenshot in case_screenshots:
                file_image = s3bucket.upload_cases_imgs(
                    file=screenshot,
                    file_name=screenshot.filename,
                    case_name=title,
                    img_type="screenshots",
                )
                screenshots_urls.append(file_image)
        except TypeError as error:
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))

        new_case = m.Case(
            title=form.title.data,
            sub_title=form.sub_title.data,
            description=form.description.data,
            is_active=form.is_active.data,
            is_main=form.is_main.data,
            project_link=form.project_link.data,
            role=form.role.data,
        )
        session.add(new_case)
        session.commit()
        session.refresh(new_case)
        ActionLogs.create_case_log(m.ActionsType.CREATE, new_case.id)

        for index, img in enumerate(screenshots_urls):
            new_screenshot = m.CaseScreenshot(
                url=img,
                case_id=new_case.id,
                origin_file_name=f"screenshot_{index}",
            )

            session.add(new_screenshot)
            session.commit()

        if main_image_url and preview_image_url:
            new_main_image = m.CaseImage(
                url=main_image_url,
                origin_file_name=main_image_obj.filename,
                case_id=new_case.id,
                type_of_image=EnumCaseImageType.case_main_image,
            )
            new_preview_image = m.CaseImage(
                url=preview_image_url,
                origin_file_name=preview_image_obj.filename,
                case_id=new_case.id,
                type_of_image=EnumCaseImageType.case_preview_image,
            )

            session.add(new_main_image)
            session.add(new_preview_image)
            session.commit()
        else:
            flash("No uploaded image", "danger")
            return redirect(url_for("case.get_all"))

        for id in form.stacks.data:
            new_stack = m.CaseStack(case_id=new_case.id, stack_id=int(id))
            session.add(new_stack)
        session.commit()

        # notify_case_created(new_case) this will be provided in new version
        log(log.INFO, "Case created. Case: [%s]", new_case)
        flash("Case added!", "success")

    if form.errors:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
    return redirect(url_for("case.get_all"))


@bp.route("/update-status/<int:id>", methods=["PATCH"])
@login_required
def update_case_status(id: int):
    form = f.UpdateCaseState()
    case = db.session.get(m.Case, id)

    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    if not form.validate_on_submit():
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return "error", 422

    field = form.field.data
    if field == "is_active":
        case.is_active = not case.is_active
    if field == "is_main":
        case.is_main = not case.is_main
    db.session.commit()
    log(log.INFO, "Case updated. Case: [%s]", case)
    ActionLogs.create_case_log(m.ActionsType.EDIT, case.id)
    flash("Case updated!", "success")
    return "ok", 200


@bp.route("/update", methods=["POST"])
@login_required
def update_case():
    form = f.UpdateCase()
    form.stacks.choices = [(str(s.id), s.name) for s in db.session.query(m.Stack).all()]
    if not form.validate_on_submit():
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("case.get_all"))
    case = db.session.get(m.Case, form.case_id.data)
    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return redirect(url_for("case.get_all"))

    main_image_obj: FileStorage = form.main_image.data
    if main_image_obj:
        try:
            s3bucket.delete_cases_imgs(case.main_image_url)
        except botocore.exceptions.ClientError:
            log(log.ERROR, "Can't delete main image in case: [%s]", case.id)
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))
        try:
            main_image_url = s3bucket.upload_cases_imgs(
                file=main_image_obj,
                file_name=main_image_obj.filename,
                case_name=form.title.data,
                img_type=EnumCaseImageType.case_main_image.value,
            )
        except TypeError as error:
            log(log.ERROR, "Can't upload main image in case: [%s]", case.id)
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))
        db.session.add(
            m.CaseImage(
                url=main_image_url,
                origin_file_name=main_image_obj.filename,
                case_id=case.id,
                type_of_image=EnumCaseImageType.case_main_image,
            )
        )

    preview_image_obj: FileStorage = form.preview_image.data
    if preview_image_obj:
        try:
            s3bucket.delete_cases_imgs(case.preview_image_url)
        except botocore.exceptions.ClientError:
            log(log.ERROR, "Can't delete preview image in case: [%s]", case.id)
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))
        try:
            preview_image_url = s3bucket.upload_cases_imgs(
                file=preview_image_obj,
                file_name=preview_image_obj.filename,
                case_name=form.title.data,
                img_type=EnumCaseImageType.case_preview_image.value,
            )
        except TypeError as error:
            log(log.ERROR, "Can't upload preview image in case: [%s]", case.id)
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))

        db.session.add(
            m.CaseImage(
                url=preview_image_url,
                origin_file_name=preview_image_obj.filename,
                case_id=case.id,
                type_of_image=EnumCaseImageType.case_preview_image,
            )
        )
    sub_images = form.screenshots.data
    if sub_images:
        for idx, screenshot in enumerate(sub_images):
            if screenshot.content_type == "application/octet-stream":
                continue
            try:
                screenshot_image_url = s3bucket.upload_cases_imgs(
                    file=screenshot,
                    file_name=screenshot.filename,
                    case_name=form.title.data,
                    img_type="screenshots",
                )
            except TypeError as error:
                log(log.ERROR, "Can't upload sub image in case: [%s]", case.id)
                continue
            new_screenshot = m.CaseScreenshot(
                url=screenshot_image_url,
                case_id=case.id,
                origin_file_name=f"screenshot_{idx}",
            )
            db.session.add(new_screenshot)

    case.title = form.title.data
    case.sub_title = form.sub_title.data
    case.description = form.description.data
    case.is_active = form.is_active.data
    case.is_main = form.is_main.data
    case.project_link = form.project_link.data
    case.role = form.role.data

    cases_stacks_ids = set(s.id for s in case.stacks)
    form_stacks_ids = set(int(id) for id in form.stacks.data)

    # delete stacks form case
    for id in cases_stacks_ids.difference(form_stacks_ids):
        db.session.query(m.CaseStack).filter(
            m.CaseStack.case_id == case.id, m.CaseStack.stack_id == int(id)
        ).delete()

    # add stacks to case
    for stack_id in form_stacks_ids.difference(cases_stacks_ids):
        if stack_id not in cases_stacks_ids:
            new_stack = m.CaseStack(case_id=case.id, stack_id=int(stack_id))
            db.session.add(new_stack)
    db.session.commit()

    log(log.INFO, "Case updated. Case: [%s]", case)
    ActionLogs.create_case_log(m.ActionsType.EDIT, case.id)
    flash("Case updated!", "success")
    return redirect(url_for("case.get_all"))


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    case = db.session.get(m.Case, id)
    if not case or case.is_deleted:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404
    delete_datetime = datetime.now().strftime("%m/%d/%Y")
    case.is_deleted = True
    case.title = f"{case.title}@d_{delete_datetime}"
    db.session.commit()
    ActionLogs.create_case_log(m.ActionsType.DELETE, case.id)
    log(log.INFO, "Case deleted. Case: [%s]", case)
    return "ok", 200


@bp.route("/delete/<int:id>/screenshot", methods=["DELETE"])
@login_required
def delete_screenshot(id: int):
    case_screenshot: m.CaseScreenshot = db.session.get(m.CaseScreenshot, id)
    if not case_screenshot:
        log(log.INFO, "There is no case screenshot with id: [%s]", id)
        flash("There is no such case screenshot", "danger")
        return "no case", 404

    try:
        s3bucket.delete_cases_imgs(case_screenshot.url)
    except TypeError:
        log(log.ERROR, "Can't delete case screenshot: [%s]", case_screenshot.id)
        return "Can't delete case screenshot", 422

    case_id = case_screenshot.case_id
    db.session.delete(case_screenshot)
    db.session.commit()
    ActionLogs.create_case_log(m.ActionsType.EDIT, case_id)
    log(log.INFO, "Case screenshot deleted. Case: [%s]", case_id)
    return "ok", 200
