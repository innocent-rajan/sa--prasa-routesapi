import ast
import datetime

import pandas as pd
from flask import jsonify

# from app import create_app
from db_operations.models_file import BusRoutesDetail, BusRoute, BusStop, BusNextStop, BusAllRoute, BusRouteStopDistance

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
                    'agency': route.agency_id,
                    'trips_schedule': get_trip_schedules(route.route_id)
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
                    'lon': float(stop.stop_lon),
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


def get_transit_route_details_func(route):
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    try:
        route = BusRoute.query.filter(BusRoute.route_id == route).one()
        transit_routes = {
            'status': 'success',
            'description': '',
            'transit_route': [
                {
                    'id': route.route_id,
                    'type': 'bus',
                    'route': route.route_long_name,
                    'short_name': 'nan',
                    'long_name': f'{route.route_long_name} towards {bus_stops_dict[bus_route_details_dict[route.route_id][1]]}',
                    'direction': get_direction(route.route_long_name)[1],
                    'interchanges': 'nan',
                    'polyline': '',
                    'stops': [{'stop_id': x[0], 'name': x[1], 'lat': float(x[2]), 'lon': float(x[3])} for x in
                              ast.literal_eval(
                                  BusAllRoute.query.filter_by(route_id=route.route_id).one().stops_details)],
                    'stops_distance': ast.literal_eval(
                        BusRouteStopDistance.query.filter_by(route_id=route.route_id).one().
                            stops_distances),
                    'trips_schedule': get_trip_schedules(route.route_id)
                }
            ]
        }
        return jsonify(transit_routes), 200
    except Exception as e:
        print(e)
        transit_routes = {
            'status': 'failed',
            'description': 'some error occurred',
        }
        return jsonify(transit_routes), 400


def get_routes_on_stop_func(stop_id, time=None):
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    if time is None:
        query_time = datetime.datetime.now().time()
    else:
        query_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
    stop = BusStop.query.filter(BusStop.stop_id == stop_id).one()
    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name
    routes = list(set(trips_df[trips_df.trip_id.isin(stop_times_df[stop_times_df.stop_id == int(stop_id)].trip_id.tolist())].route_id.tolist()))
    routes_on_stop = {'status': '', 'description': '', 'stop_name': stop.stop_name,
                      'next_stop': bus_next_stop_dict[stop.stop_id], 'updated_at': datetime.datetime.now().time().strftime("%H:%M:%S")}
    upcoming_routes = []
    for route in routes:
        rt = BusRoute.query.filter(BusRoute.route_id == route).one()
        trip_schedule = get_trip_schedules(rt.route_id)
        trip_times = [datetime.datetime.strptime(time_str, "%H:%M").time() for time_str in trip_schedule]
        upcoming_times = sorted([time for time in trip_times if time > query_time])
        next_two_times = [time.strftime("%H:%M") for time in upcoming_times[:2]]
        upcoming_routes.append({'route' : rt.route_long_name , 'upcoming_trips_schedule': next_two_times,
                                               'end_stop': bus_stops_dict[bus_route_details_dict[rt.route_id][1]]})

    if len(upcoming_routes) > 0:
        routes_on_stop['routes'] = upcoming_routes
        routes_on_stop['status'] = 'success'
        routes_on_stop['description'] = ''
        return jsonify(routes_on_stop), 200
    else:
        routes_on_stop['status'] = 'failed'
        routes_on_stop['description'] = 'No upcoming buses'
    return jsonify(routes_on_stop), 400


def get_trip_schedules(route_id):
    return [convert_to_h_m(x) for x in stop_times_df[stop_times_df.trip_id.isin(trips_df[trips_df.route_id == route_id].trip_id.tolist())][
        stop_times_df.stop_sequence == 0].arrival_time.tolist()]


def convert_to_h_m(time):
    time_obj = datetime.datetime.strptime(time, "%H:%M:%S")
    return time_obj.strftime("%H:%M")


def make_combined_response():
    routes_data = []
    routes = BusRoute.query.all()
    for route in routes:
        route_id = route.route_id
        stops = [{'stop_id': x[0], 'name': x[1], 'lat': float(x[2]), 'lon': float(x[3])} for x in
                              ast.literal_eval(
                                  BusAllRoute.query.filter_by(route_id=route.route_id).one().stops_details)]
        # route_details = BusRoute.query.filter(BusRoute.route_id == route_id).one()
        route_long_name = route.route_long_name
        only_route, direction = get_direction(route_long_name)
        start_stop = stops[0]['name']
        end_stop = stops[-1]['name']
        trips_schedule = get_trip_schedules(route_id)
        trips_count = len(trips_schedule)

        route_data = {
            'id': None if route_id is None else route_id,
            'direction': None if direction is None else direction,
            'route': None if only_route is None else only_route,
            'short_name': None,
            'long_name': None if route_long_name is None else route_long_name,
            'polyline': None,
            'city': 'klb',
            'state': 'KA',
            'type': 'bus',
            'trips_schedule': [] if trips_schedule is None else trips_schedule,
            'stops': [x['stop_id'] for x in stops],
            'stops_distance': ast.literal_eval(
                BusRouteStopDistance.query.filter_by(route_id=route.route_id).one().
                    stops_distances),
            'agency': route.agency_id,
            'end': None if end_stop is None else end_stop,
            'start': [] if start_stop is None else start_stop,
            'trips_count': None if trips_count is None else trips_count,
        }
        routes_data.append(route_data)

    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name

    stops = BusStop.query.all()
    stops_data = [
        {
            'id': stop.stop_id,
            'name': stop.stop_name,
            'lat': float(stop.stop_lat),
            'lon': float(stop.stop_lon),
            'next_stop': bus_next_stop_dict[stop.stop_id]
        }
        for stop in stops
    ]

    response = {
        'status': 'success',
        'description': '',
        'routes': routes_data,
        'stops': stops_data
    }

    print(routes_data[0])
    return jsonify(response), 200


if __name__ == '__main__':
    pass
