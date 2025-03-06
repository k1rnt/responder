import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # SECRET_KEY は .env から読み込み
    app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_here")
    
    # MySQL 接続設定
    MYSQL_USER = os.environ.get("MYSQL_USER", "appuser")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "apppassword")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "app_db")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # セッション Cookie の設定（HTTPS 利用時は SESSION_COOKIE_SECURE=True）
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Blueprint の登録
    from app.views.admin import admin_bp
    from app.views.public import public_bp
    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)

    return app
