import json
from flask import Blueprint, request, jsonify, render_template_string, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Route
from app.utils import require_login

admin_bp = Blueprint('admin', __name__, url_prefix='')

# ログイン画面
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    login_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>ログイン</title>
    </head>
    <body>
        <h1>ログイン</h1>
        {% if error %}
          <p style="color:red;">{{ error }}</p>
        {% endif %}
        <form method="post">
            <label>ユーザー名: <input type="text" name="username"></label><br><br>
            <label>パスワード: <input type="password" name="password"></label><br><br>
            <button type="submit">ログイン</button>
        </form>
    </body>
    </html>
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            next_url = request.args.get('next') or url_for('admin.admin_index')
            return redirect(next_url)
        else:
            error = 'ユーザー名またはパスワードが正しくありません'
    return render_template_string(login_template, error=error)

# ログアウト
@admin_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('admin.login'))

# 管理ホーム（ログイン必須）
@admin_bp.route('/admin')
@require_login
def admin_index():
    html = """
    <h1>カスタムレスポンスサーバー 管理画面</h1>
    <ul>
      <li><a href="{{ url_for('admin.register_form') }}">パス登録フォーム</a></li>
      <li><a href="{{ url_for('admin.view_routes') }}">登録済みパス一覧</a></li>
      <li><a href="{{ url_for('admin.logs_view') }}">アクセスログ確認</a></li>
      <li><a href="{{ url_for('admin.logout') }}">ログアウト</a></li>
    </ul>
    <p>生成されたパスへのアクセスは認証不要です。</p>
    """
    return render_template_string(html)

# JSON によるパス登録（ログイン必須）
@admin_bp.route('/register', methods=['POST'])
@require_login
def register_route():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON データが必要です"}), 400

        path = data.get('path')
        response_headers = data.get('response_headers', {})
        response_body = data.get('response_body', '')

        if not path:
            return jsonify({"error": "'path' パラメータがありません"}), 400
        if not path.startswith('/'):
            return jsonify({"error": "パスは必ず '/' で始めてください"}), 400
        if Route.query.filter_by(path=path).first():
            return jsonify({"error": "このパスはすでに登録されています"}), 400
        
        new_route = Route(
            path=path,
            response_headers=json.dumps(response_headers),
            response_body=response_body
        )
        db.session.add(new_route)
        db.session.commit()
        return jsonify({"message": f"パス '{path}' の登録に成功しました"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# フォームからのパス登録（ログイン必須）
@admin_bp.route('/register-form', methods=['GET', 'POST'])
@require_login
def register_form():
    register_form_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>パス登録フォーム</title>
    </head>
    <body>
        <h1>パス登録フォーム</h1>
        {% if error %}
          <p style="color:red;">エラー: {{ error }}</p>
        {% endif %}
        <form method="post">
            <label>パス: <input type="text" name="path" value="{{ path }}" placeholder="/sample"></label><br><br>
            <label>レスポンスヘッダー (JSON形式):<br>
                <textarea name="response_headers" rows="4" cols="50" placeholder='{"Content-Type": "text/javascript"}'>{{ response_headers }}</textarea>
            </label><br><br>
            <label>レスポンスボディ:<br>
                <textarea name="response_body" rows="6" cols="50" placeholder="ここにJSやその他のコンテンツを入力">{{ response_body }}</textarea>
            </label><br><br>
            <button type="submit">登録</button>
        </form>
        <p><a href="{{ url_for('admin.admin_index') }}">管理ホームに戻る</a></p>
    </body>
    </html>
    """
    if request.method == 'POST':
        path = request.form.get('path', '').strip()
        headers_raw = request.form.get('response_headers', '').strip()
        response_body = request.form.get('response_body', '')
        error = None
        try:
            response_headers = json.loads(headers_raw) if headers_raw else {}
        except Exception as e:
            error = f"レスポンスヘッダーの JSON パースエラー: {e}"
            response_headers = {}
        if not path:
            error = "パスは必ず入力してください"
        elif not path.startswith('/'):
            error = "パスは必ず '/' で始めてください"
        elif Route.query.filter_by(path=path).first():
            error = "このパスはすでに登録されています"
        if error:
            return render_template_string(register_form_template,
                                          error=error, path=path,
                                          response_headers=headers_raw,
                                          response_body=response_body)
        else:
            new_route = Route(
                path=path,
                response_headers=json.dumps(response_headers),
                response_body=response_body
            )
            db.session.add(new_route)
            db.session.commit()
            return redirect(url_for('admin.view_routes'))
    else:
        return render_template_string(register_form_template,
                                      error=None, path='',
                                      response_headers='',
                                      response_body='')

# 登録済みパスの一覧表示（ログイン必須）
@admin_bp.route('/routes')
@require_login
def view_routes():
    routes = Route.query.all()
    html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>登録済みパス一覧</title>
    </head>
    <body>
        <h1>登録済みパス一覧</h1>
        {% if routes %}
          <ul>
          {% for r in routes %}
            <li>
              <strong>{{ r.path }}</strong> : 
              <a href="{{ r.path }}" target="_blank">アクセスする</a>
            </li>
          {% endfor %}
          </ul>
        {% else %}
          <p>現在、登録されているパスはありません。</p>
        {% endif %}
        <p><a href="{{ url_for('admin.admin_index') }}">管理ホームに戻る</a></p>
    </body>
    </html>
    """
    return render_template_string(html, routes=routes)

# アクセスログの確認（ログイン必須）
@admin_bp.route('/logs-view')
@require_login
def logs_view():
    routes = Route.query.all()
    html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>アクセスログ確認</title>
        <style>
            table, th, td { border: 1px solid #ccc; border-collapse: collapse; padding: 4px; }
        </style>
    </head>
    <body>
        <h1>アクセスログ確認</h1>
        {% if routes %}
          {% for r in routes %}
            <h2>パス: {{ r.path }}</h2>
            {% if r.logs %}
              <table>
                <tr>
                  <th>タイムスタンプ</th>
                  <th>リモートアドレス</th>
                  <th>メソッド</th>
                  <th>クエリパラメータ</th>
                </tr>
                {% for log in r.logs %}
                  <tr>
                    <td>{{ log.timestamp }}</td>
                    <td>{{ log.remote_addr }}</td>
                    <td>{{ log.method }}</td>
                    <td>{{ log.query_params }}</td>
                  </tr>
                {% endfor %}
              </table>
            {% else %}
              <p>ログはありません。</p>
            {% endif %}
          {% endfor %}
        {% else %}
          <p>登録されているパスがありません。</p>
        {% endif %}
        <p><a href="{{ url_for('admin.admin_index') }}">管理ホームに戻る</a></p>
    </body>
    </html>
    """
    return render_template_string(html, routes=routes)
