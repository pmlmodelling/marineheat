from collections import defaultdict
import pandas as pd
import nctoolkit as nc


def is_even(x):
    return x % 2 < 0.5


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

    if type(period) is not list:
        raise ValueError("You have to provide a period for the baseline")

    if type(window) is not int:
        raise TypeError("You have to provide an int for window")

    if is_even(window):
        raise ValueError("The window must be an odd number")

    if window < 1:
        raise ValueError("The window must be a positive number")

    percentile = int2ordinal_3(p)

    if window != 1:

        ds = self.data.copy()

        years = ds.years
        years = [str(x) for x in years if x <= period[1] and x >= period[0]]
        years = ",".join(years)
        print(
            f"Baseline climatology calculated based on the years {years} using a {window} day window and the {percentile} percentile within the window."
        )

        ds.select(years=range(period[0] - 1, period[1] + 2))
        ds.run()

        ds_times = ds.times

        months = [x.month for x in ds_times]
        days = [x.day for x in ds_times]
        years = [x.year for x in ds_times]
        df_times = pd.DataFrame({"year": years, "month": months, "day": days})
        ind_times = (
            df_times.loc[:, ["month", "day"]]
            .drop_duplicates()
            .sort_values(["month", "day"])
            .reset_index()
        )
        df_times = (
            df_times.reset_index()
            .rename(columns={"index": "ds_index"})
            .merge(ind_times)
            .sort_values(["year", "month", "day"])
        )

        start = period[0]
        end = period[1]

        ds_threshold = nc.open_data()

        for i in range(0, self.ndays):
            ds_years = ds.copy()
            i_indices = (
                df_times.query("year >= @start")
                .query("year <= @end")
                .query("index == @i")
            )
            ind_choice = []
            for j in list(i_indices.ds_index):
                the_j = list(
                    range(j - int((window - 1) / 2), j + int((window - 1) / 2) + 1)
                )
                ind_choice += the_j

            ind_choice = [x if x > 0 else 0 for x in ind_choice]
            ind_choice = list(set(ind_choice))

            ds_years.select(times=ind_choice)
            ds_years.tpercentile(p)
            ds_years.set_date(year=2001, month=1, day=1)
            if i > 0:
                ds_years.shift(days=i)
            ds_years.run()
            ds_threshold.append(ds_years)
        ds_threshold.merge("time")
        ds_threshold.run()

        self.baseline = ds_threshold.copy()
        return None

    ds_clim = self.data.copy()
    ds_clim.select(years=range(period[0], period[1] + 1))
    cal = ds_clim.calendar

    ds_clim.run()
    years = ds_clim.years
    years = [str(yy) for yy in years]
    years = ",".join(years)

    self.calendar = cal
    print(
        f"Baseline climatology calculated based on the years {years} using a {window} day window and the {percentile} percentile within the window."
    )

    ds_clim.tpercentile(over="day", p=p)
    ds_clim.run()

    self.baseline = ds_clim.copy()
