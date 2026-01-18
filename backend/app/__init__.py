from flask import Flask

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)

    from backend.app.vision.routes import vision_bp 
    from backend.app.api.routes import api_bp

    app.register_blueprint(vision_bp, url_prefix="/vision")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app


