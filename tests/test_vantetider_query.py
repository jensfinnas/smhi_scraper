# encoding: utf-8

from vantetider.api import Vantetider
import pytest

api = Vantetider()

def _test_not_implemented_dim():
    with pytest.raises(NotImplementedError):
        api.get("PrimarvardBesok").query(select_unit=["Foo"]).next()


def test_query():
    res = api.get("PrimarvardTelefon").query(select_region=["Blekinge"])
    dim = res.next().get("select_unit")
    import pdb;pdb.set_trace()
    assert len(dim.list()) == 19