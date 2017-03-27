# encoding: utf-8

from smhi_scraper.api import SMHI
from statscraper.dataset import Dataset

def test_list_datasets():
    api = SMHI()
    datasets = api.list()
    assert isinstance(datasets, list)
    assert isinstance(datasets[0], Dataset)
    assert len(datasets) > 0

def test_that_datasets_have_id():
    api = SMHI()
    datasets = api.list()
    for dataset in datasets:
        assert(dataset.id)


def test_get_dataset():
    api = SMHI()
    datasets = api.list()
    ds_by_id = api.get(datasets[0].id)
    ds_by_label = api.get(datasets[0].label)

    assert(isinstance(ds_by_id, Dataset))
    assert(isinstance(ds_by_label, Dataset))
