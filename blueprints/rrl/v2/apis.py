import os

from dotenv import load_dotenv
from flask import Blueprint, request

from blueprints.rrl.apis import require_api_key
from utils.main import get_fare_estimate_v2, get_fare_options_v2

load_dotenv()

API_KEY = os.getenv('x-api-key')
gtfs_zip_path = os.getenv('gtfs_zip_path')
gtfs_single_zip_path = os.getenv('gtfs_single_zip_path')

rrl_v2_bp = Blueprint('rrl_v2', __name__)


@rrl_v2_bp.route('/fare_estimate', endpoint='fare_estimate')
@require_api_key(API_KEY)
def fare_estimate():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_fare_estimate_v2(data['route_id'].lower(), data['start_idx'], data.get('end_idx'), data.get('fare'))
    else:
        return {'status': 'failed', 'description': 'Wrong input'}, 400


@rrl_v2_bp.route('/fare_options', endpoint='fare_options')
@require_api_key(API_KEY)
def fare_options():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_fare_options_v2(data['route_id'], data['start_idx'])
    else:
        return {'status': 'failed', 'description': 'Wrong input'}, 400