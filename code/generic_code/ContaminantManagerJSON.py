"""Utilities for managing air quality contaminant metadata.

This module provides a simple manager class to load contaminant definitions
from a JSON file and query units, codes, and descriptions. It also offers
helpers to export data for analysis.
"""

from typing import Any
import pandas as pd
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
        _json_contaminants_data (dict[str, Any]): Raw contaminant data loaded from JSON.
        _code_to_description (dict[int, str]): Reverse index mapping each numeric code to its contaminant description key.
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
        self._json_contaminants_data: dict[str, Any] = {}
        
        with open(file_path, encoding="utf-8") as json_file:
            self._json_contaminants_data = json.load(json_file)

        self._code_to_description: dict[int, str] = {
            code: description
            for description, data in self._json_contaminants_data.items()
            for code in data.get("codes", [])
        }
    

    def __repr__(self) -> str:
        contaminants = list(self._json_contaminants_data.keys())
        total_codes = len(self._code_to_description)
        return (
            f"{self.__class__.__name__}("
            f"{len(contaminants)} contaminants, "
            f"{total_codes} codes: "
            f"{contaminants})"
        )

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
        
        return sorted(all_codes)


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
        if not isinstance(numeric_code, int):
            return False

        return numeric_code in self._code_to_description


    def is_original_contaminant_by_code(self, numeric_code: int) -> bool:
        """Checks if a numeric code corresponds to an original contaminant.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            bool: True if the code is marked as original, False otherwise.
        """
        if not isinstance(numeric_code, int):
            return False

        description = self._code_to_description.get(numeric_code)
        if description is None:
            return False

        data = self._json_contaminants_data[description]
        return data.get("is_original_contaminant", {}).get(str(numeric_code), False)


    def get_description_by_code(self, numeric_code: int) -> dict[str, Any] | None:
        """Retrieves detailed information for a contaminant by its numeric code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            dict[str, Any] | None: Dictionary containing:
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
        if not isinstance(numeric_code, int):
            return None

        description = self._code_to_description.get(numeric_code)
        if description is None:
            return None

        data = self._json_contaminants_data[description]
        return {
            "description": description,
            "original_description": data.get("original_description", {}).get(str(numeric_code), ""),
            "extended_description": data.get("extended_description", {}).get(str(numeric_code), ""),
            "is_original_contaminant": data.get("is_original_contaminant", {}).get(str(numeric_code), False)
        }
    
    def get_codes_by_description(self, contaminant_description: str) -> list[int] | None:
        """Retrieves all numeric codes associated with a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10').
                Leading and trailing whitespace will be stripped.

        Returns:
            list[int] | None: List of numeric codes if found, None otherwise.

        Examples:
            >>> manager.get_codes_by_description('PM10')
            [10, 110]
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "" or contaminant_description not in self._json_contaminants_data.keys():
            return None
        
        return list(self._json_contaminants_data[contaminant_description]["codes"])


    def get_unit_by_code(self, numeric_code: int) -> str | None:
        """Retrieves the unit of measurement for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            str | None: Unit string (e.g., 'µg/m³') if found, None otherwise.
        """
        if not isinstance(numeric_code, int):
            return None

        description = self._code_to_description.get(numeric_code)
        if description is None:
            return None

        return self._json_contaminants_data[description].get("unit")
    
    def get_unit_by_description(self, contaminant_description: str) -> str | None:
        """Retrieves the unit of measurement for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.

        Returns:
            str | None: Unit string (e.g., 'µg/m³') if found, None otherwise.

        Examples:
            >>> manager.get_unit_by_description('PM10')
            'µg/m³'
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "":
            return None

        data = self._json_contaminants_data.get(contaminant_description)
        if data is None:
            return None

        return data['unit']


    def get_text_description_by_code(self, numeric_code: int) -> str | None:
        """Retrieves the text description for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            str | None: Text description string if found, None otherwise.
        """
        if not isinstance(numeric_code, int):
            return None

        description = self._code_to_description.get(numeric_code)
        if description is None:
            return None

        return self._json_contaminants_data[description].get("text_description")
    
    def get_text_description_by_description(self, contaminant_description: str) -> str | None:
        """Retrieves the text description for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.

        Returns:
            str | None: Text description string if found, None otherwise.
        """
        contaminant_description = contaminant_description.strip()
        
        if contaminant_description == "":
            return None

        data = self._json_contaminants_data.get(contaminant_description)
        if data is None:
            return None

        return data['text_description']


    def get_all_contaminants_data(self) -> dict[str, Any]:
        """Returns a deep copy of all contaminants metadata.

        Returns:
            dict[str, Any]: Dictionary mapping contaminant descriptions (e.g., 'PM10')
                to their metadata (unit, codes, descriptions, etc.).

        Note:
            Returns a deep copy to prevent accidental modification of internal data.
        """
        return copy.deepcopy(self._json_contaminants_data)

    def get_contaminant_data_by_description(self, contaminant_description: str) -> dict[str, Any] | None:
        """Retrieve all metadata for a contaminant description.

        Args:
            contaminant_description (str): Contaminant description (e.g., 'PM10', 'SO2').
                Leading and trailing whitespace will be stripped.

        Returns:
            dict[str, Any] | None: Dictionary containing:
                - description (str): The contaminant description
                - unit (str): Unit of measurement
                - codes (list[int]): Associated numeric codes
                - original_description (dict): Original descriptions by code
                - extended_description (dict): Extended descriptions by code
                - is_original_contaminant (dict): Originality flags by code
                Returns None if the description is not found.
        """
        
        contaminant_description = contaminant_description.strip()

        if contaminant_description == "":
            return None

        data = self._json_contaminants_data.get(contaminant_description)
        if data is not None:
            return_obj: dict[str, Any] = copy.deepcopy(data)
            return_obj["description"] = contaminant_description
            return return_obj

        return None
    
    def get_contaminant_data_by_code(self, numeric_code: int) -> dict[str, Any] | None:
        """Retrieves all metadata for a contaminant code.

        Args:
            numeric_code (int): Numeric contaminant code (e.g., 10, 109).

        Returns:
            dict[str, Any] | None: Dictionary containing:
                - description (str): The contaminant description
                - unit (str): Unit of measurement
                - codes (list[int]): Associated numeric codes
                - original_description (dict): Original descriptions by code
                - extended_description (dict): Extended descriptions by code
                - is_original_contaminant (dict): Originality flags by code
                Returns None if the code is not found.
        """
        if not isinstance(numeric_code, int):
            return None

        description = self._code_to_description.get(numeric_code)
        if description is None:
            return None

        return_obj: dict[str, Any] = copy.deepcopy(self._json_contaminants_data[description])
        return_obj["description"] = description
        return return_obj


    def to_dataframe(self) -> pd.DataFrame:
        """Exports contaminant data as a pandas DataFrame.

        Each row represents a unique combination of contaminant and code.

        Returns:
            pd.DataFrame: DataFrame with columns:
                - code (int): Numeric contaminant code
                - description (str): Contaminant description (e.g., 'PM10')
                - text_description (str): Human-readable description of the contaminant
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
    import os
    import pprint as pp
    from generic_code.util import print_sep

    print("Current directory:", os.getcwd(), '\n')

    contaminants_json_file_path = './../data/gold/contaminants/contaminants.json'
    contaminant_manager = ContaminantManagerJSON(contaminants_json_file_path)

    print_sep()
    print("ContaminantManagerJSON __repr__ [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    print(repr(contaminant_manager))

    print('\n')
    print_sep()
    print("Get all contaminant descriptions [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    descriptions = contaminant_manager.get_all_contaminants_descriptions()
    pp.pprint(descriptions)
    
    print('\n')
    print_sep()
    print("Get all contaminant codes [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    codes = contaminant_manager.get_all_contaminants_codes()
    pp.pprint(codes)
    
    print('\n')
    print_sep()
    print("Get contaminant data by description [ContaminantManagerJSON class]")
    print_sep(end_newline=True)

    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        data = contaminant_manager.get_contaminant_data_by_description(description)
        print(f"'{description}' data => ")
        pp.pprint(data)
        print('\n')


    print('\n')
    print_sep()
    print("Get unit by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for numeric_code in (10, 110, 1, 101, 6, 106, 999):
        unit = contaminant_manager.get_unit_by_code(numeric_code)
        print(f"get_unit_by_code({numeric_code}) => {unit}")


    print('\n')
    print_sep()
    print("Get contaminant units by description [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
        
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        unit = contaminant_manager.get_unit_by_description(description)
        print(f"'{description}' units => {unit}")

    
    print('\n')
    print_sep()
    print("Get contaminant text description by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
        
    for numeric_code in (10, 110, 1, 101, 6, 106, 999):
        text_description = contaminant_manager.get_text_description_by_code(numeric_code)
        print(f"get_text_description_by_code({numeric_code}) => {text_description}")


    print('\n')
    print_sep()
    print("Get contaminant text description by description [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
        
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        text_description = contaminant_manager.get_text_description_by_description(description)
        print(f"'{description}' text description => '{text_description}'")
    
    
    print('\n')
    print_sep()
    print("Get contaminant description by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)

    contaminants_mapping = ((10, "PM10"), (110, "PM10"), (9, "PM2_5"), (109, "PM2_5"),
                             (1, "SO2"), (101, "SO2"), (6, "CO"), (106, "CO"), (999, "INVALID"))

    for numeric_code, expected in contaminants_mapping:
        description = contaminant_manager.get_description_by_code(numeric_code)
        print(f"Code '{numeric_code}' (expected: '{expected}') => ")
        pp.pprint(description)
        print('\n')
    
    
    print('\n')
    print_sep()
    print("Get codes by description [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for description in ("PM10", "PM2_5", "SO2", "CO", "INVALID"):
        codes = contaminant_manager.get_codes_by_description(description)
        print(f"get_codes_by_description('{description}') => {codes}")

    
    print('\n')
    print_sep()
    print("Check contaminant by description [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for description in ("PM10", "PM2_5", "CO", "INVALID", "  PM10  "):
        exists = contaminant_manager.has_contaminant_by_description(description)
        print(f"has_contaminant_by_description('{description}') => {exists}")
    
    
    print('\n')
    print_sep()
    print("Check contaminant by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for numeric_code in (10, 110, 6, 999):
        exists = contaminant_manager.has_contaminant_by_code(numeric_code)
        print(f"has_contaminant_by_code({numeric_code}) => {exists}")

    
    print('\n')
    print_sep()
    print("Check if original contaminant by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for numeric_code in (10, 110, 1, 101, 999):
        is_original = contaminant_manager.is_original_contaminant_by_code(numeric_code)
        print(f"is_original_contaminant_by_code({numeric_code}) => {is_original}")

    
    print('\n')
    print_sep()
    print("Get contaminant data by code [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    for numeric_code in (10, 110, 1, 101, 999):
        data = contaminant_manager.get_contaminant_data_by_code(numeric_code)
        print(f"get_contaminant_data_by_code({numeric_code}) => ")
        pp.pprint(data)
        print('\n')

    
    print('\n')
    print_sep()
    print("Get all contaminants data [ContaminantManagerJSON class]")
    print_sep(end_newline=True)
    
    all_data = contaminant_manager.get_all_contaminants_data()
    pp.pprint(all_data)

    
    print('\n')
    print_sep()
    print("ContaminantManagerJSON.to_dataframe() output")
    print_sep(end_newline=True)
    
    df = contaminant_manager.to_dataframe()
    print(df)
