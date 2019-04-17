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
from dlab.common.controllers import BaseController
from dlab.common import controllers
from .nodes.dataengine.node import AWSDataEngineNode
from .nodes.dataengineserver.node import AWSDataEngineServerNode
from .nodes.edge.node import AWSEDGENode
from .nodes.notebook.node import AWSNotebookNode
from .nodes.ssn.node import AWSSSNNode
from dlab.common import node


@controllers.register('aws')
class AWSController(BaseController):

    @node.register(node.TYPE_DATA_ENGINE_NODE)
    def get_data_engine_node(self):
        self._logger.debug('AWSController.data_engine_node')
        return AWSDataEngineNode()

    @node.register(node.TYPE_DATA_ENGINE_SERVER_NODE)
    def get_data_engine_server_node(self):
        self._logger.debug('AWSController.data_engine_server_node')
        return AWSDataEngineServerNode()

    @node.register(node.TYPE_EDGE_NODE)
    def get_edge_node(self):
        self._logger.debug('AWSController.edge_node')
        return AWSEDGENode()

    @node.register(node.TYPE_NOTEBOOK_NODE)
    def get_notebook_node(self):
        self._logger.debug('AWSController.notebook_node')
        return AWSNotebookNode()

    @node.register(node.TYPE_SSN_NODE)
    def get_ssn_node(self):
        self._logger.debug('AWSController.ssn_node')
        return AWSSSNNode(logger=self._logger)
