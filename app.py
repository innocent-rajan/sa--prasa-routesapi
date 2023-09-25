import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from blueprints.klb.apis import klb_bp
from exts import db

load_dotenv()

API_KEY = os.getenv('x-api-key')
SECRET_KEY = os.getenv('secret-key')

def register_extensions(app):
    db.init_app(app)


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')
    app.config['SECRET_KEY'] = SECRET_KEY
    register_extensions(app)
    app.register_blueprint(klb_bp, url_prefix='/klb')
    return app


app = create_app()

def require_api_key(api_key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request_api_key = request.headers.get('x-api-key')
            if request_api_key == api_key:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Unauthorized'}), 401

        return wrapper
    return decorator


# with app.app_context():
#     db.create_all()
#     set_data()


@app.route('/')
def home():
    return 'Welcome to home', 200


# @app.route('/klb/get_routes')
# @require_api_key(API_KEY)
# def get_routes():
#     return 'welcome to get_routes'