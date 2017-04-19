# encoding: utf-8
from statscraper.common import Common

class Category(Common):
    """Represents a category under a dimension"""
    def __init__(self, id, label=None):
        self._id = id
        self._label = label

    @property
    def id(self):
        """ Get id of dataset
        """
        try:
            return self._id
        except:
            raise NotImplementedError("This property must be implemented")

    @property
    def label(self):
        try:
            return self._label
        except AttributeError:
            return self.id

