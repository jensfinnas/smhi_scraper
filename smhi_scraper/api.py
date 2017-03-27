# encoding: utf-8
import requests
from statscraper.api import Api
from smhi_scraper.dataset import Dataset
from smhi_scraper.common import Common


class SMHI(Api, Common):
    def list(self):
        """Get a list of all dataset
        """
        url = self.base_url + "parameter.json"
        json_data = self.json_request(url)
        datasets = [Dataset(x) for x in json_data["resource"]]

        return datasets



