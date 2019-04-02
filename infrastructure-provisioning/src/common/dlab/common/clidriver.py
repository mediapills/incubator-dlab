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

# TODO redesign nodes and controllers and use wrapper like in custodian plugins
# TODO https://packaging.python.org/guides/creating-and-discovering-plugins/

import argparse
import logging

from dlab.common.controllers import BaseController
from dlab import common


class CLIDriver:
    def __init__(self):
        self._logger = None
        self._controllers = []

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging
            self._logger.basicConfig(level=logging.DEBUG)

        return self._logger

    @property
    def option(self):
        return 'aws'

    def register(self, controller):
        self._controllers.append(controller)

    @property
    def controller(self):
        choices = []
        print common.CONTROLLERS
        for c in self._controllers:  # type: BaseController
            if c.provider() == self.option:
                return c(self.logger)
            choices.append(c.provider())

        parser = argparse.ArgumentParser()
        parser.add_argument('--provider', choices=choices)
        parser.parse_args(['--provider', self.option])
