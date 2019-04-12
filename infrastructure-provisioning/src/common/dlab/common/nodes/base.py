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

from dlab.common.exceptions import DLabException
from dlab.common.nodes import actions
import dlab.common.nodes as nodes


@six.add_metaclass(abc.ABCMeta)
class BaseProcessManager:

    @actions.register(actions.ACTION_RUN)
    @abc.abstractmethod
    def run(self):
        pass

    @actions.register(actions.ACTION_TERMINATE)
    @abc.abstractmethod
    def terminate(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseServiceManager:

    @actions.register(actions.ACTION_START)
    @abc.abstractmethod
    def start(self):
        pass

    @actions.register(actions.ACTION_STOP)
    @abc.abstractmethod
    def stop(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseLibrariesManager:

    @actions.register(actions.ACTION_LIBRARIES_INSTALL)
    @abc.abstractmethod
    def libraries_install(self):
        pass

    @actions.register(actions.ACTION_LIBRARIES_SHOW)
    @abc.abstractmethod
    def libraries_show(self):
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


@nodes.register('ssn')
@six.add_metaclass(abc.ABCMeta)
class SSNNode(BaseNode, BaseProcessManager):
    pass


@nodes.register('edge')
@six.add_metaclass(abc.ABCMeta)
class EDGENode(BaseNode, BaseProcessManager, BaseServiceManager):

    @actions.register(actions.ACTION_GET_STATUS)
    @abc.abstractmethod
    def get_status(self):
        pass

    @actions.register(actions.ACTION_RECREATE)
    @abc.abstractmethod
    def recreate(self):
        pass

    @actions.register(actions.ACTION_RELOAD_KEYS)
    @abc.abstractmethod
    def reload_keys(self):
        pass


@nodes.register('notebook')
@six.add_metaclass(abc.ABCMeta)
class NotebookNode(BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):

    @abc.abstractmethod
    def configure(self):
        pass

    @abc.abstractmethod
    def git_creds(self):
        pass


@nodes.register('dataengine')
@six.add_metaclass(abc.ABCMeta)
class DataEngineNode(BaseNode, BaseProcessManager, BaseServiceManager, BaseLibrariesManager):
    pass


@nodes.register('dataengineserver')
@six.add_metaclass(abc.ABCMeta)
class DataEngineServerNode(BaseNode, BaseProcessManager, BaseLibrariesManager):
    ACTIONS = BaseProcessManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS\
        + BaseLibrariesManager.ACTIONS


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
