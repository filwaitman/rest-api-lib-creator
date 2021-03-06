from io import IOBase

from requests.exceptions import HTTPError

from .datastructures import Meta, metalist
from .mixins import CreateMixin, DeleteMixin, ListMixin, RetrieveMixin, UpdateMixin
from .pagination_classes import DRFPageNumberPagination
from .utils import should_iterate


class OnException(object):
    @staticmethod
    def reraise(exc):
        raise exc

    @staticmethod
    def return_response(exc):
        if hasattr(exc, 'response'):
            return exc.response
        return OnException.reraise(exc)


class RestApiLib(object):
    base_api_url = None  # 'https://my.super.service/api/users'...
    instance_url = '{base_api_url}/{identifier}'

    nested_objects = None  # dictionary used to parse/cast response raw data into another RestApiLib objects
    use_str_in_place_of_repr = False  # if True __repr__ will use __str__ to render output (which sometimes is handy for debugging)

    identifier_field = 'id'  # 'id', 'pk', 'uuid'...
    pretty_identifier = '{id}'  # '{id}', '{first_name} {last_name}', 'message from {source} to {target}'...

    request_headers = None  # None is the default for requests library
    request_timeout = None  # None is the default for requests library
    request_auth = None  # None is the default for requests library

    on_exception = OnException.reraise  # OnException.reraise or OnException.return_response or any other callable you want

    pagination_class = DRFPageNumberPagination

    # Just for quick reference, parameters below can be set for the mixins customization:
    # list_expected_status_code
    # list_url
    # create_payload_mode
    # create_expected_status_code
    # create_url
    # retrieve_expected_status_code
    # retrieve_url
    # update_payload_mode
    # update_expected_status_code
    # update_url
    # delete_expected_status_code
    # delete_url

    @classmethod
    def list(cls, *args, **kwargs):
        raise NotImplementedError('Consider inheriting your base lib class from ListMixin.')

    @classmethod
    def create(cls, *args, **kwargs):
        raise NotImplementedError('Consider inheriting your base lib class from CreateMixin.')

    @classmethod
    def retrieve(cls, *args, **kwargs):
        raise NotImplementedError('Consider inheriting your base lib class from RetrieveMixin.')

    @classmethod
    def update(cls, *args, **kwargs):
        raise NotImplementedError('Consider inheriting your base lib class from UpdateMixin.')

    @classmethod
    def delete(cls, *args, **kwargs):
        raise NotImplementedError('Consider inheriting your base lib class from DeleteMixin.')

    @classmethod
    def get_base_api_url(cls):
        return cls.base_api_url

    @classmethod
    def get_instance_url(cls, identifier):
        return cls.instance_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)

    @classmethod
    def get_request_headers(cls):
        return cls.request_headers

    @classmethod
    def get_request_timeout(cls):
        return cls.request_timeout

    @classmethod
    def get_request_auth(cls):
        return cls.request_auth

    @classmethod
    def handle_request_exception(cls, e, method, url, request_kwargs):
        response = getattr(e, 'response', None)
        if isinstance(e, HTTPError) and (response is not None):
            exc = HTTPError(response.content, response=response)
        else:
            exc = e
        return cls.on_exception(exc)

    @classmethod
    def prepare_requests_call(cls, **kwargs):
        request_kwargs = kwargs.pop('_request_kwargs', {})
        files = request_kwargs.pop('request_files', {})

        for payload_type in ('data', 'json'):
            if payload_type in kwargs:
                # Move files from 'json/data' atribute to 'files' attribute
                for k, v in kwargs[payload_type].items():
                    if isinstance(v, IOBase):
                        files[k] = v
                for k in files:
                    kwargs[payload_type].pop(k)

                # Look for rich objects in data and replace them for the identifier.
                for k, v in kwargs[payload_type].items():
                    if isinstance(v, RestApiLib):
                        kwargs[payload_type][k] = v.get_identifier()

        retval = {
            'timeout': request_kwargs.pop('timeout', cls.get_request_timeout()),
            'headers': request_kwargs.pop('headers', cls.get_request_headers()),
            'auth': request_kwargs.pop('auth', cls.get_request_auth()),
            'files': files or None,
        }
        retval.update(kwargs)
        return retval

    @classmethod
    def request(cls, method, url, **kwargs):
        kwargs = cls.prepare_requests_call(**kwargs)

        try:
            response = method(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            return cls.handle_request_exception(e, method, url, request_kwargs=kwargs)

    @classmethod
    def init_existing_object(cls, **kwargs):
        return cls(_existing_instance=True, **kwargs)

    @classmethod
    def call_endpoint(cls, method, url, **outer_kwargs):
        instance_class = outer_kwargs.pop('instance_class', None)
        many = outer_kwargs.pop('many', False)

        response = cls.request(method, url, **outer_kwargs)
        if instance_class:
            return cls.prepare_response(response, instance_class, many=many)
        return response

    @classmethod
    def get_objects_from_payload(cls, json_response):
        return cls.pagination_class().get_results(json_response)

    @classmethod
    def prepare_response(cls, response, instance_class, many=False):
        json_response = response.json()

        if many:
            objects = cls.get_objects_from_payload(json_response)
            return metalist([instance_class.init_existing_object(**obj) for obj in objects], meta=Meta(response))

        return instance_class.init_existing_object(meta=Meta(response=response), **json_response)

    def __init__(self, **kwargs):
        self._meta = kwargs.pop('meta', None)
        self._existing_instance = kwargs.pop('_existing_instance', False)
        self._track_object_changes = not(self._existing_instance)
        self._nested_objects = self.nested_objects or {}
        self._instance_data = {}
        self._changed_data = {}

        for k, v in kwargs.items():
            if k in self._nested_objects:
                if should_iterate(v):
                    set_value = v.__class__([self._nested_objects[k](**v_child) for v_child in v])
                else:
                    set_value = self._nested_objects[k](**v)
            else:
                set_value = v

            setattr(self, k, set_value)
            self._instance_data[k] = set_value

        self._track_object_changes = True

    def __setattr__(self, name, value):
        if not(name.startswith('_')) and self._track_object_changes:
            self._changed_data[name] = value
            self._instance_data[name] = value

        return super(RestApiLib, self).__setattr__(name, value)

    def __repr__(self):
        if self.use_str_in_place_of_repr:
            return self.__str__()
        return '<{}: {}>'.format(self.__class__.__name__, self.get_identifier())

    def __str__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.get_pretty_identifier())

    def get_identifier(self):
        return getattr(self, self.identifier_field)

    def get_pretty_identifier(self):
        return self.pretty_identifier.format(**self._instance_data)


class ViewsetRestApiLib(ListMixin, CreateMixin, RetrieveMixin, UpdateMixin, DeleteMixin, RestApiLib):
    pass
