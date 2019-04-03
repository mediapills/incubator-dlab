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
import argparse
import sys
from contextlib import contextmanager

import six
import os


from dlab.common.exceptions import DLabException


# TODO: support python2 and python3
if six.PY2:
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser


@six.add_metaclass(abc.ABCMeta)
class BaseRepository:

    def __init__(self):
        self._data = {}

    @property
    def data(self):
        return self._data

    def find_one(self, key):
        return self.data.get(key)

    def find_all(self):
        return self.data


class ArrayRepository(BaseRepository):

    def __init__(self, data=None):
        super(ArrayRepository, self).__init__()
        if data is not None:
            self._data = data

    def append(self, key, value):
        self._data[key] = value


class EnvironRepository(BaseRepository):

    def __init__(self):
        super(EnvironRepository, self).__init__()
        self._data.update(os.environ)


class JSONContentRepository(BaseRepository):

    LC_NOT_JSON_CONTENT = 'No JSON object could be decoded'

    def __init__(self, content = None):
        super(JSONContentRepository, self).__init__()
        self.content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):

        try:
            json_data = json.loads(content)
            self._data = deepcopy(json_data)
        except ValueError:
            raise DLabException(self.LC_NOT_JSON_CONTENT)

        self._content = content


@six.add_metaclass(abc.ABCMeta)
class BaseLazyLoadRepository(BaseRepository):

    @property
    def data(self):
        if not self._data:
            self._load_data()
        return self._data

    @abc.abstractmethod
    def _load_data(self):
        pass


class ArgumentsRepository(BaseLazyLoadRepository):

    LC_ERR_WRONG_ARGUMENTS = 'Unrecognized arguments'

    def __init__(self, arg_parse=None):
        super(ArgumentsRepository, self).__init__()
        # TODO: check is arg_parse type of ArgumentParser
        if arg_parse is None:
            self._arg_parse = argparse.ArgumentParser()
        else:
            self._arg_parse = arg_parse

    @staticmethod
    @contextmanager
    def _silence_stderr():
        new_target = open(os.devnull, "w")
        old_target = sys.stderr
        sys.stderr = new_target
        try:
            yield new_target
        finally:
            sys.stderr = old_target

    def _load_data(self):
        try:
            with self._silence_stderr():
                args = self._arg_parse.parse_args()
        except SystemExit:
            raise DLabException(self.LC_ERR_WRONG_ARGUMENTS)

        for key, val in vars(args).items():
            self._data[key] = val

    def add_argument(self, *args, **kwargs):
        self._arg_parse.add_argument(*args, **kwargs)
        self._data = {}


@six.add_metaclass(abc.ABCMeta)
class BaseFileRepository(BaseLazyLoadRepository):
    # TODO: Rename error message
    LC_NO_FILE = 'There is no file with path "{file_path}"'

    def __init__(self, absolute_path):
        super(BaseFileRepository, self).__init__()
        self._file_path = None
        self.file_path = absolute_path

    @classmethod
    def _validate(cls, file_path):
        if not os.path.isfile(file_path):
            raise DLabException(cls.LC_NO_FILE.format(
                file_path=file_path
            ))

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, file_path):
        self._validate(file_path)
        self._file_path = file_path
        self._data = {}


class ConfigRepository(BaseFileRepository):
    VARIABLE_TEMPLATE = "{0}_{1}"

    def __init__(self, absolute_path):
        super(ConfigRepository, self).__init__(absolute_path)

    def _load_data(self):
        config = ConfigParser()
        config.read(self.file_path)
        for section in config.sections():
            for option in config.options(section):
                var = self.VARIABLE_TEMPLATE.format(section, option)
                if var not in self._data.keys():
                    self._data[var] = config.get(section, option)


class SQLiteRepository(BaseFileRepository):

    GET_QUERY_TEMPLATE = 'SELECT key, value FROM {}'
    LC_READING_ERROR = 'Error while data reading with message {msg}.'

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
            raise DLabException(self.LC_READING_ERROR.format(
                msg=str(e)
            ))


class ChainOfRepositories(BaseRepository):
    # TODO: maybe data should be dict? NO repos doing this
    # TODO: contact all repos data in one dict? NO repos doing this
    # TODO: investigate this
    def __init__(self, repos=()):
        self._repos = repos or []
        self._data = []

    def register(self, repo):
        self._repos.append(repo)

    def find_one(self, key):
        for repo in self._repos:
            value = repo.get(key)
            if value is not None:
                return value

        return None

    def find_all(self):
        if not self._data and len(self._repos):
            for repo in self._repos:
                self._data.extend(repo)

        return self._data
