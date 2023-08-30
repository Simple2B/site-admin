# flake8: noqa E712
from datetime import datetime

from flask import Blueprint, render_template, request, current_app, flash
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
from app.database import db
from app.logger import log
from app.controllers import ActionLogs


bp = Blueprint("candidate", __name__, url_prefix="/candidate")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = (
        m.Candidate.select()
        .where(m.Candidate.is_deleted == False)
        .order_by(m.Candidate.id)
    )
    count_query = (
        sa.select(sa.func.count())
        .where(m.Candidate.is_deleted == False)
        .select_from(m.Candidate)
    )
    if q:
        query = (
            m.Candidate.select()
            .where(
                sa.and_(
                    m.Candidate.username.ilike(f"%{q}%")
                    | m.Candidate.email.ilike(f"%{q}%"),
                    m.Candidate.is_deleted == False,
                )
            )
            .order_by(m.Candidate.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(
                sa.and_(
                    m.Candidate.username.ilike(f"%{q}%")
                    | m.Candidate.email.ilike(f"%{q}%"),
                    m.Candidate.is_deleted == False,
                )
            )
            .select_from(m.Candidate)
        )

    question_count = current_app.config["QUESTIONS_COUNT"]

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
        count=question_count,
    )


@bp.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete(id: int):
    candidate = db.session.scalar(m.Candidate.select().where(m.Candidate.id == id))
    if not candidate:
        log(log.INFO, "There is no candidate with id: [%s]", id)
        flash("There is no such candidate", "danger")
        return "no candidate", 404
    delete_datetime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    candidate.is_deleted = True
    candidate.email = f"{candidate.email}@{delete_datetime}"
    candidate.git_hub_id = f"{candidate.git_hub_id}@{delete_datetime}"
    candidate.username = f"{candidate.username}@deleted_{delete_datetime}"
    db.session.commit()
    ActionLogs.create_candidate_log(candidate.id)

    log(log.INFO, "Candidate deleted. Candidate: [%s]", candidate)
    flash("User deleted!", "success")
    return "ok", 200
