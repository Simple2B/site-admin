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
    query = m.Case.select().where(m.Case.is_deleted==False).order_by(m.Case.id)
    count_query = sa.select(sa.func.count()).where(m.Case.is_deleted==False).select_from(m.Case)

    if q:
        query = (
            m.Case.select()
            .where(sa.and_(m.Case.title.ilike(f"%{q}%"), m.Case.is_deleted==False))
            .order_by(m.Case.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(sa.and_(m.Case.title.ilike(f"%{q}%"), m.Case.is_deleted==False))
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

        title = form.title.data
        title_image = form.title_image.data
        sub_title_image = form.sub_title_image.data
        try:
            title_image = s3bucket.upload_cases_imgs(file=title_image, file_name=title_image.filename, case_name=title, img_type='title')
            sub_title_image = s3bucket.upload_cases_imgs(file=sub_title_image, file_name=sub_title_image.file_name, case_name=title, img_type='sub_title')
        except TypeError as error:
            flash(error.args[0], "danger")
            return redirect(url_for("case.get_all"))

        session = db.session
        new_case = m.Case(
            title=form.title.data,
            title_image_url=title_image,
            sub_title_image_url=sub_title_image,
            sub_title=form.sub_title.data,
            description=form.description.data,
            is_active=form.is_active.data,
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

        for img in form.sub_images.data:
            try:
                sub_image = s3bucket.upload_cases_imgs(file=img, file_name=img.filename, case_name=title, img_type='sub_image')
            except (TypeError, AttributeError):
                continue
            if sub_image:
                new_sub_image = m.CaseImage(case_id=new_case.id, url=sub_image[1])
                session.add(new_sub_image)
        session.commit()

        flash("Case added!", "success")
    if form.errors:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
    return redirect(url_for("case.get_all"))


@bp.route("/update/<int:id>", methods=["PATCH"])
@login_required
def update(id: int):
    case = db.session.get(m.Case,id)
    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    case.is_active = not case.is_active
    db.session.commit()
    log(log.INFO, "Case updated. Case: [%s]", case)
    flash("Case updated!", "success")
    return "ok", 200


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    case = db.session.get(m.Case,id)
    if not case:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    case.is_deleted = True
    db.session.commit()
    log(log.INFO, "Case deleted. Case: [%s]", case)
    flash("Case deleted!", "success")
    return "ok", 200
