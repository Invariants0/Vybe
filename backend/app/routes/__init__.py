from backend.app.routes.user_routes import users_bp
from backend.app.routes.url_routes import urls_bp
from backend.app.routes.event_routes import events_bp
from backend.app.routes.link_routes import links_bp
from backend.app.routes.metrics_routes import metrics_bp, init_metrics


def register_routes(app):
    # Register instrumentation hooks for metrics
    init_metrics(app)

    # Evaluator specs require no prefix for these endpoints:
    app.register_blueprint(users_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(metrics_bp)
