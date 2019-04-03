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

# TODO Nodes deployment versions nodes with new and old deployment procedures


import abc
import six
import sys
import argparse
import nodes
from repositories import ArrayRepository


controllers = ArrayRepository()


# TODO code duplication for nodes
def register(key):
    """Register a class as a plug-in"""
    def wrapper(cls):
        # TODO show error if key already exists
        controllers.append(key, cls)
        setattr(cls, '_type', key)
        return cls

    return wrapper


@six.add_metaclass(abc.ABCMeta)
class BaseController:
    LC_NODE_CLI_HELP = 'TODO: Add help here'

    NODES = {
        nodes.SSNNode.NODE_TYPE: 'ssn_node',
        nodes.EDGENode.NODE_TYPE: 'edge_node',
        nodes.NotebookNode.NODE_TYPE: 'notebook_node',
        nodes.DataEngineNode.NODE_TYPE: 'data_engine_node',
        nodes.DataEngineServerNode.NODE_TYPE: 'data_engine_server_node',
    }

    def __init__(self, logger):
        self._type = None
        self._logger = logger
        logger.debug('Init controller "{name}".'.format(
            name=self.__class__.__name__
        ))

    @staticmethod
    def _get_argument():
        return sys.argv[1]

    @property
    def current_node(self):
        option = self._get_argument()
        if option in self.NODES.keys():
            attr = getattr(self, self.NODES[option])
            return attr()

        parser = argparse.ArgumentParser()
        parser.add_argument(
            'node type',
            choices=self.NODES.keys(),
            help=self.LC_NODE_CLI_HELP,
        )
        parser.parse_args([option])

    @property
    @abc.abstractmethod
    def ssn_node(self):
        pass

    @property
    @abc.abstractmethod
    def edge_node(self):
        pass

    @property
    @abc.abstractmethod
    def notebook_node(self):
        pass

    @property
    @abc.abstractmethod
    def data_engine_node(self):
        pass

    @property
    @abc.abstractmethod
    def data_engine_server_node(self):
        pass
