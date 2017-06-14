# encoding: utf-8

from vantetider.api import Vantetider

LANDSTING = ["Blekinge",u"Dalarna",u"Gotland",u"Gävleborg",u"Halland",u"Jämtland Härjedalen",u"Jönköping",u"Kalmar",u"Kronoberg",u"Norrbotten",u"Skåne",u"Stockholm",u"Sörmland",u"Uppsala",u"Värmland",u"Västerbotten",u"Västernorrland",u"Västmanland",u"Västra Götaland",u"Örebro",u"Östergötland",]


api = Vantetider()
#api.get("SpecialiseradOperation").get("select_unit").generate_dictionary()

#exit()
def parse_results(res):
    df = None 
    i = 1
    for res_batch in res:
        if df is None:
            df = res_batch.to_dataframe(content="index")
        else:
            _df = res_batch.to_dataframe(content="index")
            print "batch {}, {} rows (total now {} rows)".format(i, _df.shape[0], df.shape[0])
            df = df.append(_df)
        i += 1

    return df



datasets = ["SpecialiseradBesok"]#, "SpecialiseradOperation",  ]
for dataset_id in datasets:
    dataset = api.get(dataset_id)
    params = {
        "select_region": LANDSTING,
        "select_year": [x.id for x in dataset.get("select_year").list()],
    #    "select_services": [x.id for x in dataset.get("select_services").list()],
    }

    if "select_period" in [x.id for x in dataset.dimensions]:
        params["select_period"] = [x.id for x in dataset.get("select_period").list()]

    res = dataset.query(**params)
    df = parse_results(res)
    FOLDER = u"../dagenssamhalle-notebooks/vårdköer/data/"
    df.to_csv(FOLDER + dataset_id + "_by_unit.csv", encoding="utf-8")



