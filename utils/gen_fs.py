import json
import pandas as pd

import sqlite3

conn = sqlite3.connect('/Users/rajangirsa/Documents/Development/Pune/data/fare_matrix/fare_matrix_23_7.db')

route_mapping = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/route_long_name_mapping.csv')
master = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/All_Stop_Master_V2_22.3.csv')
fare_logic = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/pmpml_fare_logic.csv')
output_folder = '/Users/rajangirsa/Documents/Development/Pune/data/fare_matrix/'
route_groups = master.groupby('RouteCode')

route_mapping_dict = dict(zip(route_mapping['raw'], route_mapping['updated']))


class FareStage:
    def __init__(self, number_of_fare_stages=None, fare_stage_matrix=None, is_ac=False):
        self.number_of_fare_stages = number_of_fare_stages
        self.fare_stage_matrix = fare_stage_matrix
        self.is_ac = is_ac

    @staticmethod
    def get_basic_fare_given_fare_stage_difference(fare_stage_difference, fare_stage_logic):
        keys = sorted(list(fare_stage_logic.keys()))

        for key in keys:
            if fare_stage_difference <= key:
                return fare_stage_logic[key]

        return -1

    # Format for fare_stage_logic: {2: 5, 5: 10, 50: 15} or {"fare_stage_diff": "price"}
    @staticmethod
    def generate_fare_stage_matrix(number_of_fare_stages, fare_stage_logic):
        fare_stage_matrix = {}

        for i in range(1, number_of_fare_stages + 1):
            fare_stage_matrix[i] = {}

            for j in range(1, number_of_fare_stages + 1):
                fare_stage_difference = abs(j - i)
                basic_fare = FareStage.get_basic_fare_given_fare_stage_difference(fare_stage_difference,
                                                                                  fare_stage_logic)
                if j <= i:
                    fare_stage_matrix[i][j] = 0
                else:
                    if basic_fare is not None and basic_fare != -1:
                        fare_stage_matrix[i][j] = basic_fare
                    else:
                        raise Exception(
                            'Some error occurred while generating fare stage matrix. Got {} fare between {} and {}'.format(
                                basic_fare, i, j))

        return fare_stage_matrix

    # Format for fare_stage_logic: {2: 5, 5: 10, 50: 15} or {"fare_stage_diff": "price"}
    def set_fare_stage_matrix(self, fare_stage_logic):
        number_of_fare_stages = self.number_of_fare_stages
        fare_stage_matrix = FareStage.generate_fare_stage_matrix(number_of_fare_stages, fare_stage_logic)

        self.fare_stage_matrix = json.dumps(fare_stage_matrix)

    @staticmethod
    def get_fare_from_fare_stage_matrix(fare_stage_matrix, start_stop_fare_stage, end_stop_fare_stage):
        return fare_stage_matrix[start_stop_fare_stage][end_stop_fare_stage]

    @staticmethod
    def get_toll_from_fare_stage_matrix(fare_stage_matrix, start_stop_fare_stage, end_stop_fare_stage):
        return 0


class Route:
    def __init__(self, route_long_name=None, route_type='general', agency='DTC', number_of_stops=None, fare_stage=None,
                 fare_matrix=None, is_ac=False, is_down_route=False, fare_stage_to_stop_idx_mapping=None,
                 stops=None, is_active=True, is_fareoptions_active=True):
        self.route_long_name = route_long_name
        self.route_type = route_type
        self.agency = agency
        self.number_of_stops = number_of_stops
        self.fare_stage = fare_stage
        self.fare_matrix = fare_matrix
        self.is_ac = is_ac
        self.is_down_route = is_down_route
        self.fare_stage_to_stop_idx_mapping = fare_stage_to_stop_idx_mapping
        self.stops = stops
        self.is_active = is_active
        self.is_fareoptions_active = is_fareoptions_active

    def __str__(self):
        return f"Route: {self.route_long_name}, Type: {self.route_type}, Agency: {self.agency}"

    @staticmethod
    def generate_fare_stage_to_stop_idx_mapping():
        try:
            fare_stage_info = stages

            fare_stage_to_stop = {}
            is_down_route = False

            for idx, stage in enumerate(fare_stage_info):
                stop_idx = idx
                fare_stage_number = stage

                if stop_idx == 0 and int(fare_stage_number) > 1:
                    is_down_route = True

                try:
                    fare_stage_to_stop[fare_stage_number]
                except:
                    fare_stage_to_stop[fare_stage_number] = stop_idx

            return json.dumps(fare_stage_to_stop), is_down_route

        except Exception as e:
            raise Exception(e)

    @staticmethod
    def get_stop_idx_to_fare_stage_mapping(fare_stage_to_stop_idx_mapping):
        fare_stage_to_stop_idx_mapping = json.loads(fare_stage_to_stop_idx_mapping)
        stop_idx_to_fare_stage_mapping = {v: k for k, v in fare_stage_to_stop_idx_mapping.items()}
        return stop_idx_to_fare_stage_mapping

    @staticmethod
    def get_fare_stage_of_start_stop(start_stop_idx, fare_stage_to_stop_idx_mapping):
        stop_idx_to_fare_stage_mapping = Route.get_stop_idx_to_fare_stage_mapping(fare_stage_to_stop_idx_mapping)

        if start_stop_idx in stop_idx_to_fare_stage_mapping.keys():
            return stop_idx_to_fare_stage_mapping[start_stop_idx]

        fare_stage_number = -1
        for stop_idx in sorted(list(stop_idx_to_fare_stage_mapping.keys())):
            if stop_idx <= start_stop_idx:
                fare_stage_number = stop_idx_to_fare_stage_mapping[stop_idx]
            else:
                break
        return fare_stage_number

    @staticmethod
    def get_fare_stage_of_end_stop(end_stop_idx, fare_stage_to_stop_idx_mapping):
        stop_idx_to_fare_stage_mapping = Route.get_stop_idx_to_fare_stage_mapping(fare_stage_to_stop_idx_mapping)

        if end_stop_idx in stop_idx_to_fare_stage_mapping.keys():
            return stop_idx_to_fare_stage_mapping[end_stop_idx]

        fare_stage_number = -1
        for stop_idx in sorted(list(stop_idx_to_fare_stage_mapping.keys())):
            if stop_idx >= end_stop_idx:
                fare_stage_number = stop_idx_to_fare_stage_mapping[stop_idx]
                return fare_stage_number

        return stop_idx_to_fare_stage_mapping[sorted(list(stop_idx_to_fare_stage_mapping.keys()))[-1]]

    @staticmethod
    def generate_fare_matrix(number_of_stops, fare_stage_matrix, fare_stage_to_stop_idx_mapping):
        fare_matrix = {}
        fare_stage_matrix = fare_stage_matrix

        try:
            for i in range(0, number_of_stops):
                fare_matrix[i] = {}

                for j in range(i + 1, number_of_stops):
                    start_stop_fare_stage = Route.get_fare_stage_of_start_stop(i, fare_stage_to_stop_idx_mapping)
                    end_stop_fare_stage = Route.get_fare_stage_of_end_stop(j, fare_stage_to_stop_idx_mapping)

                    basic_fare = FareStage.get_fare_from_fare_stage_matrix(fare_stage_matrix, start_stop_fare_stage,
                                                                           end_stop_fare_stage)
                    toll = FareStage.get_toll_from_fare_stage_matrix(fare_stage_matrix, start_stop_fare_stage,
                                                                     end_stop_fare_stage)

                    fare_matrix[i][j] = int(basic_fare + toll)
        except:
            raise

        return fare_matrix

    @staticmethod
    def create_new_route(is_ac=False, fare_stage_matrix=None, create_fare_stage_matrix_if_not_exists=True,
                         farestage_obj=None):

        result = {"status": "no_change"}
        fare_stage_obj = farestage_obj
        if fare_stage_matrix is None:
            if fare_stage_obj:
                fare_stage_matrix = fare_stage_obj.fare_stage_matrix
            else:
                result['status'] = 'error'
                return result
        else:
            if create_fare_stage_matrix_if_not_exists:
                if fare_stage_obj is None:
                    fare_stage_obj = FareStage()

                loaded_fare_stage_matrix = fare_stage_matrix
                fare_stage_obj.number_of_fare_stages = len(loaded_fare_stage_matrix.keys())
                fare_stage_obj.fare_stage_matrix = fare_stage_matrix
                fare_stage_obj.is_ac = is_ac

        try:
            fare_stage_info = stages
        except Exception as e:
            raise

        number_of_stops = len(fare_stage_info)
        fare_stage_to_stop_idx_mapping, is_down_route = Route.generate_fare_stage_to_stop_idx_mapping()

        fare_matrix = Route.generate_fare_matrix(number_of_stops, fare_stage_matrix, fare_stage_to_stop_idx_mapping)

        return fare_matrix


fare_stage_logic_general_nac = dict(zip(fare_logic['Stage'] - 1, fare_logic['Ticket Rates(Rs)']))

db_val = []
routes_to_create_fm = None
farestage_obj = FareStage()
for i, row in route_groups:
    row = row.drop_duplicates('Stop Code')
    fare_matrix = {}
    stages_mat = {}
    # route = row['RouteCode'].iloc[0]
    route = i
    if routes_to_create_fm is not None and route not in routes_to_create_fm:
        continue
    _stages = row['Stg'].tolist()
    stages = []
    for idx, x in enumerate(_stages):
        if x != 'Stg':
            stages.append(x)
        else:
            stages.append(stages[idx - 1])
    # stages = [x for x in row['Stg'].tolist() if x != 'Stg']
    stop_name = row['Stop Name'].tolist()
    number_of_stages = max([int(x) for x in stages])

    if route[-1] == 'D':
        stages = [number_of_stages - int(x) + 1 for x in stages]
    farestage_obj.number_of_fare_stages = number_of_stages
    farestage_obj.set_fare_stage_matrix(fare_stage_logic_general_nac)

    for src in range(len(stages)):
        stages_mat[src] = {}
        for dest in range(len(stages)):
            stages_mat[src][dest] = int(stages[dest]) - int(stages[src])

    fm = json.loads(farestage_obj.fare_stage_matrix)

    fare_matrix = Route.create_new_route(is_ac=False, fare_stage_matrix=fm,
                                         create_fare_stage_matrix_if_not_exists=False, farestage_obj=farestage_obj)

    df_fl = pd.DataFrame(fm)
    df_fm = pd.DataFrame(fare_matrix)
    df_fm.columns = stop_name
    df_fm.index = stop_name[1:]
    df_fm = df_fm.fillna(0).astype('int')
    df_st = pd.DataFrame(stages_mat)
    updated_route = route_mapping_dict[route]
    df_fm.to_csv(output_folder + updated_route + '.csv')

    fm_str = json.dumps(fare_matrix)

    db_val.append(
        {'route': updated_route.lower(), 'fare': fm_str, 'type': 'general', 'is_ac': False, 'stops_count': len(stop_name)})

pd.DataFrame(db_val).to_sql('fares', conn, if_exists='replace', index=False)
cursor = conn.cursor()
cursor.execute('CREATE INDEX "ix_route_type_ac" ON "fares" ("route","type","is_ac")')
conn.close()
