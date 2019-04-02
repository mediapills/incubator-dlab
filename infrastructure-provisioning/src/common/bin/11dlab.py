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

from dlab.common.clidriver import CLIDriver
from dlab.services import aws, gcp

if os.environ.get('LC_CTYPE', '') == 'UTF-8':
    os.environ['LC_CTYPE'] = 'en_US.UTF-8'


def main():
    driver = CLIDriver()
    driver.register(aws.controllers.AWSController)
    driver.register(gcp.controllers.GCPController)

    controller = driver.controller

    # step 2 get action
    # step 3 run action
    # ctl.action()
    pass


if __name__ == '__main__':
    sys.exit(main())
