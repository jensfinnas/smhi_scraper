# encoding: utf-8

from statscraper.dimension import Dimension
from vantetider.common import Common, RequestException500
from vantetider.json_api_endpoints import AJAX_API_ENDPOINTS, AJAX_API_URL
from vantetider.category import Category
from vantetider.utils import (is_list, default_list_dict, get_unique,
    get_option_value, get_elem_type, is_string)
from itertools import product
import csvkit as csv
import os


class Dimension(Dimension, Common):
    def __init__(self, id_, dataset, label=None, element=None):
        """
            :param :
            :param element: The html element

        """
        self._id = id_
        self.dataset = dataset
        self._label = label
        self.elem = element
        self._elem_type = None
        self._items = None
        self._default_value = None


    @property
    def items(self):
        """
        """
        if self._items is None:
            categories = {}
            if self.elem != None:
                categories = self._categories_from_html()
            
            """
            if self.id in AJAX_API_ENDPOINTS[self.dataset.id]:
                categories.update(self._categories_from_file())
            """

            assert len(categories.keys()) > 0

            self._items = categories

        return self._items

    def add_category(self, cat):
        if self._items is None:
            self._items = {}

        self._items[cat.id] = cat

    @property
    def default_value(self):
        """ The default category when making a query
        """
        if self._default_value is None:
            if self.elem_type == "select":
                try:
                    # Get option marked "selected"
                    def_value = get_option_value(self.elem.select_one("[selected]"))
                except AttributeError:
                    # ...or if that one doesen't exist get the first option
                    def_value = get_option_value(self.elem.select_one("option"))

            elif self.elem_type == "checkbox":
                def_value = self.elem.get("value")
            
            elif self.elem_type == "radio":
                def_value = [x for x in self.elem if x.has_attr("checked")][0].get("value")

            self._default_value = def_value

            assert def_value is not None

        return self._default_value


    @property
    def elem_type(self):
        """ :returns: "select"|"radio"|"checkbox"
        """
        if self._elem_type is None:
            self._elem_type = get_elem_type(self.elem)
        
        return self._elem_type
    
    def generate_dictionary(self):
        dataset_id = self.dataset.id
        dim_id = self.id
        if dim_id in AJAX_API_ENDPOINTS[dataset_id]:
            opts = AJAX_API_ENDPOINTS[dataset_id][dim_id]
            categories = self._categories_from_ajax_api()
            file_dir = os.path.join("vantetider/data", dataset_id)
            file_path = os.path.join(file_dir, dim_id + ".csv")
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            with open(file_path,'w') as f:
                writer = csv.writer(f)
                headers = ["id","label"]
                if "attributes" in opts:
                    headers += [x[1] for x in opts["attributes"]]

                writer.writerow(headers)
                for cat in categories.values():
                    row = [ getattr(cat, x) for x in headers ]
                    writer.writerow(row)

    def _categories_from_file(self):
        """ Get categories from cached file
        """
        categories = {}
        file_path = os.path.join("vantetider/data", self.dataset.id, self.id + ".csv")
        with open(file_path) as f:
            for row in csv.DictReader(f, encoding="utf-8"):
                cat = Category(row["id"], label=row["label"])
                for attr, value in row.iteritems():
                    if attr not in ["id","label"]:
                        setattr(cat, attr, value)

                categories[cat.id] = cat

        return categories


    def _categories_from_html(self):
        """ Parse categories from html structure
            Appends categories on the run
        """
        categories = {}
        if self.elem_type == "select":
            for option_elem in self.elem.find_all("option"):
                cat_id = get_option_value(option_elem)
                cat_label = option_elem.text.strip()
                cat = Category(cat_id, label=cat_label)
                categories[cat_id] = cat

        elif self.elem_type == "checkbox":
            # A checkbox dimension as only one value
            categories[True] = Category(True)
            categories[False] = Category(False)

        elif self.elem_type == "radio":
            cat_ids = [x.get("value").strip() for x in self.elem]
            cat_labels = [x.get("id") for x in self.elem]
            for cat_id, label in zip(cat_ids, cat_labels):
                cat = Category(cat_id, label=label)
                categories[cat_id] = cat
        else:
            raise ValueError("Unknown html element")

        assert len(categories.values()) > 0

        return categories

    def _categories_from_ajax_api(self, **kwargs):
        dataset = self.dataset
        opts = AJAX_API_ENDPOINTS[dataset.id][self.id]
        format_params = {}
        categories = {}

        if "url" in opts:
            for dim_id in opts["url_requires"]:
                try:
                    format_params[dim_id] = kwargs[dim_id].id
                except AttributeError:
                    format_params[dim_id] = kwargs[dim_id]

            url = AJAX_API_URL + opts["url"].format(**format_params)
            try:
                resp = self.get_json(url)
            except RequestException500:
                # Catch combinations of categories that don't exist
                self.log.warning("{} returned 500.".format(url))
                pass

            # Eg. [{u'AntalLakare': None, u'Vardgivarkod': u'26010', u'UnitTypeNumber': 3, u'Vardgivarnamn': u'Visby lasarett', u'Disabled': False, u'UnitType': u'Specialiserad v\xe5rd', u'Telefonisystem': None, u'Regi': u'Offentlig', u'LandstingsKod': 26, u'HSAId': u'', u'Tidbok': None, u'id': 2929}]
            for item in resp[opts["key"]]:
                if isinstance(item, dict):
                    cat = Category(unicode(item["id"]))
                    for (their_attr, our_attr) in opts["attributes"]:
                        value = item[their_attr]
                        if is_string(value):
                            value = value.strip()
                        else:
                            value = unicode(value)
                        setattr(cat, our_attr, value)
                else:
                    if is_string(item):
                        item = item.strip()
                    cat = Category(item)

                categories[cat.id] = cat
        else:
            raise NotImplementedError()

        return categories
 
    def __categories_from_ajax_api(self):
        """ TO BE REMOVED
            Fetches categories from ajax API based on settings
            in json_api_endpoints.py.
            Appends categories on the run with .add_category()
        """
        dataset = self.dataset
        opts = AJAX_API_ENDPOINTS[dataset.id][self.id]
        categories = {}

        if "url" in opts:
            # Make url
            format_params = {}
            #for dim_id in opts["url_requires"]:
            #    value = dataset.get(dim_id).default_value
            #    format_params[dim_id] = value
            
            urls = []
            dims_to_iter = opts["url_requires"]
            if not isinstance(dims_to_iter, list):
                dims_to_iter = [dims_to_iter]

            cats_to_iter = [] 
            for dim_id in dims_to_iter:
                dim = dataset.get(dim_id)
                cats_to_iter.append([cat.id for cat in dim.list()])


            category_combos = product(*cats_to_iter)
              
            for cat_combo in category_combos:

                for i, _dim_id in enumerate(dims_to_iter):

                    format_params[_dim_id] = cat_combo[i]
                      
                url = AJAX_API_URL + opts["url"].format(**format_params)
                urls.append(url)

            json_data = default_list_dict()
            for url in urls:
                try:
                    resp = self.get_json(url)
                except RequestException500:
                    # Catch combinations of categories that don't exist
                    self.log.warning("{} returned 500.".format(url))
                    pass

                for key, value in resp.iteritems():
                    if is_list(value):
                        json_data[key] += value
                    else:
                        json_data[key] = value


            # Eg. [{u'AntalLakare': None, u'Vardgivarkod': u'26010', u'UnitTypeNumber': 3, u'Vardgivarnamn': u'Visby lasarett', u'Disabled': False, u'UnitType': u'Specialiserad v\xe5rd', u'Telefonisystem': None, u'Regi': u'Offentlig', u'LandstingsKod': 26, u'HSAId': u'', u'Tidbok': None, u'id': 2929}]
            for item in json_data[opts["key"]]:
                if isinstance(item, dict):
                    cat = Category(item["id"])
                    for (their_attr, our_attr) in opts["attributes"]:
                        value = item[their_attr]
                        if is_string(value):
                            value = value.strip()
                        setattr(cat, our_attr, value)
                else:
                    if is_string(item):
                        item = item.strip()
                    cat = Category(item)

                categories[cat.id] = cat



        else:
            from_dim_id, attr = opts["from"].split("|")
            from_dim = self.dataset.get(from_dim_id)
            values = []

            for cat in from_dim.categories:
                try:
                    value = getattr(cat, attr)
                    if value not in values and value is not None:
                        values.append(value)
                except AttributeError:
                    pass

            for value in values:
                if value == "" or value == None:
                    continue
                cat = Category(value)
                categories[cat.id] = cat

        return categories



class AjaxDimension(Dimension):
    _items = {}
    
    def get(self, id_or_label, **kwargs):
        try:
            return super(Dimension,self).get(id_or_label)
        except KeyError:
            categories = self._categories_from_ajax_api(**kwargs)
            self._items.update(categories)
            return super(Dimension,self).get(id_or_label)



