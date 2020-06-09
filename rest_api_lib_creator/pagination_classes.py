class NoPagination(object):
    def get_results(self, json_response):
        return json_response


class DRFPageNumberPagination(object):
    def get_results(self, json_response):
        return json_response['results']


class DRFLimitOffsetPagination(DRFPageNumberPagination):
    pass
