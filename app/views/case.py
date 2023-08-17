# flake8: noqa E712
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import sqlalchemy as sa
from werkzeug.datastructures import FileStorage
from app.common.models.case_image import EnumCaseImageType
from app.controllers import create_pagination

from app.common import models as m
from app import schema as s
from app import forms as f
from app.controllers import case_created_notify
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

    return s.CaseOut.from_orm(case).json()


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
                img_type=EnumCaseImageType.case_main_image,
            )
            preview_image_url = s3bucket.upload_cases_imgs(
                file=preview_image_obj,
                file_name=preview_image_obj.filename,
                case_name=title,
                img_type=EnumCaseImageType.case_preview_image,
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

        case_created_notify(new_case)
        log(log.INFO, "Case created. Case: [%s]", new_case)
        flash("Case added!", "success")

    if form.errors:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
    return redirect(url_for("case.get_all"))


@bp.route("/update-status/<int:id>", methods=["PATCH"])
@login_required
def update_case_status(id: int):
    form = f.UpdateCase()
    case = db.session.get(m.Case, id)

    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    if form.validate_on_submit():
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
    else:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return "error", 422


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    case = db.session.get(m.Case, id)
    if not case or case.is_deleted:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    case.is_deleted = True
    db.session.commit()
    ActionLogs.create_case_log(m.ActionsType.DELETE, case.id)
    log(log.INFO, "Case deleted. Case: [%s]", case)
    return "ok", 200
