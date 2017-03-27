# encoding: utf-8
from statscraper.common import Common, Surfer

class Api(Common, Surfer):
    def list(self):
        raise NotImplementedError("This metod is required")
                

