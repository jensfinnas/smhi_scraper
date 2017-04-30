# encoding: utf-8
from statscraper.common import Common
import requests
from requests.exceptions import InvalidURL, RequestException
import requests_cache
from bs4 import BeautifulSoup

#requests_cache.install_cache()


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
        self.log.info(u"/GET " + url)
        r = requests.get(url)
        if hasattr(r, 'from_cache'):
            if r.from_cache:
                self.log.info("(from cache)")

        if r.status_code != 200:
            throw_request_err(r)

        return r.content

    def post_html(self, url, payload):
        self.log.info(u"/POST {} with {}".format(url, payload))
        r = requests.post(url, payload)
        if r.status_code != 200:
            throw_request_err(r)

        return r.content

    def get_json(self, url):
        """ Get json from url
        """
        self.log.info(u"/GET " + url)
        r = requests.get(url)
        if hasattr(r, 'from_cache'):
            if r.from_cache:
                self.log.info("(from cache)")
        if r.status_code != 200:
            throw_request_err(r)

        return r.json()

def throw_request_err(r):
    msg = u"Error getting {}: ({})".format(r.url, r.status_code)
    if r.status_code == 404:
        raise RequestException404(msg)
    elif r.status_code == 500:
        raise RequestException500(msg)
    else:
        raise RequestException(msg)


class RequestException404(RequestException):
    pass

class RequestException500(RequestException):
    pass