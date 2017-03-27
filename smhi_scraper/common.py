# encoding: utf-8
""" Common methods used by classes across scraper
""" 
from statscraper.common import Common
import requests
from requests.exceptions import InvalidURL, RequestException

class Common(Common):
    def json_request(self, url):
        """ Get json from request
        """
        print "Get {}".format(url)
        r = requests.get(url)
        
        if r.status_code != 200:
            raise RequestException(r.json())

        return r.json()

    def csv_request(self, url):
        """ Get and parse csv file from url
        """
        print "Get {}".format(url)
        r = requests.get(url)

        if r.status_code != 200:
            if r.status_code == 404:
                raise InvalidURL()
            else:
                raise RequestException(r.content)
        return r.content

