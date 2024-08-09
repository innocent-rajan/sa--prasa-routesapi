import json
import re

import pandas as pd

import sqlite3

conn = sqlite3.connect('/Users/rajangirsa/Documents/Development/Pune/data/fare_matrix/fare_matrix_9_8.db')

route_mapping = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/route_long_name_mapping.csv')
master = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/All_Stop_Master_V2_22.3.csv')
master_pmrda = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/final_data.csv')
fare_logic = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/pmpml_fare_logic.csv')
fare_logic_pmrda = pd.read_csv('/Users/rajangirsa/Documents/Development/Pune/data/pmrda_fare_logic.csv')
route_groups = master.groupby('RouteCode')
route_groups_pmrda = master_pmrda.groupby('Route')
output_folder = '/Users/rajangirsa/Documents/Development/Pune/data/fare_matrix/'

route_mapping_dict = dict(zip(route_mapping['raw'], route_mapping['updated']))

TOLL = 1
toll_routes = ['61UP', '228UP', '293UP', '296UP', '296AUP', '305UP', '305AUP', '305BUP', '341UP', '342UP', '368UP',
               '371UP', '61DOWN', '228DOWN', '293DOWN', '296DOWN', '296ADOWN', '305DOWN', '305ADOWN', '305BDOWN',
               '341DOWN', '342DOWN', '368DOWN', '371DOWN']

toll_stops = ['Bormal', 'Shivray Mangal Karyalay', 'Poona Poultry', 'Somatne Phata']

FLAT_FARE = 10
flat_fare_routes = ['1-D', '1-U', '2-D', '2-U', '2B-Ring Route', '3-R', '4-D', '4-U', '5-D', '5-U', '6-D', '6-U', '7-D',
                    '7-U', '8-D', '8-U', '9-D', '9-U']

EXTRA_NIGHT_FARE = 5
night_routes = ['Ratrani 1-D', 'Ratrani 1-U', 'Ratrani 2-D', 'Ratrani 2-U', 'Ratrani 3-D', 'Ratrani 3-U', 'Ratrani 4-D',
                'Ratrani 4-U', 'Ratrani 7-D', 'Ratrani 7-U', 'Ratrani7-D', 'Ratrani7-U']

pmrda_routes = ['120-U', '131-U', '135-U', '135A-U', '136-U', '137-U', '137A-U', '142-U', '147-U', '159-A-U', '159-U',
                '159B-U', '159C-U', '161-U', '161A-U', '161B-U', '162-U', '164-U', '164A-U', '183-U', '183A-U',
                '183B-U', '184-U', '190B-U', '193-A-U', '193-U', '207-U', '207A-C-U', '207A-U', '207K-U', '207N-U',
                '209-B-U', '209-U', '209A-U', '210-U', '211-U', '212-U', '226-U', '226A-U', '227-U', '227A-B-U',
                '227A-U', '228-A-U', '228-U', '228J-U', '228S-U', '231-B-U', '231-U', '232-U', '233-U', '233A-U',
                '233B-U', '257-U', '257A-U', '262-U', '262A-U', '264-U', '279-U', '292-A-U', '292-B-U', '292-C-U',
                '292-U', '292-D-U', '293-U', '296-U', '296A-U', '29A-U', '30-U', '303A-U', '303J-U', '303S-U',
                '305-A-U', '305-B-U', '305-U', '309-U', '313-B-U', '313-U', '314-U', '316-U', '320-U', '321-U', '329-U',
                '330-U', '332-U', '335-U', '341-U', '342-U', '343-U', '343A-U', '343B-U', '350-U', '351-A-U', '351-U',
                '353-U', '353A-U', '353B-U', '353C-U', '358-U', '358A-U', '358B-U', '359A-U', '35J-U', '35S-U', '364-U',
                '368-U', '369-U', '370-U', '371-U', '374A-U', '50-U', '50A-U', '50B-U', '50K-U', '52-A-U', '52-B-U',
                '52-C-U', '52-U', '52-D-U', '61-U', '65-A-U', '65-U', '66-A-U', '66-U', '67-C-U', '67-U', '67-D-U',
                '69-U', '70-U', '73A-U', '73-U', '74-A-U', '74-U', '84-A-U', '84-B-U', '84-U', '84A-C-U', '85-A-U',
                '85-U', '85A-U', '86-U', '87-D-U', '87A-U', '120-D', '131-D', '135-D', '135A-D', '136-D', '137-D',
                '137A-D', '142-D', '147-D', '159-A-D', '159-D', '159B-D', '159C-D', '161-D', '161A-D', '161B-D',
                '162-D', '164-D', '164A-D', '183-D', '183A-D', '183B-D', '184-D', '190B-D', '193-A-D', '193-D', '207-D',
                '207A-C-D', '207A-D', '207K-D', '207N-D', '209-B-D', '209-D', '209A-D', '210-D', '211-D', '212-D',
                '226-D', '226A-D', '227-D', '227A-B-D', '227A-D', '228-A-D', '228-D', '228J-D', '228S-D', '231-B-D',
                '231-D', '232-D', '233-D', '233A-D', '233B-D', '257-D', '257A-D', '262-D', '262A-D', '264-D', '279-D',
                '292-A-D', '292-B-D', '292-C-D', '292-D', '292-D-D', '293-D', '296-D', '296A-D', '29A-D', '30-D',
                '303A-D', '303J-D', '303S-D', '305-A-D', '305-B-D', '305-D', '309-D', '313-B-D', '313-D', '314-D',
                '316-D', '320-D', '321-D', '329-D', '330-D', '332-D', '335-D', '341-D', '342-D', '343-D', '343A-D',
                '343B-D', '350-D', '351-A-D', '351-D', '353-D', '353A-D', '353B-D', '353C-D', '358-D', '358A-D',
                '358B-D', '359A-D', '35J-D', '35S-D', '364-D', '368-D', '369-D', '370-D', '371-D', '374A-D', '50-D',
                '50A-D', '50B-D', '50K-D', '52-A-D', '52-B-D', '52-C-D', '52-D', '52-D-D', '61-D', '65-A-D', '65-D',
                '66-A-D', '66-D', '67-C-D', '67-D', '67-D-D', '69-D', '70-D', '73A-D', '73-D', '74-A-D', '74-D',
                '84-A-D', '84-B-D', '84-D', '84A-C-D', '85-A-D', '85-D', '85A-D', '86-D', '87-D-D', '87A-D']

pmrda_filtered_rts = []
non_pmrda_filtered_rts = []

error_routes = ['99ADOWN', '82BDOWN', '47DOWN', '363DOWN', 'H9DOWN', '77ADOWN', '329DOWN', '320DOWN', '77DOWN',
                '306DOWN', '57DOWN', '164ADOWN', '160DOWN', '311DOWN', '84DUP']


# pmrda_routes = ['29UP', '30UP', '43AUP', '50UP', '52UP', '52AUP', '61UP', '65UP', '65AUP', '66UP', '67UP', '69UP',
#                 '70UP', '73UP', '74UP', '77UP', '83UP', '84UP', '84AUP', '85UP', '86UP', '87AUP', '100UP', '100UP',
#                 '115UP', '119UP', '120UP', '131UP', '135UP', '136UP', '137UP', '142UP', '147UP', '151UP', '153UP',
#                 '159UP', '159BUP', '161UP', '162UP', '164UP', '183UP', '184UP', '190BUP', '193UP', '200UP', '201UP',
#                 '207UP', '207AUP', '208UP', '209UP', '209AUP', '210UP', '210UP', '211UP', '212UP', '213UP', '225UP',
#                 '226UP', '227UP', '227AUP', '228UP', '231UP', '232UP', '233UP', '233AUP', '233BUP', '257UP', '257AUP',
#                 '262UP', '264UP', '279UP', '292UP', '293UP', '296UP', '296AUP', '302AUP', '303AUP', '305UP', '305AUP',
#                 '305BUP', '306UP', '306AUP', '309UP', '309UP', '313UP', '314UP', '316UP', '320UP', '321UP', '324UP',
#                 '327UP', '329UP', '330UP', '333UP', '335UP', '340UP', '341UP', '342UP', '343UP', '344UP', '345UP',
#                 '347UP', '350UP', '351UP', '353UP', '358UP', '358AUP', '359AUP', '360UP', '361UP', '362UP', '364UP',
#                 '368UP', '369UP', '370UP', '371UP', '372UP', '372UP', '372MUP', '374UP', '374AUP', '375UP', '380UP',
#                 '381UP', 'B2UP', '29DOWN', '30DOWN', '43ADOWN', '50DOWN', '52DOWN', '52ADOWN', '61DOWN', '65DOWN',
#                 '65ADOWN', '66DOWN', '67DOWN', '69DOWN', '70DOWN', '73DOWN', '74DOWN', '77DOWN', '83DOWN', '84DOWN',
#                 '84ADOWN', '85DOWN', '86DOWN', '87ADOWN', '100DOWN', '100DOWN', '115DOWN', '119DOWN', '120DOWN',
#                 '131DOWN', '135DOWN', '136DOWN', '137DOWN', '142DOWN', '147DOWN', '151DOWN', '153DOWN', '159DOWN',
#                 '159BDOWN', '161DOWN', '162DOWN', '164DOWN', '183DOWN', '184DOWN', '190BDOWN', '193DOWN', '200DOWN',
#                 '201DOWN', '207DOWN', '207ADOWN', '208DOWN', '209DOWN', '209ADOWN', '210DOWN', '210DOWN', '211DOWN',
#                 '212DOWN', '213DOWN', '225DOWN', '226DOWN', '227DOWN', '227ADOWN', '228DOWN', '231DOWN', '232DOWN',
#                 '233DOWN', '233ADOWN', '233BDOWN', '257DOWN', '257ADOWN', '262DOWN', '264DOWN', '279DOWN', '292DOWN',
#                 '293DOWN', '296DOWN', '296ADOWN', '302ADOWN', '303ADOWN', '305DOWN', '305ADOWN', '305BDOWN', '306DOWN',
#                 '306ADOWN', '309DOWN', '309DOWN', '313DOWN', '314DOWN', '316DOWN', '320DOWN', '321DOWN', '324DOWN',
#                 '327DOWN', '329DOWN', '330DOWN', '333DOWN', '335DOWN', '340DOWN', '341DOWN', '342DOWN', '343DOWN',
#                 '344DOWN', '345DOWN', '347DOWN', '350DOWN', '351DOWN', '353DOWN', '358DOWN', '358ADOWN', '359ADOWN',
#                 '360DOWN', '361DOWN', '362DOWN', '364DOWN', '368DOWN', '369DOWN', '370DOWN', '371DOWN', '372DOWN',
#                 '372DOWN', '372MDOWN', '374DOWN', '374ADOWN', '375DOWN', '380DOWN', '381DOWN', 'B2DOWN']


def get_toll_for_routes():
    toll_stop_sequence = {}
    for i, row in route_groups:
        if route_mapping_dict[i] not in toll_routes:
            continue
        toll_stop_sequence[i] = {'start': max(row[row['Stop Name'].isin(toll_stops)]['Stop Code'].tolist()) - 1,
                                 'end': len(row['Stop Name'].tolist())}

    return toll_stop_sequence


toll_stop_sequence = get_toll_for_routes()


class FareStage:
    def __init__(self, number_of_fare_stages=None, fare_stage_matrix=None, fare_stage_matrix_child=None, is_ac=False):
        self.number_of_fare_stages = number_of_fare_stages
        self.fare_stage_matrix = fare_stage_matrix
        self.fare_stage_matrix_child = fare_stage_matrix_child
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
    def set_fare_stage_matrix(self, fare_stage_logic, fare_stage_logic_child):
        number_of_fare_stages = self.number_of_fare_stages
        fare_stage_matrix = FareStage.generate_fare_stage_matrix(number_of_fare_stages, fare_stage_logic)
        fare_stage_matrix_child = FareStage.generate_fare_stage_matrix(number_of_fare_stages, fare_stage_logic_child)

        self.fare_stage_matrix = json.dumps(fare_stage_matrix)
        self.fare_stage_matrix_child = json.dumps(fare_stage_matrix_child)

    @staticmethod
    def get_fare_from_fare_stage_matrix(route, fare_stage_matrix, start_stop_fare_stage, end_stop_fare_stage):
        if route in flat_fare_routes:
            return FLAT_FARE
        if route in night_routes:
            return fare_stage_matrix[start_stop_fare_stage][end_stop_fare_stage] + EXTRA_NIGHT_FARE
        # if route in ['306-D', '311-D', '363-D', '47-D', '57-D', '77A-D', '77-D', '82-B-D', '99-A-D', 'H9-D']:
        # if route in ['306-D']:
        #     print(start_stop_fare_stage, end_stop_fare_stage, fare_stage_matrix[start_stop_fare_stage][end_stop_fare_stage])
        return fare_stage_matrix[start_stop_fare_stage][end_stop_fare_stage]

    @staticmethod
    def get_toll_from_fare_stage_matrix(route, dest):
        if route_mapping_dict[route] in toll_routes and dest >= toll_stop_sequence[route]['start']:
            return TOLL
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
    def generate_fare_matrix(route, number_of_stops, fare_stage_matrix, fare_stage_to_stop_idx_mapping):
        fare_matrix = {}
        fare_stage_matrix = fare_stage_matrix

        try:
            for i in range(0, number_of_stops):
                fare_matrix[i] = {}

                for j in range(i + 1, number_of_stops):
                    start_stop_fare_stage = Route.get_fare_stage_of_start_stop(i, fare_stage_to_stop_idx_mapping)
                    end_stop_fare_stage = Route.get_fare_stage_of_end_stop(j, fare_stage_to_stop_idx_mapping)

                    basic_fare = FareStage.get_fare_from_fare_stage_matrix(route, fare_stage_matrix,
                                                                           start_stop_fare_stage,
                                                                           end_stop_fare_stage)
                    toll = FareStage.get_toll_from_fare_stage_matrix(route, j)

                    fare_matrix[i][j] = int(basic_fare + toll)
                    # fare_matrix[i][j] = {'b': basic_fare, 't': toll, 's': basic_fare + toll}
        except:
            raise

        return fare_matrix

    @staticmethod
    def create_new_route(route, is_ac=False, fare_stage_matrix=None, fare_stage_matrix_child=None,
                         create_fare_stage_matrix_if_not_exists=True, farestage_obj=None):

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

        if fare_stage_matrix_child is None:
            if fare_stage_obj:
                fare_stage_matrix_child = fare_stage_obj.fare_stage_matrix_child
            else:
                result['status'] = 'error'
                return result
        else:
            if create_fare_stage_matrix_if_not_exists:
                if fare_stage_obj is None:
                    fare_stage_obj = FareStage()

                loaded_fare_stage_matrix = fare_stage_matrix_child
                fare_stage_obj.number_of_fare_stages = len(loaded_fare_stage_matrix.keys())
                fare_stage_obj.fare_stage_matrix_child = fare_stage_matrix_child
                fare_stage_obj.is_ac = is_ac

        try:
            fare_stage_info = stages
        except Exception as e:
            raise

        number_of_stops = len(fare_stage_info)
        fare_stage_to_stop_idx_mapping, is_down_route = Route.generate_fare_stage_to_stop_idx_mapping()

        fare_matrix = Route.generate_fare_matrix(route, number_of_stops, fare_stage_matrix,
                                                 fare_stage_to_stop_idx_mapping)

        fare_matrix_child = Route.generate_fare_matrix(route, number_of_stops, fare_stage_matrix_child,
                                                       fare_stage_to_stop_idx_mapping)

        return fare_matrix, fare_matrix_child


fare_stage_logic_general_nac = dict(zip(fare_logic['Stage'] - 1, fare_logic['Ticket Rates(Rs)']))
fare_stage_logic_child_nac = dict(zip(fare_logic['Stage'] - 1, fare_logic['Children Half Ticket (Rs.)']))
fare_stage_logic_pmrda_general_nac = dict(zip(fare_logic_pmrda['Stage'] - 1, fare_logic_pmrda['General']))
fare_stage_logic_pmrda_child_nac = dict(zip(fare_logic_pmrda['Stage'] - 1, fare_logic_pmrda['Child']))


def extract_digits_from_start(s):
    if s and s[0].isdigit():
        return re.findall(r'^\d+', s)
    return []


def isPMRDA(r):
    try:
        if r in pmrda_routes:
            # rt = int(extract_digits_from_start(r)[0])
            # if r in pmrda_routes and ('(metro' not in r or '(night' not in r):
            pmrda_filtered_rts.append(r)
            return True
        else:
            non_pmrda_filtered_rts.append(r)
            return False
    except:
        non_pmrda_filtered_rts.append(r)
        return False


db_val = []
routes_to_create_fm = None
farestage_obj = FareStage()
for i, row in route_groups:
    # if route_mapping_dict[i] not in toll_routes:
    #     continue
    # if i[-2:] != '-D':
    #     continue
    # try:
    #     if isPMRDA(i):
    #         continue
    # except:
    #     pass
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
    if not isPMRDA(i):
        farestage_obj.set_fare_stage_matrix(fare_stage_logic_general_nac, fare_stage_logic_child_nac)
    else:
        farestage_obj.set_fare_stage_matrix(fare_stage_logic_pmrda_general_nac, fare_stage_logic_pmrda_child_nac)

    for src in range(len(stages)):
        stages_mat[src] = {}
        for dest in range(len(stages)):
            stages_mat[src][dest] = int(stages[dest]) - int(stages[src])

    fm = json.loads(farestage_obj.fare_stage_matrix)
    fmc = json.loads(farestage_obj.fare_stage_matrix_child)

    fare_matrix, fare_matrix_child = Route.create_new_route(route=route, is_ac=False, fare_stage_matrix=fm,
                                                            fare_stage_matrix_child=fmc,
                                                            create_fare_stage_matrix_if_not_exists=False,
                                                            farestage_obj=farestage_obj)

    df_fl = pd.DataFrame(fm)
    df_fm = pd.DataFrame(fare_matrix)
    df_fm.columns = stop_name
    df_fm.index = stop_name[1:]
    # df_fm = df_fm.fillna(0).astype('int')
    df_fm = df_fm.fillna("{'b':0, 't':0, 's':0}")
    df_st = pd.DataFrame(stages_mat)
    updated_route = route_mapping_dict[route]
    df_fm.to_csv(output_folder + updated_route + '.csv')

    fm_str = json.dumps(fare_matrix)
    fm_child_str = json.dumps(fare_matrix_child)

    db_val.append(
        {'route': updated_route.lower(), 'fare': fm_str, 'type': 'general', 'is_ac': False,
         'stops_count': len(stop_name), 'fare_type': 'PMRDA' if isPMRDA(i) else 'city', 'category': 'general'})

    # db_val.append(
    #     {'route': updated_route.lower(), 'fare': fm_child_str, 'type': 'general', 'is_ac': False,
    #      'stops_count': len(stop_name), 'fare_type': 'PMRDA' if isPMRDA(i) else 'city', 'category': 'child'})

# for i, row in route_groups_pmrda:
#     try:
#         if not isPMRDA(i):
#             continue
#         row = row.drop_duplicates('Stop Code')
#         fare_matrix = {}
#         stages_mat = {}
#         # route = row['RouteCode'].iloc[0]
#         route = i
#         if routes_to_create_fm is not None and route not in routes_to_create_fm:
#             continue
#         _stages = row['Stg'].tolist()
#         stages = []
#         for idx, x in enumerate(_stages):
#             if x != 'Stg':
#                 stages.append(int(x))
#             else:
#                 stages.append(stages[idx - 1])
#         # stages = [x for x in row['Stg'].tolist() if x != 'Stg']
#         stop_name = row['Stop Name'].tolist()
#         number_of_stages = max([int(x) for x in stages])
#
#         if route[-1] == 'D':
#             stages = [number_of_stages - int(x) + 1 for x in stages]
#         farestage_obj.number_of_fare_stages = number_of_stages
#         farestage_obj.set_fare_stage_matrix(fare_stage_logic_pmrda_general_nac)
#
#         for src in range(len(stages)):
#             stages_mat[src] = {}
#             for dest in range(len(stages)):
#                 stages_mat[src][dest] = int(stages[dest]) - int(stages[src])
#
#         fm = json.loads(farestage_obj.fare_stage_matrix)
#
#         fare_matrix = Route.create_new_route(route=route, is_ac=False, fare_stage_matrix=fm,
#                                              create_fare_stage_matrix_if_not_exists=False, farestage_obj=farestage_obj)
#
#         df_fl = pd.DataFrame(fm)
#         df_fm = pd.DataFrame(fare_matrix)
#         df_fm.columns = stop_name
#         df_fm.index = stop_name[1:]
#         df_fm = df_fm.fillna(0).astype('int')
#         df_st = pd.DataFrame(stages_mat)
#         updated_route = route_mapping_dict[route]
#         df_fm.to_csv(output_folder + updated_route + '.csv')
#
#         fm_str = json.dumps(fare_matrix)
#
#         db_val.append(
#             {'route': updated_route.lower(), 'fare': fm_str, 'type': 'general', 'is_ac': False,
#              'stops_count': len(stop_name), 'fare_type': 'pmrda'})
#     except Exception as e:
#         print(e)

pd.DataFrame(db_val).to_sql('fares', conn, if_exists='replace', index=False)
cursor = conn.cursor()
cursor.execute('CREATE INDEX "ix_route_type_ac" ON "fares" ("route","type","is_ac")')
conn.close()

'''
unknown = []
error = []
final_route_mapping = {}
opposite = ['82-B-D', '99-A-D']
for i, row in route_groups:
    try:
        if i[-2:] == '-D' and i not in opposite:
            stage = int(route_groups.get_group(i)['Stg'].tolist()[0]) - int(route_groups.get_group(i)['Stg'].tolist()[-1])
        else:
            stage = int(route_groups.get_group(i)['Stg'].tolist()[-1]) - int(route_groups.get_group(i)['Stg'].tolist()[0])
        stage += 1
        fare = route_groups.get_group(i)['Ticket Fair'].tolist()[-1]
        if 'Ratrani' in i:
            fare -= 5
        if i not in flat_fare_routes:
            if fare == fare_logic[fare_logic['Stage'] == stage]['Ticket Rates(Rs)'].squeeze():
                final_route_mapping[i] = 'city'
            elif fare == fare_logic_pmrda[fare_logic_pmrda['Stage'] == stage]['General'].squeeze():
                final_route_mapping[i] = 'pmrda'
            else:
                unknown.append({'route':i, 'fare':fare, 'stage':stage, 'pmrda_fare': fare_logic_pmrda[fare_logic_pmrda['Stage'] == stage]['General'].squeeze(),
                                'city_fare': fare_logic[fare_logic['Stage'] == stage]['Ticket Rates(Rs)'].squeeze(), '1th stage':route_groups.get_group(i)['Stg'].tolist()[0],
                                'Last stage': route_groups.get_group(i)['Stg'].tolist()[-1]})
        else:
            final_route_mapping[i] = 'city'
    except Exception as e:
        print(e)
        error.append(i)
'''
