# encoding: utf-8

from smhi_scraper.api import SMHI

api = SMHI()

ds = api.get(u"Lufttemperatur medel, 1 gång per månad")
