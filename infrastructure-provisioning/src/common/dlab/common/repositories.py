# *****************************************************************************
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
# ******************************************************************************

import abc
import json
import sqlite3
from copy import deepcopy

import six
import os


from dlab.common.exceptions import DLabException


# TODO: support python2 and python3
if six.PY2:
    import ConfigParser as configparser
else:
    import configparser


@six.add_metaclass(abc.ABCMeta)
class BaseRepository:

    @abc.abstractmethod
    def find_one(self, key):
        pass

    @abc.abstractmethod
    def find_all(self):
        pass


class Repository(BaseRepository):
    def __init__(self):
        self._data = {}

    @property
    def data(self):
        if not self._data:
            self._load_data()
        return self._data

    def _load_data(self):
        self._data = {}

    def find_one(self, key):
        return self.data.get(key)

    def find_all(self):
        return self.data


class FileRepository(Repository):
    def __init__(self, absolute_path):
        self._file_path = None
        self.file_path = absolute_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._validate(file_path)
        self._file_path = file_path
        self._data = {}

    @staticmethod
    def _validate(file_path):

        if not file_path:
            raise DLabException('No file location specified.')

        if not os.path.isfile(file_path):
            raise DLabException(
                'There is no file with path {file_path}'.format(
                    file_path=file_path
                )
            )


class ArrayRepository(Repository):

    def __init__(self, data={}):
        self._data = data

    def append(self, key, value):
        self._data[key] = value

    def find_one(self, key):
        return self._data.get(key)

    def find_all(self):
        return self._data


class ConfigRepository(FileRepository):
    VARIABLE_TEMPLATE = "{0}_{1}"

    def __init__(self, absolute_path):
        super(ConfigRepository, self).__init__(absolute_path)

    def _load_data(self):
        config = configparser.ConfigParser()
        config.read(self.file_path)
        for section in config.sections():
            for option in config.options(section):
                var = self.VARIABLE_TEMPLATE.format(section, option)
                if var not in self._data.keys():
                    self._data[var] = config.get(section, option)


class EnvironRepository(BaseRepository):

    def find_one(self, key):
        return os.environ.get(key)

    def find_all(self):
        return os.environ


class JSONContentRepository(Repository):

    def __init__(self, content):
        super(JSONContentRepository, self).__init__()
        self.content = content

    def _load_data(self):
        try:
            json_data = json.loads(self.content)
            self._data = deepcopy(json_data)
        except ValueError:
            raise DLabException('Can\'t parse content is not JSON object.')


class SQLiteRepository(FileRepository):

    GET_QUERY_TEMPLATE = 'SELECT key, value FROM {}'

    def __init__(self, absolute_path, table_name):
        super(SQLiteRepository, self).__init__(absolute_path)
        self.table_name = table_name

    def _load_data(self):
        try:
            conn = sqlite3.connect(self.file_path)
            c = conn.cursor()
            for row in c.execute(self.GET_QUERY_TEMPLATE.format(self.table_name)):
                self._data[row[0]] = row[1]
        except sqlite3.OperationalError as e:
            raise DLabException(
                'Error while data reading with message {}.'.format(str(e))
            )


class ArgumentsRepository(Repository):

    def __init__(self, argparse=None):
        if argparse is None:
            self._argparse = argparse.ArgumentParser()

        raise DLabException('Needs to be implemented.')

    def add_argument(self, *args, **kwargs):
        raise DLabException('Needs to be implemented.')

    def find_one(self, key):
        raise DLabException('Needs to be implemented.')

    def find_all(self):
        raise DLabException('Needs to be implemented.')


class ChainOfRepositories(BaseRepository):

    def __init__(self, repos=()):
        self._repos = repos
        self._data = []

    def register(self, repo):
        self._repos.append(repo)

    def find_one(self, key):
        for repo in self._repos:
            if repo[key] is not None:
                return repo[key]

        return None

    def find_all(self):
        if not self._data and len(self._repos):
            for repo in self._repos:
                self._data = self._data + repo

        return self._data
