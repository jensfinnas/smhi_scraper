# encoding: utf-8
from statscraper.dimension import Dimension 
from smhi_scraper.category import Station, Category

class Stations(Dimension):
    def __init__(self, json_data):
        self._id = "station"
        self._label = "Station"
        self.json = json_data

    def _list(self):
        return [Station(x) for x in self.json]

    def stations(self):
        """ Synonyme for .list()/.categories
        """
        return self.list()

class Periods(Dimension):
    def __init__(self):
        self._id = "period"
        self._label = "Period"

    def _list(self):
        return [
            Category("latest-hour"),
            Category("latest-day"),
            Category("latest-months"),
            Category("corrected-archive"),

        ]
