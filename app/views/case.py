# flake8: noqa E712
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
from app import forms as f
from app.logger import log
from app.database import db
from app import s3bucket


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


@bp.route("/create", methods=["POST"])
@login_required
def create():
    form = f.NewCaseForm()
    form.stacks.choices = [(str(s.id), s.name) for s in db.session.query(m.Stack).all()]

    if form.validate_on_submit():
        log(log.INFO, "Form submitted. Case: [%s]", form)
        session = db.session

        title = form.title.data
        title_image = form.title_image.data
        sub_title_image = form.sub_title_image.data
        try:
            main_image = s3bucket.upload_cases_imgs(
                file=title_image,
                file_name=title_image.filename,
                case_name=title,
                img_type="title",
            )
            full_main_image = s3bucket.upload_cases_imgs(
                file=sub_title_image,
                file_name=sub_title_image.filename,
                case_name=title,
                img_type="sub_title",
            )

            if main_image and full_main_image:
                new_main_image = m.CaseImage(
                    url=main_image, origin_file_name=title_image.filename
                )
                new_full_main_image = m.CaseImage(
                    url=full_main_image, origin_file_name=sub_title_image.filename
                )
                session.add(new_main_image)
                session.commit()
                session.refresh(new_main_image)
                session.add(new_full_main_image)
                session.commit()
                session.refresh(new_full_main_image)
                main_image_id = new_main_image.id
                full_main_image_id = new_full_main_image.id
            else:
                flash("No uploaded image", "danger")
                return redirect(url_for("case.get_all"))

        except TypeError as error:
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))

        new_case = m.Case(
            title=form.title.data,
            # title_image_url=title_image,
            # sub_title_image_url=sub_title_image,
            main_image_id=main_image_id,
            full_main_image_id=full_main_image_id,
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

        for id in form.stacks.data:
            new_stack = m.CaseStack(case_id=new_case.id, stack_id=int(id))
            session.add(new_stack)
        session.commit()

        # for img in form.sub_images.data:
        #     try:
        #         sub_image = s3bucket.upload_cases_imgs(
        #             file=img,
        #             file_name=img.filename,
        #             case_name=title,
        #             img_type="sub_image",
        #         )
        #     except (TypeError, AttributeError):
        #         continue
        #     if sub_image:
        #         new_sub_image = m.CaseImage(url=sub_image)
        #         session.add(new_sub_image)
        session.commit()

        flash("Case added!", "success")
    if form.errors:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
    return redirect(url_for("case.get_all"))


@bp.route("/update/<int:id>", methods=["PATCH"])
@login_required
def update(id: int):
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
    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    case.is_deleted = True
    db.session.commit()
    log(log.INFO, "Case deleted. Case: [%s]", case)
    flash("Case deleted!", "success")
    return "ok", 200
