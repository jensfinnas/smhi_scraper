# encoding: utf-8

from statscraper.category import Category
from datetime import datetime

class Station(Category):
    """docstring for Station"""
    def __init__(self, json_data):
        self._id = json_data["key"]
        self._label = json_data["name"]
        self.longitude = json_data["longitude"]
        self.latitude = json_data["latitude"]
        self.updated = datetime.fromtimestamp(json_data["updated"]/1000)

    @property
    def is_active(self):
        """ Was there an update in the last 100 days? 
        """
        return (datetime.now() - self.updated).days < 100
