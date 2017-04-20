# encoding: utf-8
from statscraper.common import Common, Item

class Category(Item, Common):
    """Represents a category under a dimension"""
    def list(self):
        raise NotImplementedError("Category does not have a list method.")