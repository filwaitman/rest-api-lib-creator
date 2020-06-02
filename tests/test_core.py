import os
from unittest import TestCase

import mock
from requests.exceptions import HTTPError

from rest_api_lib_creator.core import OnException, RestApiLib, ViewsetRestApiLib
from rest_api_lib_creator.mixins import CreateMixin, DeleteMixin, ListMixin, RetrieveMixin, UpdateMixin


class RestApiLibTestCase(TestCase):
    def setUp(self):
        class MyLib1(RestApiLib):
            base_api_url = 'http://super.cool/api'

        class MyLib2(RestApiLib):
            base_api_url = 'http://super.cool/api'
            instance_url = 'http://super.cool/api/custom/{identifier}'
            request_headers = {'Authorization': 'Token <TOKEN>'}
            request_timeout = 10
            request_auth = ('username', 'password')
            pretty_identifier = '{first_name} {last_name}'
            use_str_in_place_of_repr = True
            nested_objects = {
                'lib1': MyLib1,
            }

        super(RestApiLibTestCase, self).setUp()
        self.MyLib1 = MyLib1
        self.MyLib2 = MyLib2

    def test_mixin_capabilities_are_not_implemented(self):
        lib = self.MyLib1()

        for mixin in (ListMixin, CreateMixin, RetrieveMixin, UpdateMixin, DeleteMixin):
            self.assertNotIsInstance(lib, mixin)

        for method in (lib.list, lib.create, lib.retrieve, lib.update, lib.delete):
            self.assertRaises(NotImplementedError, method)

    def test_get_base_api_url(self):
        self.assertEqual(self.MyLib1().get_base_api_url(), 'http://super.cool/api')

    def test_get_instance_url(self):
        self.assertEqual(self.MyLib1().get_instance_url('<ID>'), 'http://super.cool/api/<ID>')
        self.assertEqual(self.MyLib2().get_instance_url('<ID>'), 'http://super.cool/api/custom/<ID>')

    def test_get_request_headers(self):
        self.assertEqual(self.MyLib1().get_request_headers(), None)
        self.assertEqual(self.MyLib2().get_request_headers(), {'Authorization': 'Token <TOKEN>'})

    def test_get_request_timeout(self):
        self.assertEqual(self.MyLib1().get_request_timeout(), None)
        self.assertEqual(self.MyLib2().get_request_timeout(), 10)

    def test_get_request_auth(self):
        self.assertEqual(self.MyLib1().get_request_auth(), None)
        self.assertEqual(self.MyLib2().get_request_auth(), ('username', 'password'))

    def test_init_existing_object(self):
        self.assertFalse(self.MyLib1(id='xx')._existing_instance)
        self.assertTrue(self.MyLib1.init_existing_object(id='xx')._existing_instance)

    def test_call_endpoint(self):
        response_patched = mock.Mock(json=mock.Mock(return_value={'id': 'xxx', 'name': 'Filipe Waitman'}))
        requests = mock.Mock()

        with mock.patch.object(self.MyLib1, 'request', return_value=response_patched) as request_patched:
            response = self.MyLib1.call_endpoint(requests.get, 'http://super.cool/api')
            self.assertIsInstance(response, mock.Mock)
            self.assertEqual(response, response_patched)
            request_patched.assert_called_once_with(requests.get, 'http://super.cool/api')

        with mock.patch.object(self.MyLib1, 'request', return_value=response_patched) as request_patched:
            response = self.MyLib1.call_endpoint(requests.get, 'http://super.cool/api', response_object=self.MyLib1, data={})
            self.assertIsInstance(response, self.MyLib1)
            self.assertTrue(response._existing_instance)
            request_patched.assert_called_once_with(requests.get, 'http://super.cool/api', data={})

    def test_changed_data_new_instance(self):
        lib = self.MyLib1(id='xx', first_name='Filipe')
        self.assertEqual(lib._changed_data, {'id': 'xx', 'first_name': 'Filipe'})

        lib.key1 = 'value1'
        self.assertEqual(lib._changed_data, {'id': 'xx', 'first_name': 'Filipe', 'key1': 'value1'})

        lib.key2 = 42
        self.assertEqual(lib._changed_data, {'id': 'xx', 'first_name': 'Filipe', 'key1': 'value1', 'key2': 42})

    def test_changed_data_existing_instance(self):
        lib = self.MyLib1(id='xx', first_name='Filipe', _existing_instance=True)
        self.assertEqual(lib._changed_data, {})

        lib.key1 = 'value1'
        self.assertEqual(lib._changed_data, {'key1': 'value1'})

        lib.key2 = 42
        self.assertEqual(lib._changed_data, {'key1': 'value1', 'key2': 42})

    def test_repr(self):
        self.assertEqual(self.MyLib1(id='xx', first_name='Filipe', last_name='Waitman').__repr__(), '<MyLib1: xx>')
        self.assertEqual(self.MyLib2(id='xx', first_name='Filipe', last_name='Waitman').__repr__(), '<MyLib2: Filipe Waitman>')

    def test_str(self):
        self.assertEqual(self.MyLib1(id='xx', first_name='Filipe', last_name='Waitman').__str__(), '<MyLib1: xx>')
        self.assertEqual(self.MyLib2(id='xx', first_name='Filipe', last_name='Waitman').__str__(), '<MyLib2: Filipe Waitman>')

    def test_get_identifier(self):
        self.assertEqual(self.MyLib1(id='xx', first_name='Filipe', last_name='Waitman').get_identifier(), 'xx')
        self.assertEqual(self.MyLib2(id='xx', first_name='Filipe', last_name='Waitman').get_identifier(), 'xx')

    def test_get_pretty_identifier(self):
        self.assertEqual(self.MyLib1(id='xx', first_name='Filipe', last_name='Waitman').get_pretty_identifier(), 'xx')
        self.assertEqual(self.MyLib2(id='xx', first_name='Filipe', last_name='Waitman').get_pretty_identifier(), 'Filipe Waitman')

    def test_nested_objects_casting(self):
        resource_lib1_data = {'id': 'yy', 'name': 'Lib1 data'}

        resource_lib2 = self.MyLib2(id='xx', name='Filipe', email='filipe.w@toptal.com', lib1=resource_lib1_data)
        self.assertIsInstance(resource_lib2, self.MyLib2)
        self.assertIsInstance(resource_lib2.lib1, self.MyLib1)
        self.assertEqual(resource_lib2.name, 'Filipe')
        self.assertEqual(resource_lib2.lib1.name, 'Lib1 data')

        for type_ in (list, tuple):
            resource_lib2 = self.MyLib2(id='xx', name='Filipe', email='filipe.w@toptal.com', lib1=type_([resource_lib1_data, ]))
            self.assertIsInstance(resource_lib2, self.MyLib2)
            self.assertEqual(resource_lib2.name, 'Filipe')

            self.assertIsInstance(resource_lib2.lib1, type_)
            self.assertEqual(len(resource_lib2.lib1), 1)
            self.assertEqual(resource_lib2.lib1[0].name, 'Lib1 data')


class RestApiLibRequestTestCase(TestCase):
    def setUp(self):
        class MyLib1(RestApiLib):
            pass

        class MyLib2(RestApiLib):
            identifier_field = 'custom_identifier'
            request_headers = {'Authorization': 'Token <TOKEN>'}
            request_timeout = 10
            request_auth = ('username', 'password')

            @classmethod
            def handle_request_exception(cls, e, method, url, request_kwargs):
                raise RuntimeError('API is crappy')

        class MyLib3(RestApiLib):
            on_exception = OnException.return_response

        super(RestApiLibRequestTestCase, self).setUp()
        self.MyLib1 = MyLib1
        self.MyLib2 = MyLib2
        self.MyLib3 = MyLib3

    def test_final_request_signature_common(self):
        response_patched = mock.Mock()
        requests = mock.Mock()
        requests.get.return_value = response_patched

        response = self.MyLib1.request(requests.get, 'http://super.cool/api')

        requests.get.assert_called_once_with('http://super.cool/api', timeout=None, auth=None, headers=None, files=None)
        self.assertEqual(response, response_patched)
        self.assertTrue(response.raise_for_status.called)

    def test_final_request_signature_custom_variables(self):
        response_patched = mock.Mock()
        requests = mock.Mock()
        requests.post.return_value = response_patched
        data = {'key1': 'value1'}

        response = self.MyLib2.request(requests.post, 'http://super.cool/api', data=data)

        requests.post.assert_called_once_with(
            'http://super.cool/api', timeout=10, data=data,
            auth=('username', 'password'), headers={'Authorization': 'Token <TOKEN>'}, files=None,
        )
        self.assertEqual(response, response_patched)
        self.assertTrue(response.raise_for_status.called)

    def test_final_request_signature_call_overrides(self):
        response_patched = mock.Mock()
        requests = mock.Mock()
        requests.patch.return_value = response_patched
        data = {'key1': 'value1'}

        response = self.MyLib2.request(requests.patch, 'http://super.cool/api', json=data, _request_kwargs={'timeout': 20})

        requests.patch.assert_called_once_with(
            'http://super.cool/api', json=data, timeout=20,
            auth=('username', 'password'), headers={'Authorization': 'Token <TOKEN>'}, files=None,
        )
        self.assertEqual(response, response_patched)
        self.assertTrue(response.raise_for_status.called)

    def test_final_request_signature_convert_rich_objects_from_payload_to_proper_identifiers(self):
        response_patched = mock.Mock()
        requests = mock.Mock()
        requests.post.return_value = response_patched
        data = {
            'key1': 'value1',
            'mylib1': self.MyLib1(id='<mylib1.id>', name='Filipe', email='filipe.w@toptal.com'),
            'mylib2': self.MyLib2(custom_identifier='<mylib2.custom_identifier>', name='Filipe', email='filipe.w@toptal.com'),
        }

        for payload_type in ('data', 'json'):
            requests.reset_mock()
            response_patched.reset_mock()
            payload_kwargs = {payload_type: {'key1': 'value1', 'mylib1': '<mylib1.id>', 'mylib2': '<mylib2.custom_identifier>'}}

            response = self.MyLib2.request(requests.post, 'http://super.cool/api', **{payload_type: data})

            requests.post.assert_called_once_with(
                'http://super.cool/api', timeout=10, auth=('username', 'password'),
                headers={'Authorization': 'Token <TOKEN>'}, files=None, **payload_kwargs
            )
            self.assertEqual(response, response_patched)
            self.assertTrue(response.raise_for_status.called)

    def test_final_request_signature_move_file_objects_from_payload_to_files_param(self):
        response_patched = mock.Mock()
        requests = mock.Mock()
        requests.post.return_value = response_patched

        for payload_type in ('data', 'json'):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_file.txt')) as f:
                data = {'key1': 'value1', 'f': f}

                requests.reset_mock()
                response_patched.reset_mock()
                payload_kwargs = {payload_type: {'key1': 'value1'}}

                response = self.MyLib2.request(requests.post, 'http://super.cool/api', **{payload_type: data})

                requests.post.assert_called_once_with(
                    'http://super.cool/api', timeout=10, auth=('username', 'password'),
                    headers={'Authorization': 'Token <TOKEN>'}, files={'f': f}, **payload_kwargs
                )
                self.assertEqual(response, response_patched)
                self.assertTrue(response.raise_for_status.called)

    def test_request_exception(self):
        requests = mock.Mock(get=mock.Mock(side_effect=HTTPError('', response=mock.Mock(content='Something is not good'))))
        self.assertRaisesRegexp(HTTPError, 'Something is not good', self.MyLib1.request, requests.get, 'http://super.cool/api')
        self.assertRaisesRegexp(RuntimeError, 'API is crappy', self.MyLib2.request, requests.get, 'http://super.cool/api')
        self.MyLib3.request(requests.get, 'http://super.cool/api')  # nothing raised as on_exception is OnException.return_response

        requests = mock.Mock(get=mock.Mock(side_effect=MemoryError('Wow, how did it happen?')))
        self.assertRaisesRegexp(MemoryError, 'Wow, how did it happen?', self.MyLib1.request, requests.get, 'http://super.cool/api')
        self.assertRaisesRegexp(RuntimeError, 'API is crappy', self.MyLib2.request, requests.get, 'http://super.cool/api')
        self.assertRaisesRegexp(MemoryError, 'Wow, how did it happen?', self.MyLib3.request, requests.get, 'http://super.cool/api')


class ViewsetRestApiLibTestCase(TestCase):
    def test_basic_resource_mixins_inheritance(self):
        lib = ViewsetRestApiLib()

        for mixin in (ListMixin, CreateMixin, RetrieveMixin, UpdateMixin, DeleteMixin):
            self.assertIsInstance(lib, mixin)
