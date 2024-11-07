import os

from flask import Blueprint, request, jsonify, send_file

from utils.main import get_routes_func, get_stops_func, get_transit_route_details_func, get_routes_on_stop_func, \
    get_nearby_stop_bus, get_only_routes_func, get_schedule_on_stop_func

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('x-api-key')
gtfs_zip_path = os.getenv('gtfs_zip_path')
gtfs_single_zip_path = os.getenv('gtfs_single_zip_path')

rrl_bp = Blueprint('rrl', __name__)


def require_api_key(api_key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            request_api_key = request.headers.get('x-api-key', None)
            if request_api_key is not None and request_api_key in api_key:
                return func(*args, **kwargs)
            else:
                return jsonify({'status': 'failed', 'description': 'Unauthorized'}), 401

        return wrapper

    return decorator


@rrl_bp.route('/routes', endpoint='get_routes_api')
@require_api_key(API_KEY)
def get_routes_api():
    return get_routes_func()


@rrl_bp.route('/only-routes', endpoint='get_only_routes_api')
@require_api_key(API_KEY)
def get_only_routes_api():
    return get_only_routes_func()


# @rrl_bp.route('/complete_info', endpoint='get_complete_routes_info')
# @require_api_key(API_KEY)
# def get_routes_api():
#     return make_combined_response()


@rrl_bp.route('/stops', endpoint='get_stops_api')
@require_api_key(API_KEY)
def get_stops_api():
    return get_stops_func()


@rrl_bp.route('/nearby_stops', endpoint='get_nearby_stops')
@require_api_key(API_KEY)
def get_nearby_stops():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        query_coords = [data['user_lat'], data['user_lon']]
        return get_nearby_stop_bus(query_coords)
    else:
        return {'status': 'failed', 'description': 'Wrong route'}, 400


@rrl_bp.route('/transit_route_details', endpoint='get_transit_route_details')
@require_api_key(API_KEY)
def get_transit_route_details():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_transit_route_details_func(data['route'])
    else:
        return {'status': 'failed', 'description': 'Wrong route'}, 400


@rrl_bp.route('/routes_on_stop', endpoint='get_routes_on_stop')
@require_api_key(API_KEY)
def get_routes_on_stop():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_routes_on_stop_func(int(data['stop_id']), data['time'] if 'time' in data.keys() else None)
    else:
        return {'status': 'failed', 'description': 'Wrong stop'}, 400


# @rrl_bp.route('/fare_estimate', endpoint='fare_estimate')
# @require_api_key(API_KEY)
# def fare_estimate():
#     data = None
#     if request.method == 'GET':
#         data = request.values.to_dict()
#     if data is not None:
#         return get_fare_estimate(data['route_id'].lower(), data['start_idx'], data.get('end_idx'), data.get('fare'))
#     else:
#         return {'status': 'failed', 'description': 'Wrong input'}, 400


# @rrl_bp.route('/fare_options', endpoint='fare_options')
# @require_api_key(API_KEY)
# def fare_estimate():
#     data = None
#     if request.method == 'GET':
#         data = request.values.to_dict()
#     if data is not None:
#         return get_fare_options(data['route_id'], data['start_idx'])
#     else:
#         return {'status': 'failed', 'description': 'Wrong input'}, 400


@rrl_bp.route('/gtfs_zip', endpoint='get_gtfs_zip')
def get_gtfs_zip():
    # To zip use
    # zip -9 rrl_gtfs_.zip routes.txt shapes.txt stops.txt stop_times.txt trips.txt

    if not os.path.exists(gtfs_zip_path):
        return "File not found.", 404

    return send_file(gtfs_zip_path, as_attachment=True, download_name='rrl_gtfs.zip')


@rrl_bp.route('/gtfs_zip/single', endpoint='get_gtfs_single_zip')
def get_gtfs_single_zip():
    # To zip use
    # zip -9 rrl_gtfs_.zip routes.txt shapes.txt stops.txt stop_times.txt trips.txt

    if not os.path.exists(gtfs_single_zip_path):
        return "File not found.", 404

    return send_file(gtfs_single_zip_path, as_attachment=True, download_name='rrl_gtfs_single.zip')


@rrl_bp.route('/schedule_on_stop', endpoint='get_schedule_on_stop')
@require_api_key(API_KEY)
def get_schedule_on_stop():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    return get_schedule_on_stop_func(data['route'], int(data['stop_id']), data.get('time', None))
