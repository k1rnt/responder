from app import create_app

app = create_app()

if __name__ == '__main__':
    # 本番環境では debug=False および HTTPS 化を検討してください
    app.run(host='0.0.0.0', port=5000, debug=False)
