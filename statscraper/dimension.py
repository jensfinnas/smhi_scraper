# encoding: utf-8
from statscraper.common import Item

class Dimension(Item):
    def __init__(self, id, label=None, *args, **kwargs):
        self._id = id
        self._label = label


    @property
    def categories(self):
        """ Synonyme to `.list()`
        """
        return self.list()

    def category(self):
        """ Synonyme to `.get()
        """
        return self.get
    