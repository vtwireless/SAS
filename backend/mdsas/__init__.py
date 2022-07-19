from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.config import DevConfig, ProdConfig


database = SQLAlchemy()


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(DevConfig)

    database.init_app(app)
    migration_engine = Migrate(app, database)

    CORS(app)

    with app.app_context():
        # Import blueprints
        from .users import routes as userRoutes
        from .nodes import routes as nodeRoutes

        # Register blueprints
        app.register_blueprint(userRoutes.user_routes)
        app.register_blueprint(nodeRoutes.node_routes)

        # Create database tables
        database.create_all()

        return app
