# encoding: utf-8
from collections import Counter, defaultdict
import re

def parse_value(val):
    """ Parse values from html
    """
    val = val.replace("%", " ")\
        .replace(" ","")\
        .replace(",", ".")\
        .replace("st","").strip()

    missing = ["Ejdeltagit", "N/A"]
    if val in missing:
        return val
    elif val == "":
        return None

    return float(val)

def parse_text(val):
    """ Format strings fetched from html
    """
    return val.replace("\n", " ").strip()

def parse_landsting(val):
    """ Get region/unit id from "handle_click_event_landsting(this, 1)"
    """
    try:
        return re.search("\(this, (\d+)", val).group(1)
    except AttributeError:
        return None

def is_string(val):
    return isinstance(val, str) or isinstance(val, unicode)

def guess_measure_unit(values):
    last_words = [x.split(" ")[-1] for x in values]
    counts = Counter(last_words).most_common()
    max_share = float(counts[0][1] / float(len(values)) )
    if max_share <= 0.5:
        raise ParseError(u"Not sure how to interpret the measure unit in: {}".format(values))

    return counts[0][0]


def get_elem_type(elem):
    """ Get elem type of soup selection
        :param elem: a soup element
    """
    elem_type = None
    if is_list(elem):
        if elem[0].get("type") == "radio":
            elem_type = "radio"
        else:
            raise ValueError(u"Unknown element type: {}".format(elem))
    
    elif elem.name == "select":
        elem_type = "select"
    
    elif elem.name == "input":
        elem_type = elem.get("type")
    
    else:
        raise ValueError(u"Unknown element type: {}".format(elem))
    
    # To be removed
    assert elem_type is not None

    return elem_type

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

def get_option_text(elem):
    """ Get the text of option
        <option value="foo">bar</option> => "bar"
        <option>bar</option> => "bar"
        :param elem: a soup element
    """
    return elem.text.strip()

def get_unique(l):
    """ Get unique values from list
        Placed outside the class beacuse `list` conflicts our internal 
        method with the same name.
    """
    return list(set(l))

def to_list(l):
    return list(l)

def is_list(l):
    return isinstance(l, list)

def default_list_dict():
    return defaultdict(list)

def flatten(l):
    """Flatten list of lists
    """
    return [item for sublist in l for item in sublist]

def repeat(l, n):
    """ Repeat all items in list n times
        repeat([1,2,3], 2) => [1,1,2,2,3,3]
        http://stackoverflow.com/questions/24225072/repeating-elements-of-a-list-n-times
    """
    return [x for x in l for i in range(n)]

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class ParseError(Exception):
    pass