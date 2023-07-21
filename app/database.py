from alchemical.flask import Alchemical
from flask_login import UserMixin, AnonymousUserMixin

db = Alchemical()
AppUser = UserMixin


class AnonymousUser(AnonymousUserMixin):
    pass