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

# from fabric import api as fab


def sudo(command, shell=True, pty=True, combine_stderr=None, user=None):
    """Run a shell command on a remote host, with superuser privileges."""
    # return fab.sudo(command, shell, pty, combine_stderr, user)
    pass


def local(command, capture=False):
    """Run a command on the local system."""
    # return fab.local(command, capture)
    pass


def put(local_path=None, remote_path=None, use_sudo=False,
        mirror_local_mode=False, mode=None):
    """Upload one or more files to a remote host. As with the OpenSSH ``sftp``
    program, `.put` will overwrite pre-existing remote files without requesting
    confirmation."""
    # return fab.put(local_path, remote_path, use_sudo, mirror_local_mode, mode)
    pass


def run(command, shell=True, pty=True, combine_stderr=None):
    """Run a shell command on a remote host."""
    # fab.run(command, shell, pty, combine_stderr)
    pass
