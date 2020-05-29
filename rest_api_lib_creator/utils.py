from collections import OrderedDict
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def add_querystring_to_url(url, **params):
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)
    query = OrderedDict(sorted(query.items()))  # Forcing resulting url parameters to be sorted for testing purposes
    url_parts[4] = urlencode(query)
    return urlunparse(url_parts)


def should_iterate(value):
    return isinstance(value, (list, tuple, set))
