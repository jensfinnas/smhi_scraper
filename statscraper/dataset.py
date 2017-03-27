# encoding: utf-8
from statscraper.common import Surfer
from statscraper.resultset import ResultSet

class Dataset(Surfer):
    """Represents a dataset.
        The enrty point for queries and downloads.
    """

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
    def dimensions(self):
        """ Synonyme to .list()
        """
        return self.list()

    def dimension(self, id_or_label):
        """ Synonyme to .get()
        """
        return self.get(id_or_label)

    def query(self, **kwargs):
        """ Perform a query in a dataset.
            The person building a scraper

            :returns: a resultset
        """
        # TODO (?): Validate query
        data = self._query(**kwargs) # Returns a list of dicts (or similar)
        resultset = ResultSet(data)
        # TODO: Apply metadata from Dataset
        # TODO: Validate results
        return resultset


