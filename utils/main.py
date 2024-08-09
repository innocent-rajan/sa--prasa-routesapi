import ast
import datetime
import math
import os
from collections import defaultdict

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from flask import jsonify

# from app import create_app
from db_operations.models_file import BusRoutesDetail, BusRoute, BusStop, BusNextStop, BusAllRoute, BusRouteStopDistance
from utils.fare_operations import get_fare_by_idx, get_stop_by_amount, get_fare_options_from_source, get_fare_by_idx_v2

load_dotenv()
radius = int(os.getenv('radius'))

column_data_types = {
    'stop_id': str,
    'stop_code': str,
    'stop_name': str,
    'stop_lat': float,
    'stop_lon': float,
    'zone_id': str
}

gtfs_folder = 'static/data/GTFS/'
routes_df = pd.read_csv(gtfs_folder + 'routes.txt')
stops_df = pd.read_csv(gtfs_folder + 'stops.txt', dtype=column_data_types)
trips_df = pd.read_csv(gtfs_folder + 'trips.txt')
stop_times_df = pd.read_csv(gtfs_folder + 'stop_times.txt')
try:
    polylines_df = pd.read_csv(gtfs_folder + 'polylines.csv', dtype={'route_id': 'str'})
    polylines_df.set_index('route_id', inplace=True)
except FileNotFoundError:
    polylines_df = pd.DataFrame()

bus_stops_dict = dict(zip(stops_df.stop_id, stops_df.stop_name))
bus_route_details_dict = dict()
bus_next_stop_dict = dict()
schedule_df = pd.read_csv(gtfs_folder + 'schedule.csv', dtype={'route_id': 'str'})
schedule_df.set_index('route_id', inplace=True)


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


def get_polyline(route_id):
    filtered_df = polylines_df.at[route_id, 'polyline']
    # filtered_df = polylines_df[polylines_df.route_id == route_id].polyline
    if filtered_df == '':
        return ''
    else:
        return filtered_df


def get_routes_func():
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    try:
        routes = BusRoute.query.all()
        all_routes = {'status': 'success', 'description': '', 'routes': []}
        for route in routes:
            trips = get_trip_schedules_from_dict(route.route_id)
            all_routes['routes'].append({
                'id': route.route_id,
                'short_name': 'nan',
                'long_name': route.route_long_name,
                'description': route.route_desc,
                'route': get_direction(route.route_long_name)[0],
                'direction': get_direction(route.route_long_name)[1],
                'start': bus_stops_dict[bus_route_details_dict[route.route_id][0]],
                'end': bus_stops_dict[bus_route_details_dict[route.route_id][1]],
                'polyline': get_polyline(route.route_id),
                'trips_schedule': trips,
                'trips_count': len(trips),
                'city': 'pun',
                'agency': route.agency_id
            })
        return jsonify(all_routes), 200
    except Exception as e:
        print(e)
        all_routes = {
            'status': 'failed',
            'description': 'Some error occurred'
        }
        return jsonify(all_routes), 400


def get_only_routes_func():
    try:
        routes = BusRoute.query.all()
        all_routes = {'status': 'success', 'description': '', 'routes': []}
        for route in routes:
            all_routes['routes'].append({
                'id': route.route_id,
                'short_name': 'nan',
                'long_name': route.route_long_name,
                'description': route.route_desc,
                'agency': route.agency_id
            })
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
            'message': 'success',
            'description': '',
            'stops': [
                {
                    'id': stop.stop_id,
                    'name': stop.stop_name,
                    'lat': float(stop.stop_lat),
                    'lon': float(stop.stop_lon),
                    'lng': float(stop.stop_lon),
                    'next_stop': bus_next_stop_dict[stop.stop_id],
                    'stop_type': 'bus',
                    'city': 'pun',
                    'agency': 'pmpml'
                }
                for stop in stops
            ]
        }
        return jsonify(all_stops), 200
    except Exception as e:
        print(e)
        all_routes = {
            'status': 'failed',
            'message': 'failed',
            'description': 'Some error occurred'
        }
        return jsonify(all_routes), 400


def get_transit_route_details_func(route):
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    try:
        route = BusRoute.query.filter(BusRoute.route_long_name == route).one()
        transit_routes = {
            'status': 'success',
            'msg': 'success',
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
                    'polyline': get_polyline(route.route_id),
                    'stops': [{'stop_id': x[0], 'name': x[1], 'lat': float(x[2]), 'lon': float(x[3])} for x in
                              ast.literal_eval(
                                  BusAllRoute.query.filter_by(route_id=route.route_id).one().stops_details)],
                    'stops_distance': ast.literal_eval(
                        BusRouteStopDistance.query.filter_by(route_id=route.route_id).one().
                        stops_distances),
                    'trips_schedule': get_trip_schedules_from_dict(route.route_id)
                }
            ]
        }
        return jsonify(transit_routes), 200
    except Exception as e:
        print(e)
        transit_routes = {
            'status': 'failed',
            'msg': 'failed',
            'description': 'some error occurred',
        }
        return jsonify(transit_routes), 400


def get_routes_on_stop_func(stop_id, time=None):
    val = BusRoutesDetail.query.all()
    for v in val:
        bus_route_details_dict[v.route_id] = (v.start_stop, v.end_stop)
    # if time is None:
    #     query_time = datetime.datetime.now().time()
    # else:
    #     query_time = datetime.datetime.strptime(time, "%H:%M:%S").time()
    stop = BusStop.query.filter(BusStop.stop_id == stop_id).one()
    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name
    routes = list(set(trips_df[trips_df.trip_id.isin(
        stop_times_df[stop_times_df.stop_id == stop_id].trip_id.tolist())].route_id.tolist()))
    routes_on_stop = {'status': '', 'description': '', 'stop_name': stop.stop_name,
                      'next_stop': bus_next_stop_dict[stop.stop_id],
                      'updated_at': datetime.datetime.now().time().strftime("%H:%M:%S")}
    upcoming_routes = []
    for route in routes:
        print(route)
        rt = BusRoute.query.filter(BusRoute.route_id == route).one()
        trip_schedule = get_trip_schedules_from_static(rt.route_id, int(stop_id))
        trip_times = [datetime.datetime.strptime(time_str, "%H:%M").time() for time_str in trip_schedule]
        # upcoming_times = sorted([time for time in trip_times if time > query_time])
        upcoming_times = sorted([time for time in trip_times])
        # next_two_times = [time.strftime("%H:%M") for time in upcoming_times[:2]]
        next_two_times = [time.strftime("%H:%M") for time in upcoming_times]
        if len(next_two_times) == 0:
            next_two_times.append("NA")
        upcoming_routes.append({'route': rt.route_long_name, 'upcoming_trips_schedule': next_two_times,
                                'end_stop': bus_stops_dict[bus_route_details_dict[rt.route_id][1]]})

    upcoming_routes = sorted(upcoming_routes,
                             key=lambda x: x["upcoming_trips_schedule"][0] if x["upcoming_trips_schedule"] else "")

    if len(upcoming_routes) > 0:
        routes_on_stop['routes'] = upcoming_routes
        routes_on_stop['status'] = 'success'
        routes_on_stop['description'] = ''
        return jsonify(routes_on_stop), 200
    else:
        routes_on_stop['status'] = 'failed'
        routes_on_stop['description'] = 'No upcoming buses'
    return jsonify(routes_on_stop), 400


def get_trip_schedules_from_static(route_id, stop_id=0):
    return [convert_to_h_m(x) for x in stop_times_df.loc[
        stop_times_df.trip_id.isin(trips_df[trips_df.route_id == int(route_id)].trip_id.tolist()) &
        (stop_times_df.stop_sequence == stop_id), 'arrival_time'].tolist()]


def get_trip_schedules_from_dict(route_id):
    return ast.literal_eval(schedule_df.at[route_id, 'schedule'])
    # return ast.literal_eval(schedule_df[schedule_df.route_id == route_id].schedule.squeeze())


def convert_to_h_m(time):
    time_split = time.split(":")
    if int(time_split[0]) > 23:
        time_split[0] = int(time_split[0]) - 24
        time = f'{time_split[0]}:{time_split[1]}:{time_split[2]}'
    time_obj = datetime.datetime.strptime(time, "%H:%M:%S")
    return time_obj.strftime("%H:%M")


def make_combined_response():
    # Initialize the dictionary to store next stop data
    bus_next_stop_dict = {}
    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name

    all_stops = BusStop.query.all()
    stops_data = [
        {
            'id': stop.stop_id,
            'name': stop.stop_name,
            'lat': float(stop.stop_lat),
            'lon': float(stop.stop_lon),
            'next_stop': bus_next_stop_dict[stop.stop_id],
            'type': 'bus',
            'city': 'pun',
            'agency': 'pmpml'
        }
        for stop in all_stops
    ]

    routes_data = []
    routes = BusRoute.query.all()
    for route in routes:
        try:
            route_id = route.route_id
            bus_all_route = BusAllRoute.query.filter_by(route_id=route.route_id).one()
            stops_details = ast.literal_eval(bus_all_route.stops_details)
            stops = [{'stop_id': x[0], 'name': x[1], 'lat': float(x[2]), 'lon': float(x[3])} for x in stops_details]

            only_route, direction = get_direction(route.route_long_name)
            start_stop = stops[0]['name'] if stops else None
            end_stop = stops[-1]['name'] if stops else None

            bus_route_stop_distance = BusRouteStopDistance.query.filter_by(route_id=route.route_id).one()
            stops_distance = ast.literal_eval(bus_route_stop_distance.stops_distances)

            trips_schedule = get_trip_schedules_from_dict(route_id)
            trips_count = len(trips_schedule)

            route_data = {
                'id': route_id,
                'direction': direction,
                'route': only_route,
                'short_name': None,
                'long_name': route.route_long_name,
                'description': route.route_desc,
                'polyline': get_polyline(route.route_id),
                'city': 'pun',
                'type': 'bus',
                'trips_schedule': trips_schedule,
                'stops': [x['stop_id'] for x in stops],
                'stops_distance': stops_distance,
                'agency': route.agency_id,
                'end': end_stop,
                'start': start_stop,
                'trips_count': trips_count,
            }
            routes_data.append(route_data)
        except Exception as e:
            print(f"Failed to process route {route.route_id}: {e}")

    response = {
        'status': 'success',
        'description': '',
        'routes': routes_data,
        'stops': stops_data
    }

    return jsonify(response), 200


def get_nearby_stop_bus(query_coords):
    val = BusNextStop.query.all()
    for v in val:
        bus_next_stop_dict[v.cur_stop] = v.next_stop_name
    try:
        q_lat = float(query_coords[0])
        q_lng = float(query_coords[1])

        vehicle_lats = stops_df['stop_lat'].values.astype(float)
        vehicle_lngs = stops_df['stop_lon'].values.astype(float)

        stst = 6367 * 2 * np.arcsin(np.sqrt(
            np.sin((np.radians(vehicle_lats) - math.radians(q_lat)) / 2) ** 2 + math.cos(
                math.radians(q_lat)) * np.cos(np.radians(vehicle_lats)) * np.sin(
                (np.radians(vehicle_lngs) - math.radians(q_lng)) / 2) ** 2))
        bus_record_indices_within_radius = np.where(stst <= radius)[0]
        res = stops_df.iloc[bus_record_indices_within_radius]
        res['distance'] = stst[bus_record_indices_within_radius]
        res.sort_values(by='distance', inplace=True)
        resp = {'stops': [], 'status': 'success', 'message': '', 'count': len(res)}
        for a in res.iterrows():
            resp['stops'].append({'id': a[1].stop_id, 'name': a[1].stop_name, 'lat': float(a[1].stop_lat),
                                  'lng': float(a[1].stop_lon), 'distance': round(a[1].distance * 100, 2),
                                  'stop_type': 'bus', 'next_stop': bus_next_stop_dict[a[1].stop_id]})
        return jsonify(resp), 200
    except Exception as e:
        print(e)
        resp = {'stops': [], 'status': 'failed', 'message': 'some error occurred', 'count': 0}
        return jsonify(resp), 400


def get_fare_estimate(route, start_idx, end_idx, fare=None):
    resp = {'data': {}, 'status': '', 'message': ''}
    try:
        if fare is not None:
            fare = get_stop_by_amount(route, start_idx, fare)
        else:
            fare = get_fare_by_idx(route, start_idx, end_idx)
        if fare is not None:
            resp['data'] = {'fare': fare}
            resp['status'] = 'success'
            resp['message'] = 'Fare estimate successful'
        else:
            resp['data'] = {'fare': None}
            resp['status'] = 'failed'
            resp['message'] = f'Fare estimate failed.'
    except Exception as e:
        resp['data'] = {'fare': None}
        resp['status'] = 'failed'
        resp['message'] = f'Fare estimate failed due to {e}'
    return resp, 200


def get_fare_estimate_v2(route, start_idx, end_idx, fare=None):
    resp = {'data': {}, 'status': '', 'message': ''}
    try:
        fare = get_fare_by_idx_v2(route, start_idx, end_idx)
        if fare is not None:
            resp['data'] = {'fare': fare}
            resp['status'] = 'success'
            resp['message'] = 'Fare estimate successful'
        else:
            resp['data'] = {'fare': None}
            resp['status'] = 'failed'
            resp['message'] = f'Fare estimate failed.'
    except Exception as e:
        resp['data'] = {'fare': None}
        resp['status'] = 'failed'
        resp['message'] = f'Fare estimate failed due to {e}'
    return resp, 200



def get_fare_options(route, start_idx):
    resp = {'data': {}, 'status': '', 'message': ''}
    fare = get_fare_options_from_source(route, start_idx)
    if fare is not None:
        try:
            resp['data'] = generate_fare_options_response(fare)
            resp['status'] = 'success'
            resp['message'] = 'Fare options fetched successful'
            return resp, 200
        except Exception:
            resp['data'] = {'fare': None}
            resp['status'] = 'failed'
            resp['message'] = f'Fare estimate failed.'
    else:
        resp['data'] = {'fare': None}
        resp['status'] = 'failed'
        resp['message'] = f'Fare estimate failed.'
    return resp, 400


def generate_fare_options_response(fare_dict):
    fare_list = []
    current_fare = None
    start_stop_index = None
    for idx, fare in fare_dict.items():
        if fare != current_fare:
            if current_fare is not None:
                # Append the previous fare segment
                fare_list.append({
                    "start_stop_index": start_stop_index,
                    "end_stop_index": int(idx) - 1,
                    "basic_fare": float(current_fare['basic']),
                    "toll": current_fare['toll'],
                    "total_fare": float(current_fare['total']),
                    "amount_payable_by_user": float(current_fare['total']),
                    "discount_percentage": 0
                })
            # Update variables for the new fare segment
            current_fare = fare
            start_stop_index = int(idx)

    fare_list.append({
        "start_stop_index": start_stop_index,
        "end_stop_index": int(idx),
        "basic_fare": float(current_fare['basic']),
        "toll": current_fare['toll'],
        "total_fare": float(current_fare['total']),
        "amount_payable_by_user": float(current_fare['total']),
        "discount_percentage": 0
    })

    return fare_list


if __name__ == '__main__':
    pass
