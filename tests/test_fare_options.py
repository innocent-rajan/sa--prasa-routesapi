import sqlite3
import requests
from tqdm import tqdm


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


def verify_response(param, route):
    try:
        if 'data' in param and param['data']:
            pass
        else:
            print(f"Route {route}: Failed - Data is null or empty")
            print(f"Response: {param}")
    except ValueError:
        print(f"Route {route}: Failed - Invalid JSON response")
        print(f"Response: {param}")


def test_endpoints(routes, endpoint_url):
    """
    Test endpoint with each route and print success for all.
    """
    headers = {'Accept': 'application/json', 'x-api-key': 'test'}
    for route in tqdm(routes, desc="Testing endpoints"):
        payload = {'route_id': route, 'start_idx': 0}
        response = requests.get(endpoint_url, params=payload, headers=headers)
        if response.status_code == 200:
            verify_response(response.json(), route)
        else:
            print(f"Route {route}: Failed with status code {response.status_code}")
            print(f"Parameters: {payload}")


if __name__ == "__main__":
    # Path to your SQLite database
    db_path = '../instance/fare_matrix.db'

    # The endpoint URL you want to test
    endpoint_url = 'http://192.168.34.78:9000/fare_options'

    # Fetch routes from the database
    routes = fetch_routes_from_db(db_path)

    # Test the endpoint with each route
    test_endpoints(routes, endpoint_url)
