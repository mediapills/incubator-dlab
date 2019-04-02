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
import argparse
import six
from exception import DLabException
from usecase import BaseUseCaseSSNDeploy, BaseUseCaseSSNProvision


@six.add_metaclass(abc.ABCMeta)
class BaseController:
    CLI_ARGUMENTS = {
        '--conf_service_base_name': {
            'help': 'unique name for DLab environment',
        },
        '--conf_network_type': {
            'default': '',
            'help': 'Define in which network DLab will be deployed. Possible options: public|private',
        },
        '--conf_vpc_cidr': {
            'default': '',
            'help': 'CIDR of VPC',
        },
        '--conf_allowed_ip_cidr': {
            'default': '',
            'help': 'CIDR of IPs which will have access to SSN',
        },
        '--conf_user_subnets_range': {
            'default': '',
            'help': 'Range of subnets which will be using for users environments. For example: 10.10.0.0/24 - 10.10.10.0/24'
        },
        '--conf_additional_tags': {
            'default': '',
            'help': 'Additional tags in format "Key1:Value1;Key2:Value2"'
        },
        '--aws_user_predefined_s3_policies': {
            'default': '',
            'help': 'Predefined policies for users instances'
        },
        '--aws_access_key': {
            'default': '',
            'help': 'AWS Access Key ID'
        },
        '--aws_secret_access_key': {
            'default': '',
            'help': 'AWS Secret Access Key'
        },
        '--aws_region': {
            'default': '',
            'help': 'AWS region'
        },
        '--azure_region': {
            'default': '',
            'help': 'Azure region'
        },
        '--gcp_region': {
            'default': '',
            'help': 'GCP region'
        },
        '--gcp_zone': {
            'default': '',
            'help': 'GCP zone'
        },
        '--conf_os_family': {
            'default': '',
            'help': 'Operating system type. Available options: debian, redhat'
        },
        '--conf_cloud_provider': {
            'default': '',
            'help': 'Where DLab should be deployed. Available options: aws, azure, gcp'
        },
        '--aws_vpc_id': {
            'default': '',
            'help': 'AWS VPC ID'
        },
        '--azure_vpc_name': {
            'default': '',
            'help': 'Azure VPC Name'
        },
        '--gcp_vpc_name': {
            'default': '',
            'help': 'GCP VPC Name'
        },
        '--aws_subnet_id': {
            'default': '',
            'help': 'AWS Subnet ID'
        },
        '--azure_subnet_name': {
            'default': '',
            'help': 'Azure Subnet Name'
        },
        '--gcp_subnet_name': {
            'default': '',
            'help': 'GCP Subnet Name'
        },
        '--aws_security_groups_ids': {
            'default': '',
            'help': 'One of more comma-separated Security groups IDs for SSN'
        },
        '--azure_security_group_name': {
            'default': '',
            'help': 'One of more comma-separated Security groups names for SSN'
        },
        '--gcp_firewall_name': {
            'default': '',
            'help': 'One of more comma-separated GCP Firewall rules for SSN'
        },
        '--key_path': {
            'default': '',
            'help': 'Path to admin key (WITHOUT KEY NAME)'
        },
        '--conf_key_name': {
            'default': '',
            'help': 'Admin key name (WITHOUT ".pem")'
        },
        '--workspace_path': {
            'default': '',
            'help': 'Admin key name (WITHOUT ".pem")'
        },
        '--conf_tag_resource_id': {
            'default': 'dlab',
            'help': 'The name of user tag'
        },
        '--aws_ssn_instance_size': { # TODO replace on instance type
            'default': 't2.large',
            'help': 'The SSN instance shape'
        },
        '--azure_ssn_instance_size': {
            'default': 'Standard_DS2_v2',
            'help': 'The SSN instance shape'
        },
        '--gcp_ssn_instance_size': {
            'default': 'n1-standard-2',
            'help': 'The SSN instance shape'
        },
        '--aws_account_id': {
            'default': '',
            'help': 'The ID of Amazon account'
        },
        '--aws_billing_bucket': {
            'default': '',
            'help': 'The name of S3 bucket where billing reports will be placed.'
        },
        '--aws_job_enabled': {
            'default': 'false',
            'help': 'Billing format. Available options: true (aws), false(epam)'
        },
        '--aws_report_path': {
            'default': '',
            'help': 'The path to billing reports directory in S3 bucket'
        },
        '--azure_resource_group_name': {
            'default': '',
            'help': 'Name of Resource group in Azure'
        },
        '--azure_auth_path': {
            'default': '',
            'help': 'Full path to Azure credentials JSON file'
        },
        '--azure_datalake_enable': {
            'default': '',
            'help': 'Provision DataLake storage account'
        },
        '--azure_ad_group_id': {
            'default': '',
            'help': 'ID of Azure AD group'
        },
        '--azure_offer_number': {
            'default': '',
            'help': 'Azure offer number'
        },
        '--azure_currency': {
            'default': '',
            'help': 'Azure currency code'
        },
        '--azure_locale': {
            'default': '',
            'help': 'Azure locale'
        },
        '--azure_application_id': {
            'default': '',
            'help': 'Azure login application ID'
        },
        '--azure_validate_permission_scope': {
            'default': 'true',
            'help': 'Azure permission scope validation(true|false).'
        },
        '--azure_oauth2_enabled': {
            'default': 'false',
            'help': 'Using OAuth2 for logging in DLab'
        },
        '--azure_region_info': {
            'default': '',
            'help': 'Azure region info'
        },
        '--gcp_project_id': {
            'default': '',
            'help': 'The project ID in Google Cloud Platform'
        },
        '--gcp_service_account_path': {
            'default': '',
            'help': 'The project ID in Google Cloud Platform'},
        '--dlab_id': {
            'default':"'user:user:tag'",
            'help': 'Column name in report file that contains dlab id tag'},
        '--usage_date': {
            'default': 'UsageStartDate',
            'help': 'Column name in report file that contains usage date tag'},
        '--product': {
            'default': 'ProductName',
            'help': 'Column name in report file that contains product name tag'},
        '--usage_type': {
            'default': 'UsageType',
            'help': 'Column name in report file that contains usage type tag'},
        '--usage': {
            'default': 'UsageQuantity',
            'help': 'Column name in report file that contains usage tag'},
        '--cost': {
            'default': 'BlendedCost',
            'help': 'Column name in report file that contains cost tag'},
        '--resource_id': {
            'default': 'ResourceId',
            'help': 'Column name in report file that contains dlab resource id tag'},
        '--ldap_hostname': {
            'default': '',
            'help': 'Ldap instance hostname'},
        '--ldap_dn': {
            'default': '',
            'help': 'Ldap distinguished name (dc=example,dc=com)'},
        '--ldap_ou': {
            'default': '',
            'help': 'Ldap organisation unit (ou=People)'},
        '--ldap_service_username': {
            'default': '',
            'help': 'Ldap admin user name'},
        '--ldap_service_password': {
            'default': '',
            'help': 'Ldap password for admin user'},
        '--tags': {
            'default': 'Operation,ItemDescription',
            'help': 'Column name in report file that contains tags'},
    },
#        '--action': { 'required'=True, 'type': str, 'default': '',
#                        'choices':['build', 'deploy', 'create', 'terminate'],
#                        'help': 'Available options: build, deploy, create, terminate'},
#        }

    def __init__(self):
        self._parser = None


    def _add_argument(self, name, default, help=''):

    def _get_ssn_argument_parser(self):
        if self._parser is None
            self._parser = argparse.ArgumentParser()
            # TODO full fill arguments
        return self._parser

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
