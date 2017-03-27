# encoding: utf-8
import pandas as pd

class ResultSet(object):
    """docstring for ResultSet"""
    def __init__(self, dictlist):
        self.data = dictlist

    def to_dataframe(self):
        return pd.DataFrame(self.data)
