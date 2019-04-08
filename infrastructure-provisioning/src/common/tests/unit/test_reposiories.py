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
    def test_find_one(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('key')

        self.assertEqual('value', val)

    @patch.dict('os.environ', MOCK_ENVIRON)
    def test_find_all(self):
        self.repo = repositories.EnvironRepository()
        data = self.repo.find_all()

        self.assertIn('key', data.keys())

    def test_find_one_wrong_key(self):
        self.repo = repositories.EnvironRepository()
        val = self.repo.find_one('wrong_key')

        self.assertIsNone(val)

    @patch.dict('os.environ', MOCK_ENVIRON_LOWER_CASE)
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
        none_json_object = 'not_json_content'
        err_msg = repositories.JSONContentRepository.LC_NOT_JSON_CONTENT

        with self.assertRaises(exceptions.DLabException) as context:
            repositories.JSONContentRepository(none_json_object)

        self.assertTrue(err_msg, str(context.exception))


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
        err_msg = self.repo.LC_ERR_WRONG_ARGUMENTS
        sys.argv.append('argument')

        with self.assertRaises(exceptions.DLabException) as context:
            self.repo.find_one('option')

        self.assertTrue(err_msg, str(context.exception))


def config_repo_mock():

    def wrapper(cls):
        if six.PY2:
            parser = 'ConfigParser.ConfigParser.'
        else:
            parser = 'configparser.ConfigParser.'

        with patch(parser + 'sections', return_value=['section']):
            with patch(parser + 'options', return_value=['key']):
                with patch(parser + 'get', return_value='value'):
                    return cls
    return wrapper


# TODO: merge 4 decorators in one and remove args
# TODO: implement BaseRepositoryTestCase
class TestConfigRepository(unittest.TestCase):
    MOCK_FILE_PATH = '/tmp/test.ini'

    if six.PY2:
        PARSER = 'ConfigParser.ConfigParser.'
    else:
        PARSER = 'configparser.ConfigParser.'

    PARSER_SECTIONS = PARSER + 'sections'
    PARSER_OPTIONS = PARSER + 'options'
    PARSER_GET = PARSER + 'get'

    VALUE_SECTIONS = ['section']
    VALUE_KEY = ['key']
    VALUE_VALUE = 'value'

    def setUp(self):
        self.targets = {
            'sections': 'sections',
            'options': 'options',
            'get': 'get',
        }

        for key, val in self.targets.items():
            self.targets.update({key: self.PARSER + val})

    @patch('os.path.isfile', return_value=True)
    @patch(PARSER_SECTIONS, return_value=VALUE_SECTIONS)
    @patch(PARSER_OPTIONS, return_value=VALUE_KEY)
    @patch(PARSER_GET, return_value=VALUE_VALUE)
    def test_find_one(self, *args):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = repo.find_one('section_key')

        self.assertEqual('value', val)

    @config_repo_mock
    @patch('os.path.isfile', return_value=True)
    def test_find_all(self, *args):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        data = repo.find_all()
        self.assertEqual({'section_key': 'value'}, data)

    @patch('os.path.isfile', return_value=True)
    @patch(PARSER_SECTIONS, return_value=VALUE_SECTIONS)
    @patch(PARSER_OPTIONS, return_value=VALUE_KEY)
    @patch(PARSER_GET, return_value=VALUE_VALUE)
    def test_find_one_wrong_key(self, * args):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        val = repo.find_one('wrong_key')

        self.assertIsNone(val)

    def test_file_not_exist(self):
        err_msg = repositories.ConfigRepository.LC_NO_FILE.format(
            file_path=self.MOCK_FILE_PATH
        )

        with self.assertRaises(Exception) as context:
            repositories.ConfigRepository(self.MOCK_FILE_PATH)

        self.assertEqual(err_msg, str(context.exception))

    @patch('os.path.isfile', return_value=True)
    def test_file_exist_check(self, *args):
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)

        self.assertEqual(self.MOCK_FILE_PATH, repo.file_path)

    @patch('os.path.isfile', return_value=True)
    def test_change_file(self, *args):
        file_path = '/tmp/new_test.ini'
        repo = repositories.ConfigRepository(self.MOCK_FILE_PATH)
        repo.file_path = '/tmp/new_test.ini'

        self.assertEqual(file_path, repo.file_path)


'''
class TestSQLiteRepository(unittest.TestCase):
    FILE_NAME = 'dblab.db'
    DATA_FILE = os.path.join(BASE_TEST_DIR, PATH_TO_FILE, 'sql_repository', FILE_NAME)
    DB_TABLE = 'config'

    def test_file_exist(self):
        config_repo = SQLiteRepository(self.DATA_FILE, self.DB_TABLE)
        self.assertEqual(config_repo.file_path, self.DATA_FILE)

    def test_empty_file_path(self):
        file_path = ''
        with self.assertRaises(DLabException):
            config_repo = SQLiteRepository(file_path, self.DB_TABLE)
            self.assertEqual(
                'Cant specify file with path {file_path}'.format(file_path=file_path),
                str(config_repo.exception)
            )

    def test_file_not_exist(self):
        file_path = self.DATA_FILE + 'test'
        with self.assertRaises(DLabException):
            config_repo = SQLiteRepository(file_path, self.DB_TABLE)
            self.assertEqual(
                'Cant specify file with path {file_path}'.format(file_path=file_path),
                str(config_repo.exception)
            )

    def test_wrong_table_name(self):
        file_path = self.DATA_FILE
        table_name = self.DB_TABLE + 'test'
        with self.assertRaises(DLabException):
            config_repo = SQLiteRepository(file_path, table_name)
            self.assertIn(
                'Error while data reading with message ',
                str(config_repo.data)
            )

    def test_find_one(self):
        config_repo = SQLiteRepository(self.DATA_FILE, self.DB_TABLE)
        config = config_repo.find_one('conf_os_user')
        self.assertEqual('dlab-user', config)

    def test_find_one_wrong_key(self):
        config_repo = SQLiteRepository(self.DATA_FILE, self.DB_TABLE)
        config = config_repo.find_one('test')
        self.assertIsNone(config)

    def test_find_all(self):
        config_repo = SQLiteRepository(self.DATA_FILE, self.DB_TABLE)
        configs = config_repo.find_all()
        self.assertIn('conf_os_user', configs.keys())
'''
