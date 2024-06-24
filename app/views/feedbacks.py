from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination
from app import forms as f
from app.common import models as m
from app.database import db
from app.logger import log


bp = Blueprint("feedback", __name__, url_prefix="/feedbacks")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = sa.select(m.FeedBack).order_by(m.FeedBack.id.desc())
    count_query = sa.select(sa.func.count()).select_from(m.FeedBack)
    if q:
        query = (
            sa.select(m.FeedBack)
            .where(m.FeedBack.client_name.like(f"%{q}%"))
            .order_by(m.FeedBack.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(m.FeedBack.client_name.like(f"{q}%"))
            .group_by(m.FeedBack.id)
            .order_by(m.FeedBack.id)
        )

    pagination = create_pagination(total=db.session.scalar(count_query) or 0)

    return render_template(
        "feedback/feedbacks.html",
        feedbacks=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
    )


@bp.route("/add", methods=["GET"])
@login_required
def get_add_form():
    """htmx"""
    form = f.NewFeedBackForm()
    return render_template("feedback/add_feedback.html", form=form)


@bp.route("/add", methods=["POST"])
@login_required
def add():
    form = f.NewFeedBackForm()
    if not form.validate_on_submit():
        log(log.ERROR, "Form validation failed")
        flash(f"Form validation failed {form.errors}", "danger")
        return redirect(url_for("feedback.get_all"))
    feedback = m.FeedBack(**form.data)
    db.session.add(feedback)
    db.session.commit()

    return redirect(url_for("feedback.get_all"))


@bp.route("/edit/<uuid>", methods=["GET"])
@login_required
def get_edit_form(uuid: str):
    """htmx"""
    feedback = db.session.scalar(sa.select(m.FeedBack).where(m.FeedBack.uuid == uuid))
    if not feedback:
        log(log.ERROR, f"Feedback with uuid {uuid} not found")
        return render_template(
            "toast.html", message="Feedback not found", category="danger"
        )

    form = f.EditFeedBackForm(obj=feedback)
    return render_template("feedback/edit_feedback.html", form=form)


@bp.route("/edit", methods=["POST"])
@login_required
def edit():
    form = f.EditFeedBackForm()
    if not form.validate_on_submit():
        log(log.ERROR, "Form validation failed")
        flash(f"Form validation failed {form.errors}", "danger")
        return redirect(url_for("feedback.get_all"))
    feedback = db.session.scalar(
        sa.select(m.FeedBack).where(m.FeedBack.uuid == form.uuid.data)
    )
    if not feedback:
        log(log.ERROR, f"Feedback with uuid {feedback.uuid.data} not found")
        flash("Feedback not found", "danger")
        return redirect(url_for("feedback.get_all"))

    feedback.client_name = form.client_name.data
    feedback.project_name = form.project_name.data
    feedback.link = form.link.data
    feedback.language = form.language.data
    feedback.comment = form.comment.data
    db.session.commit()

    flash("Feedback updated successfully", "success")
    return redirect(url_for("feedback.get_all"))


@bp.route("/delete/<uuid>", methods=["DELETE"])
@login_required
def delete(uuid: str):
    """htmx"""
    feedback = db.session.scalar(sa.select(m.FeedBack).where(m.FeedBack.uuid == uuid))
    if not feedback:
        log(log.ERROR, f"Feedback with uuid {uuid} not found")
        return render_template(
            "toast.html", message="Feedback not found", category="danger"
        )

    db.session.delete(feedback)
    db.session.commit()
    return render_template("toast.html", message="Feedback deleted", category="success")
