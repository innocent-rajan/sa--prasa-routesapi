import json
import math
import os
import sqlite3

import pandas as pd

data_dir = 'data/Formatted with schedule/'
conn = sqlite3.connect('data/fare_matrix/fare_matrix_14_9.db')

dist_dict = {}


def verify_dist_type(df, f):
    if df['dist'].iloc[-1] - df['dist'].iloc[1] > 3:
        return 'sum'
    else:
        return 'difference'


def process_dataframe(df, is_diff=True):
    if is_diff:
        df['cumm_dist'] = df['dist'] + df['dist'].shift(1)
        df['indi_dist'] = df['dist']
    else:
        df['indi_dist'] = df['dist'] - df['dist'].shift(1)
        df['cumm_dist'] = df['dist']
    df.fillna(0, inplace=True)

    return df


error = []
for f in os.listdir(data_dir):
    if f.endswith('.csv'):
        try:
            rt = f.split('.')[0]
            df = pd.read_csv(data_dir + f)
            _type = verify_dist_type(df, f)
            if _type == 'difference':
                _df = process_dataframe(df, is_diff=True)
            else:
                _df = process_dataframe(df, is_diff=False)

            dist_dict[rt] = _df['indi_dist'].to_dict()
        except Exception as e:
            error.append(f)
            print(f'{e} in {f}')

for k, v in dist_dict.items():
    try:
        for i, j in v.items():
            if j < 0:
                print(f'{0}: {k}')
    except Exception as e:
        print(f'{e} in {k}')

with open(data_dir + 'dist_dict.json', 'w') as f:
    json.dump(dist_dict, f)


ac_fare_dict = {1: 5, 2: 5, 3: 10, 4: 10, 5: 15, 6: 15, 7: 15, 8: 15, 9: 20, 10: 20, 11: 25, 12: 25, 13: 25, 14: 25,
                15: 30, 16: 30, 17: 30, 18: 30, 19: 35, 20: 35, 21: 35, 22: 35, 23: 40, 24: 40, 25: 40, 26: 40, 27: 45,
                28: 45, 29: 45, 30: 45, 31: 45, 32: 45, 33: 50, 34: 50, 35: 50, 36: 50, 37: 50, 38: 50, 39: 50, 40: 50,
                41: 50}


nac_fare_dict = {1: 5, 2: 5, 3: 5, 4: 5, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 10, 11: 10, 12: 10, 13: 10, 14: 10,
                 15: 15, 16: 15, 17: 15, 18: 15, 19: 15, 20: 15, 21: 15, 22: 15, 23: 20, 24: 20, 25: 20, 26: 20, 27: 20,
                 28: 20, 29: 20, 30: 20, 31: 25, 32: 25, 33: 25, 34: 25, 35: 25, 36: 25, 37: 30, 38: 30, 39: 30, 40: 30,
                 41: 30, 42: 30, 43: 30, 44: 30, 45: 30, 46: 30, 47: 30, 48: 30, 49: 30, 50: 30, 51: 30, 52: 30, 53: 30,
                 54: 30, 55: 30, 56: 30, 57: 30, 58: 30, 59: 30, 60: 30, 61: 30, 62: 30, 63: 30, 64: 30, 65: 30, 66: 30,
                 67: 30, 68: 30, 69: 30, 70: 30, 71: 30, 72: 30, 73: 30, 74: 30, 75: 30, 76: 30, 77: 30, 78: 30, 79: 30,
                 80: 30, 81: 30, 82: 30, 83: 30, 84: 30, 85: 30, 86: 30, 87: 30, 88: 30, 89: 30, 90: 30, 91: 30, 92: 30,
                 93: 30, 94: 30, 95: 30, 96: 30, 97: 30, 98: 30, 99: 30, 100: 30}

fares_nac = {}
fares_ac = {}
for k, v in dist_dict.items():
    try:
        fn = {}
        fa = {}
        for i, j in v.items():
            fr_nac = {}
            fr_ac = {}
            dist = 0
            for s in range(i + 1, len(v)):
                dist += v[s]
                fr_nac[s] = nac_fare_dict[math.ceil(dist)]
                fr_ac[s] = ac_fare_dict[math.ceil(dist)]
            fn[i] = fr_nac
            fa[i] = fr_ac
        fares_nac[k.replace('R0', 'R')] = {'fare': json.dumps(fn), 'is_ac': 0, 'category': 'general'}
        fares_ac[k.replace('R0', 'R')] = {'fare': json.dumps(fa), 'is_ac': 1, 'category': 'general'}
    except Exception as e:
        print(f'{e} in {k}')

final_fare_nac = pd.DataFrame(fares_nac).T
final_fare_ac = pd.DataFrame(fares_ac).T

pd.concat([final_fare_nac, final_fare_ac]).to_sql('fares', conn, if_exists='replace', index=True, index_label='route')
cursor = conn.cursor()
cursor.execute('CREATE INDEX "ix_route_type_ac" ON "fares" ("route","category","is_ac")')
conn.close()
