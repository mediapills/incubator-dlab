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
from mock import patch
import sys
import six
import unittest

from dlab.common import exceptions, repositories


def mock_data_base(func):
    def wrapper(*args):
        with patch('sqlite3.connect') as con:
            con.return_value.execute.return_value.fetchall.return_value = (('section_key', 'value'),)
            with patch('os.path.isfile', return_value=True):
                return func(*args)
    return wrapper


def config_parser_mock(isfileonly=False):

    def decorator(func):

        def wrapper(*args):

            if isfileonly:
                with patch('os.path.isfile', return_value=True):
                    return func(*args)

            # TODO: get parser name from repository.ConfigParser
            if six.PY2:
                parser = 'ConfigParser.ConfigParser.'
            else:
                parser = 'configparser.ConfigParser.'

            with patch(parser + 'sections', return_value=['section']):
                with patch(parser + 'options', return_value=['key']):
                    with patch(parser + 'get', return_value='value'):
                        with patch('os.path.isfile', return_value=True):
                            return func(*args)

        return wrapper

    return decorator


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


class TestArrayRepository(BaseRepositoryTestCase, unittest.TestCase):

    def setUp(self):
        self.repo = repositories.ArrayRepository()

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
    MOCK_ENVIRON = {'key': 'value'}
    MOCK_ENVIRON_LOWER_CASE = {'lower_case_key': 'lower_case_value'}
    MOCK_ENVIRON_UPPER_CASE = {'UPPER_CASE_KEY': 'upper_case_value'}

    @patch.dict('os.environ', MOCK_ENVIRON)
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
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

    @patch.dict('os.environ', MOCK_ENVIRON_LOWER_CASE)
    @unittest.skipIf(sys.platform == 'win32', reason="does not run on windows")
    def test_lower_case_sensitivity(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('lower_case_key')

        self.assertEqual('lower_case_value', val)
        self.assertIsNone(self.repo.find_one('LOWER_CASE_KEY'))

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
    MOCK_FILE_PATH = '/tmp/test.ini'
    if six.PY2:
        parser = 'ConfigParser.ConfigParser.'
    else:
        parser = 'configparser.ConfigParser.'

    @config_parser_mock()
    def test_find_one(self):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = repo.find_one('section_key')

        self.assertEqual('value', val)

    @config_parser_mock()
    def test_find_all(self):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        data = repo.find_all()
        self.assertEqual({'section_key': 'value'}, data)

    @config_parser_mock()
    def test_find_one_wrong_key(self):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_file_not_exist(self):
        with self.assertRaises(exceptions.DLabException):
            repositories.ConfigRepository(self.MOCK_FILE_PATH)

    @config_parser_mock(isfileonly=True)
    def test_file_exist_check(self, *args):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)

        self.assertEqual(self.MOCK_FILE_PATH, repo.file_path)

    @config_parser_mock(isfileonly=True)
    def test_change_file(self, *args):
        file_path = '/tmp/new_test.ini'
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        repo.file_path = '/tmp/new_test.ini'

        self.assertEqual(file_path, repo.file_path)

    @config_parser_mock()
    def test_lower_case_sensitivity(self, *args):
        self.repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = self.repo.find_one('section_key')
        self.assertEqual('value', val)
        self.assertIsNone(self.repo.find_one('SECTION_KEY'))

    # TODO: check how refactor this
    @config_parser_mock(isfileonly=True)
    @patch(parser + 'sections', return_value=['SECTION'])
    @patch(parser + 'options', return_value=['KEY'])
    @patch(parser + 'get', return_value='value')
    def test_upper_case_sensitivity(self, *args):
        self.repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = self.repo.find_one('SECTION_KEY')

        self.assertEqual('value', val)
        self.assertIsNone(self.repo.find_one('section_key'))


class TestSQLiteRepository(BaseRepositoryTestCase, unittest.TestCase):
    MOCK_FILE_PATH = '/tmp/test.db'
    DB_TABLE = 'config'
    GET_QUERY_TEMPLATE = 'SELECT key, value FROM {}'

    @patch('os.path.isfile', return_value=True)
    def test_file_exist(self, *args):
        config_repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        self.assertEqual(config_repo.file_path, self.MOCK_FILE_PATH)

    def test_file_not_exist(self):
        with self.assertRaises(exceptions.DLabException):
            repositories.ConfigRepository(self.MOCK_FILE_PATH)

    @patch('os.path.isfile', return_value=True)
    def test_wrong_table_name(self, *args):
        table_name = self.DB_TABLE + 'test'
        with self.assertRaises(exceptions.DLabException):
            config_repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, table_name)
            self.assertIn(
                'Error while data reading with message ',
                str(config_repo.data)
            )

    @mock_data_base
    def test_find_one(self, *args):
        config_repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        config = config_repo.find_one('section_key')
        self.assertEqual('value', config)

    @mock_data_base
    def test_find_one_wrong_key(self):
        config_repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        config = config_repo.find_one('test')
        self.assertIsNone(config)

    @mock_data_base
    def test_find_all(self):
        config_repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        configs = config_repo.find_all()
        self.assertEqual({'section_key': 'value'}, configs)

    @mock_data_base
    def test_lower_case_sensitivity(self, *args):
        self.repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        val = self.repo.find_one('section_key')
        self.assertEqual('value', val)
        self.assertIsNone(self.repo.find_one('SECTION_KEY'))

    @patch('os.path.isfile', return_value=True)
    @patch('sqlite3.connect')
    def test_upper_case_sensitivity(self, con, *args):
        con.return_value.execute.return_value.fetchall.return_value = (('SECTION_KEY', 'value'),)
        self.repo = repositories.SQLiteRepository(self.MOCK_FILE_PATH, self.DB_TABLE)
        val = self.repo.find_one('SECTION_KEY')

        self.assertEqual('value', val)
        self.assertIsNone(self.repo.find_one('section_key'))


class TestChainOfRepositories(BaseRepositoryTestCase, unittest.TestCase):

    @patch('dlab.common.repositories.ConfigRepository')
    def test_register_repo(self, repository):
        repo = repositories.ChainOfRepositories()
        repo.register(repository)
        self.assertEqual(len(repo._repos), 1)

    @patch('dlab.common.repositories.ConfigRepository')
    def test_find_all(self, repository):
        repository.data = {'section_key': 'value'}
        repo = repositories.ChainOfRepositories([repository])
        configs = repo.find_all()
        self.assertEqual({'section_key': 'value'}, configs)

    @patch('dlab.common.repositories.ConfigRepository')
    def test_find_one(self, repository):
        repository.find_one.return_value = 'value'
        repo = repositories.ChainOfRepositories([repository])
        config = repo.find_one('section_key')
        self.assertEqual('value', config)

    @patch('dlab.common.repositories.ConfigRepository')
    def test_find_one_wrong_key(self, repository):
        repository.find_one.return_value = None
        repo = repositories.ChainOfRepositories([repository])
        config = repo.find_one('test')
        self.assertIsNone(config)

    @patch('dlab.common.repositories.ConfigRepository')
    def test_lower_case_sensitivity(self, repository):
        repository.find_one.return_value = 'value'
        repo = repositories.ChainOfRepositories([repository])
        val = repo.find_one('section_key')
        self.assertEqual('value', val)
        self.assertNotEqual(repo.find_one('section_key'), {'SECTION_KEY': 'value'})

    @patch('dlab.common.repositories.ConfigRepository')
    def test_upper_case_sensitivity(self, repository):
        repository.find_one.return_value = {'SECTION_KEY': 'value'}
        repo = repositories.ChainOfRepositories([repository])
        val = repo.find_one('SECTION_KEY')
        self.assertEqual({'SECTION_KEY': 'value'}, val)
        self.assertNotEqual(repo.find_one('section_key'), {'section_key': 'value'})
