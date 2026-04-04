from backend.app.routes.api import api_bp
from backend.app.routes.redirect import redirect_bp


def register_routes(app):
    app.register_blueprint(api_bp, url_prefix=app.config["API_PREFIX"])
    app.register_blueprint(redirect_bp)
