"""Package initializer for `generic_code`.

Provides convenient access to the `ContaminantManagerJSON`, `StationEDAHelper` classes,
and utility functions:

	from generic_code import ContaminantManagerJSON
	from generic_code import StationEDAHelper
	from generic_code import print_sep

"""

from .ContaminantManagerJSON import ContaminantManagerJSON
from .StationManagerJSON import StationManagerJSON
from .StationEDAHelper import StationEDAHelper
from .station_pipeline import run_station_pipeline
from .station_pipeline import discover_station_years
from .station_pipeline import compare_years
from .station_pipeline import compare_years_sequence
from .util import print_sep, print_2D_shape_from_dataframe

__all__ = [
	"ContaminantManagerJSON",
	"StationManagerJSON",
	"StationEDAHelper",
	"run_station_pipeline",
	"discover_station_years",
	"compare_years",
	"compare_years_sequence",
	"print_sep",
	"print_2D_shape_from_dataframe",
]
