import re
import sqlite3
import pandas as pd

master = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/All_Stop_Master_V2_22.3.csv')
master_pmrda = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/final_data.csv')

conn = sqlite3.connect('/Users/rajangirsa/Documents/Development/Pune/data/fare_matrix/fare_matrix_1_8.db')

route_mapping = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/route_long_name_mapping.csv')
route_mapping_dict = dict(zip(route_mapping['raw'], route_mapping['updated']))

route_groups_pmrda = master_pmrda.groupby('Route')
route_groups = master.groupby('RouteCode')

non_pmrda = []
pmrda_routes = [29, 30, 50, 52, 61, 65, 66, 67, 69, 70, 73, 74, 77, 83, 84, 85, 86, 100, 100, 115, 119, 120, 131, 135,
                136, 137, 142, 147, 151, 153, 159, 161, 162, 164, 183, 184, 193, 200, 201, 207, 208, 209, 210, 210, 211,
                212, 213, 225, 226, 227, 228, 231, 232, 233, 257, 262, 264, 279, 292, 293, 296, 305, 306, 309, 309, 313,
                314, 316, 320, 321, 324, 327, 329, 330, 333, 335, 340, 341, 342, 343, 344, 345, 347, 350, 351, 353, 358,
                360, 361, 362, 364, 368, 369, 370, 371, 372, 372, 374, 375, 380, 381]


def extract_digits_from_start(s):
    if s and s[0].isdigit():
        return re.findall(r'^\d+', s)
    return []


def isPMRDA(r):
    try:
        rt = int(extract_digits_from_start(r)[0])
        if rt in pmrda_routes and ('(metro' not in r or '(night' not in r):
            return True
        else:
            non_pmrda.append(r)
            return False
    except:
        non_pmrda.append(r)
        return False


def get_fare_from_db(route, start_idx, end_idx):
    rt = route_mapping_dict[route]
    query = f'SELECT json_extract(fare, \'$.\"{start_idx}\".\"{end_idx}\"\') from fares where route = \"{rt.lower()}\";'
    cur.execute(query)
    try:
        fare = cur.fetchall()[0][0]
    except IndexError:
        print(query)
        fare = None
    return fare if fare is not None else None


not_match_fare = []
cur = conn.cursor()
for i, row in route_groups:
    row = row.drop_duplicates('Stop Code')
    db = get_fare_from_db(i, 0, len(row) - 1)
    # if db == 0:
    #     print(i)
    if isPMRDA(i):
        try:
            fare = {'master': route_groups_pmrda.get_group(i)['Ticket Fair'].tolist()[-1], 'db': db}
        except:
            fare = {'master': 0, 'db': db}
    else:
        fare = {'master': row['Ticket Fair'].tolist()[-1], 'db': db}
    if fare['db'] != fare['master']:
        not_match_fare.append({i: fare})
cur.close()
