# encoding: utf-8

from vantetider.api import Vantetider



api = Vantetider()
datasets = ["SpecialiseradBesok"]


for dataset_id in datasets:
    api.get(dataset_id).get("select_unit").generate_dictionary()

