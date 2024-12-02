import sqlite3
import json
import pickle
import ast

conn = sqlite3.connect('file:instance/fare_matrix_17_9.db?mode=ro', check_same_thread=False)
# conn = sqlite3.connect('file:', check_same_thread=False)
_conn = sqlite3.connect('file:', check_same_thread=False)

try:
    with open('static/data/B1UP_FARE_DICT.pickle', 'rb') as file:
        b1up_dict = pickle.load(file)
except Exception as e:
    print(e)

try:
    with open('static/data/B1DOWN_FARE_DICT.pickle', 'rb') as file:
        b1down_dict = pickle.load(file)
except Exception as e:
    print(e)


def get_fare_by_idx(route, start_idx, end_idx, type="general", is_ac=False):
    cur = _conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\') from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    fare = cur.fetchall()[0][0]
    return fare if fare is not None else None


def get_fare_by_idx_v2(route, start_idx, end_idx, type="general", is_ac=False):
    if route.upper() in ['B1UP', 'B1DOWN']:
        return get_brts_fare(route, start_idx, end_idx)
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\'), is_ac from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    fare = cur.fetchall()
    try:
        return {
            'nac' if data[1] == 0 else 'ac': {
                'basic': data[0],
                'toll': 0,
                'total': data[0]
            }
            for data in fare
        }
    except:
        return None


def get_stop_by_amount(route, start_idx, _fare, type="general", is_ac=False):
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\"\') from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    fare = cur.fetchall()[0][0]
    fare_dict = json.loads(fare)
    stop_idx = None
    for idx, fare in fare_dict.items():
        if fare == int(_fare):
            stop_idx = idx
    return stop_idx


def get_fare_options_from_source(route, start_idx, type="general", is_ac=False):
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\"\') from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    try:
        fare = cur.fetchall()[0][0]
        data = json.loads(fare)
        return {k: {'basic': v['b'], 'toll': v['t'], 'total': v['s']} for k, v in data.items()}
        # return json.loads(fare)
    except:
        print(query)
        return None


def get_fare_options_from_source_v2(route, start_idx, type="general", is_ac=False):
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\"\'), is_ac from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    try:
        fare = cur.fetchall()
        return {'nac' if data[1] == 0 else 'ac': {k: {'basic': v, 'toll': 0, 'total': v} for k, v in
                                                  json.loads(data[0]).items()} for data in fare}
    except Exception as e:
        print(e)
        return None


def get_brts_fare(route, start_idx, end_idx):
    if route.upper() == 'B1UP':
        fare = b1up_dict.get((int(end_idx), int(start_idx)))
    else:
        fare = b1down_dict.get((int(end_idx), int(start_idx)))
    return {
        'nac': {
            'basic': fare,
            'toll': 0,
            'total': fare
        }
    }
