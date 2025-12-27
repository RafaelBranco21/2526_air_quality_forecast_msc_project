"""Utilities for managing air quality contaminant metadata.

This module provides a simple manager class to load contaminant definitions
from a JSON file and query units, codes, and descriptions. It also offers
helpers to export data for analysis.
"""

import os
from typing import Dict, Any, Optional
import pandas as pd
import pprint as pp
import json
import copy


class ContaminantManagerJSON:
    """Manager for contaminant metadata loaded from a JSON file.

    This class reads a mapping of contaminant descriptions (e.g., 'PM10') to
    their metadata (unit and numeric codes) and exposes convenient lookup
    methods.

    The JSON file should have the following structure:
        {
            "PM10": {
                "unit": "µg/m³",
                "codes": [10, 110],
                "original_description": {"10": "PM10", "110": "PM10*"},
                "extended_description": {"10": "PM10 (original)", "110": "PM10 (extended)"},
                "is_original_contaminant": {"10": true, "110": false}
            },
            "SO2": {
                "unit": "µg/m³",
                "codes": [1, 101],
                "original_description": {"1": "SO2", "101": "SO2*"},
                "extended_description": {"1": "SO2 (original)", "101": "SO2 (extended)"},
                "is_original_contaminant": {"1": true, "101": false}
            }
        }

    Attributes:
        _json_contaminants_data (Dict[str, Any]): Raw contaminant data loaded from JSON.
    """
    
    def __init__(self, file_path: str) -> None:
        """Initializes the manager by loading contaminant data from a JSON file.

        Args:
            file_path (str): Filesystem path to the JSON file containing contaminant metadata.

        Raises:
            FileNotFoundError: If the specified file cannot be found.
            json.JSONDecodeError: If the file contents are not valid JSON.
            KeyError: If required keys are missing from the JSON structure.
        """
        self._json_contaminants_data: Dict[str, Any] = {}
        
        with open(file_path) as json_file:
            self._json_contaminants_data = json.load(json_file)
    

    def get_all_contaminants_descriptions(self) -> list[str]:
        """Returns a list of all contaminant descriptions available.

        Returns:
            list[str]: Contaminant descriptions (e.g., ['PM10', 'SO2', 'CO']).
        """
        return list(self._json_contaminants_data.keys())
    
    def get_all_contaminants_codes(self) -> list[int]:
        """Returns a list of all unique numeric contaminant codes available.

        Returns:
            list[int]: Numeric contaminant codes (e.g., [10, 110, 1, 101, 6, 106]).
        """
        all_codes = set()

        for value in self._json_contaminants_data.values():
            codes = value.get("codes", [])
            all_codes.update(codes)
        
        return list(all_codes)


    def has_contaminant_by_description(self, contaminant_description: str) -> bool:
        """Check if a contaminant description exists in the dataset.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10').
                Leading and trailing whitespace will be stripped.

        Returns:
            bool: True if the description exists, False otherwise.
        """

        contaminant_description = contaminant_description.strip()

        if contaminant_description == "":
            return False
        
        return contaminant_description in self._json_contaminants_data.keys()

    def has_contaminant_by_code(self, numeric_code: int) -> bool:
        """Check if a numeric code is associated with any contaminant.

        Args:
            numeric_code (int): Numeric contaminant code.

        Returns:
            bool: True if the code is found in any contaminant, False otherwise.
        """

        for value in self._json_contaminants_data.values():
            if numeric_code in value.get("codes", []):
                return True
            
        return False


    def is_original_contaminant_by_code(self, numeric_code: int) -> bool:
        """Checks if a numeric code corresponds to an original contaminant.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            bool: True if the code is marked as original, False otherwise.
        """

        for data in self._json_contaminants_data.values():
            is_original_dict = data.get("is_original_contaminant", {})
            if str(numeric_code) in is_original_dict:
                return is_original_dict[str(numeric_code)]
            
        return False


    def get_description_by_code(self, numeric_code: int) -> Optional[Dict[str, Any]]:
        """Retrieves detailed information for a contaminant by its numeric code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing:
                - description (str): Contaminant description (e.g., 'PM10')
                - original_description (str): Original name from source data
                - extended_description (str): Long-form description
                - is_original_contaminant (bool): Whether this is an original contaminant
                Returns None if the code is not found.

        Examples:
            >>> manager.get_description_by_code(10)
            {'description': 'PM10', 'original_description': '...', ...}
            >>> manager.get_description_by_code(999)
            None
        """

        for description, data in self._json_contaminants_data.items():
            if numeric_code in data.get("codes", []):
                return {
                    "description": description,
                    "original_description": data.get("original_description", {}).get(str(numeric_code), ""),
                    "extended_description": data.get("extended_description", {}).get(str(numeric_code), ""),
                    "is_original_contaminant": data.get("is_original_contaminant", {}).get(str(numeric_code), False)
                }
            
        return None
    
    def get_codes_by_description(self, contaminant_description: str) -> Optional[list[int]]:
        """Retrieves all numeric codes associated with a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10').
                Leading and trailing whitespace will be stripped.

        Returns:
            Optional[list[int]]: List of numeric codes if found, None otherwise.

        Examples:
            >>> manager.get_codes_by_description('PM10')
            [10, 110]
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "" or contaminant_description not in self._json_contaminants_data.keys():
            return None
        
        return list(self._json_contaminants_data[contaminant_description]["codes"])


    def get_unit_by_code(self, numeric_code: int) -> Optional[str]:
        """Retrieves the unit of measurement for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            Optional[str]: Unit string (e.g., 'µg/m³') if found, None otherwise.
        """
        for data in self._json_contaminants_data.values():
            if numeric_code in data.get("codes", []):
                return data.get("unit")
        
        return None
    
    def get_units_by_description(self, contaminant_description: str) -> Optional[str]:
        """Retrieves the unit of measurement for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.

        Returns:
            Optional[str]: Unit string (e.g., 'µg/m³') if found, None otherwise.

        Examples:
            >>> manager.get_units_by_description('PM10')
            'µg/m³'
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "":
            return None

        if not contaminant_description in self._json_contaminants_data.keys():
            return None

        return self._json_contaminants_data[contaminant_description]['unit']


    def get_text_description_by_code(self, numeric_code: int) -> Optional[str]:
        """Retrieves the text description for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).   
        Returns:
            Optional[str]: Text description string if found, None otherwise.
        """
        for data in self._json_contaminants_data.values():
            if numeric_code in data.get("codes", []):
                return data.get("text_description")
        
        return None
    
    def get_text_description_by_description(self, contaminant_description: str) -> Optional[str]:
        """Retrieves the text description for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.
        Returns:
            Optional[str]: Text description string if found, None otherwise.
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "":
            return None

        if not contaminant_description in self._json_contaminants_data.keys():
            return None

        return self._json_contaminants_data[contaminant_description]['text_description']


    def get_all_contaminants_data(self) -> Dict[str, Any]:
        """Returns a deep copy of all contaminants metadata.

        Returns:
            Dict[str, Any]: Dictionary mapping contaminant descriptions (e.g., 'PM10')
                to their metadata (unit, codes, descriptions, etc.).

        Note:
            Returns a deep copy to prevent accidental modification of internal data.
        """
        return copy.deepcopy(self._json_contaminants_data)

    def get_contaminant_data_by_description(self, contaminant_description: str) -> Optional[Dict[str, Any]]:
        """Retrieve all metadata for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing:
                - description (str): The contaminant description
                - unit (str): Unit of measurement
                - codes (list[int]): Associated numeric codes
                - original_description (Dict): Original descriptions by code
                - extended_description (Dict): Extended descriptions by code
                - is_original_contaminant (Dict): Originality flags by code
                Returns None if the description is not found.
        """
        
        contaminant_description = contaminant_description.strip()

        if contaminant_description == "":
            return None

        if contaminant_description in self._json_contaminants_data.keys():
            return_obj: Dict[str, Any] = copy.deepcopy(self._json_contaminants_data[contaminant_description])
            return_obj["description"] = contaminant_description
            return return_obj
        
        return None
    
    def get_contaminant_data_by_code(self, numeric_code: int) -> Optional[Dict[str, Any]]:
        """Retrieves all metadata for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing:
                - description (str): The contaminant description
                - unit (str): Unit of measurement
                - codes (list[int]): Associated numeric codes
                - original_description (Dict): Original descriptions by code
                - extended_description (Dict): Extended descriptions by code
                - is_original_contaminant (Dict): Originality flags by code
                Returns None if the code is not found.
        """
        for description, data in self._json_contaminants_data.items():
            if numeric_code in data.get("codes", []):
                return_obj: Dict[str, Any] = copy.deepcopy(data)
                return_obj["description"] = description
                return return_obj
            
        return None


    def to_dataframe(self) -> pd.DataFrame:
        """Exports contaminant data as a pandas DataFrame.

        Each row represents a unique combination of contaminant and code.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - code (int): Numeric contaminant code
                - description (str): Contaminant description (e.g., 'PM10')
                - original_description (str): Original name from source
                - extended_description (str): Long-form description
                - unit (str): Unit of measurement
                - is_original_contaminant (bool): Whether this is an original contaminant

        Examples:
            >>> df = manager.to_dataframe()
            >>> df[df['description'] == 'PM10']
        """
        rows = []

        for description, data in self._json_contaminants_data.items():
            for numeric_code in data.get("codes", []):
                row = {
                    "code": numeric_code,
                    "description": description,
                    "text_description": data.get("text_description", ""),
                    "original_description": data.get("original_description", {}).get(str(numeric_code), ""),
                    "extended_description": data.get("extended_description", {}).get(str(numeric_code), ""),
                    "unit": data.get("unit"),
                    "is_original_contaminant": data.get("is_original_contaminant", {}).get(str(numeric_code), False)
                }
                rows.append(row)

        return pd.DataFrame(rows)
        
        
if __name__ == '__main__':
    
    bar_line = "=" * 80
    print("Current directory:", os.getcwd(), '\n')    

    contaminants_json_file_path = './../data/gold/contaminants/contaminants.json'
    contaminant_manager = ContaminantManagerJSON(contaminants_json_file_path)
    
    print(bar_line)
    print("Get all contaminant descriptions [ContaminantManagerJSON class]")
    print(bar_line)
    descriptions = contaminant_manager.get_all_contaminants_descriptions()
    pp.pprint(descriptions)
    
    print('\n')
    print(bar_line)
    print("Get all contaminant codes [ContaminantManagerJSON class]")
    print(bar_line)
    codes = contaminant_manager.get_all_contaminants_codes()
    pp.pprint(codes)
    
    print('\n')
    print(bar_line)
    print("Get contaminant data by description [ContaminantManagerJSON class]")
    print(bar_line, '\n')

    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        data = contaminant_manager.get_contaminant_data_by_description(description)
        print(f"'{description}' data => ")
        pp.pprint(data)
        print('\n')


    print('\n')
    print(bar_line)
    print("Get unit by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for numeric_code in (10, 110, 1, 101, 6, 106, 999):
        unit = contaminant_manager.get_unit_by_code(numeric_code)
        print(f"get_unit_by_code({numeric_code}) => {unit}")


    print('\n')
    print(bar_line)
    print("Get contaminant units by description [ContaminantManagerJSON class]")
    print(bar_line, '\n')
        
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        unit = contaminant_manager.get_units_by_description(description)
        print(f"'{description}' units => {unit}")

    
    print('\n')
    print(bar_line)
    print("Get contaminant text description by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')
        
    for numeric_code in (10, 110, 1, 101, 6, 106, 999):
            text_description = contaminant_manager.get_text_description_by_code(numeric_code)
            print(f"get_text_description_by_code({numeric_code}) => {text_description}")


    print('\n')
    print(bar_line)
    print("Get contaminant text description by description [ContaminantManagerJSON class]")
    print(bar_line, '\n')
        
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        text_description = contaminant_manager.get_text_description_by_description(description)
        print(f"'{description}' text description => '{text_description}'")
    
    
    print('\n')
    print(bar_line)
    print("Get contaminant description by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')

    contaminants_mapping = ((10, "PM10"), (110, "PM10"), (9, "PM2_5"), (109, "PM2_5"),
                             (1, "SO2"), (101, "SO2"), (6, "CO"), (106, "CO"), (999, "INVALID"))

    for numeric_code, expected in contaminants_mapping:
        description = contaminant_manager.get_description_by_code(numeric_code)
        print(f"Code '{numeric_code}' (expected: '{expected}') => ")
        pp.pprint(description)
        print('\n')
    
    
    print('\n')
    print(bar_line)
    print("Get codes by description [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        codes = contaminant_manager.get_codes_by_description(description)
        print(f"get_codes_by_description('{description}') => {codes}")

    
    print('\n')
    print(bar_line)
    print("Check contaminant by description [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for description in ("PM10", "PM2_5", "CO", "INVALID", "  PM10  "):
        exists = contaminant_manager.has_contaminant_by_description(description)
        print(f"has_contaminant_by_description('{description}') => {exists}")
    
    
    print('\n')
    print(bar_line)
    print("Check contaminant by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for numeric_code in (10, 110, 6, 999):
        exists = contaminant_manager.has_contaminant_by_code(numeric_code)
        print(f"has_contaminant_by_code({numeric_code}) => {exists}")

    
    print('\n')
    print(bar_line)
    print("Check if original contaminant by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for numeric_code in (10, 110, 1, 101, 999):
        is_original = contaminant_manager.is_original_contaminant_by_code(numeric_code)
        print(f"is_original_contaminant_by_code({numeric_code}) => {is_original}")

    
    print('\n')
    print(bar_line)
    print("Get contaminant data by code [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    for numeric_code in (10, 110, 1, 101, 999):
        data = contaminant_manager.get_contaminant_data_by_code(numeric_code)
        print(f"get_contaminant_data_by_code({numeric_code}) => ")
        pp.pprint(data)
        print('\n')

    
    print('\n')
    print(bar_line)
    print("Get all contaminants data [ContaminantManagerJSON class]")
    print(bar_line, '\n')
    
    all_data = contaminant_manager.get_all_contaminants_data()
    pp.pprint(all_data)

    
    print('\n')
    print(bar_line)
    print("ContaminantManagerJSON.to_dataframe() output")
    print(bar_line, '\n')
    
    df = contaminant_manager.to_dataframe()
    print(df)
