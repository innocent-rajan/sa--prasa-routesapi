import os

from dotenv import load_dotenv
# from elasticapm.contrib.flask import ElasticAPM
from flasgger import Swagger
from flask import Flask
from flask_compress import Compress
from flask_cors import CORS
from flask_redis import FlaskRedis

from blueprints.rrl.apis import rrl_bp
from blueprints.rrl.v2.apis import rrl_v2_bp
from exts import db, cache

# from werkzeug.middleware.profiler import ProfilerMiddleware

load_dotenv()

API_KEY = os.getenv('x-api-key', 'default_api_key')
SECRET_KEY = os.getenv('secret-key', 'default_secret_key')
CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
CACHE_REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', 6379))
CACHE_REDIS_DB = int(os.getenv('CACHE_REDIS_DB', 0))
ELK_SECRET_TOKEN = os.getenv("ELK_SECRET_TOKEN", "default_token")
ELK_SERVER_URL = os.getenv("ELK_SERVER_URL", "http://localhost:8200")
ELK_SERVICE_NAME = os.getenv("ELK_SERVICE_NAME", "rrl-routesapi")
ELASTIC_APM_ENABLED = os.getenv("ELASTIC_APM_ENABLED", "false").lower() == "true"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def register_extensions(app):
    db.init_app(app)


def create_app():
    app = Flask(__name__)
    Compress(app)
    CORS(app)

    # Swagger UI at /apidocs for mobile-app integration
    Swagger(app, template={
        'swagger': '2.0',
        'info': {
            'title': 'PRASA Routes API',
            'description': 'Routes, stops, schedules and fares for PRASA Metrorail '
                           '(route_type=2) and long-distance coaches (route_type=3). '
                           'All endpoints require the x-api-key header. '
                           'IDs are the merged ID space: metro routes 1-34, coach '
                           'routes 1001-1040; metro stops 1-274, coach stops 10001+.',
            'version': '2.0.0',
        },
        'securityDefinitions': {
            'ApiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'x-api-key',
                'description': 'API key for all passenger endpoints',
            }
        },
        'security': [{'ApiKeyAuth': []}],
    })

    # Set configuration settings
    app.config.from_pyfile('config.cfg')
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = CACHE_REDIS_HOST
    app.config['CACHE_REDIS_PORT'] = CACHE_REDIS_PORT
    app.config['CACHE_REDIS_DB'] = CACHE_REDIS_DB
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['ELASTIC_APM'] = {
        'SERVICE_NAME': ELK_SERVICE_NAME,
        'SERVER_URL': ELK_SERVER_URL,
        'SECRET_TOKEN': ELK_SECRET_TOKEN,
        'SERVER_TIMEOUT': '5s',
        'LOG_LEVEL': 'trace',
        'CLOUD_PROVIDER': False,
        'DEBUG': DEBUG,
        'ELASTIC_APM_ENABLED': ELASTIC_APM_ENABLED
    }

    # Initialize cache with the app
    cache.init_app(app)
    # Initialize extensions
    register_extensions(app)
    app.register_blueprint(rrl_bp, url_prefix='/')
    app.register_blueprint(rrl_v2_bp, url_prefix='/v2')

    return app


app = create_app()
redis_client = FlaskRedis(app)
# apm = ElasticAPM(app)

# app.wsgi_app = ProfilerMiddleware(app.wsgi_app, profile_dir='./profs', filename_format="{method}.{path}.prof")

from db_operations.add_data import set_data

# with app.app_context():
    # db.create_all()
    # set_data()


@app.route('/')
def home():
    return 'Welcome to home', 200
