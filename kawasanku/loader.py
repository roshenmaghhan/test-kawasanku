from asyncio.windows_events import NULL
from msilib.schema import AppSearch
from re import X
from threading import _DummyThread
import pandas as pd
import numpy as np
from pathlib import Path
import json, random

"""
TODO :  - Optimise and cleaning
        - Automate changes of data
        - Caching
"""

# NEW VERSION : STATE-DISTRCT NESTED JSON FILE WILL BE GENERATED
# df = dataframe of csv file, param_1 = 'state', param_2 = 'district', filename = 'state_district_nested.json'
def state_district_nested_generation(df, param_1, param_2, filename) : 
    state_district_nested = df.groupby([param_1], as_index=True)[param_2].apply(list).to_dict()
    state_district = {}

    for x in state_district_nested :
        abbr = STATE_ABBR[x]
        district_list = []
        for y in state_district_nested[x] :
            dist_obj = {}
            dist_obj['label'] = y
            dist_obj['value'] = y.replace(' ', '-').lower()
            district_list.append(dist_obj)

        state_district[abbr] =  {'district' : district_list}

    with open(filename, 'w') as json_file:
        json.dump(state_district, json_file)
    
    return state_district

# Generates the dropdown JSON for the dropdown API using the function above
def generate_dropdown(gsp, gsdm, filename) :
    state_district_data = state_district_nested_generation(gsdm, 'state', 'district', 'state_district_nested.json')
    for choice in ['parlimen', 'dun'] :
        group_1 = gsp.groupby(['state'], as_index=True)[choice].apply(list).to_dict()
        for x in group_1 :
            abbr = STATE_ABBR[x]
            unique = set(group_1[x])
            parlimen_list = []
            for u in unique :                
                if type(u) != float :
                    dist_obj = {}
                    dist_obj['label'] = u
                    dist_obj['value'] = u.replace(' ', '-').lower()
                    parlimen_list.append(dist_obj)
            if len(parlimen_list) > 0 :
                state_district_data[abbr][choice] = parlimen_list

    with open(filename, 'w') as json_file:
        json.dump(state_district_data, json_file)

# NEW VERSION : STATE-PARLIMENT-DUN NESTED JSON FILE WILL BE GENERATED
# df = dataframe of csv file, level_1 = 'state', level_2 = 'parlimen', level_3 = 'dun', filename = 'state_parlimen_dun_nested.json'
def state_parlimen_dun_nested_generation(df, level_1, level_2, level_3, filename) :
    state_dict = {}

    group_1 = df.groupby([level_1], as_index=True)[level_2].apply(list).to_dict()
    group_2 = df.groupby(level_2)[level_3].apply(list).to_dict()

    for x in group_1 :
        district_set = set(group_1[x])
        newset = {}
        for y in district_set :
            newset[y.replace(" ", "-").lower()] = [ y.replace(' ', '-').lower() for y in group_2[y] ]
        state_dict[STATE_ABBR[x]] = newset

    with open(filename, 'w') as json_file:
        json.dump(state_dict, json_file)

# NEW VERSION : Example of using function below : generate_snapshot_json(snapshot_df / jitter_df, gdsm_df, gsp_df, 'snapshot.json')
def generate_info_json(df, gsdm, gsp, filename) :
    snapshot_dict = {}
    for index, row in df.iterrows():
        newdict = {}
        area_key = ''
        if row['area'] in STATE_ABBR : 
            area_key = STATE_ABBR[row['area']]
        else :
            area_key = row['area'].replace(' ', '-').lower()

        newdict[area_key] = row.to_dict()
        if row['area_type'] == 'state' :
            snapshot_dict[STATE_ABBR[row['area']]] = newdict
        else :
            state_name = ''
            if row['area_type'] == 'district' :
                state_name = gsdm.loc[gsdm['district'] == row['area']].state
            elif row['area_type'] == 'parliament' : 
                state_name = gsp.loc[gsp['parlimen'] == row['area']].state
            elif row['area_type'] == 'sla' :
                state_name = gsp.loc[gsp['dun'] == row['area']].state
            if len(state_name) > 0 :
                state_name = state_name.iloc[0]
                snapshot_dict[STATE_ABBR[state_name]].update(newdict)     
            
    with open(filename, 'w') as json_file:
        json.dump(snapshot_dict, json_file)

# Generates pyramid charts for age group, with each state/disctrict/parlimen/dun being keys
def generate_pyramid_chart(dummy, filename) :
    dummy_dict = {}
    for index, row in dummy.iterrows():
        area_key = ''
        new_dict = []

        if row['area_type'] == 'state' or row['area_type'] == 'country':
            area_key = STATE_ABBR[row['area']]
        elif row['area_type'] == 'district' :
            area_key = row['area'].replace(" ", "-").lower()
        else :
            break
            # area_key = row['area'].replace(" ", "-").lower()

        # Age starts at 0, end at 85 and above
        for x in range(0, 86, 5):
            age_dict = {}
            id = str(x) + '-' + str(x + 4) if  x < 85 else str(x) + '+'
            age_male = "age_" + str(x) + '_' + 'above_male' if x == 85 else "age_" + str(x) + '_' + str(x + 4) + "_male" 
            age_female = "age_" + str(x) + '_' + 'above_female' if x == 85 else "age_" + str(x) + '_' + str(x + 4) + "_female"
            
            base_val = min(row[age_male], row[age_female])

            age_dict['id'] = id
            age_dict['male_surplus'] = -abs(row[age_male] - base_val)
            age_dict['male'] = -abs(row[age_male])
            age_dict['female'] = row[age_female]
            age_dict['female_surplus'] = abs(row[age_female] - base_val)
            new_dict.append(age_dict)
        dummy_dict[area_key] = new_dict

    with open(filename, 'w') as json_file:
        json.dump(dummy_dict, json_file)

# General generate_doughnut chart for all doughnut charts
def generate_donought(row, key, keyword, value_list) : 
    obj = {}
    arr = []
    for x in value_list :
        info = {}
        info_str = keyword + x
        info['id'] = info_str
        info['value'] = row[info_str]
        arr.append(info)
    obj[key] = arr
    return obj

# Generates doughnut charts for attributes, with each state/disctrict/parlimen/dun being keys
def generate_doughnut_charts(df, filename, STATE_ABBR) :
    dummy_dict = {}
    for index, row in df.iterrows():
        area_key = ''
        custom_dict = []

        if row['area_type'] == 'state' or row['area_type'] == 'country':
            area_key = STATE_ABBR[row['area']]
        else :
            area_key = row['area'].replace(" ", "-").lower()

        sex = generate_donought(row, 'sex', 'sex_', ['male', 'female'])
        eth = generate_donought(row, 'ethnicity', 'ethnicity_', ['bumi', 'chinese', 'indian', 'other'])
        nationality = generate_donought(row, 'nationality', 'nationality_', ['local', 'foreign'])
        agegroup = generate_donought(row, 'agegroup', 'agegroup_', ['child', 'working', 'elderly'])

        if row['area_type'] == 'state' or row['area_type'] == 'district' or row['area_type'] == 'country' :
            religion = generate_donought(row, 'religion', 'religion_', ['muslim', 'christian', 'buddhist', 'hindu', 'atheist', 'other'])
            marital = generate_donought(row, 'marital', 'marital_', ['never_married', 'married', 'widowed', 'divorced'])
            custom_dict = [religion, marital]
        else :
            housing = generate_donought(row, 'housing', 'housing_', ['owned', 'rented', 'quarters'])
            labour = generate_donought(row, 'labour', 'labour_', ['working', 'unemployed', 'out'])
            custom_dict = [housing, labour]

        new_dict = [sex, eth, nationality, agegroup] + custom_dict
        dummy_dict[area_key] = new_dict

    with open(filename, 'w') as json_file:
        json.dump(dummy_dict, json_file)

# Generates static links, with 2 keys, state and area. State has only state, area has : district + parliment + dun combined
def generate_static_links(gsdm, gsp, filename) :
    static_keys = {}

    static_state = [ "/" + STATE_ABBR[x] for x in gsdm['state'].unique().tolist()]

    static_dist = []
    dist = gsdm.groupby('state')['district'].apply(list).to_dict()
    for x in dist :
        for y in dist[x] :
            m_str = "/" + STATE_ABBR[x] + "/" + y.replace(" ", "-").lower()
            static_dist.append(m_str)

    static_parl = []
    parl = gsp.groupby('state')['parlimen'].unique().apply(list).to_dict()
    for x in parl :
        for y in parl[x] :
            m_str = "/" + STATE_ABBR[x] + "/" + y.replace(" ", "-").lower()
            static_parl.append(m_str)

    static_dun = []
    dun = gsp.groupby('state')['dun'].apply(list).to_dict()
    for x in dun :
        if STATE_ABBR[x] not in ['kul', 'pjy', 'lbn'] :
            for y in dun[x] :
                m_str = "/" + STATE_ABBR[x] + "/" + y.replace(" ", "-").lower()
                static_dun.append(m_str)

    static_keys['state'] = static_state
    static_keys['district'] = static_dist 
    static_keys['parlimen'] = static_parl 
    static_keys['dun'] = static_dun

    with open(filename, 'w') as json_file:
        json.dump(static_keys, json_file)

# Generates geojson for relevant files
# Keywords = country, state, district, parlimen, dun
def generate_geojson(filepath, filename, STATE_ABBR, area_key) :
    f = open(filepath)
    data = json.load(f)
    
    geo_main = {}

    for x in range(0, len(data['features'])):
        area = data['features'][x]['properties'][area_key]
        cords = data['features'][x]['geometry']['coordinates']
        geo_info = {}

        if area_key == 'state' or area_key == 'country' :
            area = STATE_ABBR[area]
        else :
            area = area.replace(" ", "-").lower()    
        
        geo_info['name'] = area
        geo_info['area_type'] = area_key
        geo_info['shape_type'] = data['features'][x]['geometry']['type']
        geo_info['coordinates'] = cords

        if area_key == 'country' :
            geo_main = geo_info
        else :
            geo_main[area] = geo_info

    with open(filename, 'w') as json_file:
        json.dump(geo_main, json_file)

def print_page(filename, dict) : 
    with open(filename, 'w') as json_file:
        json.dump(dict, json_file)

# Generates the jitter json end_range = 29 (metric_number) type = 'individual' or 'all'
# DONT FORGET TO CHANGE ALL EMPTY VALUES TO null
def generate_jitter_json(end_range, jitter_df, filename, type) :
    jitter_json = {}
    area_list = list(jitter_df['area_type'].unique())

    for x in area_list :
        jitter_json[x] = []
        for y in range(1, end_range) :
            m_key = 'metric_' + str(y)
            m_obj = {m_key : []}
            jitter_json[x].append(m_obj)

    for index, row in jitter_df.iterrows():
        area_type = row['area_type']
        area_key = ''
        
        if area_type == 'state' or area_type == 'country' :
            area_key = row['area']
        else : 
            area_key = row['area']

        for x in range(1, end_range) :
            x_obj = {}
            x_vals = {'x' : row['metric_' + str(x)], 'y' : random.randint(1,9)}
            x_obj['id'] = area_key
            x_obj['data'] = [x_vals]
            jitter_json[area_type][(x-1)]['metric_' + str(x)].append(x_obj)
    
    jitter_json['dun'] = jitter_json.pop('sla')

    if type == 'individual' :
        for x in jitter_json :
            print_page('jitter_' + str(x) + '.json', jitter_json[x])
    elif type == 'all' :
        print_page(filename, jitter_json)

# Generates the list of keys and their area type
def generate_valid_list(gsdm, gsp, filename) :
    overview = {}
    state_list = list(gsdm['state'].unique())
    district_list = list(gsdm['district'].unique())
    parlimen_list = list(gsp['parlimen'].unique())
    dun_list = list(gsp['dun'].unique())
    
    for x in state_list :
        overview[STATE_ABBR[x]] = 'state'

    for x in district_list :
        dist_key = x.replace(" ", '-').lower()
        overview[dist_key] = 'district'

    for x in parlimen_list :
        dist_key = x.replace(" ", '-').lower()
        overview[dist_key] = 'parlimen'

    for x in dun_list :
        if type(x) != float :
            dist_key = x.replace(" ", '-').lower()
            overview[dist_key] = 'dun'

    print_page(filename, overview)

SNAPSHOT_INFO = Path("./staticfiles/src_data/snapshot.csv")
JITTER_INFO = Path("./staticfiles/src_data/jitter.csv")
STATE_DISTRICT = Path("./staticfiles/src_data/state_district.csv")
STATE_PARLIAMENT_DUN = Path("./staticfiles/src_data/state_parlimen_dun.csv")
# DUMMY = Path("./src_data/dummy.csv")

# GEO JSON
MALAYSIA_GEOJSON = Path("./staticfiles/src_data/geojson/geo_0_malaysia.json")
STATE_GEOJSON = Path("./staticfiles/src_data/geojson/geo_1_state.json")
DISTRICT_GEOJSON = Path("./staticfiles/src_data/geojson/geo_2_district.json")
PARLIMEN_GEOJSON = Path("./staticfiles/src_data/geojson/geo_3_parlimen.json")
DUN_GEOJSON = Path("./staticfiles/src_data/geojson/geo_4_dun.json")

STATE_ABBR = {'Johor': 'jhr',
              'Kedah': 'kdh',
              'Kelantan': 'ktn',
              'Klang Valley': 'kvy',
              'Melaka': 'mlk',
              'Negeri Sembilan': 'nsn',
              'Pahang': 'phg',
              'Perak': 'prk',
              'Perlis': 'pls',
              'Pulau Pinang': 'png',
              'Sabah': 'sbh',
              'Sarawak': 'swk',
              'Selangor': 'sgr',
              'Terengganu': 'trg',
              'W.P. Labuan': 'lbn',
              'W.P. Putrajaya': 'pjy',
              'W.P. Kuala Lumpur': 'kul',
              'Malaysia': 'mys'}

snapshot = pd.read_csv(SNAPSHOT_INFO)
j = pd.read_csv(JITTER_INFO)
gsdm = pd.read_csv(STATE_DISTRICT)
gsp = pd.read_csv(STATE_PARLIAMENT_DUN)
# dummy = pd.read_csv(DUMMY)

GENERATED_PATH = './staticfiles/generated/'
GEO_PATH = 'geo/'
 
index = 0
for i in ['country', 'state', 'district', 'parlimen', 'dun'] :
    ext_type = "malaysia" if i == 'country' else i
    filepath = Path("./staticfiles/src_data/geojson/geo_" + str(index) + "_" + ext_type + ".json")
    filename = GENERATED_PATH + GEO_PATH + 'geo_' + i + '.json'
    generate_geojson(filepath, filename, STATE_ABBR, i)
    index += 1