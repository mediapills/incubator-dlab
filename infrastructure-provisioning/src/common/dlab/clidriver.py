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
# TODO: CliDriver is Controllers factory
# TODO: mv dlab.* => dlabcli.*
import sys
import signal
import logging

from dlab.common.argparser import CommandAgrParser, SubCommandAgrParser, HelpCommand
from dlab.common.exceptions import DLabException
from dlab.common.controllers import BaseController, registry as cls_registry
from dlab.common import nodes
from dlab.common.logger import Logger


def main():
    driver = create_clidriver()  # type: CLIDriver
    rc = driver.main()
    return rc


def create_clidriver():
    return CLIDriver()


class CLIDriver(object):

    def __init__(self):
        self._logger = Logger()
        self.parser = self._create_parser()
        self._parsed_args = None

    def _get_ctl(self):
        # TODO: implement get option functionality
        option = 'aws'
        # TODO: implement cli help if options not in list

        ctl_name = cls_registry.find_one(option)
        ctl = ctl_name(self._logger)  # type: BaseController
        # TODO: set controller type

        return ctl

    def _get_node(self, ctl):
        # TODO: implement get option functionality
        option = self._parsed_args.command
        # TODO: implement cli help if options not in list
        attr = ctl.get_node(option)
        func = getattr(ctl, attr)
        return func()

    def _run_node(self, node):
        # TODO: implement get option functionality
        action = self._parsed_args.subcommand
        # TODO: implement cli help if options not in list

        result = getattr(node, action)
        return result()

    def _show_error(self, msg):
        self._logger.debug(msg)
        sys.stderr.write(msg)
        sys.stderr.write('\n')

    def _create_parser(self):
        return CommandAgrParser()

    def main(self):
        # try:
        self._init_parser()
        ctl = self._get_ctl()
        node = self._get_node(ctl)  # type: nodes.BaseNode

        return 0

    def _init_parser(self):
        args = sys.argv[1:]
        has_help = self.parser.has_help(args)
        parsed_args, remaining = self.parser.parse_known_args(args)
        if remaining:
            sub_parser = SubCommandAgrParser(parsed_args.command)
            parsed_args, remaining = sub_parser.parse_known_args(args=remaining, namespace=parsed_args)

        if has_help:
            help = HelpCommand()
            help(args, parsed_args)
            sys.exit()
        self._parsed_args = parsed_args

"""
        # except UnknownArgumentError as e:
        #     return 255
        except DLabException:
            self._logger.debug("Exception caught in dlabcli")
            self._logger.debug("Exiting with rc 255")
        except KeyboardInterrupt:
            # Shell standard for signals that terminate
            # the process is to return 128 + signum, in this case
            # SIGINT=2, so we'll have an RC of 130.
            sys.stdout.write("\n")
            return 128 + signal.SIGINT
        except Exception:
            self._logger.debug("Exception caught in main()")
            self._logger.debug("Exiting with rc 255")
            return 255
"""
