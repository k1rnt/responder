from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), unique=True, nullable=False)
    response_headers = db.Column(db.Text)  # JSON 文字列として保存
    response_body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    logs = db.relationship("Log", backref="route", lazy=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    remote_addr = db.Column(db.String(255))
    method = db.Column(db.String(10))
    query_params = db.Column(db.Text)  # JSON 文字列として保存
