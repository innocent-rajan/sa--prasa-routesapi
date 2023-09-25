import pandas as pd
from flask import jsonify

# from app import create_app
from db_operations.models_file import BusRoutesDetail, BusRoute, BusStop, BusNextStop

column_data_types = {
    'stop_id': str,
    'stop_code': str,
    'stop_name': str,
    'stop_lat': float,
    'stop_lon': float,
    'zone_id': str
}

gtfs_folder = 'static/data/GTFS/'
routes_df = pd.read_csv(gtfs_folder+'routes.txt')
stops_df = pd.read_csv(gtfs_folder+'stops.txt', dtype=column_data_types)
trips_df = pd.read_csv(gtfs_folder+'trips.txt')
stop_times_df = pd.read_csv(gtfs_folder+'stop_times.txt')

bus_stops_dict = dict(zip(stops_df.stop_id, stops_df.stop_name))
bus_route_details_dict = dict()
bus_next_stop_dict = dict()
schedule_dict = dict()


# app = create_app()

# def get_route_details():
    # with app.app_context():
    # val = BusRoutesDetail.query.all()
    # for v in val:
    #     bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)

# get_route_details()

def get_direction(route_long_name):
    if 'UP' in route_long_name.upper():
        direction = 1
        route = route_long_name.upper().replace('UP', "")
    elif 'DOWN' in route_long_name.upper():
        direction = 0
        route = route_long_name.upper().replace('DOWN', "")
    elif 'DN' in route_long_name.upper():
        direction = 0
        route = route_long_name.upper().replace('DN', "")
    elif '_DN' in route_long_name.upper():
        direction = 0
        route = route_long_name.upper().replace('_DN', "")
    else:
        route = route_long_name
        direction = 0
    return route, direction


def get_routes_func():
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    try:
        routes = BusRoute.query.all()
        all_routes = {
            'status': 'success',
            'description': '',
            'routes': [
                {
                    'id': route.route_id,
                    'short_name': 'nan',
                    'long_name': route.route_long_name,
                    'route': get_direction(route.route_long_name)[0],
                    'direction': get_direction(route.route_long_name)[1],
                    'start': bus_stops_dict[bus_route_details_dict[route.route_id][0]],
                    'end': bus_stops_dict[bus_route_details_dict[route.route_id][1]],
                    'trips_count': schedule_dict[
                        route.route_long_name] if route.route_long_name in schedule_dict else 0,
                    'agency': route.agency_id
                }
                for route in routes
            ]
        }
        return jsonify(all_routes), 200
    except Exception as e:
        print(e)
        all_routes = {
            'status': 'failed',
            'description': 'Some error occurred'
        }
        return jsonify(all_routes), 400


def get_stops_func():
    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name
    try:
        stops = BusStop.query.all()
        all_stops = {
            'status': 'success',
            'description': '',
            'stops': [
                {
                    'id': stop.stop_id,
                    'name': stop.stop_name,
                    'lat': float(stop.stop_lat),
                    'lng': float(stop.stop_lon),
                    'next_stop': bus_next_stop_dict[stop.stop_id]
                }
                for stop in stops
            ]
        }
        return jsonify(all_stops), 200
    except Exception as e:
        print(e)
        all_routes = {
            'status': 'failed',
            'description': 'Some error occurred'
        }
        return jsonify(all_routes), 400


if __name__ == '__main__':
    pass