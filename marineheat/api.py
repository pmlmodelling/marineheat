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

    from marineheat.adders import add_data
    from marineheat.clim import climatology
    from marineheat.wave import wave
