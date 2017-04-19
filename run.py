# encoding: utf-8

from smhi_scraper.api import SMHI
from vantetider.api import Vantetider



api = Vantetider()
dataset = api.get("PrimarvardTelefon")
res = dataset.query(select_region="Norrbotten",
    select_year=["2016","2015"],
    select_period=[u"Januari",u"Februari",u"Mars"])

df = res.to_dataframe(content="label")
print df.head()
import pdb;pdb.set_trace()
