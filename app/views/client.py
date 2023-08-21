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


bp = Blueprint("client", __name__, url_prefix="/client")


@bp.route("/", methods=["GET"])
@login_required
def get_all():
    q = request.args.get("q", type=str, default=None)
    query = m.SuperUser.select().order_by(m.SuperUser.id)
    count_query = sa.select(sa.func.count()).select_from(m.SuperUser)
    if q:
        query = (
            m.SuperUser.select()
            .where(m.SuperUser.username.like(f"{q}%") | m.SuperUser.email.like(f"{q}%"))
            .order_by(m.SuperUser.id)
        )
        count_query = (
            sa.select(sa.func.count())
            .where(m.SuperUser.username.like(f"{q}%") | m.SuperUser.email.like(f"{q}%"))
            .select_from(m.SuperUser)
        )

    pagination = create_pagination(total=db.session.scalar(count_query))

    return render_template(
        "client/clients.html",
        users=db.session.execute(
            query.offset((pagination.page - 1) * pagination.per_page).limit(
                pagination.per_page
            )
        ).scalars(),
        page=pagination,
        search_query=q,
    )
