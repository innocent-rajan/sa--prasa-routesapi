import os

from flask import Blueprint, request, jsonify

from utils.main import get_routes_func, get_stops_func

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


@klb_bp.route('/get_stops', endpoint='get_stops_api')
@require_api_key(API_KEY)
def get_stops_api():
    return get_stops_func()
