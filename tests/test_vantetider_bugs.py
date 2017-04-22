# encoding: utf-8

def test_odd_encoding():
    url = "http://www.vantetider.se/Kontaktkort/Uppsalas/PrimarvardBesok"
    payload1 = {u'select_period': u'Våren', u'select_booking_type': u'-1', u'select_unit': u'-1', u'checkbox_male': u'male', u'checkbox_regi_public': u'public', u'select_year': u'2016', u'select_number_of_doctors': u'-1', u'select_region': u'12', u'checkbox_regi_private': u'private', u'checkbox_female': u'female'}
    payload2 = {u'select_period': u'Hösten', u'select_booking_type': u'-1', u'select_unit': u'-1', u'checkbox_male': u'male', u'checkbox_regi_public': u'public', u'select_year': u'2016', u'select_number_of_doctors': u'-1', u'select_region': u'12', u'checkbox_regi_private': u'private', u'checkbox_female': u'female'}
    res1 = dataset._parse_result_page(url, payload1)
    res2 = dataset._parse_result_page(url, payload2)
    assert res1[0]["select_unit"] == res2[0]["select_unit"]
