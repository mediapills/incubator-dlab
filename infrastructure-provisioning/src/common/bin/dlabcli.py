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

<<<<<<< HEAD:infrastructure-provisioning/src/common/bin/dlabcli
from dlab.common.controllers import controllers, BaseController
from dlab.common.nodes import BaseNode
=======
from dlab.common.controllers import BaseController, controllers_list
>>>>>>> 60566aff9... Change common package name from dlab.common to dlab_common:infrastructure-provisioning/src/common/bin/dlabcli.py

if os.environ.get('LC_CTYPE', '') == 'UTF-8':
    os.environ['LC_CTYPE'] = 'en_US.UTF-8'


def get_option():
    option = 'aws'

    if controllers.find_one(option):
        return option

<<<<<<< HEAD:infrastructure-provisioning/src/common/bin/dlabcli
    choices = controllers.find_all().keys()
=======
def get_controller():
    choices = []
    option = get_option()
    controllers = controllers_list()
    for name in controllers:  # type: BaseController
        if name == option:
            cls = controllers[name]
            return cls(get_logger())
        choices.append(name)

>>>>>>> 60566aff9... Change common package name from dlab.common to dlab_common:infrastructure-provisioning/src/common/bin/dlabcli.py
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', choices=choices)
    parser.parse_args(['--provider', option])


def main():
<<<<<<< HEAD:infrastructure-provisioning/src/common/bin/dlabcli
    logger = logging
    logger.basicConfig(level=logging.DEBUG)

    option = get_option()
    ctl_name = controllers.find_one(option)
    ctl = ctl_name(logger)  # type: BaseController
=======
    controller = get_controller()
    # node = controller.get_node
>>>>>>> 60566aff9... Change common package name from dlab.common to dlab_common:infrastructure-provisioning/src/common/bin/dlabcli.py

    node = ctl.current_node()  # type: BaseNode
    ctl.execute(node)


if __name__ == '__main__':
    sys.exit(main())
