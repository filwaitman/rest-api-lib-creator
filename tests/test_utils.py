from unittest import TestCase

from rest_api_lib_creator.utils import add_querystring_to_url, should_iterate


class AddQuerystringToUrlTestCase(TestCase):
    def test_common(self):
        actual = add_querystring_to_url('http://www.google.com')
        expected = actual
        self.assertEqual(actual, expected)

        actual = add_querystring_to_url('http://www.google.com', test1='super')
        expected = 'http://www.google.com?test1=super'
        self.assertEqual(actual, expected)

        actual = add_querystring_to_url('http://www.google.com', test1='super', test2='amazing')
        expected = 'http://www.google.com?test1=super&test2=amazing'
        self.assertEqual(actual, expected)

        actual = add_querystring_to_url('http://www.google.com?existing=1', test1='super', test2='amazing')
        expected = 'http://www.google.com?existing=1&test1=super&test2=amazing'
        self.assertEqual(actual, expected)

        actual = add_querystring_to_url('http://www.google.com?test1=OLD', test1='super', test2='amazing')
        expected = 'http://www.google.com?test1=super&test2=amazing'
        self.assertEqual(actual, expected)

        actual = add_querystring_to_url('http://www.google.com', **{'user-id': '5'})
        expected = 'http://www.google.com?user-id=5'
        self.assertEqual(actual, expected)


class ShouldIterateTestCase(TestCase):
    def test_common(self):
        self.assertTrue(should_iterate(tuple()))
        self.assertTrue(should_iterate(list()))
        self.assertTrue(should_iterate(set()))

        self.assertTrue(should_iterate([1, 2, 3]))
        self.assertTrue(should_iterate((1, 2, 3)))
        self.assertTrue(should_iterate(set([1, 2, 3])))

        self.assertFalse(should_iterate({'a': 1, 'b': 2}))
        self.assertFalse(should_iterate(42))
        self.assertFalse(should_iterate('test'))
