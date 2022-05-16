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
    self.calendar = self.data.calendar

    if "360" in self.calendar:
        self.ndays = 360
    else:
        self.ndays = 365

    self.leap = False

    if "greg" in self.calendar:
        self.leap = True

    if self.leap:
        print("Removing 29th February from leap years to ensure daily baseline is consistent.") 
        self.data.no_leaps()

    vars = self.data.variables

    if variable is None:
        if len(vars) != 1:
            raise ValueError("Please provide a variable")
        if len(vars) == 1:
            self.variable = vars[0]

    if len(vars) > 1:
        self.data.select(variables=variable)
        self.variable = variable
