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


bp = Blueprint("case", __name__, url_prefix="/case")


@bp.route("/", methods=["GET", "POST"])
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
            .where(m.Case.title.like(f"{q}%") & m.Case.is_deleted==False)
            .order_by(m.Case.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(m.Case.title.like(f"{q}%") & m.Case.is_deleted==False)
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
        new_case = m.Case(
            title=form.title.data,
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
        log(log.INFO, "Form submitted. case: [%s]", new_case.title)
        flash("Case added!", "success")
    if form.errors:
        log(log.ERROR, "Case errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
    return redirect(url_for("case.get_all"))


@bp.route("/save", methods=["POST"])
@login_required
def save():
    form = f.UserForm()
    if form.validate_on_submit():
        query = m.SuperUser.select().where(m.SuperUser.id == int(form.user_id.data))
        u: m.SuperUser | None = db.session.scalar(query)
        if not u:
            log(log.ERROR, "Not found user by id : [%s]", form.SuperUser_id.data)
            flash("Cannot save user data", "danger")
        u.username = form.username.data
        u.email = form.email.data
        u.activated = form.activated.data
        if form.password.data.strip("*\n "):
            u.password = form.password.data
        u.save()
        if form.next_url.data:
            return redirect(form.next_url.data)
        return redirect(url_for("user.get_all"))

    else:
        log(log.ERROR, "User save errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("user.get_all"))


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    u = db.session.scalar(m.Case.select().where(m.Case.id == id))
    if not u:
        log(log.INFO, "There is no case with id: [%s]", id)
        flash("There is no such case", "danger")
        return "no case", 404

    u.is_deleted = True
    db.session.commit()
    log(log.INFO, "Case deleted. Case: [%s]", u)
    flash("Case deleted!", "success")
    return "ok", 200
