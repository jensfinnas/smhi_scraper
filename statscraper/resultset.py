# encoding: utf-8
import pandas as pd

class ResultSet(object):
    """docstring for ResultSet"""
    def __init__(self, dictlist, dataset):
        self._data = dictlist
        self.dataset = dataset

    def data(self, content="index"):
        if content == "index":
            return self._data
        elif content == "label":
            data = []
            for _row in self._data:
                row = {}
                for dim_id, cat_id in _row.iteritems():
                    if dim_id == "value":
                        row["value"] = cat_id
                    else:
                        dim = self.dataset.dimension(dim_id)
                        try:
                            cat = dim.get(cat_id)
                        except:
                            import pdb;pdb.set_trace()
                        row[dim.label] = cat.label
                data.append(row)

            return data

    def to_dataframe(self, content="index"):
        data = self.data(content=content)
        return pd.DataFrame(data)
