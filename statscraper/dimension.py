# encoding: utf-8
from statscraper.common import Surfer

class Dimension(Surfer):
    def __init__(self, id, label=None, *args, **kwargs):
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
            return None

    @property
    def categories(self):
        """ Synonyme to `.list()`
        """
        return self.list()

    def category(self):
        """ Synonyme to `.get()
        """
        return self.get
    