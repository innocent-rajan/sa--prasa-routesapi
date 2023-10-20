import os

from flask import Blueprint, request, jsonify

from utils.main import get_routes_func, get_stops_func, get_transit_route_details_func, get_routes_on_stop_func, \
    make_combined_response

API_KEY = os.getenv('x-api-key')

klb_bp = Blueprint('klb', __name__)


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


@klb_bp.route('/get_routes', endpoint='get_routes_api')
@require_api_key(API_KEY)
def get_routes_api():
    return get_routes_func()


@klb_bp.route('/get_complete_info', endpoint='get_complete_routes_info')
@require_api_key(API_KEY)
def get_routes_api():
    return make_combined_response()


@klb_bp.route('/get_stops', endpoint='get_stops_api')
@require_api_key(API_KEY)
def get_stops_api():
    return get_stops_func()


@klb_bp.route('/get_transit_route_details', endpoint='get_transit_route_details')
@require_api_key(API_KEY)
def get_transit_route_details():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_transit_route_details_func(data['route'])
    else:
        return 'Wrong route', 400


@klb_bp.route('/get_routes_on_stop', endpoint='get_routes_on_stop')
@require_api_key(API_KEY)
def get_routes_on_stop():
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    if data is not None:
        return get_routes_on_stop_func(data['stop_id'], data['time'] if 'time' in data.keys() else None)
    else:
        return 'Wrong route', 400
