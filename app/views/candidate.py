from flask import (
    Blueprint,
    render_template,
    request,
)
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
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
            .where(
                m.Candidate.username.ilike(f"%{q}%") | m.Candidate.email.ilike(f"%{q}%")
            )
            .order_by(m.Candidate.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(
                m.Candidate.username.ilike(f"%{q}%") | m.Candidate.email.ilike(f"%{q}%")
            )
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
