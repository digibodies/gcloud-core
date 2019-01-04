import unittest

from google.cloud import datastore
from gcloud_core.datastore import get_resource_id_from_key
from gcloud_core.datastore import get_key_from_resource_id
from gcloud_core.datastore import get_entity_by_resource_id
from gcloud_core.datastore import get_entity_key_by_keystr
from gcloud_core.datastore import InvalidKeyException
from gcloud_core.datastore import InvalidIdException


class GetResourceIdFromKeyTests(unittest.TestCase):
    def test_keyname(self):
        client = datastore.Client()

        key = client.key('UserEntity', 'does_not_exist')
        expected_id = 'VXNlckVudGl0eR5kb2VzX25vdF9leGlzdA'
        self.assertEquals(expected_id, get_resource_id_from_key(key))

    def test_id(self):
        client = datastore.Client()

        key = client.key('UserEntity', 1)
        expected_id = 'VXNlckVudGl0eR4fMQ'

        self.assertEquals(expected_id, get_resource_id_from_key(key))

    def test_odd_params(self):
        client = datastore.Client()

        # Single - this is a valid key prior to being persisted
        key = client.key('UserEntity')
        with self.assertRaises(InvalidKeyException):
            get_resource_id_from_key(key)

        # Triple - this is a valid key prior to being persisted
        key = client.key('UserEntity', 1, 'Child')
        with self.assertRaises(InvalidKeyException):
            raise Exception(get_resource_id_from_key(key))


class GetKeyFromResourceIdTests(unittest.TestCase):
    def test_keyname(self):
        # Test Key
        key = get_key_from_resource_id('VXNlckVudGl0eR5kb2VzX25vdF9leGlzdA')
        self.assertEquals(('UserEntity', 'does_not_exist'), key.flat_path)

        # A real world key
        key = get_key_from_resource_id('VmVudWUeZ2FtdXQ')
        self.assertEquals(('Venue', 'gamut'), key.flat_path)

    def test_id(self):
        # Test Key
        key = get_key_from_resource_id('VXNlckVudGl0eR4fMQ')
        self.assertEquals(('UserEntity', 1), key.flat_path)

        # A Real World Key
        key = get_key_from_resource_id('RXZlbnQeHzU2OTE5MDI1OTA0NTE3MTI')
        self.assertEquals(('Event', 5691902590451712), key.flat_path)

    def test_incorrect_padding(self):
        with self.assertRaises(InvalidIdException):
            get_key_from_resource_id('VXNlckVudGl0eR5k3')


class GetEntityKeyByKeystrTests(unittest.TestCase):
    def test_base(self):

        # Test Key
        keystr = 'ahZwb2xseXdvZy1kZXYtZGF0YXN0b3JlchALEgpVc2VyRW50aXR5GAEM'
        result = get_entity_key_by_keystr('UserEntity', keystr)
        self.assertEquals('UserEntity', result.kind)
        self.assertEquals(1, result.id)

        # Realish Key
        keystr = 'agpzfmFydHMtNjEychILEgVFdmVudBiAgIDAlZiOCgw'
        result = get_entity_key_by_keystr('Event', keystr)
        self.assertEquals('Event', result.kind)
        self.assertEquals(5691902590451712, result.id)

        # Realish Key
        keystr = 'agpzfmFydHMtNjEychALEgVWZW51ZSIFZ2FtdXQM'
        result = get_entity_key_by_keystr('Venue', keystr)
        self.assertEquals('Venue', result.kind)
        self.assertEquals(None, result.id)
        self.assertEquals('gamut', result.name)

    def test_invalid_kind(self):
        with self.assertRaises(ValueError) as ex:
            keystr = 'ahZwb2xseXdvZy1kZXYtZGF0YXN0b3JlchALEgpVc2VyRW50aXR5GAEM'
            get_entity_key_by_keystr('OtherEntity', keystr)
        err = 'Expected keystr for kind OtherEntity but found kind UserEntity instead.'
        self.assertEqual(err, ex.exception.message)


"""
# This is commented out until we can figure out a replacement for the nosegae stubs
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/datastore/cloud-client/snippets_test.py
class GetEntityByResourceIdTests(unittest.TestCase):
    def test_none(self):
        result = get_entity_by_resource_id('UserEntity', 'VXNlckVudGl0eR4fMQ')
        self.assertIsNone(result)

    def test_entity(self):
        client = datastore.Client()
        complete_key = client.key('UserEntity', 9999)

        task = datastore.Entity(key=complete_key)

        task.update({
            'username': 'test',
        })

        client.put(task)

        # Note: This actually makes an RPC - we must find stub service
        result = get_entity_by_resource_id('UserEntity', 'VXNlckVudGl0eR4fOTk5OQ')
        self.assertEquals('test', result['username'])
"""
