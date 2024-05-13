import sqlite3

conn = sqlite3.connect('file:instance/fare_matrix.db?mode=ro', check_same_thread=False)


def get_fare(route, start_idx, end_idx, type="general", is_ac=False):
    cur = conn.cursor()
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\') from fares where route = \"{route}\";'
    cur.execute(query)
    fare = cur.fetchall()[0][0]
    return fare if fare is not None else None