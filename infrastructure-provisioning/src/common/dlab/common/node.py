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


@six.add_metaclass(abc.ABCMeta)
class BaseProcess:
    # deploy + provision
    def run(self):
        pass

    def terminate(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseService:
    def start(self):
        pass

    def stop(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseLibrariesManager:
    def install_libraries(self):
        pass

    def show_libraries(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class SSNNode(BaseProcess):
    pass


@six.add_metaclass(abc.ABCMeta)
class EDGENode(BaseProcess, BaseService):
    pass
    # get_status() -> do we need this ? node status + all related nodes status
    # recreate() -> ?upgrade? what cases / if node goes down during creation
    # reupload_key() -> need to be removed in SSHKeysManager


@six.add_metaclass(abc.ABCMeta)
class NotebookNode(BaseProcess, BaseService, BaseLibrariesManager):
    pass
    # Main function for configuring notebook server after deploying DataEngine service ?is it deploy?
    # configure() -> ?what is inside? join notebook and cluster ! rename
    # git_creds() -> needs to be removed in GITManaget ??? need to be investigated


@six.add_metaclass(abc.ABCMeta)
class DataEngineNode(BaseProcess, BaseService, BaseLibrariesManager):
    pass


@six.add_metaclass(abc.ABCMeta)
class DataEngineServerNode(BaseProcess, BaseLibrariesManager):
    pass
