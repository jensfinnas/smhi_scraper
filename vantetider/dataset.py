# encoding: utf-8
from statscraper.dataset import Dataset 
from vantetider.common import Common
from vantetider.dimension import Dimension
from vantetider.category import Category

from bs4 import BeautifulSoup

class Dataset(Dataset, Common):
    def __init__(self, id):
        self._id = id
        self._label = None
        self.url = self.base_url + "Sveriges/" + id 
        self._html = None
        self._dimensions = None

        # For storing requests to json api
        self._json_cache = {}

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value
    

    @property
    def html(self):
        if self._html is None:
            self._html = self.get_html(self.url)
        return self._html

    @property
    def soup(self):
        return BeautifulSoup(self.html, 'html.parser')
    
    #def get(self, id_or_label):
    #    if id_or_label == 


    def _list(self):
        """
        Primärvård:
        - #select_region => region (region/landsting)
        - #select_unit => unit (vårdcentral)
        - publicprivate

        Primärvård - Telefontillgänglighet:
        - phonesystem
        """
        if self._dimensions is None:
            self._dimensions = []
            try:
                form = [x for x in self.soup.find_all("form") 
                    if "/Kontaktkort/" in x.get("action")][0]
            except IndexError:
                # http://www.vantetider.se/Kontaktkort/Sveriges/Aterbesok
                # does not have form element
                form = self.soup.find("div", {"class": "container_12 filter_section specialised_operation"})

            # 1. Get select elements (dropdowns)
            select_elems = form.find_all("select")
            for elem in select_elems:
                dim_id = elem.get("name")
                dim = Dimension(dim_id)

                option_elems = elem.find_all("option")
                # 1.1 Regular, html rendered select menu
                if len(option_elems) > 1: 
                    for option_elem in option_elems:
                        cat_id = option_elem.get("value")
                        cat_label = option_elem.text.strip()
                        if cat_id is None:
                            cat_id = option_elem.text.strip()

                        cat = Category(cat_id, label=cat_label)
                        dim.add_category(cat)
                # 1.2 Dropdown that is populated with ajax query
                else:
                    # The json api takes get request with three parameters:
                    # region, year and period (eg. "Januari", "Hösten")
                    try:
                        json_api = JSON_API_ENDPOINTS[self.id]
                    except KeyError:
                        msg = "json_api settings missing for '{}' on {}".format(dim_id, self.url)
                        raise NotImplementedError(msg)

                    # 1.2.1 Query with the preselected values for year and period
                    query = {
                        "select_year": form.select_one("[id=select_year]").select_one("[selected]").text.strip(),
                        "select_period": form.select_one("[id=select_period]").select_one("[selected]").text.strip()
                    }
                    
                    json_data = {}
                    # 1.2.2 Query all regions in
                    for elem_region in form.select_one("[id=select_region]").find_all("option"):
                        query["select_region"] = elem_region.get("value")

                        url = self.json_base_url + json_api["url"].format(**query)
                        resp = self.get_json(url)
                            
                        for key, values in resp.iteritems():
                            if key not in json_data:
                                json_data[key] = []
                            json_data[key] += values

                    json_key =  json_api["dimensions"][dim_id]

                    # 1.2.3 Parse response
                    for _cat in json_data[json_key]:
                        if isinstance(_cat, dict):
                            # Slightly hard-coded, the only dimension
                            # in the json api that contains more than
                            # label/id is the unit 
                            # TODO: Here we could add more metadata about
                            # the category (in practice, the unit)
                            cat = Category(_cat["id"],
                                label=_cat["Vardgivarnamn"])
                        else:
                            cat = Category(_cat)
                        dim.add_category(cat)

                self._dimensions.append(dim)

                        
            # 2. Get checkboxes (gender, ownership)
            checkbox_ids = [x.get("id") for x in form.find_all("input", {"type": "checkbox"})]
            checkbox_labels = [x.text for x in form.find_all("label", {"class": "checkbox"})]

            # We have to map this manually as the html structure is unclear
            checkbox_to_dimension = {
                'public': "ownership",
                'private': "ownership",
                'male': 'gender',
                'female': 'gender',
            }
            checkbox_dims = {}
            for cat_id, cat_label in zip(checkbox_ids, checkbox_labels):
                cat = Category(cat_id, label=cat_label)
                dim_id = checkbox_to_dimension[cat_id]
                
                if dim_id not in checkbox_dims:
                    checkbox_dims[dim_id] = Dimension(dim_id)

                checkbox_dims[dim_id].add_category(cat)

            self._dimensions += checkbox_dims.values()
            
            # 3. Get radio buttons
            radio_elems = [x for x in form.find_all("input", {"type": "radio"})]
            dim_ids = get_unique([x.get("name") for x in radio_elems])
            for dim_id in dim_ids:
                dim = Dimension(dim_id)
                cat_ids = [x.get("value") for x in radio_elems]
                cat_labels = [x.get("id") for x in radio_elems]
                for id_, label in zip(cat_ids, cat_labels):
                    cat = Category(id_, label=label)
                    dim.add_category(cat)

                self._dimensions.append(dim)

        return self._dimensions

    def get_json_api_url(self, url_format, ):
        base_url = "http://www.vantetider.se/api/Ajax/"


def get_unique(l):
    """ Get unique values from list
        Placed outside the class beacuse `list` conflicts our internal 
        method with the same name.
    """
    return list(set(l))

JSON_API_ENDPOINTS = {
    "PrimarvardTelefon": {
        "url": u"GetUnitsByLandstingAndMatningPrimarTelefon/{select_region}/{select_period}%20{select_year}",
        "dimensions": {
            "select_unit": "Units",
            "select_phonesystem_type": "Telefonisystem",
        }
    },
    "Overbelaggning": {
        "url": u"GetUnitsByLandstingAndMatning/{select_region}/{select_period}%20{select_year}/0",
        "dimensions": {
            "select_unit": "Units",
        }
    },
    "PrimarvardBesok": {
        "url": u"GetUnitsByLandstingAndMatningPrimarBesok/{select_region}/{select_period}%20{select_year}",
        "dimensions": {
            "select_number_of_doctors": "Lakare",
            "select_booking_type":"Tidbok",
            "select_unit":"Units",
        }
    }
}
