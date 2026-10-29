import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from app.config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.onboarding import onboarding_bp
    from app.routes.workout import workout_bp
    from app.routes.nutrition import nutrition_bp
    from app.routes.habits import habits_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(onboarding_bp, url_prefix='/onboarding')
    app.register_blueprint(workout_bp, url_prefix='/workout')
    app.register_blueprint(nutrition_bp, url_prefix='/nutrition')
    app.register_blueprint(habits_bp, url_prefix='/habits')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    # Seed data helper inside application context if needed
    with app.app_context():
        if not app.config.get('TESTING'):
            try:
                db.create_all()
                from app.services.seed_data import seed_initial_data
                seed_initial_data()
            except Exception as e:
                app.logger.warning(f"Could not auto-create/seed tables on startup: {e}")

    return app
