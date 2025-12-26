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

class ContaminantManagerJSON:
    """Manager for contaminant metadata loaded from a JSON file.

    This class reads a mapping of contaminant descriptions (e.g., 'PM10') to
    their metadata (unit and numeric codes) and exposes convenient lookup
    methods.

    Attributes:
        _json_contaminants_data: Raw contaminant data loaded from JSON.
    """
    
    def __init__(self, file_path: str) -> None:
        """Initialize the manager by loading contaminant data.

        Args:
            file_path: Filesystem path to the JSON file containing contaminant data.
        Raises:
            FileNotFoundError: If the file cannot be found.
            json.JSONDecodeError: If the file contents are not valid JSON.
        """
        self._json_contaminants_data: Dict[str, Any] = {}
        
        with open(file_path) as json_file:
            self._json_contaminants_data = json.load(json_file)
    
    
    def get_description_by_code(self, numeric_code: int) -> Optional[str]:
        """Return the contaminant description for a numeric code.

        Args:
            numeric_code: Numeric contaminant code (e.g., 10, 109).
        Returns:
            The corresponding contaminant description (e.g., 'PM10') if found,
            otherwise None.

        Examples:
            >>> manager.get_description_by_code(10)
            'PM10'
            >>> manager.get_description_by_code(999)
            None
        """

        for description, data in self._json_contaminants_data.items():
            if numeric_code in data.get("codes", []):
                return description
            
        return None

    
    def get_units_by_description(self, contaminant_description: str) -> Optional[str]:
        """Return the unit string for a contaminant description.

        Args:
            contaminant_description: Contaminant description (e.g., 'PM10', 'SO2'). Leading and
                trailing whitespace will be stripped.

        Returns:
            The unit string (e.g., 'µg/m³') if the contaminant exists, otherwise
            None.
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "":
            return None

        if not contaminant_description in self._json_contaminants_data.keys():
            return None

        return self._json_contaminants_data[contaminant_description]['unit']

    
    def get_all_contaminants(self) -> Dict[str, Any]:
        """Return a copy of the contaminants data.

        Returns:
            A dictionary mapping contaminant descriptions (e.g., 'PM10') to
            their metadata (e.g., unit, codes).
        """
        return self._json_contaminants_data.copy()

    
    def get_contaminant_data_by_description(self, contaminant_description: str) -> Optional[Dict[str, Any]]:
        """Return all data for a contaminant description.

        Args:
            contaminant_description: Contaminant description (e.g., 'PM10', 'SO2'). Leading and
                trailing whitespace will be stripped.

        Returns:
            A dictionary with the contaminant data (including 'unit', 'codes',
            and 'description') if found, otherwise None.
        """
        
        contaminant_description = contaminant_description.strip()

        if contaminant_description == "":
            return None

        if contaminant_description in self._json_contaminants_data.keys():
            return_obj: Dict[str, Any] = self._json_contaminants_data[contaminant_description].copy()
            return_obj["description"] = contaminant_description
            return return_obj
        
        return None


    def get_codes_by_description(self, contaminant_description: str) -> Optional[list[int]]:
        """Return numeric codes for a given contaminant description.

        Args:
            contaminant_description: Contaminant description (e.g., 'PM10'). Whitespace is
                stripped.

        Returns:
            List of numeric codes if found, otherwise None.
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "" or contaminant_description not in self._json_contaminants_data.keys():
            return None
        
        codes = self._json_contaminants_data[contaminant_description]["codes"]
        return list(codes)


    def has_contaminant(self, contaminant_description: str) -> bool:
        """Return True if the contaminant description exists.

        Args:
            contaminant_description: Contaminant description (e.g., 'PM10'). Whitespace is stripped.
        Returns:
            True if present in the dataset, otherwise False.
        """

        contaminant_description = contaminant_description.strip()
        return contaminant_description in self._json_contaminants_data.keys()


    def has_contaminant_by_code(self, numeric_code: int) -> bool:
        """Return True if any contaminant contains the numeric code.

        Args:
            numeric_code: Numeric contaminant code.
        Returns:
            True if found in any contaminant, otherwise False.
        """

        for value in self._json_contaminants_data.values():
            if numeric_code in value.get("codes", []):
                return True
            
        return False


    def to_dataframe(self) -> pd.DataFrame:
        """Return contaminant data as a pandas DataFrame.

        The DataFrame contains columns: 'description', 'unit', and 'codes'.

        Returns:
            A pandas DataFrame with one row per contaminant.
        """
        rows = []

        for description, data in self._json_contaminants_data.items():
            row = {
                "description": description,
                "unit": data.get("unit"),
                "codes": data.get("codes", []),
            }

            rows.append(row)

        return pd.DataFrame(rows)
        
        
if __name__ == '__main__':
    
    print("Current directory:", os.getcwd(), '\n')    

    contaminants_json_file_path = './../data/gold/contaminants/contaminants.json'
    contaminant_manager = ContaminantManagerJSON(contaminants_json_file_path)
    
    print("Get all contaminants [ContaminantManagerJSON class]")
    pp.pprint(contaminant_manager.get_all_contaminants())
    
    
    print('\n')
    print("Get contaminant data by description [ContaminantManagerJSON class]\n")

    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        data = contaminant_manager.get_contaminant_data_by_description(description)
        print(f"'{description}' data => {data}")
    
    
    print('\n')
    print("Get contaminant units by description [ContaminantManagerJSON class]\n")
    
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        unit = contaminant_manager.get_units_by_description(description)
        print(f"'{description}' units => {unit}")
    
    
    print('\n')
    print("Get contaminant description by code [ContaminantManagerJSON class]\n")

    contaminants_mapping = ((10, "PM10"), (110, "PM10"), (9, "PM2_5"), (109, "PM2_5"),
                             (1, "SO2"), (101, "SO2"), (6, "CO"), (106, "CO"), (999, "INVALID"))

    for numeric_code, expected in contaminants_mapping:
        description = contaminant_manager.get_description_by_code(numeric_code)
        print(f"Code '{numeric_code}' (expected: '{expected}') => {description}")
    
    
    print('\n')
    print("Additional methods demonstration\n")
    
    # Test get_codes_by_description
    for description in ("PM10", "PM2_5", "SO2", "INVALID"):
        codes = contaminant_manager.get_codes_by_description(description)
        print(f"get_codes_by_description('{description}') => {codes}")
    
    # Test has_contaminant
    for description in ("PM10", "PM2_5", "CO", "INVALID"):
        exists = contaminant_manager.has_contaminant(description)
        print(f"has_contaminant('{description}') => {exists}")
    
    # Test has_contaminant_by_code
    for numeric_code in (10, 110, 6, 999):
        exists = contaminant_manager.has_contaminant_by_code(numeric_code)
        print(f"has_contaminant_by_code({numeric_code}) => {exists}")
    
    # Test to_dataframe
    print('\n')
    print("ContaminantManagerJSON.to_dataframe() output:")
    df = contaminant_manager.to_dataframe()
    print(df)
    