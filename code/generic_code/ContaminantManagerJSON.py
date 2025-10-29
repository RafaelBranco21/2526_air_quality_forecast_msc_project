import pandas as pd
import pprint as pp
import json

class ContaminantManagerJSON:
    
    def __init__(self, path: str):
        
        with open(path) as json_file:
            self._json_contaminants_data = json.load(json_file)
    
    
    def get_description_by_code(self, code: int) -> str:
        
        for key, value in self._json_contaminants_data.items():
            if code in value["codes"]:
                return key

        return ""

    
    def get_units_by_code(self, code: str) -> str:
        """Returns a string (text) for a given contaminant code. 
           None if the contaminant does not exist."""
           
        code = code.strip()
        
        if code == "":
            return None

        if not code in self._json_contaminants_data.keys():
            return None

        return self._json_contaminants_data[code]['unit']

    
    def get_all_contaminants(self) -> pd.DataFrame:
        """Returns a copy of the contaminants data (dictionary)."""
        
        return self._json_contaminants_data.copy()

    
    def get_contaminant_data_by_code(self, code: str) -> dict:
        """Returns all data for a given contaminant code as a dictionary."""
        
        code = code.strip()
        if code == "":
            return None

        if code in self._json_contaminants_data:
            return_obj = self._json_contaminants_data[code].copy()
            return_obj["description"] = code
            return return_obj
        
        return None
        
        
if __name__ == '__main__':
    
    contaminants_json_file_path = './../../data/processed/contaminants/contaminants.json'
    c_manager_obj = ContaminantManagerJSON(contaminants_json_file_path)
    
    print("Get all contaminants [ContaminantManagerJSON class]")
    pp.pprint(c_manager_obj.get_all_contaminants())
    
    
    print('\n')
    print("Get contaminant data by code [ContaminantManagerJSON class]\n")

    template = "'{0}' data => '{1}'"
    print(template.format("PM10", c_manager_obj.get_contaminant_data_by_code("PM10")))
    print(template.format("PM2_5", c_manager_obj.get_contaminant_data_by_code("PM2_5")))
    print(template.format("SO2", c_manager_obj.get_contaminant_data_by_code("SO2")))
    print(template.format("CO", c_manager_obj.get_contaminant_data_by_code("CO")))
    
    
    print('\n')
    print("Get contaminant units by code [ContaminantManagerJSON class]\n")
    
    template = "'{0}' units => '{1}'"
    print(template.format("PM10", c_manager_obj.get_units_by_code("PM10")))
    print(template.format("PM2_5", c_manager_obj.get_units_by_code("PM2_5")))
    print(template.format("SO2", c_manager_obj.get_units_by_code("SO2")))
    print(template.format("CO", c_manager_obj.get_units_by_code("CO")))
    
    
    print('\n')
    print("Get contaminant description by code [ContaminantManagerJSON class]\n")

    template = "Code '{0}' ('{1}') => '{2}'"

    print(template.format("10", "PM10", c_manager_obj.get_description_by_code(10)))
    print(template.format("110", "PM10", c_manager_obj.get_description_by_code(110)))

    print(template.format("9", "PM2_5", c_manager_obj.get_description_by_code(9)))
    print(template.format("109", "PM2_5", c_manager_obj.get_description_by_code(109)))

    print(template.format("1", "SO2", c_manager_obj.get_description_by_code(1)))
    print(template.format("101", "SO2", c_manager_obj.get_description_by_code(101)))

    print(template.format("6", "CO", c_manager_obj.get_description_by_code(6)))
    print(template.format("106", "CO", c_manager_obj.get_description_by_code(106)))
    