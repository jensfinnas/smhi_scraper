# encoding: utf-8

from smhi_scraper.api import SMHI
from smhi_scraper.dataset import DataCsv

def test_query_all_datasets():
    """ Make a sample query on all datasets
    """
    api = SMHI()
    for dataset in api.list():
        stations = [x.id for x in dataset.stations
            if x.updated.year >= 2016][:3]
        data = dataset.query(
            station=stations,      
            period=[
            "latest-day",
            "latest-months"]
            ).data
        if len(data) == 0:
            data = dataset.query(
                station=stations,      
                period=[
                "corrected-archive"]
                ).data

        assert len(data) > 0


def test_data_csv():
    file_path = "tests/data/query/smhi-opendata_11_71415_latest-day_2017-03-26_12-00-00.csv"
    data_csv = DataCsv().from_file(file_path)
    assert data_csv.headers == [
        "Datum",
        "Tid (UTC)",
        "Global Irradians (svenska stationer)",
        "Kvalitet",
    ]
    assert len(data_csv.data) == 24
    assert data_csv.data[0][2] == "524.03"
    assert data_csv.data[-1][2] == "529.36"

def test_empty_data_csv():
    file_path = "tests/data/query/smhi-opendata_2_188800_latest-day_2017-03-26_12-00-00.csv"
    data_csv = DataCsv().from_file(file_path)
    assert data_csv.headers == [
        u"Från Datum Tid (UTC)",
        u"Till Datum Tid (UTC)",
        u"Representativt dygn",
        u"Lufttemperatur",
        u"Kvalitet",
    ]
    assert len(data_csv.data) == 0