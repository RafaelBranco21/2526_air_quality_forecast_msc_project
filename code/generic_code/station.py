import pandas as pd
import generic_code.contaminants as conts


STATIONS_BASE_PATH = './../data/original_data/stations_data'

station_cols = ['station', 'station_name', 'code_dtes', 'zqa', 'code_eoi', 'longitude',
       'latitude', 'location', 'district_code', 'district_name', 'neighborhood_code',
       'neighborhood_name', 'class_1', 'class_2', 'contaminant_code']

contaminants_df = conts.load_contaminants()

def print_individual_col(df, col):
    d = df[col]
    print("Column: '%s'" % col, end = '\n\n')
    print('Data = %s' % str(list(d.unique())))
    print('Length = %d' % len(d.unique()), end = '\n\n')
    print(d.value_counts(), end='\n\n\n')

def print_categorical_cols(df, station_eda_cols):
    for col in station_eda_cols:
        print_individual_col(df, col)
        print('============================================================')

def condense_stations_data(df, contaminants_df):
    station_ids = list(df.station.unique())
    station_ids.sort()
    
    d = {}

    for x in df.columns:
        d[x] = list()

    initial_cols = df.columns
    d['station'] = station_ids
    d['contaminant_names'] = list()
    
    for _id in d['station']:
        station_data = df[df['station'] == _id] # filter data by station id
        
        # copy columns
        for col in initial_cols[1:-1]:
            d[col].append(station_data[col].values[0])
    
        # contaminant codes to list
        contaminant_codes = list(station_data['contaminant_code'].values)
        d['contaminant_code'].append(contaminant_codes)
        contaminant_names = list()

        # get contaminant names
        for i in contaminant_codes:
            cont_data = conts.get_contaminant_by_code(contaminants_df, i)
            if len(cont_data) == 0:
                contaminant_names.append('None')
            else:
                contaminant_names.append(cont_data[1]) # get description
        
        d['contaminant_names'].append(contaminant_names)
    
    return d, pd.DataFrame.from_dict(d)


def load_station_data(path, station_cols):
    df = pd.read_csv(path)
    df.columns = station_cols
    eda_cols = list(df.select_dtypes(include=['object', 'int64']).columns)
    return eda_cols, df