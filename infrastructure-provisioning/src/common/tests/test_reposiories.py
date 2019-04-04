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
import os
import unittest

from dlab.common.exceptions import DLabException
from dlab.common.repositories import ConfigRepository

FILE_NAME = 'dlab.ini'
BASE_TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_TO_FILE = os.path.join(BASE_TEST_DIR, 'tests', 'test_data', 'config_repository')
DATA_FILE = os.path.join(BASE_TEST_DIR, 'tests', 'test_data', 'config_repository', FILE_NAME)


class TestConfigRepository(unittest.TestCase):

    def test_file_exist(self):
        config_repo = ConfigRepository(DATA_FILE)
        self.assertEqual(config_repo.file_path, DATA_FILE)

    # TODO: check this case
    # def test_empty_file_path(self):
    #     with self.assertRaises(DLabException):
    #         config_repo = ConfigRepository()
    #         self.assertEqual(
    #             'Cant specify file with path {file_path}'.format(file_path=file_path),
    #             str(config_repo.exception)
    #         )

    def test_file_not_exist(self):
        file_path = DATA_FILE + 'test'
        with self.assertRaises(DLabException):
            config_repo = ConfigRepository(file_path)
            self.assertEqual(
                'Cant specify file with path {file_path}'.format(file_path=file_path),
                str(config_repo.exception)
            )

    def test_find_one(self):
        config_repo = ConfigRepository(DATA_FILE)
        config = config_repo.find_one('conf_os_user')
        self.assertEqual('dlab-user', config)

    def test_find_one_wrong_key(self):
        config_repo = ConfigRepository(DATA_FILE)
        config = config_repo.find_one('test')
        self.assertIsNone(config)

    def test_find_all(self):
        config_repo = ConfigRepository(DATA_FILE)
        configs = config_repo.find_all()
        self.assertIn('conf_os_user', configs.keys())
        self.assertIn('aws_edge_instance_size', configs.keys())

    def test_change_file(self):
        test_file = 'dlab_test.ini'
        config_repo = ConfigRepository(DATA_FILE)
        configs = config_repo.find_all()
        self.assertIn('conf_os_user', configs.keys())
        config_repo.file_path = os.path.join(PATH_TO_FILE, test_file)
        configs = config_repo.find_all()
        self.assertNotIn('conf_os_user', configs.keys())
        self.assertIn('conf_key_dir', configs.keys())
