from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)

    # Initialize OCR reader (singleton)
    from app.services.ocr_service import init_ocr_reader
    with app.app_context():
        init_ocr_reader(app.config['OCR_LANGUAGES'])

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.ocr import ocr_bp
    from app.routes.work import work_bp
    from app.routes.tools import tools_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
    app.register_blueprint(work_bp, url_prefix='/api/works')
    app.register_blueprint(tools_bp, url_prefix='/api/tools')

    print("👉 DB URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    from sqlalchemy import text
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Database connection OK")
        except Exception as e:
            print("❌ Database connection FAILED:", e)
    # Create database tables
    with app.app_context():
        db.create_all()

    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')

    return app
