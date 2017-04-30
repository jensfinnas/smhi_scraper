# encoding: utf-8
from statscraper.dataset import Dataset 
from vantetider.common import Common, RequestException404, RequestException500
from vantetider.dimension import Dimension
from vantetider.category import Category
from vantetider.utils import (parse_value, parse_text, parse_landsting,
    guess_measure_unit, get_unique, flatten, to_list,
    get_option_value, get_option_text, repeat)
from vantetider.json_api_endpoints import AJAX_API_ENDPOINTS

from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import product

import csvkit as csv
import os

class Dataset(Dataset, Common):
    def __init__(self, id):
        if id in ["Aterbesok", "VantatKortareAn60Dagar"]:
            # These datasets require calls to the app.vantetider.se api
            raise NotImplementedError()
        self._id = id
        self._label = None
        self.url_format = self.base_url + "{region}/" + id
        self.url = self.url_format.format(region="Sveriges") 

        self._html = None
        self._dimensions = None

        # For storing what periods are available to each region
        self._region_periods = {}

        if id not in AJAX_API_ENDPOINTS:
            msg = u"Config for {} missging in AJAX_API_ENDPOINTS."
            raise Exception(msg.format(id))



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
    
    @property
    def regions(self):
        """ Convinience method for getting regions
        """
        return self.get("select_region").categories


    @property
    def items(self):
        """
        Primärvård:
        - #select_region => region (region/landsting)
        - #select_unit => unit (vårdcentral)
        - publicprivate

        Primärvård - Telefontillgänglighet:
        - phonesystem
        """
        if self._items is None:
            dimensions = {}
            dataset_id = self.id
            try:
                form = [x for x in self.soup.find_all("form") 
                    if "/Kontaktkort/" in x.get("action")][0]
            except IndexError:
                # http://www.vantetider.se/Kontaktkort/Sveriges/Aterbesok
                # does not have form element
                form = self.soup.find("div", {"class": "container_12 filter_section specialised_operation"})
            self._form = form

            # 1. Get select elements (dropdowns)
            select_elems = form.find_all("select")
            for elem in select_elems:
                dim_id = elem.get("name")
                dim = Dimension(dim_id, self, element=elem)
                dimensions[dim_id] = dim
                        
            # 2. Get checkboxes (gender, ownership)
            checkbox_elems = [x for x in form.find_all("input", {"type": "checkbox"})]
            checkbox_labels = [x.text for x in form.find_all("label", {"class": "checkbox"})]
            for elem, label in zip(checkbox_elems, checkbox_labels):
                dim_id = elem.get("name")
                dim = Dimension(dim_id, self, label=label, element=elem)
                dimensions[dim_id] = dim

            # 3. Get radio buttons
            radio_elems = [x for x in form.find_all("input", {"type": "radio"})]
            dim_ids = get_unique([x.get("name") for x in radio_elems])

            for dim_id in dim_ids:
                elems = [x for x in radio_elems if x.get("name") == dim_id]
                dim = Dimension(dim_id, self, element=elems)
                dimensions[dim_id] = dim

            # 4. Add measure and measure key 
            datatable = Datatable(self.html)
            dim_measure = Dimension("measure", self, label="Nyckeltal")
            for measure in datatable.measures:
                dim_measure.add_category(Category(measure))


            dimensions["measure"] = dim_measure

            self._items = dimensions

        return self._items

    @property
    def time_dimensions(self):
        return [x for x in self.list() if x.id in ["select_year","select_period"]]
    
    def generate_dictionary(self):
        for dim in self.list():
            dim.generate_dictionary()
                        

    def _dimension_from_select(self, elem):
        """ Take a select html elemet and parse it a dimension
            :param elem: a soup element
            :returns (Dimension): a dimension (with categories)
        """
        dim_id = elem.get("name")
        dim = Dimension(dim_id)
        try:
            # Get option marked "selected"
            dim.default_value = get_option_value(elem.select_one("[selected]"))
        except AttributeError:
            # ...or if that one doesen't exist get the first option
            dim.default_value = get_option_value(elem.select_one("option"))

        dim.elem_type = "select"

        option_elems = elem.find_all("option")
        # 1.1 Regular, html rendered select menu
        if len(option_elems) > 1: 
            for option_elem in option_elems:
                cat_id = get_option_value(option_elem)
                cat_label = option_elem.text.strip()
                cat = Category(cat_id, label=cat_label)
                dim.add_category(cat)
        # 1.2 Dropdown that is populated with ajax query
        else:
            # The unit api takes GET request with three parameters:
            # region, year and period (eg. "Januari", "Hösten")
            try:
                unit_api = UNIT_API_ENDPOINTS[self.id]
            except KeyError:
                msg = "unit_api settings missing for '{}' on {}".format(dim_id, self.url)
                raise NotImplementedError(msg)

            # 1.2.1 Query with the preselected values for year and period
            query = {
                "select_year": self._form.select_one("[id=select_year]").select_one("[selected]").text.strip(),
                "select_period": self._form.select_one("[id=select_period]").select_one("[selected]").text.strip()
            }
            
            json_data = {}
            # 1.2.2 Query all regions in
            for elem_region in self._form.select_one("[id=select_region]").find_all("option"):
                query["select_region"] = elem_region.get("value")

                url = self.json_base_url + unit_api["url"].format(**query)
                resp = self.get_json(url)
                    
                for key, values in resp.iteritems():
                    if key not in json_data:
                        json_data[key] = []
                    json_data[key] += values

            json_key =  unit_api["dimensions"][dim_id]

            # 1.2.3 Parse response
            for _cat in json_data[json_key]:
                if isinstance(_cat, dict):
                    # Slightly hard-coded, the only dimension
                    # in the json api that contains more than
                    # label/id is the unit 
                    # TODO: Here we could add more metadata about
                    # the category (in practice, the unit)
                    cat = Category(_cat["id"],
                        label=_cat["Vardgivarnamn"].strip())
                else:
                    cat = Category(_cat)
                dim.add_category(cat)

        return dim

    def _query(self,**kwargs):
        params = kwargs
        only_region = kwargs.keys() == ["select_region"]
        NO_QUERY_DIMS = ["measure"]
        query_keys = [x.id for x in self.dimensions if x.id not in NO_QUERY_DIMS]
        
        queries = []

        # Create payload for post request
        # Get a list of values to query by
        query_values = []
        for dim in self.dimensions:
            if dim.id in NO_QUERY_DIMS:
                continue

            # Pass default value if dimension is not in query
            if dim.id not in kwargs:
                value = [dim.default_value]

            else:
                # Translate passed values to ids
                value = kwargs[dim.id]
                if isinstance(value, list):
                    value = [dim.get(cat).id for cat in value]
                else:
                    value = [dim.get(value).id]

            if value is None:
                raise ValueError()
            query_values.append(value)

        queries = to_list(product(*query_values))

        self.log.info(u"Making a total of {} queries".format(len(queries)))

        data = []

        for query in queries:
            payload =  dict(zip(query_keys, query))
            region_slug = self._get_region_slug(payload["select_region"])
            url = self.url_format.format(region=region_slug)
            yield self._parse_result_page(url, payload, only_region=only_region)

    def _parse_result_page(self, url, payload, only_region=False):
        """ Get data from a result page
            :param url: url to query
            :param payload: payload to pass
            :return: a dictlist with data
        """ 
        data = []
        try:
            if only_region:
                html = self.get_html(url)
            else:
                html = self.post_html(url, payload=payload)

        except RequestException500:
            self.log.warning(u"Status code 500 on {} with {}".format(url, payload))
            return None


        current_selection = self._get_current_selection(html)

        table = Datatable(html)
        dim_region = self.get("select_region")
        for row in table.data:
            region_or_unit_id, region_or_unit_label = row["region_or_unit"]
            if region_or_unit_id is None:
                region_or_unit_id = region_or_unit_label
            try:
                region = dim_region.get(region_or_unit_id)
                row["select_region"] = region.id
            except KeyError:
                unit = self.get("select_unit").get(region_or_unit_id)
                row["select_unit"] = unit.id
                try:
                    row["select_region"] = dim_region.get(unit.landsting_id).id
                except AttributeError:
                    row["select_region"] = None

            row.pop("region_or_unit", None)

            for dim in self.dimensions:
                if dim.id not in row:
                    row[dim.id] = current_selection[dim.id].label

            data.append(row)

        return data


    def _get_region_slug(self, id_or_label):
        """ Get the regional slug to be used in url
            "Norrbotten" => "Norrbottens"

            :param id_or_label: Id or label of region
        """      
        region = self.dimension("select_region").get(id_or_label)
        slug = region.label\
            .replace(u" ","-")\
            .replace(u"ö","o")\
            .replace(u"Ö","O")\
            .replace(u"ä","a")\
            .replace(u"å","a") + "s"

        EXCEPTIONS = {
            "Jamtland-Harjedalens": "Jamtlands",
            "Rikets": "Sveriges",
        }
        if slug in EXCEPTIONS:
            slug = EXCEPTIONS[slug]

        return slug

    def _get_region_periods(self, region_id):
        """ Get available periods for a given region by querying the
            period api.

            :returns: the result json object from api
        """
        if region_id not in self._region_periods:
            try:
                endpoint = PERIOD_API_ENDPOINTS[self.id]["url"].format(select_region=region_id)
                url = self.json_base_url + endpoint
            except KeyError:
                msg = u"URL to period api missing for {}".format(self.id)
                raise ValueError(msg)

            resp = self.get_json(url)
            self._region_periods[region_id] = resp


        return self._region_periods[region_id]


    def _get_current_selection(self, html):
        if isinstance(html, str):
            html = BeautifulSoup(html, "html.parser")
        selected_cats = {}
        for dim in self.dimensions:
            if dim.id in ["measure"]:
                continue
            
            elem = html.select("[name={}]".format(dim.id))

            if len(elem) > 1 or len(elem) == 0:
                import pdb;pdb.set_trace()
                raise Exception("DEBUG!")
            else:
                elem = elem[0]

            if dim.elem_type == "select":
                try:
                    option_elem = elem.select_one("[selected]")
                    selected_id = get_option_value(option_elem)
                    selected_label = get_option_text(option_elem)
                except AttributeError:
                    option_elem = elem.select_one("option")
                    selected_id = get_option_value(option_elem)
                    selected_label = get_option_text(option_elem)

                selected_cat = Category(selected_id, label=selected_label)
            elif dim.elem_type == "radio":
                import pdb;pdb.set_trace()
                raise NotImplementedError()
            elif dim.elem_type == "checkbox":
                selected_cat = Category(elem.has_attr("checked"))

            selected_cats[dim.id] = selected_cat

        return selected_cats







class Datatable(object):
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.data = self._parse_values()
        self._measures = None
        # Assumption: the data table is the last table on the page


    @property
    def has_tabs(self):
        """ Does the table have tabs?
            Like http://www.vantetider.se/Kontaktkort/Sveriges/VantatKortareAn60Dagar/
        """
        return len(self.soup.select(".table_switch")) > 0
    
    @property
    def has_horizontal_scroll(self):
        """ Does the table have horizontal scroll?
            Like http://www.vantetider.se/Kontaktkort/Sveriges/VantatKortareAn60Dagar/
        """
        return len(self.soup.select(".DTFC_ScrollWrapper")) > 0

    @property
    def has_vertical_scroll(self):
        """ Does the table have vertical scroll?
            Like http://www.vantetider.se/Kontaktkort/Sveriges/PrimarvardTelefon/
        """
        return bool(self.soup.select_one("#DataTables_Table_0_wrapper"))
    
    

    @property
    def measures(self):
        """ Get a list of the measuers of this datatable
            Measures can be "Antal Besök inom 7 dagar",
            "Måluppfyllelse vårdgarantin", etc
        """
        if self._measures == None:
            self._measures = get_unique([x["measure"] for x in self.data])
        
        return self._measures

    def _parse_values(self):
        """ Get values 
        """
        data = []
        if self.has_tabs:
            def _parse_tab_text(tab):
                # Annoying html in tabs
                if tab.select_one(".visible_normal"):
                    return tab.select_one(".visible_normal").text
                else:
                    return tab.text

            sub_table_ids = [_parse_tab_text(x) for x in self.soup.select(".table_switch li")]
            sub_tables = self.soup.select(".dataTables_wrapper")
            assert len(sub_tables) == len(sub_table_ids)
            assert len(sub_tables) > 0

            for measure, table in zip(sub_table_ids, sub_tables):
                if self.has_horizontal_scroll:
                    _data = self._parse_horizontal_scroll_table(table)                   
                    for region, col, value in _data:
                        data.append({
                            "region_or_unit": region,
                            "select_period": col, # Hardcode warning!
                            "measure": measure,
                            })

        else:
            if self.has_horizontal_scroll:
                raise NotImplementedError()
            
            if self.has_vertical_scroll:
                table = self.soup.select_one("#DataTables_Table_0_wrapper")
                _data = self._parse_vertical_scroll_table(table)
            else:
                table = self.soup.select(".chart.table.scrolling")[-1]
                _data = self._parse_regular_table(table)

            for region, measure, value in _data:
                data.append({
                    "region_or_unit": region,
                    "measure": measure,
                    "value": value
                })

        return data

    def _parse_horizontal_scroll_table(self, table_html):
        """ Get list of dicts from horizontally scrollable table
        """
        row_labels = [parse_text(x.text) for x  in table_html.select(".DTFC_LeftBodyWrapper tbody tr")]
        row_label_ids = [None] * len(row_labels)
        cols = [parse_text(x.text) for x in table_html.select(".dataTables_scrollHead th")]
        value_rows = table_html.select(".dataTables_scrollBody tbody tr")

        values = []
        for row_i, value_row in enumerate(value_rows):
            row_values = [parse_value(x.text) for x in value_row.select("td")]
            values.append(row_values)

        sheet = Sheet(zip(row_label_ids, row_labels), cols, values)

        return sheet.long_format

    def _parse_vertical_scroll_table(self, table_html):
        value_rows = table_html.select("tbody tr")
        row_labels = [parse_text(x.select_one("td").text) for x in value_rows]
        row_label_ids = [None] * len(row_labels)
        if table_html.select_one("td .clickable"):
            row_label_ids = [parse_landsting(x.select_one("td .clickable").get("onclick")) for x in value_rows]

        cols = [parse_text(x.text) for x in table_html.select(".dataTables_scrollHead th")][1:]
        values = []
        for row in value_rows:
            row_values = [ parse_value(x.text) for x in row.select("td")[1:] ]
            values.append(row_values)

        sheet = Sheet(zip(row_label_ids, row_labels), cols, values)

        return sheet.long_format

    def _parse_regular_table(self, table_html):
        value_rows = table_html.select("tbody tr")
        row_labels = [parse_text(x.select_one("td").text) for x in value_rows]
        row_label_ids = [None] * len(row_labels)
        if table_html.select_one("td .clickable"):
            row_label_ids = [parse_landsting(x.select_one("td .clickable").get("onclick")) for x in value_rows]
        cols = [parse_text(x.text) for x in table_html.select("th")][1:]
        values = []
        for row in value_rows:
            row_values = [ parse_value(x.text) for x in row.select("td")[1:] ]
            values.append(row_values)

        sheet = Sheet(zip(row_label_ids, row_labels), cols, values)

        return sheet.long_format



class Sheet(object):
    """ Represents a two-dimensional sheet/table with data
    """
    def __init__(self, rows, cols, values):
        """
            :param rows: a list with row values    
            :param cols: a list with column headers
            :param values: a list of lists with row values
        """
        self.values_by_row = values
        self.values = flatten(values)

        if len(rows) * len(cols) == len(self.values):
            msg = ("Error initing sheet. Factor of n rows ({})",
                "and cols ({}) don't add up. Got {}, expected {}."\
                .format(len(rows), len(cols), len(rows) * len(cols), len(self.values)))
                
        assert len(rows) == len(values)
        assert len(cols) == len(values[0])

        self.row_index = rows
        self.col_index = cols

    @property
    def as_dictlist(self):
        """ Returns a dictlist with values
            [
                {
                    "row": "row_a",
                    "col": "col_a",
                    "value": 1,
                }
            ]
        """
        data = []
        for row_i, row in enumerate(self.row_index):
            for col_i, col in enumerate(self.col_index):
                value = self.values_by_row[row_i][col_i]
                data.append({
                    "row": row,
                    "col": col,
                    "value": value,
                    })
        return data

    @property
    def long_format(self):
        return zip(
            repeat(self.row_index, len(self.col_index)),
            self.col_index * len(self.row_index),
            self.values
            )
    

def guess_dimension(value):
    """ Guess dimension of a category value
    """
    if value in ["Jan","Feb","Mars","Apr","Maj","Juni","Juli","Aug","Sep","Okt","Nov","Dec"]:
        return "select_month"
    elif is_int(value):
        return "select_year"

    raise ValueError("Not able to determine dimension for '{}'".format(value))
