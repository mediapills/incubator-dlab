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

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

ACTION_DEPLOY = 'deploy'
ACTION_PROVISION = 'provision'


class BaseUseCase(ABC):
    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass


class BaseUseDeploy(BaseUseCase, metaclass=ABC):
    pass


class BaseUseProvision(BaseUseCase, metaclass=ABC):
    pass
