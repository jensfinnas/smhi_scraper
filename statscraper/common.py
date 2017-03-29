# encoding
""" Common methods and properties shared by several
    classes
"""
from settings import BASE_URL

class Common(object):
    @property
    def base_url(self):
        return BASE_URL


class Surfer(object):
    def list(self):
        return self._list()

    def _list(self):
        """ list a all entities
        """
        return []

    def get(self, id_or_label):
        """ Get an enitity by id or label
        """
        for item in self.list():
            if item.id == id_or_label:
                return item
            elif item.label == id_or_label:
                return item

        msg = u"'{}' is not a valid id or key".format(id_or_label)
        raise KeyError(msg)