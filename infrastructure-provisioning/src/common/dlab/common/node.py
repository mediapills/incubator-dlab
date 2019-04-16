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
import abc
import six

from dlab.common.repositories import ArrayRepository

TYPE_DATA_ENGINE_NODE = 'dataengine'
TYPE_DATA_ENGINE_SERVER_NODE = 'dataengineserver'
TYPE_EDGE_NODE = 'edge'
TYPE_NOTEBOOK_NODE = 'notebook'
TYPE_SSN_NODE = 'ssn'

registry = ArrayRepository()


def register(key):
    """Register a class as a plug-in"""
    def wrapper(cls):
        # TODO show error if key already exists
        a = cls
        registry.append(key, cls.__class__)
        return cls

    return wrapper


@six.add_metaclass(abc.ABCMeta)
class BaseNode:

    NODE_TYPE = None

    LC_MSG_UNKNOWN_CONSTANT = 'Constant "{name}" needs to be defined'
    LC_MSG_WRONG_ACTION = '{clsname} does not support action "{action}"'


'''
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
'''
