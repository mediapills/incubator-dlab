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

#  TODO: Log Formatter which formats messages by RFC 3164 - BSD-syslog protocol

ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10


def log(level, msg):
    """
    Low-level logging routine which creates a LogRecord and then calls
    all the handlers of this logger to handle the record.
    """
    print(msg)


def debug(msg):
    """
    Delegate an debug call to the underlying logger.
    """
    return log(DEBUG, msg)


def info(msg):
    """
    Delegate an info call to the underlying logger.
    """
    return log(INFO, msg)


def warn(msg):
    """
    Delegate a warning call to the underlying logger.
    """
    return log(WARN, msg)


def err(msg):
    """
    Delegate an error call to the underlying logger.
    """
    log(ERROR, msg)
    exit(1)
