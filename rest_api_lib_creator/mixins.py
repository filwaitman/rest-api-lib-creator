import requests

from .datastructures import Meta, NoContent, UnhandledResponse
from .utils import add_querystring_to_url


class ListMixin(object):
    list_expected_status_code = 200
    list_url = None

    @classmethod
    def get_list_url(cls):
        if cls.list_url:
            return cls.list_url.format(base_api_url=cls.get_base_api_url())
        return cls.get_base_api_url()

    @classmethod
    def list(cls, **kwargs):
        url = add_querystring_to_url(cls.get_list_url(), **kwargs)
        response = cls.request(requests.get, url)
        if response.status_code != cls.list_expected_status_code:
            return UnhandledResponse(meta=Meta(response))
        return cls.prepare_response(response, cls, many=True)


class CreateMixin(object):
    create_payload_mode = 'data'  # 'data or 'json
    create_expected_status_code = 201
    create_url = None

    @classmethod
    def get_create_url(cls):
        if cls.create_url:
            return cls.create_url.format(base_api_url=cls.get_base_api_url())
        return cls.get_base_api_url()

    @classmethod
    def create(cls, **kwargs):
        outer_kwargs = {cls.create_payload_mode: kwargs}
        response = cls.request(requests.post, cls.get_create_url(), **outer_kwargs)
        if response.status_code != cls.create_expected_status_code:
            return UnhandledResponse(meta=Meta(response))
        return cls.prepare_response(response, cls)

    def save(self):
        if not(self._existing_instance):
            return self.create(**self._changed_data)
        return self.update(self.get_identifier(), **self._changed_data)


class RetrieveMixin(object):
    retrieve_expected_status_code = 200
    retrieve_url = None

    @classmethod
    def get_retrieve_url(cls, identifier):
        if cls.retrieve_url:
            return cls.retrieve_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)
        return cls.get_instance_url(identifier)

    @classmethod
    def retrieve(cls, identifier):
        response = cls.request(requests.get, cls.get_retrieve_url(identifier))
        if response.status_code != cls.retrieve_expected_status_code:
            return UnhandledResponse(meta=Meta(response))
        return cls.prepare_response(response, cls)


class UpdateMixin(object):
    update_payload_mode = 'data'  # 'data or 'json
    update_expected_status_code = 200
    update_url = None

    @classmethod
    def get_update_url(cls, identifier):
        if cls.update_url:
            return cls.update_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)
        return cls.get_instance_url(identifier)

    @classmethod
    def update(cls, identifier, **kwargs):
        outer_kwargs = {cls.update_payload_mode: kwargs}
        response = cls.request(requests.patch, cls.get_update_url(identifier), **outer_kwargs)
        if response.status_code != cls.update_expected_status_code:
            return UnhandledResponse(meta=Meta(response))
        return cls.prepare_response(response, cls)

    def save(self):
        if not(self._existing_instance):
            return self.create(**self._changed_data)
        return self.update(self.get_identifier(), **self._changed_data)


class DeleteMixin(object):
    delete_expected_status_code = 204
    delete_url = None

    @classmethod
    def get_delete_url(cls, identifier):
        if cls.delete_url:
            return cls.delete_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)
        return cls.get_instance_url(identifier)

    @classmethod
    def delete(cls, identifier):
        response = cls.request(requests.delete, cls.get_delete_url(identifier))
        if response.status_code != cls.delete_expected_status_code or (response.status_code != 204):
            return UnhandledResponse(meta=Meta(response))
        return NoContent(meta=Meta(response))

    def destroy(self):
        return self.delete(self.get_identifier())
