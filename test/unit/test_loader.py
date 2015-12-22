import unittest
import os
import json

from unittest.mock import Mock, patch, PropertyMock

from pipeline.loaders import Datapusher, InvalidConfigException

HERE = os.path.abspath(os.path.dirname(__file__))

class TestDatapusher(unittest.TestCase):
    def setUp(self):
        super(TestDatapusher, self).setUp()
        self.data_pusher = Datapusher(
            server='testing',
            settings_file=os.path.join(HERE, 'test_settings.json')
        )

    def test_datapusher_init(self):
        self.assertIsNotNone(self.data_pusher)
        self.assertEquals(self.data_pusher.ckan_url, 'localhost:9000/api/3/')
        self.assertEquals(self.data_pusher.dump_url, 'localhost:9000/datastore/dump/')

    def test_datapusher_exception_no_settings(self):
        with self.assertRaises(InvalidConfigException):
            Datapusher()
        with self.assertRaises(InvalidConfigException):
            Datapusher(
                server='Does not exist',
                settings_file=os.path.join(HERE, 'test_settings.json')
            )

    @patch('requests.post')
    def test_resource_exists(self, post):
        mock_post = Mock()
        mock_post.json.side_effect = [
            {'result': {'resources': []}},
            {'result': {'resources': [{'name': 'NOT EXIST'}]}},
            {'result': {'resources': [{'name': 'exists'}]}},
        ]
        post.return_value = mock_post

        self.assertFalse(self.data_pusher.resource_exists(None, 'exists'))
        self.assertFalse(self.data_pusher.resource_exists(None, 'exists'))
        self.assertTrue(self.data_pusher.resource_exists(None, 'exists'))

    @patch('requests.post')
    def test_create_resource(self, post):
        mock_post = Mock()
        mock_post.json.side_effect = [
            {'success': True, 'result': {'id': 1}},
            {'error': {'name': ['not successful']}}
        ]
        post.return_value = mock_post

        self.assertEquals(self.data_pusher.create_resource(None, None), 1)
        self.assertEquals(self.data_pusher.create_resource(None, None), None)

    @patch('requests.post')
    def test_create_datastore(self, post):
        mock_post = Mock()
        mock_post.json.side_effect = [
            {'success': True, 'result': {'resource_id': 1}},
            {'error': {'name': ['not successful']}}
        ]
        post.return_value = mock_post

        self.assertEquals(self.data_pusher.create_datastore(None, []), 1)
        self.assertEquals(self.data_pusher.create_datastore(None, []), None)

    @patch('requests.post')
    def test_delete_datastore(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=204)
        self.assertEquals(self.data_pusher.delete_datastore(None), 204)

    @patch('requests.post')
    def test_upsert(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=200)
        self.assertEquals(self.data_pusher.upsert(None, None), 200)

    @patch('requests.post')
    def test_update_metadata(self, post):
        type(post.return_value).status_code = PropertyMock(return_value=200)
        self.assertEquals(self.data_pusher.update_metadata(None), 200)