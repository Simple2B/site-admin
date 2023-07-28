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


bp = Blueprint("candidate", __name__, url_prefix="/candidate")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = m.Candidate.select().order_by(m.Candidate.id)
    count_query = sa.select(sa.func.count()).select_from(m.Candidate)
    if q:
        query = (
            m.Candidate.select()
            .where(m.Candidate.username.like(f"{q}%") | m.Candidate.email.like(f"{q}%"))
            .order_by(m.Candidate.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(m.Candidate.username.like(f"{q}%") | m.Candidate.email.like(f"{q}%"))
            .select_from(m.Candidate)
        )

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "candidate/candidates.html",
        candidates=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
    )


@bp.route("/save", methods=["POST"])
@login_required
def save():
    form = f.UserForm()
    if form.validate_on_submit():
        query = m.SuperUser.select().where(m.SuperUser.id == int(form.user_id.data))
        u: m.SuperUser | None = db.session.scalar(query)
        if not u:
            log(log.ERROR, "Not found admin by id : [%s]", form.SuperUser_id.data)
            flash("Cannot save admin data", "danger")
        u.username = form.username.data
        u.email = form.email.data
        u.activated = form.activated.data
        if form.password.data.strip("*\n "):
            u.password = form.password.data
        u.save()
        if form.next_url.data:
            return redirect(form.next_url.data)
        return redirect(url_for("admin.get_all"))

    else:
        log(log.ERROR, "admin save errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("admin.get_all"))


@bp.route("/create", methods=["POST"])
@login_required
def create():
    form = f.NewUserForm()
    if form.validate_on_submit():
        admin = m.SuperUser(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            activated=form.activated.data,
        )
        log(log.INFO, "Form submitted. admin: [%s]", admin)
        flash("admin added!", "success")
        admin.save()
        return redirect(url_for("admin.get_all"))


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    u = db.session.scalar(m.SuperUser.select().where(m.SuperUser.id == id))
    if not u:
        log(log.INFO, "There is no admin with id: [%s]", id)
        flash("There is no such admin", "danger")
        return "no admin", 404

    db.session.delete(u)
    db.session.commit()
    log(log.INFO, "admin deleted. admin: [%s]", u)
    flash("admin deleted!", "success")
    return "ok", 200
