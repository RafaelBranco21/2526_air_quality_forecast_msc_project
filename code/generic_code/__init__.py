"""Package initializer for `generic_code`.

Provides convenient access to the `ContaminantManagerJSON` and `StationEDAHelper` classes:

	from generic_code import ContaminantManagerJSON
	from generic_code import StationEDAHelper

"""

from .ContaminantManagerJSON import ContaminantManagerJSON
from .StationEDAHelper import StationEDAHelper

__all__ = ["ContaminantManagerJSON", "StationEDAHelper"]
