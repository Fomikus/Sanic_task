from .users import users_bp
from .admins import admins_bp
from .transactions import transactions_bp


def register_routes(app):
    app.blueprint(transactions_bp)
    app.blueprint(admins_bp)
    app.blueprint(users_bp)
