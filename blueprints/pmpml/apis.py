import os

from flask import Blueprint, request, jsonify, send_file

from utils.main import get_routes_func, get_stops_func, get_transit_route_details_func, get_routes_on_stop_func, \
    make_combined_response

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('x-api-key')

pmpml_bp = Blueprint('pmpml', __name__)


def require_api_key(api_key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request_api_key = request.headers.get('x-api-key')
            if request_api_key in api_key:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Unauthorized'}), 401

        return wrapper

    return decorator


@pmpml_bp.route('/routes', endpoint='get_routes_api')
@require_api_key(API_KEY)
def get_routes_api():
    return get_routes_func()


@pmpml_bp.route('/complete_info', endpoint='get_complete_routes_info')
@require_api_key(API_KEY)
def get_routes_api():
    return make_combined_response()


@pmpml_bp.route('/stops', endpoint='get_stops_api')
@require_api_key(API_KEY)
def get_stops_api():
    return get_stops_func()


@pmpml_bp.route('/transit_route_details', endpoint='get_transit_route_details')
@require_api_key(API_KEY)
def get_transit_route_details():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_transit_route_details_func(data['route'])
    else:
        return 'Wrong route', 400


@pmpml_bp.route('/routes_on_stop', endpoint='get_routes_on_stop')
@require_api_key(API_KEY)
def get_routes_on_stop():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_routes_on_stop_func(int(data['stop_id']), data['time'] if 'time' in data.keys() else None)
    else:
        return 'Wrong route', 400


@pmpml_bp.route('/gtfs_zip', endpoint='get_gtfs_zip')
def get_gtfs_zip():
    # To zip use
    # zip -9 pmpml_gtfs_.zip routes.txt shapes.txt stops.txt stop_times.txt trips.txt
    path_to_zip = 'static/data/GTFS/gtfs.zip'

    if not os.path.exists(path_to_zip):
        return "File not found.", 404

    return send_file(path_to_zip, as_attachment=True, download_name='pmpml_gtfs.zip')
