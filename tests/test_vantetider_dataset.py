# encoding: utf-8
from vantetider.dataset import Dataset
from vantetider.dimension import Dimension
from vantetider.category import Category
from vantetider.api import Vantetider

def is_string(s):
    return isinstance(s, unicode) or isinstance(s, str)

def test_complete_iteration():
    api = Vantetider()
    for dataset in api.list():
        assert isinstance(dataset, Dataset)
        assert is_string(dataset.id)

        try:
            for dim in dataset.list():
                assert isinstance(dim, Dimension)
                assert dim.id is not None
                for cat in dim.list():
                    assert isinstance(cat, Category)
                    assert cat.id is not None
                    assert is_string(cat.label)
        except NotImplementedError:
            pass
