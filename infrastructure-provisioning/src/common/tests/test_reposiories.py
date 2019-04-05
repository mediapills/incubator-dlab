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
import argparse
import os
import unittest

from dlab.common.exceptions import DLabException
from dlab.common.repositories import ConfigRepository, JSONContentRepository, SQLiteRepository, ArgumentsRepository, \
    EnvironRepository, ArrayRepository

BASE_TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_FILE = os.path.join(BASE_TEST_DIR, 'tests', 'test_data')


class TestConfigRepository(unittest.TestCase):
    FILE_NAME = 'dlab.ini'
    DATA_FILE = os.path.join(BASE_TEST_DIR, PATH_TO_FILE, 'config_repository', FILE_NAME)

    def test_file_exist(self):
        config_repo = ConfigRepository(self.DATA_FILE)
        self.assertEqual(config_repo.file_path, self.DATA_FILE)

    def test_empty_file_path(self):
        file_path = ''
        with self.assertRaises(DLabException):
            config_repo = ConfigRepository(file_path)
            self.assertEqual(
                'Cant specify file with path {file_path}'.format(file_path=file_path),
                str(config_repo.exception)
            )

    def test_file_not_exist(self):
        file_path = self.DATA_FILE + 'test'
        with self.assertRaises(DLabException):
            config_repo = ConfigRepository(file_path)
            self.assertEqual(
                'Cant specify file with path {file_path}'.format(file_path=file_path),
                str(config_repo.exception)
            )

    def test_find_one(self):
        config_repo = ConfigRepository(self.DATA_FILE)
        config = config_repo.find_one('conf_os_user')
        self.assertEqual('dlab-user', config)

    def test_find_one_wrong_key(self):
        config_repo = ConfigRepository(self.DATA_FILE)
        config = config_repo.find_one('test')
        self.assertIsNone(config)

    def test_find_all(self):
        config_repo = ConfigRepository(self.DATA_FILE)
        configs = config_repo.find_all()
        self.assertIn('conf_os_user', configs.keys())

    def test_change_file(self):
        test_file = 'dlab_test.ini'
        config_repo = ConfigRepository(self.DATA_FILE)
        configs = config_repo.find_all()
        self.assertIn('conf_os_user', configs.keys())
        config_repo.file_path = os.path.join(PATH_TO_FILE, 'config_repository', test_file)
        configs = config_repo.find_all()
        self.assertNotIn('conf_os_user', configs.keys())
        self.assertIn('conf_key_dir', configs.keys())


class TestJSONContentRepository(unittest.TestCase):
    TEST_JSON_DATA = """
                      {
                      "@class": "com.epam.dlab.dto.userenvironmentresources",
                      "aws_iam_user": "dlab_user2@epam.com",
                      "aws_region": "us-west-2",
                      "aws_subnet_id": "subnet-22db937a",
                      "aws_security_groups_ids": "sg-4d42dc35,sg-f19a0389,sg-71e27b09,sg-d3e67fab",
                      "aws_vpc_id": "vpc-83c469e4",
                      "conf_tag_resource_id": "user:tag",
                      "aws_notebook_subnet_id": "subnet-22db937a",
                      "aws_notebook_vpc_id": "vpc-83c469e4",
                      "edge_user_name": "dlab_user2",
                      "conf_service_base_name": "rc21-k",
                      "conf_os_family": "debian",
                      "edge_list_resources": {
                        "host": [
                          {
                            "id": "i-087ed5dec87c4a9d6",
                            "resourceType": "EDGE"
                          }
                        ],
                        "cluster": [
                        ]
                      }
                    }"""

    def test_find_one(self):
        json_repo = JSONContentRepository(self.TEST_JSON_DATA)
        config = json_repo.find_one("aws_region")
        self.assertEqual("us-west-2", config)

    def test_find_all(self):
        json_repo = JSONContentRepository(self.TEST_JSON_DATA)
        configs = json_repo.find_all()
        self.assertIn('aws_vpc_id', configs.keys())

    def test_find_one_wrong_key(self):
        json_repo = JSONContentRepository(self.TEST_JSON_DATA)
        config = json_repo.find_one("aws_region1")
        self.assertIsNone(config)

    def test_load_data(self):
        json_repo = JSONContentRepository(self.TEST_JSON_DATA)
        config = json_repo.find_all()
        self.assertEqual(len(config.keys()), 13)

    def test_load_none_json_object(self):
        none_json_object = 'none_json_object'
        with self.assertRaises(DLabException):
            json_repo = JSONContentRepository(none_json_object)
            self.assertEqual(
                'Can\'t parse content is not JSON object.',
                str(json_repo.data)
            )


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


class TestArgumentsRepository(unittest.TestCase):
    TEST_ARGUMENTS = {
            '--conf_service_base_name': {
                'help': 'unique name for DLab environment',
            },
            '--conf_network_type': {
                'default': '',
                'help': 'Define in which network DLab will be deployed. Possible options: public|private',
            }
        }
    TEST_PARAMS = ['--conf_network_type', 'test', '--conf_service_base_name', 'test2']

    def setUp(self):
        self.arguments = argparse.ArgumentParser()
        for key, value in self.TEST_ARGUMENTS.items():
            self.arguments.add_argument(key, **value)

    def test_add_argument(self):
        arg_repo = ArgumentsRepository(self.arguments)
        arg_repo.add_argument('--provider', default='')
        self.assertIn('provider', arg_repo.data.keys())

    def test_find_one(self):
        arg_repo = ArgumentsRepository(self.arguments, self.TEST_PARAMS)
        conf = arg_repo.find_one('conf_network_type')
        self.assertEqual('test', conf)

    def test_find_all(self):
        arg_repo = ArgumentsRepository(self.arguments, self.TEST_PARAMS)
        conf = arg_repo.find_all()
        self.assertIn('conf_network_type', conf.keys())

    def test_find_one_wrong_key(self):
        arg_repo = ArgumentsRepository(self.arguments, self.TEST_PARAMS)
        conf = arg_repo.find_one('conf_network_type_test')
        self.assertIsNone(conf)


class TestEnvironRepository(unittest.TestCase):

    def setUp(self):
        os.environ['conf_os_user'] = 'dlab-user'
        os.environ['conf_os_user2'] = 'dlab-user2'
        self.env_repo = EnvironRepository()

    def test_find_one(self):
        conf = self.env_repo.find_one('conf_os_user')
        self.assertEqual('dlab-user', conf)

    def test_find_all(self):
        conf = self.env_repo.find_all()
        self.assertIn('conf_os_user2'.upper(), conf.keys())

    def test_find_one_wrong_key(self):
        conf = self.env_repo.find_one('conf_os_user3')
        self.assertIsNone(conf)


class TestArrayRepository(unittest.TestCase):

    def setUp(self):
        self.arr_repo = ArrayRepository()
        self.arr_repo.append('conf_os_user2', 'dlab-user2')

    def test_append(self):
        self.arr_repo.append('conf_os_user', 'dlab-user')
        self.assertIn('conf_os_user', self.arr_repo._data.keys())

    def test_find_one(self):
        conf = self.arr_repo.find_one('conf_os_user')
        self.assertEqual('dlab-user', conf)

    def test_find_all(self):
        conf = self.arr_repo.find_all()
        self.assertIn('conf_os_user2', conf.keys())

    def test_find_one_wrong_key(self):
        conf = self.arr_repo.find_one('conf_os_user3')
        self.assertIsNone(conf)
