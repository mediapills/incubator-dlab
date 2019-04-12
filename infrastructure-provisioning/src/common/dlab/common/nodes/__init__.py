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
import dlab.common.nodes.base                                      # noqa: F401
import dlab.common.nodes.dataengine                                # noqa: F401
import dlab.common.nodes.dataengineserver                          # noqa: F401
import dlab.common.nodes.edge                                      # noqa: F401
import dlab.common.nodes.notebook                                  # noqa: F401
import dlab.common.nodes.ssn                                       # noqa: F401

from dlab.common.repositories import ArrayRepository

__all__ = ['register']

registry = ArrayRepository()


def register(key):
    """Register a class as a plug-in"""
    def wrapper(cls):
        # TODO show error if key already exists
        registry.append(key, cls)
        return cls

    return wrapper
