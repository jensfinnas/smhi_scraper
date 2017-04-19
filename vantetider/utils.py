# encoding: utf-8
from collections import Counter, defaultdict


def parse_value(val):
    """ Parse values from html
    """
    val = val.replace("%", " ")\
        .replace(" ","")\
        .replace(",", ".")\
        .replace("st","").strip()

    missing = ["Ejdeltagit"]
    if val in missing:
        return val
    elif val == "":
        return None

    return float(val)

def parse_text(val):
    """ Format strings fetched from html
    """
    return val.replace("\n", " ").strip()

def guess_measure_unit(values):
    last_words = [x.split(" ")[-1] for x in values]
    counts = Counter(last_words).most_common()
    max_share = float(counts[0][1] / float(len(values)) )
    if max_share <= 0.5:
        raise ParseError(u"Not sure how to interpret the measure unit in: {}".format(values))

    return counts[0][0]

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

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class ParseError(Exception):
    pass