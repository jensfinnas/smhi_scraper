# encoding: utf-8

from vantetider.dataset import Datatable
import os

DATA_DIR = "tests/data/vantetider/datatable"

TABLE_WITH_TABS = os.path.join(DATA_DIR, "BUP.html")
TABLE_WITH_H_SCROLL = os.path.join(DATA_DIR, "BUP.html")
TABLE_WITHOUT_SCROLL = os.path.join(DATA_DIR, "PrimarvardBesok.html")
TABLE_WITH_V_SCROLL = os.path.join(DATA_DIR, "PrimarvardTelefon.html")



def open_file(file_path):
    with open(file_path) as f:
        return f.read()

def test_init():
    table = Datatable(open_file(TABLE_WITH_TABS))
    assert len(table.data) == 572

    table = Datatable(open_file(TABLE_WITH_V_SCROLL))
    assert len(table.data) == 28 * 3

    table = Datatable(open_file(TABLE_WITHOUT_SCROLL))
    assert len(table.data) == 28 * 3

def test_has_tabs():
    html = open_file(TABLE_WITH_TABS)
    table = Datatable(html)
    assert table.has_tabs

    for file_path in [TABLE_WITHOUT_SCROLL, TABLE_WITH_V_SCROLL]:
        html = open_file(file_path)
        table = Datatable(html)
        assert not table.has_tabs

def test_has_horizontal_scroll():
    table = Datatable(open_file(TABLE_WITH_H_SCROLL))
    assert table.has_horizontal_scroll

    table = Datatable(open_file(TABLE_WITH_V_SCROLL))
    assert not table.has_horizontal_scroll

    table = Datatable(open_file(TABLE_WITHOUT_SCROLL))
    assert not table.has_horizontal_scroll

def test_measures():
    table = Datatable(open_file(TABLE_WITH_H_SCROLL))
    assert table.measures == [
        u"Första bedömning",
        u"Påbörjad fördjupad utredning/behandling"]

    table = Datatable(open_file(TABLE_WITHOUT_SCROLL))
    assert table.measures == [
        u"Måluppfyllelse vårdgarantin (Andel Besök inom 7 dagar)",
        u"Antal Besök inom 7 dagar",
        u"Totalt antal besök",
    ]

    # Order gets mixed up here, but that shouldn't be an issue
    table = Datatable(open_file(TABLE_WITH_V_SCROLL))
    measures = [
        u"Måluppfyllelse vårdgarantin (Andel besvarade samtal samma dag)",
        u"Antal besvarade samtal",
        u"Totalt antal samtal",
    ]
    for measure in table.measures:
        assert measure in measures



    