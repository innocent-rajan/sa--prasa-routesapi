from sqlalchemy import UniqueConstraint

from exts import db


# Bus models
class BusRoute(db.Model):
    __bind_key__ = 'data-db'
    route_id = db.Column(db.String, primary_key=True)
    route_short_name = db.Column(db.String(), nullable=True)
    route_long_name = db.Column(db.String())
    route_desc = db.Column(db.String())
    route_type = db.Column(db.Integer)
    agency_id = db.Column(db.String())

    bus_trips = db.relationship('BusTrip', backref='bus_route', lazy='dynamic')
    bus_all_routes = db.relationship('BusAllRoute', backref='bus_route', lazy='dynamic')
    bus_fare_stage = db.relationship('BusFareStage', backref='bus_route', lazy='dynamic')
    bus_route_details = db.relationship('BusRoutesDetail', backref='bus_route', lazy='dynamic')
    bus_stop_dist = db.relationship('BusRouteStopDistance', backref='bus_route', lazy='dynamic')

    def __repr__(self):
        return f"<BusRoute {self.route_long_name}, {self.agency_id}>"


class BusStop(db.Model):
    __bind_key__ = 'data-db'
    stop_id = db.Column(db.String(), primary_key=True)
    stop_code = db.Column(db.String(), nullable=True)
    stop_name = db.Column(db.String())
    stop_lat = db.Column(db.String())
    stop_lon = db.Column(db.String())

    stop_times = db.relationship('BusStopTime', backref='bus_stops', lazy='dynamic')
    route_detail_start = db.relationship('BusRoutesDetail', foreign_keys='BusRoutesDetail.start_stop')
    route_detail_end = db.relationship('BusRoutesDetail', foreign_keys='BusRoutesDetail.end_stop')
    next_stop_cur = db.relationship('BusNextStop', foreign_keys='BusNextStop.cur_stop')
    next_stop_next = db.relationship('BusNextStop', foreign_keys='BusNextStop.next_stop')

    def __repr__(self):
        return f"<BusStop {self.stop_name}, {self.stop_id}>"


class BusTrip(db.Model):
    __bind_key__ = 'data-db'
    trip_id = db.Column(db.String(), primary_key=True)
    shape_id = db.Column(db.String(), nullable=True)
    service_id = db.Column(db.Integer)
    route_id = db.Column(db.String(), db.ForeignKey('bus_route.route_id'))

    stop_times = db.relationship('BusStopTime', backref='bus_trip', lazy='dynamic')

    def __repr__(self):
        return f"<BusTrips {self.trip_id}, {self.route_id}>"


class BusStopTime(db.Model):
    __bind_key__ = 'data-db'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.String(), db.ForeignKey('bus_trip.trip_id'))
    arrival_time = db.Column(db.String())
    departure_time = db.Column(db.String())
    stop_id = db.Column(db.String(), db.ForeignKey('bus_stop.stop_id'))
    stop_sequence = db.Column(db.Integer)
    __table_args__ = (UniqueConstraint("trip_id", "stop_sequence", name="unique_trip_id_stop_sequence"),)

    def __repr__(self):
        return f"<BusStopTimes {self.trip_id}, {self.route_id}>"


class BusAllRoute(db.Model):
    __bind_key__ = 'data-db'
    route_id = db.Column(db.String(), db.ForeignKey('bus_route.route_id'), nullable=False, primary_key=True)
    stops_details = db.Column(db.String(10000))

    def __repr__(self):
        return f"<BusAllRoute {self.route_id}>"


class BusRoutesDetail(db.Model):
    __bind_key__ = 'data-db'
    route_id = db.Column(db.String(), db.ForeignKey('bus_route.route_id'), nullable=False, primary_key=True)
    start_stop = db.Column(db.String(), db.ForeignKey('bus_stop.stop_id'), nullable=False)
    end_stop = db.Column(db.String(), db.ForeignKey('bus_stop.stop_id'), nullable=False)

    def __repr__(self):
        return f"<BusRoutesDetail {self.route_id}>"


class BusNextStop(db.Model):
    __bind_key__ = 'data-db'
    cur_stop = db.Column(db.String(10), db.ForeignKey('bus_stop.stop_id'), nullable=False, primary_key=True)
    next_stop = db.Column(db.String(10), db.ForeignKey('bus_stop.stop_id'), nullable=False)
    next_stop_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<BusNextStop {self.cur_stop}>"


class BusRouteStopDistance(db.Model):
    __bind_key__ = 'data-db'
    id = db.Column(db.Integer, autoincrement=True)
    route_id = db.Column(db.String(), db.ForeignKey('bus_route.route_id'), nullable=False, primary_key=True)
    stops_distances = db.Column(db.String(1000))

    def __repr__(self):
        return f"<BusRouteStopDistance {self.route_id}>"


class BusFareStage(db.Model):
    __bind_key__ = 'data-db'
    route_id = db.Column(db.String(), db.ForeignKey('bus_route.route_id'), nullable=False, primary_key=True)
    fare_stage = db.Column(db.String(10000))

    def __repr__(self):
        return f"<BusFareStage {self.route_id}>"


# User models
class UsersActivity(db.Model):
    __bind_key__ = 'user-db'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(100))
    time_stamp = db.Column(db.DateTime)
    end_point = db.Column(db.String(24))
    session_id = db.Column(db.String(64))
    params = db.Column(db.String(24), nullable=True)
    location = db.Column(db.String(24), nullable=True)

    def __repr__(self):
        return f"UsersActivity {self.device_id}, {self.end_point}>"


if __name__ == '__main__':
    pass