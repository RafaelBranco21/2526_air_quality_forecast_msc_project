import pandas as pd
import json

class ContaminantManagerJSON:

    def __init__(self, path: str = './../data/processed/contaminants/contaminants.json'):
        _json_data_test_read = {}
        with open(path) as json_file:
            json_data_test_read = json.load(json_file)

    def get_description_by_code(self, code: str = None) -> str:
        if code is None:
            return None

        match = self.df[self.df['code'] == code]
        if match.empty:
            return None

        return match.iloc[0]['description']

    def get_units_by_code(self, code: str = None) -> str:
        if code is None:
            return None

        match = self.df[self.df['code'] == code]
        if match.empty:
            return None

        return match.iloc[0]['units']

    def get_all_contaminants(self) -> pd.DataFrame:
        return self.df.copy()

    def get_contaminant_data_by_code(self, code: str = None) -> dict:
        """Returns all data for a given contaminant code as a dictionary."""
        if code is None:
            return None

        match = self.df[self.df['code'] == code]
        if match.empty:
            return None

        return match.iloc[0].to_dict()

    def get_column_names(self) -> list:
        """Returns the list of column names."""
        return list(self.df.columns)
    
    