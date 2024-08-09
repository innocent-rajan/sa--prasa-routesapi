import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_compress import Compress

from blueprints.pmpml.apis import pmpml_bp
from blueprints.pmpml.v2.apis import pmpml_v2_bp
from exts import db

# from werkzeug.middleware.profiler import ProfilerMiddleware

load_dotenv()

API_KEY = os.getenv('x-api-key')
SECRET_KEY = os.getenv('secret-key')


def register_extensions(app):
    db.init_app(app)


def create_app():
    app = Flask(__name__)
    Compress(app)
    app.config.from_pyfile('config.cfg')
    app.config['SECRET_KEY'] = SECRET_KEY
    register_extensions(app)
    app.register_blueprint(pmpml_bp, url_prefix='/')
    app.register_blueprint(pmpml_v2_bp, url_prefix='/v2')
    return app


app = create_app()
# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='./profs', filename_format="{method}.{path}.prof")

bus_next_stop_dict = {}


# from db_operations.add_data import set_data

# with app.app_context():
#     db.create_all()
#     set_data()


@app.route('/')
def home():
    return 'Welcome to home', 200
