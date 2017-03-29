# encoding: utf-8
from statscraper.common import Common
import requests
from requests.exceptions import InvalidURL, RequestException
import requests_cache
from bs4 import BeautifulSoup

requests_cache.install_cache()

class Common(Common):
    @property
    def base_url(self):
        return u"http://www.vantetider.se/Kontaktkort/"
    
    @property
    def json_base_url(self):
        return u"http://www.vantetider.se/api/Ajax/"
    

    def get_html(self, url):
        """ Get html from url
        """
        print u"/GET " + url
        r = requests.get(url)
        if r.status_code != 200:
            msg = u"Error getting {}: ({})".format(url, r.status_code)
            raise RequestException(msg)

        return r.content

    def get_json(self, url):
        """ Get json from url
        """
        print u"/GET " + url
        r = requests.get(url)
        if r.status_code != 200:
            msg = u"Error getting {}: ({})".format(url, r.status_code)
            raise RequestException(msg)

        return r.json()
