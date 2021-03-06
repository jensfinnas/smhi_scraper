# encoding: utf-8

from statscraper.collection import Api
from vantetider.common import Common
from vantetider.dataset import Dataset
import requests
from bs4 import BeautifulSoup
from . import dataset

class Vantetider(Api, Common):
    """
        Begränsningar:
        - Går inte in specifkt på operation/åtgärd (t.ex. http://www.vantetider.se/Kontaktkort/Dalarnas/SpecialiseradOperation/)
        - Går inte in specifikt på vårdtyper
    """

    @property
    def items(self):
        if self._items is None:
            items = {}
            html = self.get_html(self.base_url + "Sveriges")
            soup = BeautifulSoup(html, 'html.parser')
            # Get links to datasets
            links = soup.find_all("ul", {"class":"main-nav page-width"})[0]\
                .find_all("li")[1]\
                .find_all("a")\
                [2:] # First two are not relevant

            ids = [x.get("href").split("/Sveriges/")[-1].replace("/","") 
                for x in links]
            labels = [x.text for x in links]

            for i, id_ in enumerate(ids):
                try:
                    dataset = Dataset(id_)
                except NotImplementedError:
                    # Don't list datasets that we haven't implemented yet
                    continue
                dataset.label = labels[i]
                
                items[id_] = dataset

            self._items = items

        return self._items

    def generate_dictionary(self, **kwargs):
        for dataset in self.list():
            dataset.generate_dictionary()
