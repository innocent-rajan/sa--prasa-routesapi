import datetime

import requests
from tqdm import tqdm

headers = {'Accept': 'application/json', 'x-api-key': 'test'}


def fetch_routes_from_api():
    url = 'http://192.168.32.18:9000/routes'
    response = requests.get(url, headers=headers)
    return [x['long_name'] for x in response.json()['routes']]


def fetch_route_details_from_api(route):
    start = datetime.datetime.now()
    url = 'http://192.168.32.18:9000/transit_route_details'
    payload = {'route': route}
    response = requests.get(url, params=payload, headers=headers)
    return len(response.json()['transit_route'][0]['stops']), (datetime.datetime.now() - start).microseconds


if __name__ == '__main__':
    routes = fetch_routes_from_api()
    _time_elapsed = {}
    for i in range(3):
        for idx, route in tqdm(enumerate(routes)):
            stops_count, time_elapsed = fetch_route_details_from_api(route)
            if route in _time_elapsed:
                _time_elapsed[route].append(time_elapsed)
            else:
                _time_elapsed[route] = [time_elapsed]
