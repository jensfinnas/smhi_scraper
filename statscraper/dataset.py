# encoding: utf-8
from statscraper.common import Item
from statscraper.resultset import ResultSet
from inspect import isgeneratorfunction

class Dataset(Item):
    """Represents a dataset.
        The enrty point for queries and downloads.
    """
    
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

        for data_batch in self._query(**kwargs):
            resultset = ResultSet(data_batch, self)
            yield resultset
        
        
        # TODO: Apply metadata from Dataset
        # TODO: Validate results
        


