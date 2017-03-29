""" encoding: utf-8
"""
from smhi_scraper.api import SMHI
from smhi_scraper.category import Category

def test_dimension():
    api = SMHI()
    dataset = api.list()[0]
    dims = dataset.dimensions
    for dim in dataset.dimensions:
        assert isinstance(dim.categories, list)
        assert isinstance(dim.list(), list)

        for category in dim.categories:
            assert category.id
            assert isinstance(category, Category)
