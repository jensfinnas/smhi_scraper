# encoding: utf-8
from statscraper.dataset import Dataset 
from smhi_scraper.dimension import Dimension, Stations, Periods
from smhi_scraper.common import Common
import csvkit as csv
import StringIO
from datetime import datetime
from requests.exceptions import InvalidURL

class Dataset(Dataset, Common):
    """Represents a parameter"""
    def __init__(self, json_data):
        self._id = json_data["key"]
        self._label = u"{} {}".format(
            json_data["title"],
            json_data["summary"]
            ) 
        self._parameter = json_data["title"]
        self.url = "{}parameter/{}".format(self.base_url, self._id)
        self._json = None

    @property
    def json(self):
        if self._json is None:
            self._json = self.json_request(self.url + ".json")
        return self._json

    @property
    def parameter(self):
        """ Name of parameter
        """
        return self._parameter

    @property
    def periodicity(self):
        return PERIODICITIES[self.label]
    
    

    @property
    def updated(self):
        """ ;returns: Latest update
            :rtype: datetimedatetime
        """
        return datetime.fromtimestamp(self.json["updated"]/1000)

    @property
    def active_stations(self):
        return [x for x in self.stations if x.is_active]
    
    

    def _query(self, station=None, period="latest-day",
        timepoint_start=None, timepoint_end=None):
        """ Make a query
        """
        data = []
        if isinstance(station, str) or isinstance(station, unicode):
            station = [station]

        if isinstance(period, str) or isinstance(period, unicode):
            period = [period]


        dim_stations = self.dimension("station")
        dim_periods = self.dimension("period")
        for _station in station:
            station_id = dim_stations.get(_station).id
            for _period in period:

                period_id = dim_periods.get(_period).id

                url = "{}/station/{}/period/{}/data.csv"\
                    .format(self.url, station_id, period_id)
                try:
                    csv_content = self.csv_request(url)

                except InvalidURL:
                    # Some stations may not have data fro this period
                    continue

                raw_data = DataCsv().from_string(csv_content).to_dictlist()
                
                # TODO: This is a very hard coded parse function
                # Expects fixed start row and number of cols 
                for row in raw_data:
                    if "Datum" in row and "Tid (UTC)" in row:
                        timepoint_str = "{} {}".format(
                            row["Datum"], row["Tid (UTC)"])
                    elif u"Från Datum Tid (UTC)":
                        timepoint_str = row[u"Från Datum Tid (UTC)"] 

                    timepoint = datetime.strptime(timepoint_str, "%Y-%m-%d %H:%M:%S")
                    data.append({
                        "timepoint": timepoint,
                        "quality": row["Kvalitet"],
                        "parameter": self.parameter,
                        "station": station_id,
                        "period": period_id,
                        "value": row[self.parameter],
                        })

        return data

    
    def list(self):
        """
        """
        return [
            Stations(self.json["station"]),
            Periods(),
            Dimension("quality"),
            Dimension("timepoint"),
            Dimension("parameter"),
        ]

    @property
    def stations(self):
        """ Convinience for listing all stations
        """
        return self.dimension("station").list()
    

class DataCsv(object):
    def __init__(self):
        self.headers = None
        self.data = None


    def from_file(self, file_path):
        with open(file_path) as f:
            self._parse(f)

        return self

    def from_string(self, csv_content):
        f = StringIO.StringIO(csv_content)
        self._parse(f)

        return self

    def to_dictlist(self):
        return [dict(zip(self.headers, row)) 
            for row in self.data]
    
    def _parse(self, f):
        rows = list(csv.reader(f, delimiter=';'))
        tables = []
        table = []
        for i, row in enumerate(rows):
            is_last = i == len(rows) - 1

            # Check if new table
            if is_empty(row):
                if len(table) > 0:
                    tables.append(table)
                table = []
                continue

            is_header = len(table) == 0
            if is_header:
                n_cols = table_width(row)

            table.append(row[:n_cols])

            if is_last:
                tables.append(table)

        data_table = tables[-1]
        self.headers = data_table[0]
        try:
            self.data = data_table[1:]
        except IndexError:
            self.data = []


def is_empty(row):
    """ Check if a csv row (represented as a list
        of values) is empty.
        
        [] => True
        ["","","foo"] => True
        ["foo","bar"] => False
    """
    if len(row) == 0:
        return True
    if row[0] == "":
        return True
    return False

def table_width(row):
    """ Get number of cols in row
        ["col1", "col2","","","other_col"] => 2
    """

    for i, val in enumerate(row):
        if val == "":
            break
    return i



PERIODICITIES = {
    u"Byvind max, 1 gång/tim": "hourly",
    u"Global Irradians (svenska stationer) medelvärde 1 timme, 1 gång/tim": "hourly",
    u"Lufttemperatur medel, 1 gång per månad": "monthly",
    u"Lufttemperatur min, 1 gång per dygn": "daily",
    u"Lufttemperatur momentanvärde, 1 gång/tim": "hourly",
    u"Lufttemperatur medelvärde 1 dygn, 1 gång/dygn, kl 00": "daily",
    u"Lufttemperatur max, 1 gång per dygn": "daily",
    u"Lufttryck reducerat havsytans nivå vid havsytans nivå, momentanvärde, 1 gång/tim": "hourly",
    u"Långvågs-Irradians Långvågsstrålning, medel 1 timme, varje timme": "hourly",
    u"Nederbörd 2 gånger/dygn, kl 06 och 18": "bi-daily",
    u"Nederbörd 1 gång/dygn, kl 18": "daily",
    u"Nederbördsintensitet max under 15 min, 4 gånger/tim": "every_15_minutes",
    u"Nederbördsmängd summa, 1 gång per månad": "monthly",
    u"Nederbördsmängd summa 15 min, 4 gånger/tim": "every_15_minutes",
    u"Nederbördsmängd summa 1 dygn, 1 gång/dygn, kl 06": "daily",
    u"Nederbördsmängd summa 1 timme, 1 gång/tim": "hourly",
    u"Present weather momentanvärde, 1 gång/tim resp 8 gånger/dygn": "hourly",
    u"Relativ Luftfuktighet momentanvärde, 1 gång/tim": "hourly",
    u"Sikt momentanvärde, 1 gång/tim": "hourly",
    u"Snödjup momentanvärde, 1 gång/dygn, kl 06": "daily",
    u"Solskenstid summa 1 timme, 1 gång/tim": "hourly",
    u"Total molnmängd momentanvärde, 1 gång/tim": "hourly",
    u"Vindhastighet medelvärde 10 min, 1 gång/tim": "hourly",
    u"Vindriktning medelvärde 10 min, 1 gång/tim": "hourly",    
}
