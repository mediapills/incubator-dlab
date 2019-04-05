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
class BaseNode:

    NODE_TYPE = None

    LC_MSG_UNKNOWN_CONSTANT = 'Constant "{name}" needs to be defined'
    LC_MSG_WRONG_ACTION = '{clsname} does not support action "{action}"'

    @classmethod
    def get_type(cls):
        if cls.NODE_TYPE is None:
            raise DLabException(cls.LC_MSG_UNKNOWN_CONSTANT.format(
                name='NODE_TYPE'
            ))

        return cls.NODE_TYPE

    @classmethod
    def has_action(cls, action):
        return action in cls.ACTIONS

    def execute(self, action):
        if not self.has_action(action):
            raise DLabException(self.LC_MSG_WRONG_ACTION.format(
                clsname=self.__class__.__name__,
                action=action
            ))

        method = getattr(self, action)
        return method()


@six.add_metaclass(abc.ABCMeta)
class SSNNode(BaseNode, BaseProcessManager):

    NODE_TYPE = 'ssn'


@six.add_metaclass(abc.ABCMeta)
class EDGENode(BaseNode, BaseProcessManager, BaseServiceManager):

    ACTION_GET_STATUS = 'get_status'  # Gets all edge related infrastructure status
    ACTION_RECREATE = 'recreate'  # Recreate broken nodes
    ACTION_RELOAD_KEYS = 'reload_keys'  # (reupload_key) reload user SSH keys

    ACTIONS = BaseProcessManager.ACTIONS\
        + BaseServiceManager.ACTIONS\
        + (ACTION_GET_STATUS, ACTION_RECREATE, ACTION_RELOAD_KEYS)

    NODE_TYPE = 'edge'

    @abc.abstractmethod
    def get_status(self):
        pass

    @abc.abstractmethod
    def recreate(self):
        pass

    @abc.abstractmethod
    def reload_keys(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class NotebookNode(BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):

    # TODO rename this action
    ACTION_CONFIGURE = 'configure'  # join notebook and cluster
    # TODO rename this action
    ACTION_GIT_CREDS = 'git_creds'  # setup git credentials

    ACTIONS = BaseProcessManager.ACTIONS\
        + BaseServiceManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS\
        + (ACTION_CONFIGURE, ACTION_GIT_CREDS)

    NODE_TYPE = 'notebook'

    @abc.abstractmethod
    def configure(self):
        pass

    @abc.abstractmethod
    def git_creds(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class DataEngineNode(BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
        + BaseServiceManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS

    NODE_TYPE = 'dataengine'


@six.add_metaclass(abc.ABCMeta)
class DataEngineServerNode(BaseNode, BaseProcessManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS

    NODE_TYPE = 'dataengineserver'


'''
    @abc.abstractmethod
    def _get_ssn_deploy_uc(self):
        pass

    @abc.abstractmethod
    def _get_ssn_provision_uc(self):
        pass

    def ssn_run(self):
        uc = self._get_ssn_deploy_uc()  # type:  BaseUseCaseSSNDeploy
        try:
            uc.execute()
        except DLabException:
            uc.rollback()  # TODO is it needs to be here ?

        uc = self._get_ssn_provision_uc()  # type:  BaseUseCaseSSNProvision
        try:
            uc.execute()
        except DLabException:
            uc.rollback()  # TODO is it needs to be here ?

    def ssn_terminate(self):
        pass

    @abc.abstractmethod
    def get_ssn_node(self):
        pass
'''
