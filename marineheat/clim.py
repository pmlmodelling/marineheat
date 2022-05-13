
from collections import defaultdict

def int2ordinal_3(num):
    ordinal_dict = defaultdict(lambda: "th")
    ordinal_dict.update({1: "st", 2: "nd", 3: "rd"})
    mod = num % 10
    if num % 100 == 11:
        suffix = "th"
    else:
        suffix = ordinal_dict[mod]
    return f"{num}{suffix}"


def climatology(self, period=None, p=90, window=1):
    """
    Generate the historical climatology
    Add model data
    Parameters
    -------------
    period: list
        2 element list. Must be the first and last year for the climatology.
    p: int
        Percentile to use
    windows: int
        Rolling window to use for the climatology. Default is 1, so it uses a daily climatology

    """

    if window != 1:
        raise NotImplementedError("Windows other than 1 have not been implemented")

    ds_clim = self.data.copy()
    ds_clim.select(years=range(period[0], period[1] + 1))
    cal = ds_clim.calendar

    ds_clim.run()
    years = ds_clim.years
    percentile = int2ordinal_3(p)
    print(f"Baseline climatology calculated based on the years {years} using a {window} day window and the {percentile} percentile")

    self.calendar = cal

    ds_clim.tpercentile(over="day", p=p)
    ds_clim.run()

    self.baseline = ds_clim.copy()
