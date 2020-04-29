import requests

from .utils import add_querystring_to_url


class ListMixin(object):
    list_url = None

    @classmethod
    def get_objects_from_payload(cls, payload):
        if 'results' in payload:  # DRF default
            return payload['results']
        return payload

    @classmethod
    def get_list_url(cls):
        if cls.list_url:
            return cls.list_url.format(base_api_url=cls.get_base_api_url())
        return cls.get_base_api_url()

    @classmethod
    def list(cls, **kwargs):
        url = add_querystring_to_url(cls.get_list_url(), **kwargs)
        objects = cls.get_objects_from_payload(cls.request(requests.get, url).json())
        return [cls.init_existing_object(**obj) for obj in objects]


class CreateMixin(object):
    create_payload_mode = 'data'  # 'data or 'json
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
        return cls.init_existing_object(**response.json())

    def save(self):
        if not(self._existing_instance):
            return self.create(**self._changed_data)
        return self.update(self.get_identifier(), **self._changed_data)


class RetrieveMixin(object):
    retrieve_url = None

    @classmethod
    def get_retrieve_url(cls, identifier):
        if cls.retrieve_url:
            return cls.retrieve_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)
        return cls.get_instance_url(identifier)

    @classmethod
    def retrieve(cls, identifier):
        response = cls.request(requests.get, cls.get_retrieve_url(identifier))
        return cls.init_existing_object(**response.json())


class UpdateMixin(object):
    update_payload_mode = 'data'  # 'data or 'json
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
        return cls.init_existing_object(**response.json())

    def save(self):
        if not(self._existing_instance):
            return self.create(**self._changed_data)
        return self.update(self.get_identifier(), **self._changed_data)


class DeleteMixin(object):
    delete_url = None

    @classmethod
    def get_delete_url(cls, identifier):
        if cls.delete_url:
            return cls.delete_url.format(base_api_url=cls.get_base_api_url(), identifier=identifier)
        return cls.get_instance_url(identifier)

    @classmethod
    def delete(cls, identifier):
        cls.request(requests.delete, cls.get_delete_url(identifier))

    def destroy(self):
        return self.delete(self.get_identifier())
