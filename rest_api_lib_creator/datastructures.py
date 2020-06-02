class Meta(object):
    def __init__(self, response=None):
        self.response = response
        self.request = response.request

    def to_curl(self):
        import curlify
        return curlify.to_curl(self.request)


class DefaultResponseMixin(object):
    repr_return = ''

    def __init__(self, meta):
        self._meta = meta


class NoContent(DefaultResponseMixin):
    repr_return = '<NO CONTENT>'


class UnhandledResponse(DefaultResponseMixin):
    repr_return = '<UNHANDLED RESPONSE>'


class metalist(list):
    def __init__(self, objects, meta):
        super().__init__(objects)
        self._meta = meta
