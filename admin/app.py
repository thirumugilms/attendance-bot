from flask import Flask

def create_app():
    app = Flask(__name__)
    from config import config
    app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY

    from admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
