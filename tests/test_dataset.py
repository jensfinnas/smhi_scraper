# encoding: utf-8

from smhi_scraper.api import SMHI
from smhi_scraper.dimension import Dimension, Stations
from smhi_scraper.category import Station

def test_basics():
    api = SMHI()
    for dataset in api.list():
        assert dataset.id

def test_dimension():
    api = SMHI()
    dataset = api.list()[0]
    dims = dataset.dimensions
    for dim in dims:
        assert(isinstance(dim, Dimension))
        assert dim.id
        assert(isinstance(dim.list(), list))
        assert(isinstance(dim.categories, list))

def test_stations():
    api = SMHI()
    dataset = api.list()[0]
    stations = dataset.stations
    assert len(stations) > 0
    for station in stations:
        assert isinstance(station, Station)
