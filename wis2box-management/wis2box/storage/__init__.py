###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

import logging
from typing import Any

from wis2box.env import (STORAGE_TYPE, STORAGE_SOURCE,
                         STORAGE_USERNAME, STORAGE_PASSWORD)
from wis2box.plugin import load_plugin, PLUGINS

LOGGER = logging.getLogger(__name__)

"""
F9 (local fork): four of the six facade functions stripped the bucket name from
the storage path but not the leading slash, so they addressed "/key" where
put_data() wrote "key".

This is invisible against MinIO, whose server collapses the resulting "//key"
request path. minio-py performs no such normalisation client-side
(helpers.check_object_name only rejects "."/".." segments; BaseURL.build emits
"//key" verbatim), so against AWS S3 "/key" is a DISTINCT object and:

  exists()        -> always False  -> is_new always True -> every reprocess
                     rewrites the object and re-emits a WIS2 notification
  delete_data()   -> deletes a nonexistent key; S3 DeleteObject succeeds anyway
  list_content()  -> prefix "//..." matches nothing, so `wis2box data clean`
                     iterates an empty list and reports success having deleted
                     nothing -- storage grows without bound, silently

Verified empirically: see tests/local/test_storage_facade_slash.sh
"""



def exists(path: str) -> bool:
    """
    Check if storage path exists

    :param path: path to check

    :returns: `bool` of result
    """
    LOGGER.debug(f'exists: {path}')
    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    identifier = storage_path.replace(name, '').lstrip('/')

    LOGGER.debug(f'Checking if {identifier} exists')
    return storage.exists(identifier)


def get_data(path: str) -> Any:
    """
    Get data from storage

    :param path: path of object/file

    :returns: content of object/file
    """
    LOGGER.debug(f'get_data from : {path}')
    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    # remove name and leading /
    identifier = storage_path.replace(name, '').lstrip('/')

    LOGGER.debug(f'Fetching data from {identifier}')
    return storage.get(identifier)


def list_content(basepath: str) -> Any:
    """
    List storage paths starting

    :param basepath: basepath

    :returns: list of 'str'-objects
    """
    LOGGER.debug(f'get_data from : {basepath}')
    storage_path = basepath.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    prefix = storage_path.replace(name, '').lstrip('/')

    LOGGER.debug(f'List identifiers matching {prefix}')
    return storage.list_objects(prefix)


def put_data(data: bytes, path: str,
             content_type: str = 'application/octet-stream') -> Any:
    """
    Put data into storage

    :param data: bytes of object/file
    :param path: path to use object id
    :param content_type: media type (default is `application/octet-stream`)

    :returns: content of object/file
    """

    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    identifier = storage_path.replace(name, '').lstrip('/')

    LOGGER.debug(f'Storing data into {identifier}')
    return storage.put(data, identifier, content_type)


def delete_data(path: str) -> Any:
    """
    Delete data from storage

    :param path: path of object/file

    :returns: content of object/file
    """

    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    identifier = storage_path.replace(name, '').lstrip('/')

    LOGGER.debug(f'Delete data for {identifier}')
    return storage.delete(identifier)


def move_data(old_path: str, path: str) -> Any:
    """
    Move data to a new storage-path

    :param path: path of object/file

    :returns: content of object/file
    """

    storage_path = path.replace(f'{STORAGE_SOURCE}/', '')
    name = storage_path.split('/')[0]

    defs = {
        'storage_type': STORAGE_TYPE,
        'source': STORAGE_SOURCE,
        'name': name,
        'auth': {'username': STORAGE_USERNAME, 'password': STORAGE_PASSWORD},
        'codepath': PLUGINS['storage'][STORAGE_TYPE]['plugin']
    }

    LOGGER.debug(f'Connecting to storage: {name}')
    storage = load_plugin('storage', defs)

    identifier = storage_path.replace(name, '').lstrip('/')

    data = get_data(old_path)

    LOGGER.debug(f'Delete data for {identifier}')

    if storage.put(data, identifier):
        return delete_data(old_path)
    else:
        return False
