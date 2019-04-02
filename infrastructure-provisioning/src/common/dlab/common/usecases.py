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
class BaseUseCase:
    @abc.abstractmethod
    def execute(self):
        pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseDeploy(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseProvision(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseTerminate(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseStart(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseStop(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseInstallLibraries(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseShowLibraries(BaseUseCase):
    pass


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseSSNDeploy(BaseUseCaseDeploy):
    @abc.abstractmethod
    def _setup_infrastructure(self):
        pass

    def _configure_network(self):
        pass

    def _create_instance(self):
        pass

    def execute(self):
        self._setup_infrastructure()
        self._configure_network()
        self._create_instance()


@six.add_metaclass(abc.ABCMeta)
class BaseUseCaseSSNProvision(BaseUseCaseProvision):

    @abc.abstractmethod
    def _install_db(self):
        pass

    @abc.abstractmethod
    def _create_db(self):
        pass

    def _setup_db(self):
        self._install_db()
        self._create_db()

    @abc.abstractmethod
    def _build_ui(self):
        pass

    @abc.abstractmethod
    def _start_ui(self):
        pass

    def execute(self):
        # TODO discuss other steps
        # step 1
        # step 2
        # step 3
        # step 4
        # step 5
        self._setup_db()
        # step 7
        self._build_ui()
        self._start_ui()
