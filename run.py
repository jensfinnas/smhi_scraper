# encoding: utf-8

from smhi_scraper.api import SMHI
from vantetider.api import Vantetider

api = Vantetider()

"""
for dataset in api.list():
    print dataset.id, dataset.label
    for dim in dataset.list():
        dim.list()
"""

#dataset = api.get("PrimarvardBesok")
#for dataset in api.list():
#    if dataset.id == "Aterbesok":
#        continue

dataset = api.get("Overbelaggning")
for dataset in api.list():
    for dim in dataset.list():
        print "*****"
        print dim.id
        for cat in dim.list():
            print "* ",cat.id, cat.label 
