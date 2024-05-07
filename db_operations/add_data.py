import ast

import datetime
import geopy.distance
import pandas as pd

from app import app
from exts import db
from db_operations.models_file import BusRoute, BusTrip, BusStopTime, BusStop, BusAllRoute, BusRoutesDetail, \
    BusNextStop, BusRouteStopDistance, UsersActivity

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import polyline

from utils.main import get_trip_schedules_from_static

static_path_bus = 'static/data/GTFS/'

bus_routes_df = pd.read_csv(static_path_bus + 'routes.txt')
bus_stops_df = pd.read_csv(static_path_bus + 'stops.txt')
bus_trips_df = pd.read_csv(static_path_bus + 'trips.txt')
bus_stop_times_df = pd.read_csv(static_path_bus + 'stop_times.txt')
bus_shapes_df = pd.read_csv(static_path_bus + 'shapes.txt')


def add_routes_bus():
    with app.app_context():
        val = bus_routes_df.to_dict('records')
        with db.engine.begin() as conn:
            try:
                conn.execute(BusRoute.__table__.insert(), val)
                conn.execute(text('CREATE INDEX ix_bus_routes_route_id_index ON bus_route (route_id)'))
                conn.commit()
                print("Added routes.")
            except Exception as e:
                print(f'add_routes_bus {e}')


def add_stops_bus():
    val = bus_stops_df.to_dict('records')
    with db.engine.begin() as conn:
        try:
            conn.execute(BusStop.__table__.insert(), val)
            conn.execute(text("CREATE INDEX ix_bus_stops_stop_id_index ON bus_stop (stop_id)"))
            conn.commit()
        except Exception as e:
            print(f'add_stops_bus {e}')
    print("Added stops.")


def add_trips_bus():
    val = bus_trips_df.to_dict('records')
    with db.engine.begin() as conn:
        try:
            conn.execute(BusTrip.__table__.insert(), val)
            conn.execute(text("CREATE INDEX ix_bus_trips_trip_id_index ON bus_trip (trip_id)"))
            conn.commit()
        except Exception as e:
            print(f'add_trips_bus {e}')
    print('Added trips.')


# This is used to add the static stop_time data to database.
def add_stop_times_bus():
    val = bus_stop_times_df.to_dict('records')
    with db.engine.begin() as conn:
        try:
            conn.execute(BusStopTime.__table__.insert(), val)
            conn.execute(text("CREATE INDEX ix_bus_stop_times_trip_id_index ON bus_stop_time (trip_id)"))
            conn.commit()
        except Exception as e:
            print(f'add_stop_times_bus {e}')
    print('Added stop times.')


def generate_routes_bus():
    a = "Generated routes."
    try:
        Session = sessionmaker(bind=db.engine)
        # Open a session
        with Session() as session:
            for r in bus_routes_df.route_id:
                t = BusTrip.query.filter_by(route_id=r).first().trip_id
                seq = BusStopTime.query.filter_by(trip_id=t).all()
                dar = BusAllRoute()
                dar.route_id = r
                stops_details = []
                for s in seq:
                    stops_details.append(
                        [s.bus_stops.stop_id, s.bus_stops.stop_name, s.bus_stops.stop_lat, s.bus_stops.stop_lon])
                dar.stops_details = str(stops_details)
                session.add(dar)

            # Commit the changes made during the session
            session.commit()

        # Execute raw SQL outside of the session
        with db.engine.connect() as conn:
            conn.execute(text("CREATE INDEX ix_bus_all_routes_route_id_index ON bus_all_route (route_id)"))

    except Exception as e:
        print(f'generate_routes_bus {e}')

    print(a)


def generate_routes_bus_():
    a = "Generated routes."

    with db.engine.begin() as conn:
        try:
            for r in bus_routes_df.route_id:
                t = BusTrip.query.filter_by(route_id=r).first().trip_id
                seq = BusStopTime.query.filter_by(trip_id=t).all()
                dar = BusAllRoute()
                dar.route_id = r
                stops_details = []
                for s in seq:
                    stops_details.append(
                        [s.bus_stops.stop_id, s.bus_stops.stop_name, s.bus_stops.stop_lat, s.bus_stops.stop_lon])
                dar.stops_details = str(stops_details)
                conn.add(dar)
                conn.commit()
            conn.execute(text("CREATE INDEX ix_bus_all_routes_route_id_index ON bus_all_route (route_id)"))
            conn.commit()
        except Exception as e:
            print(f'generate_routes_bus {e}')

    print(a)


def set_route_details_bus():
    a = 'Added route details.'

    try:
        Session = sessionmaker(bind=db.engine)
        # Open a session for ORM operations
        with Session() as session:
            for r in bus_routes_df.route_id:
                try:
                    route_details = BusRoutesDetail()
                    route_details.route_id = BusRoute.query.filter_by(route_id=r).first().route_id
                    ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                    arv = ast.literal_eval(ar)
                    route_details.start_stop = BusStop.query.filter_by(stop_id=arv[0][0]).first().stop_id
                    route_details.end_stop = BusStop.query.filter_by(stop_id=arv[-1][0]).first().stop_id

                    session.add(route_details)
                except Exception as e:
                    print(f'set_route_details_bus inner {e}')

            # Commit the session once all objects are added
            session.commit()

        # Execute raw SQL command using a separate connection
        with db.engine.connect() as conn:
            conn.execute(text("CREATE INDEX ix_bus_routes_details_route_id_index ON bus_routes_detail (route_id)"))

    except Exception as e:
        print(f'set_route_details_bus outer {e}')

    print(a)


def set_route_details_bus_():
    a = 'Added route details.'

    with db.engine.begin() as conn:
        try:
            for r in bus_routes_df.route_id:
                try:
                    route_details = BusRoutesDetail()
                    route_details.route_id = BusRoute.query.filter_by(route_id=r).first().route_id
                    ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                    arv = ast.literal_eval(ar)
                    route_details.start_stop = BusStop.query.filter_by(stop_id=arv[0][0]).first().stop_id
                    route_details.end_stop = BusStop.query.filter_by(stop_id=arv[-1][0]).first().stop_id
        
                    conn.add(route_details)
                    conn.commit()
                except Exception as e:
                    print(f'set_route_details_bus {e}')
            conn.execute(text("CREATE INDEX ix_bus_routes_details_route_id_index ON bus_routes_detail (route_id)"))
            conn.commit()
        except Exception as e:
            print(f'set_route_details_bus {e}')

    print(a)


def set_transit_route_stops_dist_bus():
    a = 'Added route distances.'

    try:
        Session = sessionmaker(bind=db.engine)
        # Open a session for ORM operations
        with Session() as session:
            for r in bus_routes_df.route_id:
                distance = BusRouteStopDistance()
                distance.route_id = BusRoute.query.filter_by(route_id=r).first().route_id
                ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                arv = ast.literal_eval(ar)
                r_dist_list = []
                for i in range(len(arv) - 1):
                    coords1 = (arv[i][2], arv[i][3])
                    coords2 = (arv[i + 1][2], arv[i + 1][3])
                    r_dist_list.append(geopy.distance.distance(coords1, coords2).km)
                distance.stops_distances = str(r_dist_list)
                session.add(distance)

            # Commit the session once all objects are added
            session.commit()

        # Execute raw SQL command using a separate connection
        with db.engine.connect() as conn:
            conn.execute(
                text("CREATE INDEX ix_bus_route_stops_distance_route_id_index ON bus_route_stop_distance (route_id)"))

    except Exception as e:
        print(f'set_transit_route_stops_dist_bus {e}')

    print(a)


def set_transit_route_stops_dist_bus_():
    a = 'Added route distances.'
    
    with db.engine.begin() as conn:
        try:
            for r in bus_routes_df.route_id:
                distance = BusRouteStopDistance()
                distance.route_id = BusRoute.query.filter_by(route_id=r).first().route_id
                ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                arv = ast.literal_eval(ar)
                r_dist_list = []
                for i in range(len(arv) - 1):
                    coords1 = (arv[i][2], arv[i][3])
                    coords2 = (arv[i + 1][2], arv[i + 1][3])
                    r_dist_list.append(geopy.distance.distance(coords1, coords2).km)
                distance.stops_distances = str(r_dist_list)
                conn.add(distance)
                conn.commit()
                # print(r)
            conn.execute(text("CREATE INDEX ix_bus_route_stops_distance_route_id_index ON bus_route_stop_distance"
                          "(route_id)"))
        except Exception as e:
            print(f'set_transit_route_stops_dist_bus {e}')

    print(a)


def set_next_stop_bus():
    a = 'Added next stop.'

    try:
        Session = sessionmaker(bind=db.engine)
        # Open a session for ORM operations
        with Session() as session:
            stops_dict = {}
            for r in bus_routes_df.route_id:
                ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                arv = ast.literal_eval(ar)
                if len(arv) != 0:
                    for j in range(len(arv) - 1):
                        if arv[j][0] in stops_dict:
                            stops_dict[arv[j][0]].append(arv[j + 1][0])
                        else:
                            stops_dict[arv[j][0]] = [arv[j + 1][0]]

            all_stops = BusStop.query.all()
            all_stops = [x.stop_id for x in all_stops]

            for s in all_stops:
                next_stop = BusNextStop()
                next_stop.cur_stop = BusStop.query.filter_by(stop_id=s).first().stop_id
                try:
                    next_stop.next_stop = BusStop.query.filter_by(stop_id=max(stops_dict[s], key=stops_dict[s].count)) \
                        .first().stop_id
                    next_stop.next_stop_name = BusStop.query.filter_by(
                        stop_id=max(stops_dict[s], key=stops_dict[s].count)) \
                        .first().stop_name
                except KeyError:
                    next_stop.next_stop = -1
                    next_stop.next_stop_name = 'Terminal'

                session.add(next_stop)

            # Commit the session once all objects are added
            session.commit()

        # Execute raw SQL command using a separate connection
        with db.engine.connect() as conn:
            conn.execute(text("CREATE INDEX ix_bus_next_stop_cur_stop_index ON bus_next_stop (cur_stop)"))

    except Exception as e:
        print(f'set_next_stop_bus {e}')

    print(a)


def set_next_stop_bus_():
    a = 'Added next stop.'

    with db.engine.begin() as conn:
        try:
            stops_dict = {}
            for r in bus_routes_df.route_id:
                ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
                arv = ast.literal_eval(ar)
                if len(arv) != 0:
                    for j in range(len(arv) - 1):
                        if arv[j][0] in stops_dict:
                            stops_dict[arv[j][0]].append(arv[j + 1][0])
                        else:
                            stops_dict[arv[j][0]] = [arv[j + 1][0]]
        
            all_stops = BusStop.query.all()
            all_stops = [x.stop_id for x in all_stops]
        
            for s in all_stops:
                next_stop = BusNextStop()
                next_stop.cur_stop = BusStop.query.filter_by(stop_id=s).first().stop_id
                try:
                    next_stop.next_stop = BusStop.query.filter_by(stop_id=max(stops_dict[s], key=stops_dict[s].count)) \
                        .first().stop_id
                    next_stop.next_stop_name = BusStop.query.filter_by(stop_id=max(stops_dict[s], key=stops_dict[s].count)) \
                        .first().stop_name
                except KeyError:
                    next_stop.next_stop = -1
                    next_stop.next_stop_name = 'Terminal'
        
                conn.add(next_stop)
                conn.commit()
        
                conn.execute(text("CREATE INDEX ix_bus_next_stop_cur_stop_index ON bus_next_stop (cur_stop)"))
        except Exception as e:
            print(f'set_next_stop_bus {e}')

    print(a)


def add_user_activity(device_id, end_point, params=None, location=None, session_id=None):
    with db.engine.begin() as conn:
        user_activity = UsersActivity(device_id=device_id, time_stamp=datetime.datetime.now(), end_point=end_point,
                                      params=params, location=location, session_id=session_id)
        conn.add(user_activity)
        conn.commit()


def generate_polylines():
    merged_df = pd.merge(bus_trips_df, bus_shapes_df, on='shape_id', how='inner')

    merged_df = merged_df.drop_duplicates(subset=['route_id', 'shape_pt_sequence'])
    # Group by route_id
    grouped = merged_df.groupby('route_id')

    # Initialize empty lists to store route_ids and polylines
    route_ids = []
    polylines = []

    # Iterate over groups
    for route_id, group in grouped:
        # Concatenate latitude and longitude into a list of tuples
        points = list(zip(group['shape_pt_lat'], group['shape_pt_lon']))

        # Encode the polyline
        encoded_polyline = polyline.encode(points)

        if not encoded_polyline:
            encoded_polyline = ''

        if route_id not in route_ids:
            # Append route_id and encoded polyline to lists
            route_ids.append(str(route_id))
            polylines.append(encoded_polyline)

    # Create DataFrame from lists
    polyline_df = pd.DataFrame({'route_id': route_ids, 'polyline': polylines})
    polyline_df.to_csv(static_path_bus+'polylines.csv', index=False)

    return polyline_df


def generate_bus_route_details():
    headers = ['start', 'start_id', 'end', 'end_id', 'lat', 'lng', 'route_id_id']
    val = []
    for r in bus_routes_df.route_id:
        ar = BusAllRoute.query.filter_by(route_id=r).first().stops_details
        arv = ast.literal_eval(ar)
        start = BusStop.query.filter_by(stop_id=arv[0][0]).first()
        end = BusStop.query.filter_by(stop_id=arv[-1][0]).first()
        val.append([start.stop_name, start.stop_id, end.stop_name, end.stop_id, end.stop_lat, end.stop_lon, r])
    df = pd.DataFrame([dict(zip(headers, x)) for x in val])
    df.to_csv(static_path_bus+'bus_route_details.csv', index_label='id', columns=headers)


def generate_schedule():
    schedule_dict = dict()
    for r in bus_routes_df.route_id:
        schedule_dict[r] = str(get_trip_schedules_from_static(r))
    df = pd.DataFrame.from_dict(schedule_dict, orient='index')
    df.columns = ['schedule']
    df.to_csv(static_path_bus+'schedule.csv', index_label='route_id')


def set_data():
    add_routes_bus()
    add_stops_bus()
    add_trips_bus()
    add_stop_times_bus()
    generate_routes_bus()
    set_route_details_bus()
    set_transit_route_stops_dist_bus()
    set_next_stop_bus()
    generate_polylines()
    generate_bus_route_details()


generate_schedule()

# set_data()