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

# TODO: redesign multi inheritance on mixin

import abc
import six

from dlab.common.nodes import action
from dlab.common import node

from dlab.common.repositories import ArrayRepository

registry = ArrayRepository()


def register(key):
    """Register a class as a plug-in"""
    def wrapper(cls):
        # TODO show error if key already exists
        registry.append(key, cls.__name__)
        return cls

    return wrapper


@six.add_metaclass(abc.ABCMeta)
class BaseProcessManager:

    @action.register(action.ACTION_RUN)
    @abc.abstractmethod
    def run(self):
        pass

    @action.register(action.ACTION_TERMINATE)
    @abc.abstractmethod
    def terminate(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseServiceManager:

    @action.register(action.ACTION_START)
    @abc.abstractmethod
    def start(self):
        pass

    @action.register(action.ACTION_STOP)
    @abc.abstractmethod
    def stop(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseLibrariesManager:

    @action.register(action.ACTION_LIBRARIES_INSTALL)
    @abc.abstractmethod
    def libraries_install(self):
        pass

    @action.register(action.ACTION_LIBRARIES_SHOW)
    @abc.abstractmethod
    def libraries_show(self):
        pass


@register(node.TYPE_DATA_ENGINE_NODE)
@six.add_metaclass(abc.ABCMeta)
class BaseDataEngineNode(node.BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):
    pass


@register(node.TYPE_DATA_ENGINE_SERVER_NODE)
@six.add_metaclass(abc.ABCMeta)
class BaseDataEngineServerNode(node.BaseNode, BaseProcessManager, BaseLibrariesManager):
    pass


@register(node.TYPE_EDGE_NODE)
@six.add_metaclass(abc.ABCMeta)
class BaseEDGENode(node.BaseNode, BaseProcessManager, BaseServiceManager):

    @action.register(action.ACTION_GET_STATUS)
    @abc.abstractmethod
    def get_status(self):
        pass

    @action.register(action.ACTION_RECREATE)
    @abc.abstractmethod
    def recreate(self):
        pass

    @action.register(action.ACTION_RELOAD_KEYS)
    @abc.abstractmethod
    def reload_keys(self):
        pass


@register(node.TYPE_NOTEBOOK_NODE)
@six.add_metaclass(abc.ABCMeta)
class BaseNotebookNode(node.BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):

    @abc.abstractmethod
    def configure(self):
        pass

    @abc.abstractmethod
    def git_creds(self):
        pass


@register(node.TYPE_SSN_NODE)
@six.add_metaclass(abc.ABCMeta)
class BaseSSNNode(node.BaseNode, BaseProcessManager):
    pass
