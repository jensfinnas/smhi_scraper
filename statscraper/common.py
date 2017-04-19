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

    @property
    def log(self):
        if not hasattr(self, "_logger"):
            self._logger = PrintLogger() 
        return self._logger

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