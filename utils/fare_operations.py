import sqlite3
import json

conn = sqlite3.connect('file:instance/fare_matrix_8_8_child.db?mode=ro', check_same_thread=False)
_conn = sqlite3.connect('file:instance/fare_matrix_9_8.db?mode=ro', check_same_thread=False)


def get_fare_by_idx(route, start_idx, end_idx, type="general", is_ac=False):
    cur = _conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\') from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    fare = cur.fetchall()[0][0]
    return fare if fare is not None else None


def get_fare_by_idx_v2(route, start_idx, end_idx, type="general", is_ac=False):
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\'), category from fares where route = \"{route.lower()}\";'
    cur.execute(query)
    fare = cur.fetchall()
    try:
        return {
            data[1]: {
                'basic': json.loads(data[0])['b'],
                'toll': json.loads(data[0])['t'],
                'total': json.loads(data[0])['s']
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
