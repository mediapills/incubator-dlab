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


class ArrayRepository(BaseRepository):

    def __init__(self, data={}):
        self._data = data

    def append(self, key, value):
        self._data[key] = value

    def find_one(self, key):
        return self._data.get(key)

    def find_all(self):
        return self._data


class ConfigRepository(BaseRepository):
    VARIABLE_TEMPLATE = "{0}_{1}"

    def __init__(self, absolute_path):

        self._data = {}
        self._file_path = None
        self.file_path = absolute_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._validate_file_path(file_path)
        self._file_path = file_path
        self._data = {}

    @staticmethod
    def _validate_file_path(file_path):

        if not file_path:
            raise DLabException('No file location specified.')

        if not os.path.isfile(file_path):
            raise DLabException(
                'There is no file with path {file_path}'.format(
                    file_path=file_path
                )
            )

    @property
    def data(self):
        if not self._data:
            self._load_data()
        return self._data

    def _load_data(self):
        config = configparser.ConfigParser()
        config.read(self.file_path)
        for section in config.sections():
            for option in config.options(section):
                var = self.VARIABLE_TEMPLATE.format(section, option)
                if var not in self._data.keys():
                    self._data[var] = config.get(section, option)

    def find_one(self, key):
        data = self._get_data()
        return data.get(key)

    def find_all(self):
        return self._get_data()


class EnvironRepository(BaseRepository):

    def find_one(self, key):
        return os.environ[key]

    def find_all(self):
        return os.environ


class JSONContentRepository(BaseRepository):

    def __init__(self, content=''):
        self._content = content
        # validate JSON
        # parse JSON
        raise DLabException('Needs to be implemented.')

    def find_one(self, key):
        raise DLabException('Needs to be implemented.')

    def find_all(self):
        raise DLabException('Needs to be implemented.')


class SQLiteRepository(BaseRepository):

    def __init__(self, filename):
        self.filename = filename
        raise DLabException('Needs to be implemented.')

    def find_one(self, key):
        raise DLabException('Needs to be implemented.')

    def find_all(self):
        raise DLabException('Needs to be implemented.')


class ArgumentsRepository(BaseRepository):

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
