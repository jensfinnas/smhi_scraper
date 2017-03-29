# encoding: utf-8

from statscraper.dimension import Dimension
from vantetider.common import Common

class Dimension(Dimension, Common):
    pass
    def __init__(self, id_):
        self._id = id_
        self._categories = []

    def list(self):
        return self._categories


    def add_category(self, category):
        if category not in self._categories:
            self._categories.append(category)

