#!/usr/bin/env python

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
import os
import logging
import argparse

from dlab.common import CONTROLLERS
from dlab.common.controllers import BaseController

if os.environ.get('LC_CTYPE', '') == 'UTF-8':
    os.environ['LC_CTYPE'] = 'en_US.UTF-8'


def get_logger():
    logger = logging
    logger.basicConfig(level=logging.DEBUG)

    return logger


def get_option():
    return 'aws12'


def get_controller():
    choices = []
    option = get_option()
    for name in CONTROLLERS:  # type: BaseController
        if name == option:
            cls = CONTROLLERS[name]
            return cls(get_logger())
        choices.append(name)

    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=choices)
    parser.parse_args(['--provider', option])


def main():
    # controller = get_controller()
    # node = controller.get_node

    # step 2 get action
    # step 3 run action
    # ctl.action()
    pass


if __name__ == '__main__':
    sys.exit(main())
