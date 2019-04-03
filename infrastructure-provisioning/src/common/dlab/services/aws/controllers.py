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

import nodes
from dlab.common.controllers import BaseController
from dlab.common import controllers


@controllers.register('aws')
class AWSController(BaseController):

    def ssn_node(self):
        self._logger.debug('AWSController.ssn_node')
        return nodes.AWSSSNNode()

    def edge_node(self):
        self._logger.debug('AWSController.edge_node')
        return nodes.AWSEDGENode()

    def notebook_node(self):
        self._logger.debug('AWSController.notebook_node')
        return nodes.AWSNotebookNode()

    def data_engine_node(self):
        self._logger.debug('AWSController.data_engine_node')
        return nodes.AWSDataEngineNode()

    def data_engine_server_node(self):
        self._logger.debug('AWSController.data_engine_server_node')
        return nodes.AWSDataEngineServerNode()
