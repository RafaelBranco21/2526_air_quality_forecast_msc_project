"""Helper class for EDA on station data files."""

import numpy as np
import pandas as pd
import pprint as pp
import json
import os
import re

# Auto eda packages references:
# https://www.nb-data.com/p/python-packages-for-automated-eda
# usar: sweetviz, dtale, autoviz, ydata-profiling


class StationMetadata:
    """Class to hold metadata about station files."""
    def __init__(self):
        self.__columns_from_2019_foward_es = ['Estacio', 'nom_cabina', 'codi_dtes',
        'zqa', 'codi_eoi', 'Longitud', 'Latitud', 'ubicacio', 'Codi_districte',
        'Nom_districte', 'Codi_barri', 'Nom_barri', 'Clas_1', 'Clas_2', 'Codi_Contaminant']

        self.__columns_from_2019_foward_en = ['station_number', 'station_name', 'station_code', 
        'aqzc', 'eoi_code', 'longitude', 'latitude', 'location', 'district_code',
        'district_name', 'neighborhood_code', 'neighborhood_name', 'class_1', 'class_2', 'contaminant_code']

        self.__columns_from_2019_foward_en_description = [
            'Station number', # naybe can be ignored (each station has multiple rows, one per contaminant measured)
            'Name of the station',
            'Station code', # station identifier (should be unique) -> lookup key
            'Air Quality Zone Code where the station/cabine is located',
            'European code to identify the station/cabine',
            'Longitude',
            'Latitude',
            'Address/Crossroads',
            'District code',
            'District name',
            'Neighbourhood code',
            'Name of the neighbourhood',
            'Type of station - classification 1',
            'Type of station - classification 2',
            'Pollutant code'
        ]

        # Mapping of Spanish column names to English names and descriptions
        self.columns_from_2019_foward = {
            col: {
                'en': self.__columns_from_2019_foward_en[i],
                'en_description': self.__columns_from_2019_foward_en_description[i]
            } for i, col in enumerate(self.__columns_from_2019_foward_es)
        }

        # criar dict com cada ano e com as colunas e traducao daquele ano
        # esta classe vem depois da outra e usa os metodos para criar a metadata
        # talvez seja melhor criar uma funcao que cria a metadata e retorna um dicionario
        # Colocar em outro ficheiro .py


class StationEDAHelper:
    """Helper class for EDA on station data files."""

    @staticmethod
    def get_all_station_files(folder_path: str) -> list[str]:
        """
        Get all station files in the given folder path that match the pattern 'YYYY_stations.csv',
        where YYYY is a year from 2000 to 2099.
        Args:
            folder_path (str): The path to the folder containing station files.
        Returns:
            list[str]: A list of filenames matching the pattern.
        """

        # We use r'' to indicate a raw string, which is best for regex.
        # We also escape the dot "\." to strictly match a period, not "any character".
        regex_pattern = r'20[0-9]{2}_stations\.csv'
        all_files_in_dir = os.listdir(folder_path)

        # List of filenames that match the regex pattern
        matching_files = []

        for filename in all_files_in_dir:
            # re.match checks if the pattern matches the START of the filename
            if re.match(regex_pattern, filename):
                matching_files.append(filename)
        
        return matching_files
    
    @staticmethod
    def print_all_station_files(folder_path: str):
        """Print all station files in the given folder path."""
        matching_files = StationEDAHelper.get_all_station_files(folder_path)

        print(f"Found {len(matching_files)} files:")
        for file in matching_files:
            print(f" * '{file}'")

    @staticmethod
    def calculate_station_years_metadata(folder_path: str, log: bool = True) -> dict:    
        """Calculate metadata about station files in the given folder path.
        Args:
            folder_path (str): The path to the folder containing station files.
            log (bool): Whether to print log messages. Default is True.
        Returns:
            dict: A dictionary containing:
                - complete_years (list[int]): List of all years from min to max year.
                - existent_years (list[int]): List of years for which station files exist.
                - missing_station_years (set[int]): Set of years for which station files are missing.
                - previous_year_mapping (dict[int, int|None]): Mapping of each year to its previous year.
        """ 

        matching_files = StationEDAHelper.get_all_station_files(folder_path)
        existent_years = [int(file_name[:4]) for file_name in matching_files]

        max_year = max(existent_years)
        min_year = min(existent_years)

        if log:
            print(f"Station files range from year {min_year} to {max_year}.")
            print(f"Existent years: {existent_years}")
        
        # Check for missing years in the range
        # For example, if we have files for 2018, 2019, 2021, we should note that 2020 is missing.
        # Missing years will have the same metadata as the previous year.
        missing_station_years = set(range(min_year, max_year + 1)) - set(existent_years)
        if log:
            print(f"Missing station files for years: {missing_station_years}")

        complete_years = list(range(min_year, max_year + 1))
        if log:
            print(f"Complete years should be: {complete_years}")

        previous_year_mapping = {}
        for i, y in enumerate(existent_years):
            if i == 0:
                previous_year_mapping[y] = None # No previous year
            else:
                previous_year_mapping[y] = existent_years[i - 1]
            # print(i , ' -> ' , y)

        return {
            'complete_years': complete_years,
            'existent_years': existent_years, 
            'missing_station_years': missing_station_years, 
            'previous_year_mapping': previous_year_mapping
        }
    
    @staticmethod
    def fetch_station_data_of_year(folder_path: str, year: int) -> pd.DataFrame | None:
        """Fetch station data for a specific year from the given folder path.   
        Args:
            folder_path (str): The path to the folder containing station files.
            year (int): The year for which to fetch station data.
        Returns:
            pandas.DataFrame: A DataFrame containing the station data for the specified year. If the file does not exist, returns None.
        """
        file_path = f"{folder_path}/{year}_stations.csv"
        
        try:
            df_station = pd.read_csv(file_path)
            # deve colocar os nomes das colunas em ingles usando a metadata de colunas
            #if year >= 2019:             
                #df_station = df_station.rename(columns={es_col: columns_from_2019_foward[es_col]['en'] for es_col in columns_from_2019_foward_es})
                
        except FileNotFoundError:
            return None
        
        return df_station

    @staticmethod
    def fetch_all_station_columns(folder_path: str, years: list[int]) -> dict[int, list[str]]: 
        """Fetch all station columns for the given years from the specified folder path.
        Args:
            folder_path (str): The path to the folder containing station files.
            years (list[int]): A list of years for which to fetch station columns.
        Returns:
            dict[int, list[str]]: A dictionary mapping each year to its list of station columns.
        """

        columns_dict = {}

        for year in years:
            df_station = StationEDAHelper.fetch_station_data_of_year(folder_path, year)
            if df_station is not None:
                columns_dict[year] = df_station.columns.tolist()

        return columns_dict



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



if __name__ == "__main__":
    # this should run the methods to create the station years metadata and print all station files
    # also trasnform the data to its final format

    bronze_stations_folder_path = '../data/bronze/stations'
    StationEDAHelper.print_all_station_files(bronze_stations_folder_path)
    years_metadata =  StationEDAHelper.calculate_station_years_metadata(bronze_stations_folder_path)
    pp.pprint(years_metadata)
    all_station_columns = StationEDAHelper.fetch_all_station_columns(
        bronze_stations_folder_path,
        years_metadata['existent_years'])   

    pp.pprint(all_station_columns)