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

# TODO redesign multi inheritance on mixin
# TODO redesign ACTIONS generation move in __new__ method

import abc
import six


from dlab.common.exceptions import DLabException


@six.add_metaclass(abc.ABCMeta)
class BaseProcessManager:

    ACTION_RUN = 'run'
    ACTION_TERMINATE = 'terminate'

    ACTIONS = (
        ACTION_RUN,
        ACTION_TERMINATE,
    )

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def terminate(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseServiceManager:

    ACTION_START = 'start'
    ACTION_STOP = 'stop'

    ACTIONS = (
        ACTION_START,
        ACTION_STOP,
    )

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseLibrariesManager:

    ACTION_INSTALL_LIBRARIES = 'install_libraries'
    ACTION_SHOW_LIBRARIES = 'show_libraries'

    ACTIONS = (
        ACTION_INSTALL_LIBRARIES,
        ACTION_SHOW_LIBRARIES,
    )

    @abc.abstractmethod
    def install_libraries(self):
        pass

    @abc.abstractmethod
    def show_libraries(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class Node:

    NODE_TYPE = None

    ACTIONS = []

    @classmethod
    def get_type(cls):
        if cls.NODE_TYPE is None:
            raise DLabException("Constant 'NODE_TYPE' needs to be defined")

        return cls.NODE_TYPE

    @classmethod
    def has_action(cls, action):
        return action in cls.ACTIONS

    def execute(self, action):
        if not self.has_action(action):
            raise DLabException("{clsname} does not support action {action}".format(
                clsname=self.__class__.__name__,
                action=action
            ))

        method = getattr(self, action)
        return method()


@six.add_metaclass(abc.ABCMeta)
class SSNNode(Node, BaseProcessManager):

    NODE_TYPE = 'ssn'


@six.add_metaclass(abc.ABCMeta)
class EDGENode(Node, BaseProcessManager, BaseServiceManager):

    ACTIONS = BaseProcessManager.ACTIONS\
              + BaseServiceManager.ACTIONS

    NODE_TYPE = 'edge'

    # get_status() -> do we need this ? node status + all related nodes status
    # recreate() -> ?upgrade? what cases / if node goes down during creation
    # reupload_key() -> need to be removed in SSHKeysManager


@six.add_metaclass(abc.ABCMeta)
class NotebookNode(Node, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
              + BaseServiceManager.ACTIONS\
              + BaseLibrariesManager.ACTIONS

    NODE_TYPE = 'notebook'

    # Main function for configuring notebook server after deploying DataEngine service ?is it deploy?
    # configure() -> ?what is inside? join notebook and cluster ! rename
    # git_creds() -> needs to be removed in GITManaget ??? need to be investigated


@six.add_metaclass(abc.ABCMeta)
class DataEngineNode(Node, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
              + BaseServiceManager.ACTIONS\
              + BaseLibrariesManager.ACTIONS

    NODE_TYPE = 'dataengine'


@six.add_metaclass(abc.ABCMeta)
class DataEngineServerNode(Node, BaseProcessManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
              + BaseLibrariesManager.ACTIONS

    NODE_TYPE = 'dataengine'