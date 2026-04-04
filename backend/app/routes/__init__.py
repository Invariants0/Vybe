from backend.app.routes.user_routes import users_bp
from backend.app.routes.url_routes import urls_bp
from backend.app.routes.event_routes import events_bp
from backend.app.routes.link_routes import links_bp


def register_routes(app):
    # Evaluator specs require no prefix for these endpoints:
    app.register_blueprint(users_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(links_bp)
