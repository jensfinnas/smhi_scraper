# encoding: utf-8

from statscraper.dimension import Dimension
from vantetider.common import Common
from vantetider.json_api_endpoints import AJAX_API_ENDPOINTS, AJAX_API_URL
from vantetider.category import Category
from vantetider.utils import is_list, default_list_dict, get_unique

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
        self._items = {}
        self._default_value = None
        # For storing data from ajax api
        self._has_queried_ajax_api = False
        if element is not None:
            self._categories_from_html()


    @property
    def items(self):
        """
        """
        if self._items is None:
            categories = {}
            if self.id in AJAX_API_ENDPOINTS[self.dataset.id]:
                if not self._has_queried_ajax_api:
                    self._categories_from_ajax_api()

            if self.id == "select_period":
                self.log.info("Note that data for all periods may not be available for all regions. Eg. some landsting don't report monthly data, only spring/autumn.")
            
            self._items = categories

        return self._items

    def add_category(self, cat):
        self.items[cat.id] = cat

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
                import pdb;pdb.set_trace()

            self._default_value = def_value

            assert def_value is not None

        return self._default_value


    @property
    def elem_type(self):
        """ :returns: "select"|"radio"|"checkbox"
        """
        if self._elem_type is None:
            elem = self.elem

            if is_list(elem):
                if elem[0].get("type") == "radio":
                    self._elem_type = "radio"
                else:
                    raise ValueError(u"Unknown element type: {}".format(elem))
    
            elif elem.name == "select":
                self._elem_type = "select"
    
            elif elem.name == "input":
                self._elem_type = elem.get("type")
    
            else:
                raise ValueError(u"Unknown element type: {}".format(elem))
            
            # To be removed
            assert self._elem_type is not None
        
        return self._elem_type
    

    def _categories_from_html(self):
        """ Parse categories from html structure
            Appends categories on the run
        """
        if self.elem_type == "select":
            for option_elem in self.elem.find_all("option"):
                cat_id = get_option_value(option_elem)
                cat_label = option_elem.text.strip()
                cat = Category(cat_id, label=cat_label)
                self.add_category(cat)

        elif self.elem_type == "checkbox":
            # A checkbox dimension as only one value
            cat_id = self.elem.get("value")
            cat = Category(cat_id)
            self.add_category(cat)

        elif self.elem_type == "radio":
            cat_ids = [x.get("value") for x in self.elem]
            cat_labels = [x.get("id") for x in self.elem]
            for id_, label in zip(cat_ids, cat_labels):
                cat = Category(id_, label=label)
                self.add_category(cat)
        else:
            raise ValueError("Unknown html element")

        if len(self.list()) == 0:
            import pdb;pdb.set_trace()
        assert len(self.list()) > 0

    def _categories_from_ajax_api(self):
        """ Fetches categories from ajax API based on settings
            in json_api_endpoints.py.
            Appends categories on the run with .add_category()
        """
        dataset = self.dataset
        opts = AJAX_API_ENDPOINTS[dataset.id][self.id]
        if "url" in opts:
            # Make url
            format_params = {}
            for dim_id in opts["url_requires"]:
                value = dataset.get(dim_id).default_value
                format_params[dim_id] = value
            
            urls = []
            if "iterates" in opts:
                dim_id = opts["iterates"]
                dim = dataset.get(dim_id)

                for cat in dim.list():
                    format_params[dim_id] = cat.id
                    url = AJAX_API_URL + opts["url"].format(**format_params)
                    urls.append(url)
            else:
                url = AJAX_API_URL + opts["url"].format(**format_params)
                urls.append(url)

            json_data = default_list_dict()
            for url in urls:
                resp = self.get_json(url)

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
                        setattr(cat, our_attr, value)
                else:
                    cat = Category(item)

                self.add_category(cat)

            self._has_queried_ajax_api = True
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
                cat = Category(value)
                self.add_category(cat)

        

def get_option_value(elem):
    """ Get the value attribute, or if it doesn't exist the text 
        content.
        <option value="foo">bar</option> => "foo"
        <option>bar</option> => "bar"
        :param elem: a soup element
    """
    value = elem.get("value")
    if value is None:
        value = elem.text.strip()
    if value is None or value == "":
        msg = u"Error parsing value from {}.".format(elem)
        raise ValueError(msg)

    return value

"""
        # 1.2 Get periods and years from period api
        if dataset_id in PERIOD_API_ENDPOINTS:
            # Would like to do self.get("region") here, but .get() uses .list() now
            regions = [ x for x in self._dimensions 
                if x.id == "select_region" ][0].categories
            
            periods = default_list_dict()
            for region in regions:
                _periods = self._get_region_periods(region.id)
                for key, value in _periods.iteritems():
                    if is_list(value):
                        periods[key] += value
                        periods[key] = get_unique(periods[key]) 
                    else:
                        if periods[key] != value and periods[key]:
                            raise Exception("Unexpted result from period api, didn't expect {} to differ. ".format(key))
                        periods[key] = value
            
            dim_period = Dimension("select_period", label="Period")
            for period in periods["Names"]:
                cat = Category(period)
                dim_period.add_category(cat)
            
            dim_period.default_value = periods["LatestName"]
            self._dimensions.append(dim_period)

            dim_year = Dimension("select_year", label=u"År")
            for period in periods["Years"]:
                cat = Category(period)
                dim_year.add_category(cat)
            
            dim_year.default_value = periods["LatestYear"]
            self._dimensions.append(dim_year)
"""    