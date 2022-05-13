def open_hw():

    heat = Heatwave()
    return heat


class Heatwave(object):
    """
    A modifiable ensemble of netCDF files
    """

    def __init__(self, start=""):
        """Initialize the starting file name etc"""
        # Attribuates of interest to users
        self.data = None
        self.variable = None

    # Import any methods

    from heatwaves.adders import add_data
    from heatwaves.clim import climatology
    from heatwaves.wave import wave
