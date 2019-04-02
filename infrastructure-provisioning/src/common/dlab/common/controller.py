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
from exception import DLabException
from usecase import BaseUseCaseSSNDeploy, BaseUseCaseSSNProvision


@six.add_metaclass(abc.ABCMeta)
class BaseController:
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
