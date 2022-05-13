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

    self.calendar = cal

    if ("360" not in cal) or ("365" not in cal):
        ds_clim.drop(day=29, month=2)
    ds_clim.tpercentile(over="day", p=p)
    ds_clim.run()

    self.baseline = ds_clim.copy()
