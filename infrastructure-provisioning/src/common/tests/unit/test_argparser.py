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
import sys
import unittest

from mock import patch

from dlab.clidriver import create_clidriver
from dlab.common import constants
from dlab.common.argparser import CommandAgrParser, HelpCommand, SubCommandAgrParser


class TestAgrParser(unittest.TestCase):
    MOCK_ARGS_MAIN = ['ssn']
    MOCK_ARGS = ['ssn', 'run']
    MOCK_ARGS_WITH_NAME = [__name__, 'ssn', 'run']

    def setUp(self):
        self.clidriver = create_clidriver()

    @patch('sys.argv', MOCK_ARGS)
    def test_init_parser(self):

        self.assertIsInstance(self.clidriver.parser, CommandAgrParser)

    @patch('sys.argv', MOCK_ARGS + [constants.HELP_KEY])
    def test_has_help(self):

        self.assertTrue(self.clidriver.parser.has_help(args=sys.argv))

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_command_parsed_args(self):
        self.clidriver._init_parser()

        self.assertTrue(hasattr(self.clidriver._parsed_args, constants.COMMAND_NAME))
        self.assertEqual(self.clidriver._parsed_args.command, 'ssn')

    @patch('sys.argv', MOCK_ARGS)
    def test_remaining(self):
        parsed_args, remaining = self.clidriver.parser.parse_known_args(sys.argv)

        self.assertIn('run', remaining)

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_args(self):
        self.clidriver._init_parser()

        self.assertTrue(hasattr(self.clidriver._parsed_args, constants.SUB_COMMAND_NAME))
        self.assertEqual(self.clidriver._parsed_args.subcommand, 'run')

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_help_file(self):
        self.clidriver._init_parser()
        help = HelpCommand()

        self.assertIsInstance(help._get_file(self.clidriver._parsed_args), str)

    @patch('sys.argv', [__name__, 'ssss',  'help'])
    def test_help_file_is_none(self):
        with self.assertRaises(SystemExit):
            self.clidriver._init_parser()

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_command_build(self):
        command_parser = CommandAgrParser()

        self.assertEqual(command_parser._actions[0].dest, constants.COMMAND_NAME)
        self.assertEqual(command_parser._actions[0].choices, command_parser.build_command_table())

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_subcommand_build(self):
        command_parser = SubCommandAgrParser('ssn')

        self.assertEqual(command_parser._actions[0].dest, constants.SUB_COMMAND_NAME)
        self.assertEqual(command_parser._actions[0].choices, command_parser.build_command_table())

    @patch('sys.argv', MOCK_ARGS_WITH_NAME)
    def test_subcommand_build_wrong_command(self):

        with self.assertRaises(KeyError):
            command_parser = SubCommandAgrParser('sss')

