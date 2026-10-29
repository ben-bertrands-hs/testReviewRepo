from flask import Flask

from app import config


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    from app.routes import bp
    from app.webhooks import webhooks_bp

    app.register_blueprint(bp)
    app.register_blueprint(webhooks_bp)
    return app
