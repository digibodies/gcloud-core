# Datastore utilities
import binascii
import base64
from google.cloud import datastore

SEPARATOR = chr(30)
INTPREFIX = chr(31)
# Error Templates
_keystr_type_err = 'Keystrings must of type str. Received: %s'
_id_type_err = 'Resource Ids must be an instance of str. Received: %s'
_kind_err = 'Expected keystr for kind %s but found kind %s instead.'
_invalid_id_err = "'%s' is not a valid resource id.'"
_pair_err = 'Key must have an even number of positional pairs. Received: %s'


class Client:
    """
    Singleton Object to ensure we only use one instance per request
    """
    ds_client = None

    def __init__(self):
        if not Client.ds_client:
            Client.ds_client = datastore.Client()

    def __getattr__(self, name):
        if name == 'ds_client':
            return self.ds_client
        return getattr(self.ds_client, name)


def get_resource_id_from_key(key):
    """
    Convert a ndb.Key() into a portable `str` resource id
    :param key: An instance of `google.cloud.Key`
    """
    # https://googleapis.github.io/google-cloud-python/latest/_modules/google/cloud/datastore/key.html
    pair_strings = []
    path = key.flat_path
    if len(path) & 1:  # slightly faster odd check than %
        raise InvalidKeyException(_pair_err % key)

    # Split into pairs
    a = iter(key.flat_path)
    pairs = zip(a, a)

    for pair in pairs:
        kind = str(pair[0])
        key_or_id = pair[1]

        if not (kind and key_or_id):
            raise InvalidKeyException(_pair_err % pair)

        if isinstance(key_or_id, int):
            key_or_id = str(INTPREFIX + str(key_or_id))

        pair_strings.append(kind + SEPARATOR + key_or_id)

    # Rejoin pairs
    buff = SEPARATOR.join(pair_strings).encode('ascii')
    encoded = base64.urlsafe_b64encode(buff)
    encoded = encoded.replace(b'=', b'')
    return encoded.decode()


def get_key_from_resource_id(resource_id):
    """
    Convert a portable `str` resource id into a ndb.Key
    :param resource_id: A `str` resource_id
    """

    # Add padding back on as needed...
    modulo = len(resource_id) % 4
    if modulo != 0:
        resource_id += ('=' * (4 - modulo))

    # decode the url safe resource id
    try:
        decoded = base64.urlsafe_b64decode(str(resource_id)).decode()
    except binascii.Error:
        raise InvalidIdException('Could not base64 decode resource_id')

    key_pairs = []
    bits = decoded.split(SEPARATOR)

    for bit in bits:
        if (bit[0] == INTPREFIX):
            bit = int(bit[1:])
        key_pairs.append(bit)

    return Client().key(*key_pairs)


def get_entity_key_by_keystr(expected_kind, keystr):
    """
    Deprecated legacy helper to get a key for an ndb entity by its urlsafe keystr
    Args:
        expected_kind: The expected kind of ndb.Key as case-sensative string
        keystr: ndb.Key string representation
    Returns:
        An instance of Entity with key of keystr
    Raises:
        ValueError: The keystr is None or of wrong type
        ValueError: The expected_kind does not match the kind of keystr
    """

    if not keystr or not isinstance(keystr, str):
        raise ValueError(_keystr_type_err % keystr)

    # Resolve the ndb key
    ndb_key = datastore.Key.from_legacy_urlsafe(keystr)

    # Validate the kind
    if not ndb_key.kind == expected_kind:
        raise ValueError(_kind_err % (expected_kind, ndb_key.kind))

    return ndb_key


def get_entity_by_resource_id(expected_kind, resource_id):
    """
    Get an entity by its resource_id
    Args:
        expected_kind: The expected kind of `Key` as case-sensative string
        resource_id: Portable string id that resolves to an `Key`
    Returns:
        An instance of Entity corresponding to resource_id
    Raises:
        ValueError: The keystr is None or of wrong type
        ValueError: The expected_kind does not match the kind of keystr
        InvalidIdException: resource_id could not be converted to ndb.Key
    """

    if not resource_id or not isinstance(resource_id, str):
        raise ValueError(_id_type_err % resource_id)

    try:
        # Resolve the datastore key - Note: This will throw if invalid
        key = get_key_from_resource_id(resource_id)

        # Validate the kind
        if not key.kind == expected_kind:
            raise ValueError(_kind_err % (expected_kind, key.kind))

        return Client().get(key)  # Could return None
    except (ValueError, AttributeError, IndexError, TypeError):
        raise InvalidIdException(_invalid_id_err % resource_id)

    return None


class EntityExists(RuntimeError):
    """Exception to throw for duplicate"""
    pass


class InvalidKeyException(ValueError):
    pass


class InvalidIdException(ValueError):
    pass


class DoesNotExistException(RuntimeError):
    pass
