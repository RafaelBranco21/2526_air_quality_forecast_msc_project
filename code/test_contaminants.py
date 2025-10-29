import unittest
import pandas as pd
from contaminants import ContaminantManager

class MockContaminantManager(ContaminantManager):
    def __init__(self):
        data = {
            'code': ['NO2', 'O3', 'PM10'],
            'description': ['Nitrogen Dioxide', 'Ozone', 'Particulate Matter < 10µm'],
            'units': ['µg/m³', 'µg/m³', 'µg/m³']
        }
        self.df = pd.DataFrame(data)
        self.df = self.df.sort_values(by='code')

class TestContaminantManager(unittest.TestCase):

    def setUp(self):
        self.manager = MockContaminantManager()

    def test_existing_description(self):
        self.assertEqual(self.manager.get_description_by_code('O3'), 'Ozone')

    def test_non_existing_description(self):
        self.assertIsNone(self.manager.get_description_by_code('CO'))

    def test_none_description(self):
        self.assertIsNone(self.manager.get_description_by_code())

    def test_existing_units(self):
        self.assertEqual(self.manager.get_units_by_code('PM10'), 'µg/m³')

    def test_non_existing_units(self):
        self.assertIsNone(self.manager.get_units_by_code('CO'))

    def test_get_all_contaminants(self):
        df = self.manager.get_all_contaminants()
        self.assertEqual(len(df), 3)
        self.assertIn('NO2', df['code'].values)
        
    def test_get_contaminant_data_by_code(self):
        data = self.manager.get_contaminant_data_by_code('NO2')
        self.assertIsInstance(data, dict)
        self.assertEqual(data['description'], 'Nitrogen Dioxide')
        self.assertEqual(data['units'], 'µg/m³')

    def test_get_contaminant_data_invalid(self):
        self.assertIsNone(self.manager.get_contaminant_data_by_code('CO'))

    def test_get_column_names(self):
        columns = self.manager.get_column_names()
        self.assertEqual(columns, ['code', 'description', 'units'])

if __name__ == '__main__':
    unittest.main()