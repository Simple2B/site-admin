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


bp = Blueprint("action", __name__, url_prefix="/action")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = m.Action.select().order_by(m.Action.created_at.desc())
    count_query = sa.select(sa.func.count()).select_from(m.Action)
    if q:
        query = m.Action.select().order_by(m.Action.created_at.decs())
        count_query = sa.select(sa.func.count()).select_from(m.Action)

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "action/actions.html",
        actions=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
    )
