# encoding: utf-8
from statscraper.common import Common, Item
from statscraper.dataset import Dataset

class Collection(Common, Item):
    """ A collection can contain either a number of other 
        collections or datasets.
    """

    def has_collections(self):
        """ Does the collection contain sub-collections?
        """
        try:
            return isinstance(self.list()[0], Collection)
        except IndexError:
            False

    def has_datasets(self):
        """ Does the collection contain datasets?
        """
        try:
            return isinstance(self.list()[0], Dataset)
        except IndexError:
            False

class Api(Collection):
    def __init__(self):
        pass