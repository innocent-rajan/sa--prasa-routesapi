import sqlite3
import time

import requests
from tqdm import tqdm


headers = {'Accept': 'application/json', 'x-api-key': 'test'}


def fetch_routes_from_api():
    url = 'http://192.168.34.78:9000/routes'
    response = requests.get(url, headers=headers)
    return [x['long_name'] for x in response.json()['routes']]


def fetch_route_details_from_api(route):
    url = 'http://192.168.34.78:9000/transit_route_details'
    payload = {'route': route}
    response = requests.get(url, params=payload, headers=headers)
    return len(response.json()['transit_route'][0]['stops'])


def fetch_routes_from_db(db_path):
    """
    Fetch all routes from the database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT route FROM fares")
    routes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return routes


def verify_response(param, route, comb):
    try:
        if 'data' in param and param['data']:
            if param['data']['fare'] is None or param['data']['fare'] == 0:
                print(f"Route {route}: Failed - Data is null or empty")
                print(f"Response: {param} & comb: {comb}")
        else:
            print(f"Route {route}: Failed - Data is null or empty")
            print(f"Response: {param}")
    except ValueError:
        print(f"Route {route}: Failed - Invalid JSON response")
        print(f"Response: {param}")


def test_endpoints(routes, endpoint_url):
    for route in tqdm(routes, desc="Testing endpoints"):
        payload = {'route_id': route, 'start_idx': 0}
        response = requests.get(endpoint_url, params=payload, headers=headers)
        if response.status_code == 200:
            verify_response(response.json(), route)
        else:
            print(f"Route {route}: Failed with status code {response.status_code}")
            print(f"Parameters: {payload}")


def test_endpoints_for_all(route, endpoint_url, stops_count):
    all_comb = [(x,y) for x in range(stops_count - 1) for y in range(x + 1, stops_count)]
    for comb in tqdm(all_comb, desc=f"Testing endpoints : {route}"):
        payload = {'route_id': route, 'start_idx': comb[0], 'end_idx': comb[1]}
        response = requests.get(endpoint_url, params=payload, headers=headers)
        if response.status_code == 200:
            verify_response(response.json(), route, comb)
        else:
            print(f"Route {route}: Failed with status code {response.status_code}")
            print(f"Parameters: {payload}")


if __name__ == "__main__":
    # Path to your SQLite database
    db_path = '../instance/fare_matrix_6_8_updated.db'

    # The endpoint URL you want to test
    endpoint_url = 'http://192.168.34.78:9000/fare_options'
    estimate_endpoint_url = 'http://192.168.34.78:9000/fare_estimate'

    # Fetch routes from the database
    # routes = fetch_routes_from_db(db_path)
    routes = fetch_routes_from_api()

    for route in routes:
        stops_count = fetch_route_details_from_api(route)
        test_endpoints_for_all(route, estimate_endpoint_url, stops_count)
        time.sleep(3)
