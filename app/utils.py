from functools import wraps
from flask import session, redirect, url_for, request

def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            # ログインしていなければログイン画面へリダイレクト
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated
