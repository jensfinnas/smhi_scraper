# encoding: utf-8

from vantetider.api import Vantetider
from vantetider.dataset import Dataset

def test_list():
    api = Vantetider()
    datasets = api.list()
    assert len(datasets) == 9
    for dataset in datasets:
        assert isinstance(dataset, Dataset)
