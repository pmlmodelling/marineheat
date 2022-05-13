import pandas as pd
import nctoolkit as nc
import xarray as xr
from matchpoint.utils import get_type


def add_data(self, files=None, variable=None):
    """
    Add model data
    Parameters
    -------------
    files: str or list
        File path(s) of the data
    variable: str
        Temperature variable

    """

    self.data = nc.open_data(files, checks=False)

    vars = self.data.variables

    if variable is None:
        if len(vars) != 1:
            raise ValueError("Please provide a variable")
        if len(vars) == 1:
            self.variable = vars[0]

    if len(vars) > 1:
        self.data.select(variables=variable)
        self.variable = variable
