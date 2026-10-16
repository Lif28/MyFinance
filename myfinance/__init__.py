import os

from flask import Flask, render_template, g, redirect, url_for
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    os.makedirs("logs", exist_ok=True)

    handler = RotatingFileHandler("logs/app.log", maxBytes=100000, backupCount=3)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DATABASE=os.path.join(app.instance_path, 'myfinance.db'),
    )


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Logs
    setup_logging(app)

    # dashboard
    @app.route('/')
    def index():
        if g.user:
            return redirect(url_for('dashboard.index'))

        return render_template("index.html")

    
    from . import db
    db.init_app(app)


    # creates database
    with app.app_context():
        if not os.path.exists(app.config['DATABASE']):
            db.init_db()

    from .errors import error_handlers

    error_handlers(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)

    from . import table
    app.register_blueprint(table.bp)

    from . import rules
    app.register_blueprint(rules.bp)

    from . import settings
    app.register_blueprint(settings.bp)

    from . import income_expenses
    app.register_blueprint(income_expenses.bp)
    
    return app