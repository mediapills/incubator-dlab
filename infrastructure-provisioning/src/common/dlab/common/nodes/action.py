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
from dlab.common.repositories import ArrayRepository

ACTION_RUN = 'run'
ACTION_TERMINATE = 'terminate'
ACTION_START = 'start'
ACTION_STOP = 'stop'
ACTION_LIBRARIES_INSTALL = 'libraries_install'
ACTION_LIBRARIES_SHOW = 'libraries_show'

# EDGE node actions
ACTION_GET_STATUS = 'get_status'  # Gets all edge related infrastructure status
ACTION_RECREATE = 'recreate'  # Recreate broken nodes
ACTION_RELOAD_KEYS = 'reload_keys'  # (reupload_key) reload user SSH keys

# Notebook node actions
# TODO: rename action 'configure'
ACTION_CONFIGURE = 'configure'  # join notebook and cluster
# TODO rename action 'git_creds'
ACTION_GIT_CREDS = 'git_creds'  # setup git credentials

ACTIONS_PROCESS = (
    ACTION_RUN,
    ACTION_TERMINATE,
)

ACTIONS_SERVICE = (
    ACTION_START,
    ACTION_STOP,
)

ACTIONS_LIBRARIES = (
    ACTION_LIBRARIES_INSTALL,
    ACTION_LIBRARIES_SHOW,
)

ACTIONS_EDGE = ACTIONS_PROCESS \
          + ACTIONS_SERVICE \
          + (ACTION_GET_STATUS, ACTION_RECREATE, ACTION_RELOAD_KEYS)

ACTIONS_NOTEBOOK = ACTIONS_PROCESS \
          + ACTIONS_SERVICE \
          + ACTIONS_LIBRARIES \
          + (ACTION_CONFIGURE, ACTION_GIT_CREDS)

DATA_ENGINE_ACTIONS = ACTIONS_PROCESS \
          + ACTIONS_SERVICE \
          + ACTIONS_LIBRARIES

DATA_ENGINE_SERVER_ACTIONS = ACTIONS_PROCESS \
          + ACTIONS_LIBRARIES

registry = ArrayRepository()


def register(key):
    """Register a class as a plug-in"""
    def wrapper(cls):
        # TODO show error if key already exists
        registry.append(key, cls)
        return cls

    return wrapper
