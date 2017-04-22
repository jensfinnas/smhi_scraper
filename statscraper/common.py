# encoding
""" Common methods and properties shared by several
    classes
"""
from settings import BASE_URL

class Common(object):
    @property
    def base_url(self):
        return BASE_URL


class Item(object):
    """ Common methods and properties for Datasets,
        Dimensions and Categories.
        TODO: Come up with better name.
    """
    _items = None
    _items_by_label = None
    _id = None
    _label = None

    def __init__(self, id, label=None):
        self._id = id
        self._label = label 

    @property
    def id(self):
        if self._id is None:
            raise NotImplementedError("This item must have an id")
        return self._id


    @property
    def label(self):
        if self._label == None:
            return self.id
        else:
            return self._label
    
    
    @property
    def items(self):
        if self._items is None:
            raise NotImplementedError("You must define an items property for every item")
        return self._items

    @property
    def items_by_label(self):
        """ Returns a  dict of items with labels as key
        """
        if self._items_by_label is None:
            cat_labels = [x.label for x in self.items.values()]
            self._items_by_label = dict(zip(cat_labels, self.items.values()))
        
        return self._items_by_label


    def list(self):
        """ Get a list of all items
        """
        return self.items.values()


    def get(self, id_or_label):
        """ Get a subitem by id or label
        """
        try:
            return self.items[id_or_label]
        except KeyError:
            try:
                return self.items_by_label[id_or_label]
            except:
                msg = u"'{}' is not a valid id or key for {}".format(id_or_label, self.id)
                raise KeyError(msg)

    def add_item(self, id, item):
        """ Add subitem
        """
        self._items[id] = item

    @property
    def log(self):
        if not hasattr(self, "_logger"):
            self._logger = PrintLogger() 
        return self._logger

    def __repr__(self):
        return "<{}: {}>".format(type(self).__name__, self.label.encode("utf-8"))

class SilentLogger():
    """ Empyt "fake" logger
    """

    def log(self, msg, *args, **kwargs):
        pass

    def debug(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def warning(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass

    def critical(self, msg, *args, **kwargs):
        pass

class PrintLogger():
    """ Empyt "fake" logger
    """

    def log(self, msg, *args, **kwargs):
        print msg

    def debug(self, msg, *args, **kwargs):
        print msg

    def info(self, msg, *args, **kwargs):
        print msg

    def warning(self, msg, *args, **kwargs):
        print msg

    def error(self, msg, *args, **kwargs):
        print msg

    def critical(self, msg, *args, **kwargs):
        print msg