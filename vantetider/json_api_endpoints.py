# encoding:utf-8

UNIT_ATTRS = [
    # ( their id, our id)
    ( "AntalLakare", "number_of_doctors" ),
    ( "LandstingsKod", "landsting_id" ),
    ( "Regi", "ownership" ),
    ( "Telefonisystem", "phonesystem"),
    ( "Tidbok", "booking_type"),
    ( "UnitType", "unit_type" ),
    ( "UnitTypeNumber", "unit_type_number" ),
    ( "Vardgivarkod", "code" ),
    ( "Vardgivarnamn", "_label" ),
]

SERVICE_ATTRS = [
    ( "Dtype", "dtype" ),
    ( "Name", "_label" ),
    ( "Parent_id", "parent_id" ),
    ( "Servicecode", "code" ),
    ( "Uppdaterad", "updated" ),

]

AJAX_API_URL = u"http://www.vantetider.se/api/Ajax/"
AJAX_API_ENDPOINTS = {
    "VantatKortareAn60Dagar": {},
    "Aterbesok": {},
    "BUPdetalj": {},
    "BUP": {},
    "Overbelaggning":{
        "select_months": {
            "url": u"GetOverbelaggningVisitMonths/{select_year}}/",
            "url_requires": ["select_year"],
            "iterates": "select_year",
            "key": "Names",
        },
        "select_unit": {
            "url": u"GetUnitsByLandstingAndMatning/{select_region}/{select_period}%20{select_year}/0",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Units",
            "attributes": UNIT_ATTRS,
        },
    },
    "PrimarvardTelefon": {
        "select_unit": {
            "url": u"GetUnitsByLandstingAndMatningPrimarTelefon/{select_region}/{select_period}%20{select_year}",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Units",
            "attributes": UNIT_ATTRS,
        },
        "select_phonesystem_type": {
            "from": "select_unit|phonesystem"
        },
        "select_year": {
            "url": "GetTelefonMatningar/{select_region}",
            "url_requires": ["select_region"],
            "iterates": "select_region",
            "key": "Years",
        },
        "select_period": {
            "url": "GetTelefonMatningar/{select_region}",
            "url_requires": ["select_region"],
            "iterates": "select_region",
            "key": "Names",
        },
    },
    "PrimarvardBesok": {
        "select_unit": {
            "url": u"GetUnitsByLandstingAndMatningPrimarBesok/{select_region}/{select_period}%20{select_year}",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Units",
            "attributes": UNIT_ATTRS,
        },
        "select_number_of_doctors": {
            "from": "select_unit|number_of_doctors",
        },
        "select_booking_type": {
            "from": "select_unit|booking_type",
        },
        "select_year": {
            "url": "GetTelefonMatningar/{select_region}",
            "url_requires": ["select_region"],
            "iterates": "select_region",
            "key": "Years",
        },
        "select_period": {
            "url": "GetTelefonMatningar/{select_region}",
            "url_requires": ["select_region"],
            "iterates": "select_region",
            "key": "Names",
        },

    },
    "SpecialiseradBesok": {
        "select_period": {
            "url": u"GetSpecializedVisitMonths/{select_year}/",
            "url_requires": [ "select_year" ],
            "iterates": "select_year",
            "key": "Months",
        },
        "select_unit": {
            "url": u"GetUnitsByLandstingAndServiceAndMatning/{select_region}/{select_period}%20{select_year}/0",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Units",
            "attributes": UNIT_ATTRS,
        },
        "select_services": {
            "url": u"GetServicesByUnitSpecialiseradBesokMatning/{select_region}/{select_period}%20{select_year}/0",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Services",
            "attributes": SERVICE_ATTRS,
        },
    },
    "SpecialiseradOperation": {
        "select_period": {
            "url": u"GetSpecializedOperationMonths/{select_year}/",
            "url_requires": [ "select_year" ],
            "iterates": "select_year",
            "key": "Months",
        },
        "select_unit": {
            "url": u"GetUnitsByLandstingAndServiceAndMatning/{select_region}/{select_period}%20{select_year}/2",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Units",
            "attributes": UNIT_ATTRS,
        },
        "select_services": {
            "url": u"GetServicesByUnitSpecialiseradBesokMatning/{select_region}/{select_period}%20{select_year}/0",
            "url_requires": [ "select_region", "select_period", "select_year" ],
            "iterates": "select_region",
            "key": "Services",
            "attributes": SERVICE_ATTRS,
        },
    }
}

