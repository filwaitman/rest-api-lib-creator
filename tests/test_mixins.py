from unittest import TestCase

import mock
import requests

from rest_api_lib_creator.core import RestApiLib
from rest_api_lib_creator.datastructures import NoContent, UnhandledResponse
from rest_api_lib_creator.mixins import CreateMixin, DeleteMixin, ListMixin, RetrieveMixin, UpdateMixin
from rest_api_lib_creator.pagination_classes import NoPagination


class ListMixinTestCase(TestCase):
    def setUp(self):
        super(ListMixinTestCase, self).setUp()

        class Pet(ListMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        self.response_json = {
            'count': 2,
            'previous_url': None,
            'next_url': None,
            'results': [
                {'id': 'xx', 'name': 'Luna'},
                {'id': 'yy', 'name': 'Estrela'},
            ]
        }

        self.Pet = Pet
        self._request_patched = mock.patch.object(
            RestApiLib, 'request', return_value=mock.Mock(status_code=200, json=mock.Mock(return_value=self.response_json))
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        super(ListMixinTestCase, self).tearDown()
        self._request_patched.stop()

    def test_common(self):
        pets = self.Pet.list()

        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets')
        self.assertIsInstance(pets, list)
        self.assertEqual(len(pets), 2)

        self.assertIsInstance(pets[0], self.Pet)
        self.assertTrue(pets[0]._existing_instance)
        self.assertEqual(pets[0].id, 'xx')
        self.assertEqual(pets[0].name, 'Luna')

        self.assertIsInstance(pets[1], self.Pet)
        self.assertTrue(pets[1]._existing_instance)
        self.assertEqual(pets[1].id, 'yy')
        self.assertEqual(pets[1].name, 'Estrela')

        self.assertIsNotNone(pets._meta.request)
        self.assertIsNotNone(pets._meta.response)

    def test_common_response_as_a_plain_list_of_objects(self):
        class PetNoPagination(self.Pet):
            pagination_class = NoPagination

        self.request_patched.return_value = mock.Mock(status_code=200, json=mock.Mock(return_value=self.response_json['results']))

        pets = PetNoPagination.list()

        self.assertIsInstance(pets, list)
        self.assertEqual(len(pets), 2)

    def test_kwargs_passed_as_query_params(self):
        self.request_patched.reset_mock()
        self.Pet.list(page=2)
        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets?page=2')

        self.request_patched.reset_mock()
        self.Pet.list(type='dog')
        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets?type=dog')

    def test_custom_capabilities(self):
        class CustomPet(ListMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'
            list_url = 'http://super.cool/api/pets/custom'

            @classmethod
            def get_objects_from_payload(cls, payload):
                return payload['data']

        response_json = self.response_json.copy()
        response_json['data'] = response_json['results']
        del response_json['results']

        self.request_patched.return_value = mock.Mock(status_code=200, json=mock.Mock(return_value=response_json))

        pets = CustomPet.list()

        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets/custom')
        self.assertIsInstance(pets, list)
        self.assertEqual(len(pets), 2)

    def test_unhandled_response(self):
        self.request_patched.return_value.status_code = 401
        response = self.Pet.list()
        self.assertIsInstance(response, UnhandledResponse)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)


class CreateMixinTestCase(TestCase):
    def setUp(self):
        super(CreateMixinTestCase, self).setUp()

        class Pet(CreateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        self.response_json = {
            'id': 'xx',
            'name': 'Luna',
        }

        self.Pet = Pet
        self._request_patched = mock.patch.object(
            RestApiLib, 'request', return_value=mock.Mock(status_code=201, json=mock.Mock(return_value=self.response_json))
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        super(CreateMixinTestCase, self).tearDown()
        self._request_patched.stop()

    def test_common(self):
        pet = self.Pet.create(name='Luna')

        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets', data={'name': 'Luna'})
        self.assertIsInstance(pet, self.Pet)
        self.assertTrue(pet._existing_instance)
        self.assertEqual(pet.id, 'xx')
        self.assertEqual(pet.name, 'Luna')
        self.assertIsNotNone(pet._meta.request)
        self.assertIsNotNone(pet._meta.response)

    def test_common_via_save(self):
        self.request_patched.reset_mock()
        pet = self.Pet()
        pet.name = 'Luna'
        pet.save()
        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets', data={'name': 'Luna'})

        self.request_patched.reset_mock()
        pet = self.Pet(x='dog')
        pet.save()
        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets', data={'x': 'dog'})

        self.request_patched.reset_mock()
        pet = self.Pet(x='dog')
        pet.name = 'Luna'
        pet.save()
        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets', data={'x': 'dog', 'name': 'Luna'})

    def test_save_old_instances_behavior(self):
        class CreateUpdatePet(CreateMixin, UpdateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        # If class inherits from UpdateMixin this is a valid operation
        pet = CreateUpdatePet(_existing_instance=True, id='xyz')
        pet.name = 'Luna'
        pet.save()
        self.request_patched.assert_called_once_with(requests.patch, 'http://super.cool/api/pets/xyz', data={'name': 'Luna'})

        # Otherwise this have to fail
        pet = self.Pet(_existing_instance=True, id='xyz')
        pet.name = 'Luna'
        self.assertRaisesRegexp(NotImplementedError, 'Consider inheriting your base lib class from UpdateMixin.', pet.save)

    def test_custom_capabilities(self):
        class CustomPet(CreateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'
            create_payload_mode = 'json'  # 'data or 'json
            create_url = 'http://super.cool/api/pets/create'

        CustomPet.create(name='Luna')

        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets/create', json={'name': 'Luna'})

    def test_unhandled_response(self):
        self.request_patched.return_value.status_code = 400
        response = self.Pet.create(name='Luna')
        self.assertIsInstance(response, UnhandledResponse)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)


class RetrieveMixinTestCase(TestCase):
    def setUp(self):
        super(RetrieveMixinTestCase, self).setUp()

        class Pet(RetrieveMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        self.response_json = {
            'id': 'xx',
            'name': 'Luna',
        }

        self.Pet = Pet
        self._request_patched = mock.patch.object(
            RestApiLib, 'request', return_value=mock.Mock(status_code=200, json=mock.Mock(return_value=self.response_json))
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        super(RetrieveMixinTestCase, self).tearDown()
        self._request_patched.stop()

    def test_common(self):
        pet = self.Pet.retrieve('xx')

        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets/xx')
        self.assertIsInstance(pet, self.Pet)
        self.assertTrue(pet._existing_instance)
        self.assertEqual(pet.id, 'xx')
        self.assertEqual(pet.name, 'Luna')
        self.assertIsNotNone(pet._meta.request)
        self.assertIsNotNone(pet._meta.response)

    def test_custom_capabilities(self):
        class CustomPet(RetrieveMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'
            retrieve_url = '{base_api_url}/get/{identifier}'

        CustomPet.retrieve('xx')

        self.request_patched.assert_called_once_with(requests.get, 'http://super.cool/api/pets/get/xx')

    def test_unhandled_response(self):
        self.request_patched.return_value.status_code = 404
        response = self.Pet.retrieve('xx')
        self.assertIsInstance(response, UnhandledResponse)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)


class UpdateMixinTestCase(TestCase):
    def setUp(self):
        super(UpdateMixinTestCase, self).setUp()

        class Pet(UpdateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        self.response_json = {
            'id': 'xx',
            'name': 'Luna',
        }

        self.Pet = Pet
        self._request_patched = mock.patch.object(
            RestApiLib, 'request', return_value=mock.Mock(status_code=200, json=mock.Mock(return_value=self.response_json))
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        super(UpdateMixinTestCase, self).tearDown()
        self._request_patched.stop()

    def test_common(self):
        pet = self.Pet.update('xx', name='Luna')

        self.request_patched.assert_called_once_with(requests.patch, 'http://super.cool/api/pets/xx', data={'name': 'Luna'})
        self.assertIsInstance(pet, self.Pet)
        self.assertTrue(pet._existing_instance)
        self.assertEqual(pet.id, 'xx')
        self.assertEqual(pet.name, 'Luna')
        self.assertIsNotNone(pet._meta.request)
        self.assertIsNotNone(pet._meta.response)

    def test_common_via_save(self):
        pet = self.Pet(id='xx', _existing_instance=True)  # When RetrieveMixin is present this should be like ".retrieve('xx')"
        pet.name = 'Luna'
        pet.save()

        self.request_patched.assert_called_once_with(requests.patch, 'http://super.cool/api/pets/xx', data={'name': 'Luna'})

    def test_save_new_instances_behavior(self):
        class CreateUpdatePet(CreateMixin, UpdateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        # If class inherits from CreateMixin this is a valid operation
        pet = CreateUpdatePet(name='Luna')
        pet.save()
        self.request_patched.assert_called_once_with(requests.post, 'http://super.cool/api/pets', data={'name': 'Luna'})

        # Otherwise this have to fail
        pet = self.Pet(name='Luna')
        self.assertRaisesRegexp(NotImplementedError, 'Consider inheriting your base lib class from CreateMixin.', pet.save)

    def test_custom_capabilities(self):
        class CustomPet(UpdateMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'
            update_payload_mode = 'json'  # 'data or 'json
            update_url = '{base_api_url}/update/{identifier}'

        CustomPet.update('xx', name='Luna')

        self.request_patched.assert_called_once_with(requests.patch, 'http://super.cool/api/pets/update/xx', json={'name': 'Luna'})

    def test_unhandled_response(self):
        self.request_patched.return_value.status_code = 400
        response = self.Pet.update('xx', name='Luna')
        self.assertIsInstance(response, UnhandledResponse)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)


class DeleteMixinTestCase(TestCase):
    def setUp(self):
        super(DeleteMixinTestCase, self).setUp()

        class Pet(DeleteMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'

        self.response_json = {}

        self.Pet = Pet
        self._request_patched = mock.patch.object(
            RestApiLib, 'request', return_value=mock.Mock(status_code=204, json=mock.Mock(return_value=self.response_json))
        )
        self.request_patched = self._request_patched.start()

    def tearDown(self):
        super(DeleteMixinTestCase, self).tearDown()
        self._request_patched.stop()

    def test_common(self):
        response = self.Pet.delete('xx')

        self.request_patched.assert_called_once_with(requests.delete, 'http://super.cool/api/pets/xx')
        self.assertIsInstance(response, NoContent)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)

    def test_common_via_destroy(self):
        pet = self.Pet(id='xx', _existing_instance=True)  # When RetrieveMixin is present this should be like ".retrieve('xx')"
        pet.destroy()

        self.request_patched.assert_called_once_with(requests.delete, 'http://super.cool/api/pets/xx')

    def test_custom_capabilities(self):
        class CustomPet(DeleteMixin, RestApiLib):
            base_api_url = 'http://super.cool/api/pets'
            delete_url = '{base_api_url}/delete/{identifier}'

        CustomPet.delete('xx')

        self.request_patched.assert_called_once_with(requests.delete, 'http://super.cool/api/pets/delete/xx')

    def test_unhandled_response(self):
        self.request_patched.return_value.status_code = 405
        response = self.Pet.delete('xx')
        self.assertIsInstance(response, UnhandledResponse)
        self.assertIsNotNone(response._meta.request)
        self.assertIsNotNone(response._meta.response)
