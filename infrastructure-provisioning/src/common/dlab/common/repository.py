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


@six.add_metaclass(abc.ABCMeta)
class BaseRepository:
    @abc.abstractmethod
    def _find_one(self, key):
        pass

    @abc.abstractmethod
    def _find_all(self):
        pass

    def find(self, key=None):
        return self._find_one(key) if key is None else self._find_all()


class FileRepository(BaseRepository):
    def __init__(self, filename):
        self._file = filename
        self._data = []

    def _get_data(self):
        if self._data is None:
            print "load data"

        return self._data

    def _find_one(self, key):
        data = self._get_data()
        return data[key]

    def _find_all(self):
        return self._get_data()


class EnvironRepository(BaseRepository):
    def _find_one(self, key):
        return os.environ[key]

    def _find_all(self):
        return os.environ

