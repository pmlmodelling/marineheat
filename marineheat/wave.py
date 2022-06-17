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

    if len(period) != 2:
        raise ValueError("Please provide the start and end of the period")

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
    ds_thresh.rename({self.variable: "above"})
    ds_thresh.assign(below=lambda x: x.above < 1)
    ds_thresh.run()
    ds_thresh.run()

    n_times = len(ds_thresh.times)

    ds_end = ds_thresh.copy()
    ds_end.subset(variable="below")
    ds_end.rolling_sum(gap)
    ds_end.shift(day=1)
    ds_end.compare("> 0")
    ds_end.rename({"below": "end"})
    ds_end.run()
    ds_end.run()

    ds_thresh.subset(variables="above")

    print("Calculating days within gaps")

    ds_tracker = ds_thresh.copy()
    ds_tracker.subset(time=0)
    ds_tracker.rename({"above": "tracker"})
    ds_tracker.subset(variables="tracker")
    ds_tracker.run()

    ds_day = ds_thresh.copy()
    ds_day.subset(time=1)
    ds_day.run()

    ds_tracker.append(ds_day)
    ds_tracker.merge("variable")
    ds_tracker.run()

    # tracker keeps track of the number of days above the temperature threshold
    # a heat wave occurs when this has gone on for as long as the duration
    # previous keeps track of how many heat wave days occured before the year, but when the heat wave is still ongoing
    # Both tracker and previous are set to 0 at the start

    ds_tracker.assign(previous=lambda x: x.tracker - x.tracker + 0.0)
    ds_tracker.assign(tracker=lambda x: x.tracker - x.tracker + 0.0)

    ds_tracker.run()

    ds_tracker.run()

    the_times = ds_end.times

    all_ds = nc.open_data()
    print("Calculating heat wave occurrences for each day")

    ds_thresh.subset(years=range(period[0], period[1] + 1))
    ds_end.subset(years=range(period[0], period[1] + 1))

    ds_thresh.is_corrupt()
    ds_end.is_corrupt()

    ds_events = nc.open_data()

    ds_thresh.run()
    ds_end.run()

    j = -1

    n_years = period[1] - period[0] + 1

    yy = period[0]
    for j in tqdm(range(0, n_years * self.ndays)):
    #for yy in range(period[0], period[1] + 1):
        if j > 0:
            if (j % self.ndays) == 0:
                yy += 1

        if (j % self.ndays) == 0:
            yy_thresh = ds_thresh.copy()
            yy_end = ds_end.copy()
            yy_thresh.subset(year=yy)
            yy_end.subset(year=yy)
            yy_end.run()
            yy_thresh.run()
            ds_year = nc.open_data()

        j += 1
        #for i in tqdm(range(0, self.ndays)):
        i = j % self.ndays
        #for i in range(0, self.ndays):

        if True:
            while True:
                command = (
                    f"cdo -aexpr,'previous=previous*(tracker > 1)' "
                    + f"-aexpr,'tracker=(hw>0)*0+(hw<1)*tracker' " 
                    + f"-aexpr,'hw=(tracker -previous) * (tracker > {duration-1})*end' "
                    + f"-aexpr,'tracker=(tracker < {duration})*(above)*(tracker+above)+(tracker>{duration-1})*(tracker + above)' "
                    + " -merge -selname,tracker,previous "
                    + ds_tracker[0]
                    + f" -seltimestep,{i + 1} "
                    + yy_thresh[0]
                    + " "
                    f"-seltimestep,{i +1} " + yy_end[0]
                )
                temp = nc.temp_file.temp_file("nc")
               # nc.session.append_safe(temp)
                ds_tracker.current = temp

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

                if os.path.exists(temp):
                    break


            #nc.session.remove_safe(temp)


            if os.path.exists(temp) is False:
                raise ValueError("does not exist")


            if i == (self.ndays - 1):
                ds_tracker.assign( hw=lambda x: x.hw + (x.tracker >= duration) * (x.tracker - x.previous))
                #ds_tracker.run()
                ds_tracker.assign(previous=lambda x: (x.tracker) * (x.tracker > duration) )
                ds_tracker.run()

            ds_year.append(ds_tracker)

            #if i == 0:
            #    ds_year = ds_tracker.copy()
            #    ds_year.subset(variable = "hw")
            #else:
            #    ds_year.add(ds_tracker, "hw")
            #    ds_year.run()

            if i == (self.ndays -1):
                ##yy_events = ds_year.copy()
                ##yy_events.merge("time")
                ##yy_events.compare(">0")
                ##yy_events.tsum()
                ##yy_events.rename({"hw":"n_events"})
                ##ds_events.append(yy_events)
                #for ff in ds_year:
                #    if os.path.exists(ff) == False:
                #        print(ff)
                #ds_year.nco_command("ncea -y sum -v hw", ensemble=True)
                ds_year.subset(variable="hw")
                ds_year.ensemble_sum()
                #ds_year.run()
                ##ds_year.subset(variable="hw")
                ds_year.set_year(yy)
                #print("here 3")
                #ds_year.run()
                #print("here 4")
                all_ds.append(ds_year)


    print("Summarizing results")

    all_ds.merge("time")

    all_ds.rename({"hw": "days"})
    all_ds.run()


    self.hwdays = all_ds.copy()
    #self.nevents = ds_events.copy()
    #self.nevent = all_ds.copy()




