import functools
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
        # functools.wraps preserves __doc__ so Flasgger can read the Swagger spec
        @functools.wraps(func)
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
    """All routes with schedules, polylines, start/end stops and operating days.
    ---
    tags: [routes]
    responses:
      200:
        description: Full route list with trip schedules and operating days
        examples:
          application/json:
            status: success
            routes:
              - id: "1"
                long_name: CAPE TOWN - CHRIS HANI
                route_type: 2
                start: CAPE TOWN
                end: CHRIS HANI
                trips_schedule: ["04:30", "04:45", "05:00"]
                trips_count: 71
                operating_days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    """
    return get_routes_func()


@rrl_bp.route('/only-routes', endpoint='get_only_routes_api')
@require_api_key(API_KEY)
def get_only_routes_api():
    """Lightweight route list (id, names, agency) for pickers.
    ---
    tags: [routes]
    responses:
      200:
        description: Route list without schedules
        examples:
          application/json:
            routes:
              - id: "1"
                long_name: CAPE TOWN - CHRIS HANI
                agency: "1"
    """
    return get_only_routes_func()


# @rrl_bp.route('/complete_info', endpoint='get_complete_routes_info')
# @require_api_key(API_KEY)
# def get_routes_api():
#     return make_combined_response()


@rrl_bp.route('/stops', endpoint='get_stops_api')
@require_api_key(API_KEY)
def get_stops_api():
    """All stops with coordinates.
    ---
    tags: [stops]
    responses:
      200:
        description: Stop list (metro stops 1-274, coach stops 10001+)
        examples:
          application/json:
            status: success
            stops:
              - stop_id: "1"
                stop_name: CAPE TOWN
                stop_lat: -33.923631
                stop_lon: 18.427186
    """
    return get_stops_func()


@rrl_bp.route('/nearby_stops', endpoint='get_nearby_stops')
@require_api_key(API_KEY)
def get_nearby_stops():
    """Stops nearest to a coordinate, with distance and next stop.
    ---
    tags: [stops]
    parameters:
      - name: user_lat
        in: query
        type: number
        required: true
        example: -33.9236
      - name: user_lon
        in: query
        type: number
        required: true
        example: 18.4271
    responses:
      200:
        description: Nearest stops sorted by distance (km)
        examples:
          application/json:
            status: success
            count: 9
            stops:
              - id: "1"
                name: CAPE TOWN
                distance: 0.86
                next_stop: WOODSTOCK
      400:
        description: Missing or invalid coordinates
    """
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
    """Full detail for one route: ordered stops, distances, polyline, schedule.
    ---
    tags: [routes]
    parameters:
      - name: route
        in: query
        type: string
        required: true
        description: Route long_name (exact match)
        example: CAPE TOWN - CHRIS HANI
    responses:
      200:
        description: Route detail with ordered stop list
        examples:
          application/json:
            status: success
            transit_route:
              - id: "1"
                long_name: CAPE TOWN - CHRIS HANI towards CHRIS HANI
                stops:
                  - stop_id: "1"
                    name: CAPE TOWN
                trips_schedule: ["04:30", "04:45"]
      400:
        description: Unknown route
    """
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
    """All routes serving a stop with their full departure times.
    ---
    tags: [schedules]
    parameters:
      - name: stop_id
        in: query
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Routes at the stop with upcoming trip times
        examples:
          application/json:
            status: success
            stop_name: CAPE TOWN
            next_stop: WOODSTOCK
            routes:
              - route: CAPE TOWN - CHRIS HANI
                end_stop: CHRIS HANI
                upcoming_trips_schedule: ["04:30", "04:30", "04:45"]
      400:
        description: No routes serve this stop
    """
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
    """Download the full GTFS zip (metro + coaches merged feed).
    ---
    tags: [gtfs]
    responses:
      200:
        description: GTFS zip file (no API key required)
        schema:
          type: file
      404:
        description: Zip not found on server
    """
    if not os.path.exists(gtfs_zip_path):
        return "File not found.", 404

    return send_file(gtfs_zip_path, as_attachment=True, download_name='rrl_gtfs.zip')


@rrl_bp.route('/gtfs_zip/single', endpoint='get_gtfs_single_zip')
def get_gtfs_single_zip():
    """Download the single-mode GTFS zip (coaches feed).
    ---
    tags: [gtfs]
    responses:
      200:
        description: GTFS zip file (no API key required)
        schema:
          type: file
      404:
        description: Zip not found on server
    """

    if not os.path.exists(gtfs_single_zip_path):
        return "File not found.", 404

    return send_file(gtfs_single_zip_path, as_attachment=True, download_name='rrl_gtfs_single.zip')


@rrl_bp.route('/schedule_on_stop', endpoint='get_schedule_on_stop')
@require_api_key(API_KEY)
def get_schedule_on_stop():
    """Departure times at one stop for one route, after a given time.
    ---
    tags: [schedules]
    parameters:
      - name: route
        in: query
        type: string
        required: true
        description: Route long_name (exact match)
        example: CAPE TOWN - CHRIS HANI
      - name: stop_id
        in: query
        type: integer
        required: true
        example: 1
      - name: time
        in: query
        type: string
        description: HH:MM - only return departures after this time (default now)
        example: "16:00"
    responses:
      200:
        description: Departure times HH:MM (may be empty outside service hours)
        examples:
          application/json:
            status: success
            data: ["16:45", "17:00", "17:15"]
      400:
        description: Unable to fetch schedule
    """
    data = None
    if request.method == 'GET':
        data = request.values.to_dict()
    return get_schedule_on_stop_func(data['route'], int(data['stop_id']), data.get('time', None))
