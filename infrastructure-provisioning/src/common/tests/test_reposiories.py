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
import unittest
from mock import patch
import sys
import six

from dlab.common import exceptions, repositories


class TestArrayRepository(unittest.TestCase):

    def setUp(self):
        self.repo = repositories.ArrayRepository()
        self.repo.append('key', 'value')

    def test_find_one(self):
        val = self.repo.find_one('key')
        self.assertEqual('value', val)

    def test_find_all(self):
        data = self.repo.find_all()
        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')
        self.assertIsNone(val)

    def test_append(self):
        self.repo.append('other_key', 'other_value')
        val = self.repo.find_one('other_key')
        self.assertIn('other_value', val)

    def test_replace(self):
        self.repo.append('key', 'other_value')
        val = self.repo.find_one('key')
        self.assertIn('other_value', val)


class TestEnvironRepository(unittest.TestCase):

    def setUp(self):
        with patch.dict('os.environ', {'key': 'value'}):
            self.repo = repositories.EnvironRepository()

    def test_find_one(self):
        val = self.repo.find_one('key')
        self.assertEqual('value', val)

    def test_find_all(self):
        data = self.repo.find_all()
        self.assertIn('key', data.keys())

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')
        self.assertIsNone(val)


class TestJSONContentRepository(unittest.TestCase):

    def setUp(self):
        self.repo = repositories.JSONContentRepository('{"key": "value"}')

    def test_find_one(self):
        val = self.repo.find_one('key')
        self.assertEqual('value', val)

    def test_find_all(self):
        data = self.repo.find_all()
        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')
        self.assertIsNone(val)

    def test_reload_data(self):
        self.repo.content = '{"new_key": "new_value"}'
        data = self.repo.find_all()
        self.assertEqual({'new_key': 'new_value'}, data)

    def test_no_json_object(self):
        none_json_object = 'no_json_object'
        err_msg = self.repo.LC_NOT_JSON_CONTENT

        with self.assertRaises(exceptions.DLabException) as context:
            repositories.JSONContentRepository(none_json_object)
        self.assertTrue(err_msg, str(context.exception))


class TestArgumentsRepository(unittest.TestCase):
    ARGS = [
        'unittest_runner.py',
        '--key', 'value',
    ]

    def setUp(self):
        self.repo = repositories.ArgumentsRepository()

    def test_find_one(self):
        self.repo.add_argument('--key')

        with patch('sys.argv', self.ARGS):
            val = self.repo.find_one('key')
        self.assertEqual('value', val)

    def test_find_all(self):
        self.repo.add_argument('--key')

        with patch('sys.argv', self.ARGS):
            data = self.repo.find_all()
        self.assertEqual({'key': 'value'}, data)

    def test_find_one_wrong_key(self):
        val = self.repo.find_one('wrong_key')
        self.assertIsNone(val)

    def test_unrecognized_arguments(self):
        err_msg = self.repo.LC_ERR_WRONG_ARGUMENTS
        sys.argv.append('argument')

        with self.assertRaises(exceptions.DLabException) as context:
            self.repo.find_one('option')
        self.assertTrue(err_msg, str(context.exception))


class TestConfigRepository(unittest.TestCase):

    FILE_PATH = '/tmp/test.ini'

    def setUp(self):
        parser = 'ConfigParser' if six.PY2 else 'configparser'
        parser += '.ConfigParser'

        self.targets = {
            'sections': '{parser}.sections',
            'options': '{parser}.options',
            'get': '{parser}.get',
        }

        for key, val in self.targets.items():
            self.targets.update({key: val.format(parser=parser)})

    def test_find_one(self):
        with patch('os.path.isfile', return_value=True):
            repo = repositories.ConfigRepository(self.FILE_PATH)

        with patch(self.targets['sections'], return_value=['section']),\
            patch(self.targets['options'],  return_value=['key']),\
                patch(self.targets['get'], return_value=['value']):
            val = repo.find_one('section_key')
        self.assertEqual(['value'], val)

    def test_find_all(self):
        with patch('os.path.isfile', return_value=True):
            repo = repositories.ConfigRepository(self.FILE_PATH)

        with patch(self.targets['sections'], return_value=['section']),\
            patch(self.targets['options'],  return_value=['key']),\
                patch(self.targets['get'], return_value=['value']):
            data = repo.find_all()
        self.assertEqual({'section_key': ['value']}, data)

    def test_find_one_wrong_key(self):
        with patch('os.path.isfile', return_value=True):
            repo = repositories.ConfigRepository(self.FILE_PATH)

        with patch(self.targets['sections'], return_value=['section']),\
            patch(self.targets['options'],  return_value=['key']),\
                patch(self.targets['get'], return_value=['value']):
            val = repo.find_one('wrong_key')
        self.assertIsNone(val)

    def test_file_not_exist(self):
        err_msg = repositories.ConfigRepository.LC_NO_FILE.format(
            file_path=self.FILE_PATH
        )

        with self.assertRaises(Exception) as context:
            repositories.ConfigRepository(self.FILE_PATH)
        self.assertEqual(err_msg, str(context.exception))

    def test_file_exist_check(self):
        with patch('os.path.isfile', return_value=True):
            repo = repositories.ConfigRepository(self.FILE_PATH)
        self.assertEqual(self.FILE_PATH, repo.file_path)

    def test_change_file(self):
        file_path = '/tmp/new_test.ini'

        with patch('os.path.isfile', return_value=True):
            repo = repositories.ConfigRepository(self.FILE_PATH)
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
