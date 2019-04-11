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
import argparse
import sys
import six
import unittest

from dlab.common import exceptions, repositories
from mock import patch


# TODO: check keys and values with quotes, single and double
def config_parser_mock(data):

    def decorator(func):

        def wrapper(*args):
            parser = '.'.join([repositories.ConfigParser.__module__, repositories.ConfigParser.__name__])
            with patch(parser + '.sections', return_value=data['s']):
                with patch(parser + '.options', return_value=data['k']):
                    with patch(parser + '.get', return_value=data['v']):
                        return func(*args)

        return wrapper

    return decorator


def sqlite3_mock(data=()):

    def decorator(func):

        def wrapper(*args):
            with patch('sqlite3.connect') as con:
                con.return_value.execute.return_value.fetchall.return_value = data
                return func(*args)

        return wrapper

    return decorator


def file_exists_mock(func):

    def wrapper(*args):
        with patch('os.path.isfile', return_value=True):
            return func(*args)

    return wrapper


@six.add_metaclass(abc.ABCMeta)
class BaseRepositoryTestCase:

    @abc.abstractmethod
    def test_find_one(self):
        pass

    @abc.abstractmethod
    def test_find_all(self):
        pass

    @abc.abstractmethod
    def test_find_one_wrong_key(self):
        pass

    @abc.abstractmethod
    def test_lower_case_sensitivity(self):
        pass

    @abc.abstractmethod
    def test_upper_case_sensitivity(self):
        pass

    def test_valid_input_data(self):
        pass

    def test_invalid_input_data(self):
        pass


class TestArrayRepository(BaseRepositoryTestCase, unittest.TestCase):

    def setUp(self):
        self.repo = repositories.ArrayRepository()

    def test_valid_input_data(self):
        self.repo = repositories.ArrayRepository({'key': 'value'})

        self.assertIsInstance(self.repo._data, dict)

    def test_invalid_input_data(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo = repositories.ArrayRepository('value')

    def test_find_one(self):
        self.repo.append('key', 'value')
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        self.repo.append('key', 'value')
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        self.repo.append('lower_case_key', 'lower_case_value')
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        self.repo.append('UPPER_CASE_KEY', 'upper_case_value')
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_append(self):
        self.repo.append('key', 'value')
        self.repo.append('other_key', 'other_value')
        val = self.repo.find_one('other_key')

        self.assertEqual('other_value', val)

    def test_replace(self):
        self.repo.append('key', 'value')
        self.repo.append('key', 'other_value')
        val = self.repo.find_one('key')

        self.assertEqual('other_value', val)


class TestEnvironRepository(BaseRepositoryTestCase, unittest.TestCase):
    # TODO: fix this dicts for win (uppercase them) to
    MOCK_ENVIRON = {'key': 'value'}
    MOCK_ENVIRON_LOWER_CASE = {'lower_case_key': 'lower_case_value'}
    MOCK_ENVIRON_UPPER_CASE = {'UPPER_CASE_KEY': 'upper_case_value'}

    @patch.dict('os.environ', MOCK_ENVIRON)
    def test_find_one(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @patch.dict('os.environ', MOCK_ENVIRON)
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    def test_find_all(self):
        self.repo = repositories.EnvironRepository()
        data = self.repo.find_all()

        self.assertIn('key', data.keys())

    def test_find_one_wrong_key(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    @patch.dict('os.environ', MOCK_ENVIRON_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    @patch.dict('os.environ', MOCK_ENVIRON_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))


class TestJSONContentRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_CONTENT = '{"key": "value"}'
    MOCK_CONTENT_LOWER_CASE = '{"lower_case_key": "lower_case_value"}'
    MOCK_CONTENT_UPPER_CASE = '{"UPPER_CASE_KEY": "upper_case_value"}'

    def test_valid_input_data(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT)

        self.assertIsInstance(self.repo._data, dict)

    def test_invalid_input_data(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo = repositories.JSONContentRepository('value')

    def test_find_one(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT_LOWER_CASE)
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT_UPPER_CASE)
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_reload_content(self):
        self.repo = repositories.JSONContentRepository(self.MOCK_CONTENT)
        self.repo.content = '{"new_key": "new_value"}'
        data = self.repo.find_all()

        self.assertEqual({'new_key': 'new_value'}, data)

    def test_no_json_object(self):
        with self.assertRaises(exceptions.DLabException):
            repositories.JSONContentRepository('not_json_content')


class TestArgumentsRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_ARGS = [
        'unittest_runner.py',
        '--key', 'value',
    ]

    MOCK_ARGS_LOWER_CASE = [
        'unittest_runner.py',
        '--lower_case_key', 'lower_case_value',
    ]

    MOCK_ARGS_UPPER_CASE = [
        'unittest_runner.py',
        '--UPPER_CASE_KEY', 'upper_case_value',
    ]

    def setUp(self):
        self.repo = repositories.ArgumentsRepository()

    def test_valid_input_data(self):
        _arg_parse = argparse.ArgumentParser()
        self.repo = repositories.ArgumentsRepository(_arg_parse)

        self.assertIsInstance(self.repo._arg_parse, argparse.ArgumentParser)

    def test_invalid_input_data(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo = repositories.ArgumentsRepository('value')

    @patch('sys.argv', MOCK_ARGS)
    def test_find_one(self):
        self.repo.add_argument('--key')
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @patch('sys.argv', MOCK_ARGS)
    def test_find_all(self):
        self.repo.add_argument('--key')
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')
        self.assertIsNone(val)

    @patch('sys.argv', MOCK_ARGS_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        self.repo.add_argument('--lower_case_key')
        val = self.repo.find_one('lower_case_key')
        
        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

    @patch('sys.argv', MOCK_ARGS_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        self.repo.add_argument('--UPPER_CASE_KEY')
        val = self.repo.find_one('UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))

    def test_unrecognized_arguments(self):
        sys.argv.append('argument')

        with self.assertRaises(exceptions.DLabException):
            self.repo.find_one('option')


class TestConfigRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_FILE_PATH = '/test.ini'

    MOCK_CONFIG = {
        's': ['section'],
        'k': ['key'],
        'v': 'value',
    }
    MOCK_CONFIG_LOWER_CASE = {
        's': ['section'],
        'k': ['lower_case_key'],
        'v': 'lower_case_value',
    }
    MOCK_CONFIG_UPPER_CASE = {
        's': ['SECTION'],
        'k': ['UPPER_CASE_KEY'],
        'v': 'upper_case_value',
    }

    @file_exists_mock
    def setUp(self):
        self.repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)

    def test_valid_input_data(self):
        self.assertIsInstance(self.repo.file_path, str)

    def test_invalid_input_data(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo = repositories.ConfigRepository({})

    @config_parser_mock(data=MOCK_CONFIG)
    def test_find_one(self):
        val = self.repo.find_one('section_key')

        self.assertEqual('value', val)

    @config_parser_mock(data=MOCK_CONFIG)
    def test_find_all(self):
        data = self.repo.find_all()
        self.assertEqual({'section_key': 'value'}, data)

    @config_parser_mock(data=MOCK_CONFIG)
    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_file_not_exist(self):
        file_path = 'new_test.ini'

        with self.assertRaises(exceptions.DLabException):
            self.repo.file_path = file_path

    @file_exists_mock
    def test_change_file(self):
        file_path = 'new_test.ini'
        self.repo.file_path = file_path

        self.assertEqual(file_path, self.repo.file_path)

    @config_parser_mock(data=MOCK_CONFIG_LOWER_CASE)
    def test_lower_case_sensitivity(self):
        val = self.repo.find_one('section_lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('SECTION_LOWER_CASE_KEY'))

    @config_parser_mock(data=MOCK_CONFIG_UPPER_CASE)
    def test_upper_case_sensitivity(self):
        val = self.repo.find_one('SECTION_UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))


# TODO: investigate why after test i got new files test.db :)
class TestSQLiteRepository(unittest.TestCase):
    MOCK_FILE_PATH = 'test.db'
    DB_TABLE = 'config'
    DATA = (('key', 'value'),)
    DATA_LOWER_CASE = (('lower_case_key', 'lower_case_value'),)
    DATA_UPPER_CASE = (('UPPER_CASE_KEY', 'upper_case_value'),)

    @file_exists_mock
    def setUp(self):
        self.repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)

    def test_valid_input_data(self):
        self.assertIsInstance(self.repo.file_path, str)

    def test_invalid_input_data(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo = repositories.ConfigRepository({})

    def test_file_not_exist(self):
        file_path = 'new_test.ini'

        with self.assertRaises(exceptions.DLabException):
            self.repo.file_path = file_path

    @sqlite3_mock(data=DATA)
    def test_find_one(self):
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @sqlite3_mock(data=DATA)
    def test_find_all(self):
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_table_not_found_exception(self):
        with self.assertRaises(exceptions.DLabException):
            self.repo.find_all()


class TestChainOfRepositories(BaseRepositoryTestCase, unittest.TestCase):

    def setUp(self):
        arr = repositories.ArrayRepository()
        arr.append('key', 'value')

        self.repo = repositories.ChainOfRepositories()
        self.repo.register(arr)

    def test_valid_input_data(self):
        arr = repositories.ArrayRepository()
        self.repo = repositories.ChainOfRepositories(repos=[arr])

        self.assertIn(arr, self.repo._repos)

    def test_invalid_input_data(self):

        with self.assertRaises(exceptions.DLabException):
            repo = repositories.ChainOfRepositories(repos='')

    def test_append_valid(self):
        env = repositories.EnvironRepository()
        self.repo.register(env)

        self.assertIn(env, self.repo._repos)

    def test_append_invalid_repo(self):

        with self.assertRaises(exceptions.DLabException):
            self.repo.register('')

    def test_find_one(self):
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    def test_find_all(self):
        data = self.repo.find_all()

        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_lower_case_sensitivity(self):
        arr = repositories.ArrayRepository()
        arr.append('lower_case_key', 'lower_case_value')
        self.repo.register(arr)
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('SECTION_LOWER_CASE_KEY'))

    def test_upper_case_sensitivity(self):
        arr = repositories.ArrayRepository()
        arr.append('SECTION_UPPER_CASE_KEY', 'upper_case_value')
        self.repo.register(arr)
        val = self.repo.find_one('SECTION_UPPER_CASE_KEY')

        self.assertEqual('upper_case_value', val)
        self.assertIsNone(self.repo.find_one('upper_case_key'))
