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

        for dim in dataset.list():
            assert isinstance(dim, Dimension)
            assert dim.id is not None
            if dim.label is not None:
                assert is_string(dim.label)

            categories = dim.list()
            if "checkbox" not in dim.id:
                assert len(categories) > 0 

            for cat in dim.list():
                assert isinstance(cat, Category)
                assert cat.id is not None, u", in {}".format(dim.id)
                if cat.label is not None:
                    assert is_string(cat.label)

