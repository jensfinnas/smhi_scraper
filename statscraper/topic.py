
from statscraper.api import Api

class Topic(Api):
    @property
    def id(self):
        raise NotImplementedError("This property must be implemented")
    
