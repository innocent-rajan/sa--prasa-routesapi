import datetime

import requests
from tqdm import tqdm

headers = {'Accept': 'application/json', 'x-api-key': 'test'}


def fetch_routes_from_api(local=False):
    if local:
        url = 'http://192.168.32.18:9000/routes'
    else:
        url = 'https://dev-rrl-routesapi.chartr.in/routes'
    response = requests.get(url, headers=headers)
    return [x['long_name'] for x in response.json()['routes']]


def fetch_stops_from_api(local=False):
    if local:
        url = 'http://192.168.32.18:9000/stops'
    else:
        url = 'https://dev-rrl-routesapi.chartr.in/stops'
    response = requests.get(url, headers=headers)
    return response.json()['stops']


def fetch_route_details_from_api(route, local=False):
    start = datetime.datetime.now()
    if local:
        url = 'http://192.168.32.18:9000/transit_route_details'
    else:
        url = 'https://dev-rrl-routesapi.chartr.in/transit_route_details'
    payload = {'route': route}
    response = requests.get(url, params=payload, headers=headers)
    return response.json()


if __name__ == '__main__':
    routes_local = fetch_routes_from_api(True)
    routes_server = fetch_routes_from_api(False)
    print(routes_local == routes_server)

    stops_local = fetch_stops_from_api(True)
    stops_server = fetch_stops_from_api(False)
    print(stops_local == stops_server)

    for idx, route in tqdm(enumerate(routes_local)):
        resp_local = fetch_route_details_from_api(route, True)
        resp_server = fetch_route_details_from_api(route, False)
        if resp_local != resp_server:
            print(route)
