import sys


if sys.version_info.major == 2:
    IOBase = file
    from urlparse import urlparse, parse_qsl, urlunparse
    from urllib import urlencode

else:
    from io import IOBase

    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
