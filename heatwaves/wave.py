import nctoolkit as nc
import os
import subprocess
from tqdm import tqdm
import numpy as np


def wave(self, duration=5, gap=3, period=None):
    """
    Calculate future heat wave metrics
    Parameters
    -------------
    files: str or list
        File path(s) of the data
    variable: str
        Temperature variable

    """

    if type(duration) is not int:
        raise ValueError("duration must be an integer")

    if duration < 3:
        raise ValueError("Minimum value of duration is 3 days")

    if gap < 3:
        raise ValueError("Minimum value of gap is 3 days")

    if type(gap) is not int:
        raise ValueError("gap must be an integer")

    years = self.data.years

    if period[0] == np.min(years):
        raise ValueError(
            "Heat waves cannot be calculated for the first year in the time series"
        )

    print("Calculating days above threshold")
    ds_clim = self.baseline.copy()

    ds_thresh = self.data.copy()
    ds_thresh.split("year")

    if len(self.data) > 1:
        raise NotImplementedError("Only works with single file datasets currently!")

    ds_thresh.gt(ds_clim)
    ds_thresh.merge("time")
    ds_thresh.rename({"tos": "above"})
    ds_thresh.assign(below=lambda x: x.above < 1)
    ds_thresh.run()
    ds_thresh.run()

    n_times = len(ds_thresh.times)

    ds_end = ds_thresh.copy()
    ds_end.select(variable="below")
    ds_end.rolling_sum(gap)
    ds_end.shift(day=1)
    ds_end.compare("> 0")
    ds_end.rename({"below": "end"})
    ds_end.run()
    ds_end.run()

    ds_thresh.select(variables="above")

    print("Calculating days within gaps")

    ds_tracker = ds_thresh.copy()
    ds_tracker.select(time=0)
    ds_tracker.rename({"above": "tracker"})
    ds_tracker.select(variables="tracker")
    ds_tracker.run()

    ds_day = ds_thresh.copy()
    ds_day.select(time=1)
    ds_day.run()

    ds_tracker.append(ds_day)
    ds_tracker.merge("variable")
    ds_tracker.run()

    ds_tracker.assign( tracker=lambda x: (x.tracker < duration) * (x.above) * x.tracker + (x.tracker > (duration - 1)) * x.tracker)
    ds_tracker.assign(previous=lambda x: x.tracker - x.tracker + 0.0)
    ds_tracker.assign(tracker=lambda x: x.tracker - x.tracker + 0.0)

    ds_tracker.run()

    ds_tracker.run()

    the_times = ds_end.times

    all_ds = nc.open_data()
    ds_year = nc.open_data()
    print("Calculating heat wave occurrences for each day")

    ds_thresh.select(years=range(period[0], period[1] + 1))
    ds_end.select(years=range(period[0], period[1] + 1))

    ds_thresh.is_corrupt()
    ds_end.is_corrupt()

    j = -1
    for yy in range(period[0], period[1] + 1):
        yy_thresh = ds_thresh.copy()
        yy_end = ds_end.copy()
        yy_thresh.select(year=yy)
        yy_end.select(year=yy)
        yy_end.run()
        yy_thresh.run()

        j += 1
        ds_year = nc.open_data()
        for i in tqdm(range(0, self.ndays)):

            while True:
                command = (
                    f"cdo -aexpr,'previous=previous*(tracker > 1)' "
                    + f"-aexpr,'tracker=(hw>0)*0+(hw<1)*tracker' -aexpr,'hw=(tracker -previous) * (tracker > {duration-1})*end' -aexpr,'tracker=(tracker < {duration})*(above)*(tracker+above)+(tracker>{duration-1})*(tracker + above)' -merge -selname,tracker,previous "
                    + ds_tracker[0]
                    + f" -seltimestep,{i + 1} "
                    + yy_thresh[0]
                    + " "
                    f"-seltimestep,{i +1} " + yy_end[0]
                )
                temp = nc.temp_file.temp_file("nc")
                command = command + " " + temp
                out = subprocess.Popen(
                    command,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                result, ignore = out.communicate()

                result = result.decode("utf-8")
                if "No data arrays " in result:
                    raise ValueError(result)

                break


            ds_tracker.current = temp

            if os.path.exists(temp) is False:
                raise ValueError("does not exist")


            if i == (self.ndays - 1):
                ds_tracker.assign( hw=lambda x: x.hw + (x.tracker > duration) * (x.tracker - x.previous))
                ds_tracker.assign(previous=lambda x: x.tracker + 1 - 1)
                ds_tracker.run()

            ds_year.append(ds_tracker)

            if i == (self.ndays -1):
                ds_year.ensemble_sum()
                ds_year.select(variable="hw")
                ds_year.set_year(yy)
                all_ds.append(ds_year)


    print("Summarizing results")

    all_ds.merge("time")

    all_ds.rename({"hw": "days"})
    if period is not None:
        all_ds.select(years=range(period[0], period[1] + 1))
    all_ds.run()

    self.results = all_ds.copy()
