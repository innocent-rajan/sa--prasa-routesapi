import os

from flask import Blueprint, request, jsonify, send_file

from blueprints.rrl.apis import require_api_key
from utils.main import get_routes_func, get_stops_func, get_transit_route_details_func, get_routes_on_stop_func, \
    make_combined_response, get_nearby_stop_bus, get_fare_estimate, get_only_routes_func, get_fare_options, \
    get_fare_estimate_v2, get_fare_options_v2

from dotenv import load_dotenv

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