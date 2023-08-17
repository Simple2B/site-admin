# flake8: noqa E712
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
from app import forms as f
from app.logger import log
from app.database import db
from app.controllers.actions import admin_action_log


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = (
        m.SuperUser.select()
        .where(m.SuperUser.is_deleted == False)
        .order_by(m.SuperUser.id)
    )
    count_query = (
        sa.select(sa.func.count())
        .where(m.SuperUser.is_deleted == False)
        .select_from(m.SuperUser)
    )
    if q:
        query = (
            m.SuperUser.select()
            .where(
                sa.and_(
                    m.SuperUser.username.ilike(f"%{q}%")
                    | m.SuperUser.email.ilike(f"%{q}%"),
                    m.SuperUser.is_deleted == False,
                )
            )
            .order_by(m.SuperUser.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(
                sa.and_(
                    m.SuperUser.username.like(f"{q}%")
                    | m.SuperUser.email.like(f"{q}%"),
                    m.SuperUser.is_deleted == False,
                )
            )
            .select_from(m.SuperUser)
        )

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "admin/admins.html",
        admins=db.session.execute(
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
        return redirect(url_for("admin.get_all"))

    else:
        log(log.ERROR, "User save errors: [%s]", form.errors)
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
        )
        log(log.INFO, "Form submitted. Admin: [%s]", admin)
        flash("User added!", "success")
        admin.save()
        admin_action_log(m.ActionsType.CREATE, admin.id, current_user.id)
        return redirect(url_for("admin.get_all"))
    else:
        log(log.ERROR, "Admin save errors: [%s]", form.errors)
        flash(f"{form.errors}", "danger")
        return redirect(url_for("admin.get_all"))


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    admin = db.session.scalar(m.SuperUser.select().where(m.SuperUser.id == id))
    if not admin:
        log(log.INFO, "There is no admin with id: [%s]", id)
        flash("There is no such admin", "danger")
        return "no admin", 404
    admin.is_deleted = True
    db.session.add(admin)
    db.session.commit()
    admin_action_log(m.ActionsType.DELETE, admin.id, current_user.id)

    log(log.INFO, "Admin deleted. Admin: [%s]", admin)
    flash("User deleted!", "success")
    return "ok", 200
