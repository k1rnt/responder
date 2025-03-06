import json
from flask import Blueprint, request, make_response
from app import db
from app.models import Route, Log

public_bp = Blueprint('public', __name__)

@public_bp.route('/', defaults={'req_path': ''})
@public_bp.route('/<path:req_path>')
def serve_registered_route(req_path):
    full_path = '/' + req_path
    route = Route.query.filter_by(path=full_path).first()
    if route:
        # アクセスログの記録
        log_entry = Log(
            route_id=route.id,
            remote_addr=request.remote_addr,
            method=request.method,
            query_params=json.dumps(request.args.to_dict())
        )
        db.session.add(log_entry)
        db.session.commit()
        # 保存されたレスポンスヘッダー（JSON）を反映
        try:
            headers = json.loads(route.response_headers) if route.response_headers else {}
        except Exception:
            headers = {}
        response = make_response(route.response_body)
        for header, value in headers.items():
            response.headers[header] = value
        return response
    else:
        return "Not Found", 404
