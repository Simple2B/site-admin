from flask import (
    Blueprint,
    render_template,
    request,
)
from datetime import datetime, timedelta
from flask_login import login_required
import sqlalchemy as sa
from app.controllers import create_pagination

from app.common import models as m
from app.database import db


bp = Blueprint("action", __name__, url_prefix="/action")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    sort = request.args.get("sort")
    entity = request.args.get("entity")
    thirty_days_ago = datetime.now() - timedelta(days=30)
    query = (
        m.Action.select()
        .where(m.Action.created_at > thirty_days_ago)
        .order_by(m.Action.created_at.desc())
    )
    count_query = (
        sa.select(sa.func.count())
        .where(m.Action.created_at > thirty_days_ago)
        .select_from(m.Action)
    )
    if sort and sort != "ALL":
        query = query.where(m.Action.action == sort)
        count_query = count_query.where(m.Action.action == sort)
    if entity and entity != "ALL":
        query = query.where(m.Action.entity == entity)
        count_query = count_query.where(m.Action.entity == entity)
    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "action/actions.html",
        actions=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        sort=sort,
        entity=entity,
    )
