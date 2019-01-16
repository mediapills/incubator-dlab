#!/usr/bin/python
# *****************************************************************************
#
# Copyright (c) 2016, EPAM SYSTEMS INC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ******************************************************************************

from fabric.api import *
from fabric.contrib.files import exists
import argparse
import boto3
import traceback
import sys
import json
import time
import string
import random

parser = argparse.ArgumentParser()
parser.add_argument('--service_base_name', required=True, type=str, default='',
                    help='unique name for repository environment')
parser.add_argument('--vpc_id', type=str, default='', help='AWS VPC ID')
parser.add_argument('--vpc_cidr', type=str, default='172.31.0.0/16', help='Cidr of VPC')
parser.add_argument('--subnet_id', type=str, default='', help='AWS Subnet ID')
parser.add_argument('--subnet_cidr', type=str, default='172.31.0.0/24', help='Cidr of subnet')
parser.add_argument('--sg_id', type=str, default='', help='AWS VPC ID')
parser.add_argument('--billing_tag', type=str, default='product:dlab', help='Tag in format: "Key1:Value1"')
parser.add_argument('--additional_tags', type=str, default='', help='Tags in format: "Key1:Value1;Key2:Value2"')
parser.add_argument('--tag_resource_id', type=str, default='dlab', help='The name of user tag')
parser.add_argument('--allowed_ip_cidr', type=str, default='', help='Comma-separated CIDR of IPs which will have '
                                                                    'access to the instance')
parser.add_argument('--key_name', type=str, default='', help='Key name (WITHOUT ".pem")')
parser.add_argument('--key_path', type=str, default='', help='Key path')
parser.add_argument('--instance_type', type=str, default='t2.medium', help='Instance shape')
parser.add_argument('--region', required=True, type=str, default='', help='AWS region name')
parser.add_argument('--elastic_ip', type=str, default='', help='Elastic IP address')
parser.add_argument('--network_type', type=str, default='public', help='Network type: public or private')
parser.add_argument('--hosted_zone_name', type=str, default='', help='Name of hosted zone')
parser.add_argument('--hosted_zone_id', type=str, default='', help='ID of hosted zone')
parser.add_argument('--subdomain', type=str, default='', help='Subdomain name')
parser.add_argument('--efs_enabled', type=str, default='False', help="True - use AWS EFS, False - don't use AWS EFS")
parser.add_argument('--efs_id', type=str, default='', help="ID of AWS EFS")
parser.add_argument('--primary_disk_size', type=str, default='30', help="Disk size of primary volume")
parser.add_argument('--additional_disk_size', type=str, default='50', help="Disk size of additional volume")
parser.add_argument('--action', required=True, type=str, default='', help='Action: create or terminate')
args = parser.parse_args()


def id_generator(size=10, with_digits=True):
    if with_digits:
        chars = string.digits + string.ascii_letters
    else:
        chars = string.ascii_letters
    return ''.join(random.choice(chars) for _ in range(size))


def vpc_exist(return_id=False):
    try:
        vpc_created = False
        for vpc in ec2_resource.vpcs.filter(Filters=[{'Name': 'tag-key', 'Values': [tag_name]},
                                                     {'Name': 'tag-value', 'Values': [args.service_base_name]}]):
            if return_id:
                return vpc.id
            vpc_created = True
        return vpc_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS VPC: {}'.format(str(err)))
        raise Exception


def create_vpc(vpc_cidr):
    try:
        tag = {"Key": tag_name, "Value": args.service_base_name}
        name_tag = {"Key": "Name", "Value": args.service_base_name + '-vpc'}
        vpc = ec2_resource.create_vpc(CidrBlock=vpc_cidr)
        create_tag(vpc.id, tag)
        create_tag(vpc.id, name_tag)
        return vpc.id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS VPC: {}'.format(str(err)))
        raise Exception


def enable_vpc_dns(vpc_id):
    try:
        ec2_client.modify_vpc_attribute(VpcId=vpc_id,
                                        EnableDnsHostnames={'Value': True})
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with modifying AWS VPC attributes: {}'.format(str(err)))
        raise Exception


def create_rt(vpc_id):
    try:
        tag = {"Key": tag_name, "Value": args.service_base_name}
        name_tag = {"Key": "Name", "Value": args.service_base_name + '-rt'}
        route_table = []
        rt = ec2_client.create_route_table(VpcId=vpc_id)
        rt_id = rt.get('RouteTable').get('RouteTableId')
        route_table.append(rt_id)
        print('Created AWS Route-Table with ID: {}'.format(rt_id))
        create_tag(route_table, json.dumps(tag))
        create_tag(route_table, json.dumps(name_tag))
        ig = ec2_client.create_internet_gateway()
        ig_id = ig.get('InternetGateway').get('InternetGatewayId')
        route_table = list()
        route_table.append(ig_id)
        create_tag(route_table, json.dumps(tag))
        create_tag(route_table, json.dumps(name_tag))
        ec2_client.attach_internet_gateway(InternetGatewayId=ig_id, VpcId=vpc_id)
        ec2_client.create_route(DestinationCidrBlock='0.0.0.0/0', RouteTableId=rt_id, GatewayId=ig_id)
        return rt_id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS Route Table: {}'.format(str(err)))
        raise Exception


def remove_vpc(vpc_id):
    try:
        ec2_client.delete_vpc(VpcId=vpc_id)
        print("AWS VPC {} has been removed".format(vpc_id))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS VPC: {}'.format(str(err)))
        raise Exception


def create_tag(resource, tag, with_tag_res_id=True):
    try:
        tags_list = list()
        if type(tag) == dict:
            resource_name = tag.get('Value')
            resource_tag = tag
        else:
            resource_name = json.loads(tag).get('Value')
            resource_tag = json.loads(tag)
        if type(resource) != list:
            resource = [resource]
        tags_list.append(resource_tag)
        if with_tag_res_id:
            tags_list.append(
                {
                    'Key': args.tag_resource_id,
                    'Value': args.service_base_name + ':' + resource_name
                }
            )
            tags_list.append(
                {
                    'Key': args.billing_tag.split(':')[0],
                    'Value': args.billing_tag.split(':')[1]
                }
            )
        if args.additional_tags:
            for tag in args.additional_tags.split(';'):
                tags_list.append(
                    {
                        'Key': tag.split(':')[0],
                        'Value': tag.split(':')[1]
                    }
                )
        ec2_client.create_tags(
            Resources=resource,
            Tags=tags_list
        )
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with setting tag: {}'.format(str(err)))
        raise Exception


def create_efs_tag():
    try:
        tag = {"Key": tag_name, "Value": args.service_base_name}
        name_tag = {"Key": "Name", "Value": args.service_base_name + '-efs'}
        efs_client.create_tags(
            FileSystemId=args.efs_id,
            Tags=[
                tag,
                name_tag
            ]
        )
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with setting EFS tag: {}'.format(str(err)))
        raise Exception


def create_subnet(vpc_id, subnet_cidr):
    try:
        tag = {"Key": tag_name, "Value": "{}".format(args.service_base_name)}
        name_tag = {"Key": "Name", "Value": "{}-subnet".format(args.service_base_name)}
        subnet = ec2_resource.create_subnet(VpcId=vpc_id, CidrBlock=subnet_cidr)
        create_tag(subnet.id, tag)
        create_tag(subnet.id, name_tag)
        subnet.reload()
        print('AWS Subnet has been created')
        return subnet.id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS Subnet: {}'.format(str(err)))
        raise Exception


def remove_subnet():
    try:
        subnets = ec2_resource.subnets.filter(
            Filters=[{'Name': 'tag:{}'.format(tag_name), 'Values': [args.service_base_name]}])
        if subnets:
            for subnet in subnets:
                ec2_client.delete_subnet(SubnetId=subnet.id)
                print("The AWS subnet {} has been deleted successfully".format(subnet.id))
        else:
            print("There are no private AWS subnets to delete")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS Subnet: {}'.format(str(err)))
        raise Exception


def get_route_table_by_tag(tag_value):
    try:
        route_tables = ec2_client.describe_route_tables(
            Filters=[{'Name': 'tag:{}'.format(tag_name), 'Values': ['{}'.format(tag_value)]}])
        rt_id = route_tables.get('RouteTables')[0].get('RouteTableId')
        return rt_id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS Route tables: {}'.format(str(err)))
        raise Exception


def create_security_group(security_group_name, vpc_id, ingress, egress, tag, name_tag):
    try:
        group = ec2_resource.create_security_group(GroupName=security_group_name, Description='security_group_name',
                                                   VpcId=vpc_id)
        time.sleep(10)
        create_tag(group.id, tag)
        create_tag(group.id, name_tag)
        try:
            group.revoke_egress(IpPermissions=[{"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                                                "UserIdGroupPairs": [], "PrefixListIds": []}])
        except:
            print("Mentioned rule does not exist")
        for rule in ingress:
            group.authorize_ingress(IpPermissions=[rule])
        for rule in egress:
            group.authorize_egress(IpPermissions=[rule])
        return group.id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS security group: {}'.format(str(err)))
        raise Exception


def get_vpc_cidr_by_id(vpc_id):
    try:
        cidr_list = list()
        for vpc in ec2_client.describe_vpcs(VpcIds=[vpc_id]).get('Vpcs'):
            for cidr_set in vpc.get('CidrBlockAssociationSet'):
                cidr_list.append(cidr_set.get('CidrBlock'))
            return cidr_list
        return ''
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS VPC CIDR: {}'.format(str(err)))
        raise Exception


def format_sg(sg_rules):
    try:
        formatted_sg_rules = list()
        for rule in sg_rules:
            if rule['IpRanges']:
                for ip_range in rule['IpRanges']:
                    formatted_rule = dict()
                    for key in rule.keys():
                        if key == 'IpRanges':
                            formatted_rule['IpRanges'] = [ip_range]
                        else:
                            formatted_rule[key] = rule[key]
                    if formatted_rule not in formatted_sg_rules:
                        formatted_sg_rules.append(formatted_rule)
            else:
                formatted_sg_rules.append(rule)
        return formatted_sg_rules
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with formating AWS SG rules: {}'.format(str(err)))
        raise Exception


def remove_sgroups():
    try:
        sgs = ec2_resource.security_groups.filter(
            Filters=[{'Name': 'tag:{}'.format(tag_name), 'Values': [args.service_base_name]}])
        if sgs:
            for sg in sgs:
                ec2_client.delete_security_group(GroupId=sg.id)
                print("The AWS security group {} has been deleted successfully".format(sg.id))
        else:
            print("There are no AWS security groups to delete")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS SG: {}'.format(str(err)))
        raise Exception


def create_instance():
    try:
        user_data = ''
        ami_id = get_ami_id('ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20160907.1')
        instances = ec2_resource.create_instances(ImageId=ami_id, MinCount=1, MaxCount=1,
                                                  BlockDeviceMappings=[
                                                      {
                                                          "DeviceName": "/dev/sda1",
                                                          "Ebs":
                                                              {
                                                                  "VolumeSize": int(args.primary_disk_size)
                                                              }
                                                      },
                                                      {
                                                          "DeviceName": "/dev/sdb",
                                                          "Ebs":
                                                              {
                                                                  "VolumeSize": int(args.additional_disk_size)
                                                              }
                                                      }],
                                                  KeyName=args.key_name,
                                                  SecurityGroupIds=[args.sg_id],
                                                  InstanceType=args.instance_type,
                                                  SubnetId=args.subnet_id,
                                                  UserData=user_data)
        for instance in instances:
            print("Waiting for instance {} become running.".format(instance.id))
            instance.wait_until_running()
            tag = {'Key': 'Name', 'Value': args.service_base_name + '-repository'}
            instance_tag = {"Key": tag_name, "Value": args.service_base_name}
            create_tag(instance.id, tag)
            create_tag(instance.id, instance_tag)
            tag_intance_volume(instance.id, args.service_base_name + '-repository', instance_tag)
            return instance.id
        return ''
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS EC2 instance: {}'.format(str(err)))
        raise Exception


def tag_intance_volume(instance_id, node_name, instance_tag):
    try:
        volume_list = get_instance_attr(instance_id, 'block_device_mappings')
        counter = 0
        instance_tag_value = instance_tag.get('Value')
        for volume in volume_list:
            if counter == 1:
                volume_postfix = '-volume-secondary'
            else:
                volume_postfix = '-volume-primary'
            tag = {'Key': 'Name',
                   'Value': node_name + volume_postfix}
            volume_tag = instance_tag
            volume_tag['Value'] = instance_tag_value + volume_postfix
            volume_id = volume.get('Ebs').get('VolumeId')
            create_tag(volume_id, tag)
            create_tag(volume_id, volume_tag)
            counter += 1
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with tagging AWS EC2 instance volumes: {}'.format(str(err)))
        raise Exception


def get_instance_attr(instance_id, attribute_name):
    try:
        instances = ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-id', 'Values': [instance_id]},
                     {'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            return getattr(instance, attribute_name)
        return ''
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS EC2 instance attributes: {}'.format(str(err)))
        raise Exception


def get_ami_id(ami_name):
    try:
        image_id = ''
        response = ec2_client.describe_images(
            Filters=[
                {
                    'Name': 'name',
                    'Values': [ami_name]
                },
                {
                    'Name': 'virtualization-type', 'Values': ['hvm']
                },
                {
                    'Name': 'state', 'Values': ['available']
                },
                {
                    'Name': 'root-device-name', 'Values': ['/dev/sda1']
                },
                {
                    'Name': 'root-device-type', 'Values': ['ebs']
                },
                {
                    'Name': 'architecture', 'Values': ['x86_64']
                }
            ])
        response = response.get('Images')
        for i in response:
            image_id = i.get('ImageId')
        if image_id == '':
            raise Exception("Unable to find AWS AMI id with name: " + ami_name)
        return image_id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS AMI ID: {}'.format(str(err)))
        raise Exception


def remove_route_tables():
    try:
        rtables = ec2_client.describe_route_tables(Filters=[{'Name': 'tag-key', 'Values': [tag_name]}]).get('RouteTables')
        for rtable in rtables:
            if rtable:
                rtable_associations = rtable.get('Associations')
                rtable = rtable.get('RouteTableId')
                for association in rtable_associations:
                    ec2_client.disassociate_route_table(AssociationId=association.get('RouteTableAssociationId'))
                    print("Association {} has been removed".format(association.get('RouteTableAssociationId')))
                ec2_client.delete_route_table(RouteTableId=rtable)
                print("AWS Route table {} has been removed".format(rtable))
            else:
                print("There are no AWS route tables to remove")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS Route Tables: {}'.format(str(err)))
        raise Exception


def remove_ec2():
    try:
        inst = ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'pending', 'stopping']},
                     {'Name': 'tag:{}'.format(tag_name), 'Values': ['{}'.format(args.service_base_name)]}])
        instances = list(inst)
        if instances:
            for instance in instances:
                ec2_client.terminate_instances(InstanceIds=[instance.id])
                waiter = ec2_client.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[instance.id])
                print("The instance {} has been terminated successfully".format(instance.id))
        else:
            print("There are no instances with '{}' tag to terminate".format(tag_name))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing EC2 instances: {}'.format(str(err)))
        raise Exception


def remove_internet_gateways(vpc_id, tag_value):
    try:
        ig_id = ''
        response = ec2_client.describe_internet_gateways(
            Filters=[
                {'Name': 'tag-key', 'Values': [tag_name]},
                {'Name': 'tag-value', 'Values': [tag_value]}]).get('InternetGateways')
        for i in response:
            ig_id = i.get('InternetGatewayId')
        ec2_client.detach_internet_gateway(InternetGatewayId=ig_id, VpcId=vpc_id)
        print("AWS Internet gateway {0} has been detached from VPC {1}".format(ig_id, vpc_id))
        ec2_client.delete_internet_gateway(InternetGatewayId=ig_id)
        print("AWS Internet gateway {} has been deleted successfully".format(ig_id))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS Internet gateways: {}'.format(str(err)))
        raise Exception


def enable_auto_assign_ip(subnet_id):
    try:
        ec2_client.modify_subnet_attribute(MapPublicIpOnLaunch={'Value': True}, SubnetId=subnet_id)
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with enabling auto-assign of public IP addresses: {}'.format(str(err)))
        raise Exception


def subnet_exist(return_id=False):
    try:
        subnet_created = False
        if args.vpc_id:
            filters = [{'Name': 'tag-key', 'Values': [tag_name]},
                       {'Name': 'tag-value', 'Values': [args.service_base_name]},
                       {'Name': 'vpc-id', 'Values': [args.vpc_id]}]
        else:
            filters = [{'Name': 'tag-key', 'Values': [tag_name]},
                       {'Name': 'tag-value', 'Values': [args.service_base_name]}]
        for subnet in ec2_resource.subnets.filter(Filters=filters):
            if return_id:
                return subnet.id
            subnet_created = True
        return subnet_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS Subnet: {}'.format(str(err)))
        raise Exception


def sg_exist(return_id=False):
    try:
        sg_created = False
        for security_group in ec2_resource.security_groups.filter(
                Filters=[{'Name': 'group-name', 'Values': [args.service_base_name + "-sg"]}]):
            if return_id:
                return security_group.id
            sg_created = True
        return sg_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS Security group: {}'.format(str(err)))
        raise Exception


def ec2_exist(return_id=False):
    try:
        ec2_created = False
        instances = ec2_resource.instances.filter(
            Filters=[{'Name': 'tag:Name', 'Values': [args.service_base_name + '-repository']},
                     {'Name': 'instance-state-name', 'Values': ['running', 'pending', 'stopping', 'stopped']}])
        for instance in instances:
            if return_id:
                return instance.id
            ec2_created = True
        return ec2_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS EC2 instance: {}'.format(str(err)))
        raise Exception


def allocate_elastic_ip():
    try:
        tag = {"Key": tag_name, "Value": "{}".format(args.service_base_name)}
        name_tag = {"Key": "Name", "Value": "{}-eip".format(args.service_base_name)}
        allocation_id = ec2_client.allocate_address(Domain='vpc').get('AllocationId')
        create_tag(allocation_id, tag)
        create_tag(allocation_id, name_tag)
        print('AWS Elastic IP address has been allocated')
        return allocation_id
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS Elastic IP: {}'.format(str(err)))
        raise Exception


def release_elastic_ip():
    try:
        allocation_id = elastic_ip_exist(True)
        ec2_client.release_address(AllocationId=allocation_id)
        print("AWS Elastic IP address has been released.")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS Elastic IP: {}'.format(str(err)))
        raise Exception


def associate_elastic_ip(instance_id, allocation_id):
    try:
        ec2_client.associate_address(InstanceId=instance_id, AllocationId=allocation_id).get('AssociationId')
        print("AWS Elastic IP address has been associated.")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with associating AWS Elastic IP: {}'.format(str(err)))
        raise Exception


def disassociate_elastic_ip(association_id):
    try:
        ec2_client.disassociate_address(AssociationId=association_id)
        print("AWS Elastic IP address has been disassociated.")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with disassociating AWS Elastic IP: {}'.format(str(err)))
        raise Exception


def elastic_ip_exist(return_id=False, return_parameter='AllocationId'):
    try:
        elastic_ip_created = False
        elastic_ips = ec2_client.describe_addresses(
            Filters=[
                {'Name': 'tag-key', 'Values': [tag_name]},
                {'Name': 'tag-value', 'Values': [args.service_base_name]}
            ]
        ).get('Addresses')
        for elastic_ip in elastic_ips:
            if return_id:
                return elastic_ip.get(return_parameter)
            elastic_ip_created = True
        return elastic_ip_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS Elastic IP: {}'.format(str(err)))
        raise Exception


def create_route_53_record(hosted_zone_id, hosted_zone_name, subdomain, ip_address):
    try:
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': "{}.{}".format(subdomain, hosted_zone_name),
                            'Type': 'A',
                            'TTL': 300,
                            'ResourceRecords': [
                                {
                                    'Value': ip_address
                                }
                            ]
                        }
                    }
                ]
            }
        )
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS Route53 record: {}'.format(str(err)))
        raise Exception


def remove_route_53_record(hosted_zone_id, hosted_zone_name, subdomain):
    try:
        for record_set in route53_client.list_resource_record_sets(
                HostedZoneId=hosted_zone_id).get('ResourceRecordSets'):
            if record_set['Name'] == "{}.{}.".format(subdomain, hosted_zone_name):
                for record in record_set['ResourceRecords']:
                    route53_client.change_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        ChangeBatch={
                            'Changes': [
                                {
                                    'Action': 'DELETE',
                                    'ResourceRecordSet': {
                                        'Name': record_set['Name'],
                                        'Type': 'A',
                                        'TTL': 300,
                                        'ResourceRecords': [
                                            {
                                                'Value': record['Value']
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    )
        print("AWS Route53 record has been removed.")
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS Route53 record: {}'.format(str(err)))
        raise Exception


def get_instance_ip_address_by_id(instance_id, ip_address_type):
    try:
        instances = ec2_resource.instances.filter(
            Filters=[{'Name': 'instance-id', 'Values': [instance_id]},
                     {'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            return getattr(instance, ip_address_type)
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS EC2 instance IP address: {}'.format(str(err)))
        raise Exception


def create_efs():
    try:
        token = id_generator(10, False)
        efs = efs_client.create_file_system(
            CreationToken=token,
            PerformanceMode='generalPurpose',
            Encrypted=True
        )
        while efs_client.describe_file_systems(
                FileSystemId=efs.get('FileSystemId')).get('FileSystems')[0].get('LifeCycleState') != 'available':
            time.sleep(5)
        return efs.get('FileSystemId')
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS EFS: {}'.format(str(err)))
        raise Exception


def create_mount_target(efs_sg_id):
    try:
        mount_target_id = efs_client.create_mount_target(
            FileSystemId=args.efs_id,
            SubnetId=args.subnet_id,
            SecurityGroups=[
                efs_sg_id
            ]
        ).get('MountTargetId')
        while efs_client.describe_mount_targets(
                MountTargetId=mount_target_id).get('MountTargets')[0].get('LifeCycleState') != 'available':
            time.sleep(10)
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating AWS mount target: {}'.format(str(err)))
        raise Exception


def efs_exist(return_id=False):
    try:
        efs_created = False
        for efs in efs_client.describe_file_systems().get('FileSystems'):
            if efs.get('Name') == args.service_base_name + '-efs':
                if return_id:
                    return efs.get('FileSystemId')
                efs_created = True
        return efs_created
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with getting AWS EFS: {}'.format(str(err)))
        raise Exception


def remove_efs():
    try:
        efs_id = efs_exist(True)
        mount_targets = efs_client.describe_mount_targets(FileSystemId=efs_id).get('MountTargets')
        for mount_target in mount_targets:
            efs_client.delete_mount_target(MountTargetId=mount_target.get('MountTargetId'))
        while efs_client.describe_file_systems(
                FileSystemId=efs_id).get('FileSystems')[0].get('NumberOfMountTargets') != 0:
            time.sleep(5)
        efs_client.delete_file_system(FileSystemId=efs_id)
        while efs_exist():
            time.sleep(5)
        print('AWS EFS has been deleted')
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with removing AWS EFS: {}'.format(str(err)))
        raise Exception


def ensure_ssh_user(initial_user, os_user):
    try:
        if not exists('/home/{}/.ssh_user_ensured'.format(initial_user)):
            sudo('useradd -m -G sudo -s /bin/bash {0}'.format(os_user))
            sudo('echo "{} ALL = NOPASSWD:ALL" >> /etc/sudoers'.format(os_user))
            sudo('mkdir /home/{}/.ssh'.format(os_user))
            sudo('chown -R {0}:{0} /home/{1}/.ssh/'.format(initial_user, os_user))
            sudo('cat /home/{0}/.ssh/authorized_keys > /home/{1}/.ssh/authorized_keys'.format(initial_user, os_user))
            sudo('chown -R {0}:{0} /home/{0}/.ssh/'.format(os_user))
            sudo('chmod 700 /home/{0}/.ssh'.format(os_user))
            sudo('chmod 600 /home/{0}/.ssh/authorized_keys'.format(os_user))
            sudo('mkdir /home/{}/.ensure_dir'.format(os_user))
            sudo('touch /home/{}/.ssh_user_ensured'.format(initial_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with creating dlab-user: {}'.format(str(err)))
        raise Exception


def install_java():
    try:
        if not exists('/home/{}/.ensure_dir/java_ensured'.format(os_user)):
            sudo('apt-get update')
            sudo('apt-get install -y default-jdk ')
            sudo('touch /home/{}/.ensure_dir/java_ensured'.format(os_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with installing Java: {}'.format(str(err)))
        raise Exception


def install_groovy():
    try:
        if not exists('/home/{}/.ensure_dir/groovy_ensured'.format(os_user)):
            sudo('apt-get install -y unzip')
            sudo('mkdir /usr/local/groovy')
            sudo('wget https://bintray.com/artifact/download/groovy/maven/apache-groovy-binary-{0}.zip -O \
                  /tmp/apache-groovy-binary-{0}.zip'.format(groovy_version))
            sudo('unzip /tmp/apache-groovy-binary-{}.zip -d \
                  /usr/local/groovy'.format(groovy_version))
            sudo('ln -s /usr/local/groovy/groovy-{} \
                  /usr/local/groovy/latest'.format(groovy_version))
            sudo('touch /home/{}/.ensure_dir/groovy_ensured'.format(os_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with installing Groovy: {}'.format(str(err)))
        raise Exception
    
    
def install_nexus():
    try:
        if not exists('/home/{}/.ensure_dir/nexus_ensured'.format(os_user)):
            if args.efs_enabled == 'False':
                mounting_disks()
            else:
                mount_efs()
            sudo('apt-get install -y maven')
            sudo('mkdir -p /opt/nexus')
            sudo('wget https://sonatype-download.global.ssl.fastly.net/nexus/{0}/nexus-{1}-unix.tar.gz -O \
                  /opt/nexus-{1}-unix.tar.gz'.format(
                  nexus_version.split('.')[0], nexus_version))
            sudo('tar -zhxvf /opt/nexus-{}-unix.tar.gz -C /opt/'.format(
                  nexus_version))
            sudo('mv /opt/nexus-{}/* /opt/nexus/'.format(nexus_version))
            sudo('mv /opt/nexus-{}/.[!.]* /opt/nexus/'.format(
                  nexus_version))
            sudo('rm -rf /opt/nexus-{}'.format(nexus_version))
            sudo('useradd nexus')
            sudo('echo \"run_as_user="nexus"\" > /opt/nexus/bin/nexus.rc')
            sudo('chown -R nexus:nexus /opt/nexus /opt/sonatype-work')
            create_keystore()
            put('templates/jetty-https.xml', '/tmp/jetty-https.xml')
            sudo('sed -i "s/KEYSTORE_PASSWORD/{}/g" /tmp/jetty-https.xml'.format(keystore_pass))
            sudo('cp -f /tmp/jetty-https.xml /opt/nexus/etc/jetty/')
            put('files/nexus.service', '/tmp/nexus.service')
            sudo('cp /tmp/nexus.service /etc/systemd/system/')
            sudo('systemctl daemon-reload')
            sudo('systemctl start nexus')
            time.sleep(120)
            put('files/nexus.properties', '/tmp/nexus.properties')
            sudo('cp -f /tmp/nexus.properties /opt/sonatype-work/nexus3/etc/nexus.properties')
            sudo('systemctl restart nexus')
            sudo('systemctl enable nexus')
            put('templates/configureNexus.groovy', '/tmp/configureNexus.groovy')
            sudo('sed -i "s/REGION/{}/g" /tmp/configureNexus.groovy'.format(args.region))
            put('scripts/addUpdateScript.groovy', '/tmp/addUpdateScript.groovy')
            script_executed = False
            while not script_executed:
                try:
                    sudo('/usr/local/groovy/latest/bin/groovy /tmp/addUpdateScript.groovy -u "admin" -p "admin123" \
                          -n "configureNexus" -f "/tmp/configureNexus.groovy" -h "http://localhost:8081"')
                    script_executed = True
                except:
                    time.sleep(10)
                    pass
            sudo('curl -u admin:admin123 -X POST --header \'Content-Type: text/plain\' \
                   http://localhost:8081/service/rest/v1/script/configureNexus/run')
            sudo('systemctl stop nexus')
            sudo('git clone https://github.com/sonatype-nexus-community/nexus-repository-apt')
            with cd('nexus-repository-apt'):
                sudo('mvn')
            apt_plugin_version = sudo('find nexus-repository-apt/ -name "nexus-repository-apt-*.jar" '
                                      '-printf "%f\\n" | grep -v "sources"').replace('nexus-repository-apt-',
                                                                                     '').replace('.jar', '')
            compress_plugin_version = sudo('find /opt/nexus/ -name "commons-compress-*.jar" '
                                           '-printf "%f\\n" ').replace('commons-compress-', '').replace('.jar', '')
            xz_plugin_version = sudo('find /opt/nexus/ -name "xz-*.jar" '
                                     '-printf "%f\\n" ').replace('xz-', '').replace('.jar', '')
            sudo('mkdir -p /opt/nexus/system/net/staticsnow/nexus-repository-apt/{0}/'.format(apt_plugin_version))
            plugin_jar_path = sudo('find nexus-repository-apt/ -name "nexus-repository-apt-{0}.jar"'.format(
                apt_plugin_version))
            sudo('cp -f {0} /opt/nexus/system/net/staticsnow/nexus-repository-apt/{1}/'.format(
                plugin_jar_path, apt_plugin_version
            ))
            sudo('sed -i "$ d" /opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'
                 'nexus-core-feature-{0}-features.xml'.format(nexus_version))
            sudo('''echo '<feature name="nexus-repository-apt" description="net.staticsnow:nexus-repository-apt" '''
                 '''version="{1}">' >> /opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version, apt_plugin_version))
            sudo('''echo '<details>net.staticsnow:nexus-repository-apt</details>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version))
            sudo('''echo '<bundle>mvn:net.staticsnow/nexus-repository-apt/{1}</bundle>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version, apt_plugin_version))
            sudo('''echo '<bundle>mvn:org.apache.commons/commons-compress/{1}</bundle>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version, compress_plugin_version))
            sudo('''echo '<bundle>mvn:org.tukaani/xz/{1}</bundle>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version, xz_plugin_version))
            sudo('''echo '</feature>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version))
            sudo('''echo '</features>' >> '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/'''
                 '''nexus-core-feature-{0}-features.xml'''.format(nexus_version))
            sudo('''sed -i 's|<feature prerequisite=\"true\" dependency=\"false\">wrap</feature>|'''
                 '''<feature prerequisite=\"true\" dependency=\"false\">wrap</feature>\\n'''
                 '''<feature prerequisite=\"false\" dependency=\"false\">nexus-repository-apt</feature>|g' '''
                 '''/opt/nexus/system/org/sonatype/nexus/assemblies/nexus-core-feature/{0}/nexus-core-feature-'''
                 '''{0}-features.xml'''.format(nexus_version))
            sudo('chown -R nexus:nexus /opt/nexus')
            sudo('systemctl start nexus')
            time.sleep(60)
            put('templates/addAptRepository.groovy', '/tmp/addAptRepository.groovy')
            sudo('sed -i "s|REGION|{0}|g" /tmp/addAptRepository.groovy'.format(args.region))
            script_executed = False
            while not script_executed:
                try:
                    sudo('/usr/local/groovy/latest/bin/groovy /tmp/addUpdateScript.groovy -u "admin" -p "admin123" '
                         '-n "addAptRepository" -f "/tmp/addAptRepository.groovy" -h "http://localhost:8081"')
                    script_executed = True
                except:
                    time.sleep(10)
                    pass
            sudo('curl -u admin:admin123 -X POST --header \'Content-Type: text/plain\' '
                 'http://localhost:8081/service/rest/v1/script/addAptRepository/run')
            sudo('touch /home/{}/.ensure_dir/nexus_ensured'.format(os_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with installing Nexus: {}'.format(str(err)))
        raise Exception


def install_nginx():
    try:
        if not exists('/home/{}/.ensure_dir/nginx_ensured'.format(os_user)):
            hostname = sudo('hostname')
            sudo('apt-get install -y nginx')
            sudo('rm -f /etc/nginx/conf.d/* /etc/nginx/sites-enabled/default')
            put('templates/nexus.conf', '/tmp/nexus.conf')
            if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
                sudo('sed -i "s|SUBDOMAIN|{}|g" /tmp/nexus.conf'.format(args.subdomain))
                sudo('sed -i "s|HOSTZONE|{}|g" /tmp/nexus.conf'.format(args.hosted_zone_name))
            else:
                sudo('sed -i "s|SUBDOMAIN.HOSTZONE|{}|g" /tmp/nexus.conf'.format(hostname))
            sudo('cp /tmp/nexus.conf /etc/nginx/conf.d/nexus.conf'.format(args.subdomain, args.hosted_zone_name))
            sudo('systemctl restart nginx')
            sudo('systemctl enable nginx')
            sudo('touch /home/{}/.ensure_dir/nginx_ensured'.format(os_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Error with installing Nginx: {}'.format(str(err)))
        raise Exception


def mounting_disks():
    try:
        if not exists('/home/{}/.ensure_dir/additional_disk_mounted'.format(os_user)):
            sudo('mkdir -p /opt/sonatype-work')
            disk_name = sudo("lsblk | grep disk | awk '{print $1}' | sort | tail -n 1 | tr '\\n' ',' | sed 's|.$||g'")
            sudo('bash -c \'echo -e "o\nn\np\n1\n\n\nw" | fdisk /dev/{}\' '.format(disk_name))
            sudo('sleep 10')
            partition_name = sudo("lsblk -r | grep part | grep {} | awk {} | sort | tail -n 1 | "
                                  "tr '\\n' ',' | sed 's|.$||g'".format(disk_name, "'{print $1}'"))
            sudo('mkfs.ext4 -F -q /dev/{}'.format(partition_name))
            sudo('mount /dev/{0} /opt/sonatype-work'.format(partition_name))
            sudo('bash -c "echo \'/dev/{} /opt/sonatype-work ext4 errors=remount-ro 0 1\' >> /etc/fstab"'.format(
                partition_name))
            sudo('touch /home/{}/.ensure_dir/additional_disk_mounted'.format(os_user))
    except Exception as err:
        traceback.print_exc(file=sys.stdout)
        print('Failed to mount additional volume: {}'.format(str(err)))
        raise Exception


def mount_efs():
    try:
        if not exists('/home/{}/.ensure_dir/efs_mounted'.format(os_user)):
            sudo('mkdir -p /opt/sonatype-work')
            sudo('apt-get -y install binutils')
            with cd('/tmp/'):
                sudo('git clone https://github.com/aws/efs-utils')
            with cd('/tmp/efs-utils'):
                sudo('./build-deb.sh')
                sudo('apt-get -y install ./build/amazon-efs-utils*deb')
            sudo('sed -i "s/stunnel_check_cert_hostname.*/stunnel_check_cert_hostname = false/g" '
                 '/etc/amazon/efs/efs-utils.conf')
            sudo('sed -i "s/stunnel_check_cert_validity.*/stunnel_check_cert_validity = false/g" '
                 '/etc/amazon/efs/efs-utils.conf')
            sudo('mount -t efs -o tls {}:/ /opt/sonatype-work'.format(
                args.efs_id))
            sudo('bash -c "echo \'{}:/ /opt/sonatype-work efs tls,_netdev 0 0\' >> '
                 '/etc/fstab"'.format(args.efs_id))
            put('files/mount-efs-sequentially.service', '/tmp/mount-efs-sequentially.service')
            sudo('cp /tmp/mount-efs-sequentially.service /etc/systemd/system/')
            sudo('systemctl daemon-reload')
            sudo('systemctl enable mount-efs-sequentially.service')
            sudo('touch /home/{}/.ensure_dir/efs_mounted'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to mount additional volume: ', str(err))
        sys.exit(1)


def configure_ssl():
    try:
        if not exists('/home/{}/.ensure_dir/ssl_ensured'.format(os_user)):
            hostname = sudo('hostname')
            sudo('openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/ssl/certs/repository.key \
                             -out /etc/ssl/certs/repository.crt -subj "/C=US/ST=US/L=US/O=dlab/CN={}"'.format(hostname))
            sudo('openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048')
            sudo('touch /home/{}/.ensure_dir/ssl_ensured'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to mount additional volume: ', str(err))
        sys.exit(1)


def set_hostname():
    try:
        if not exists('/home/{}/.ensure_dir/hostname_set'.format(os_user)):
            if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
                hostname = '{0}.{1}'.format(args.subdomain, args.hosted_zone_name)
            else:
                if args.network_type == 'public':
                    hostname = sudo('curl http://169.254.169.254/latest/meta-data/public-hostname')
                else:
                    hostname = sudo('curl http://169.254.169.254/latest/meta-data/hostname')
            sudo('hostnamectl set-hostname {0}'.format(hostname))
            sudo('touch /home/{}/.ensure_dir/hostname_set'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to mount additional volume: ', str(err))
        sys.exit(1)


def create_keystore():
    try:
        if not exists('/home/{}/.ensure_dir/keystore_created'.format(os_user)):
            sudo('openssl pkcs12 -export -in /etc/ssl/certs/repository.crt -inkey /etc/ssl/certs/repository.key '
                 '-out wildcard.p12 -passout pass:{}'.format(keystore_pass))
            sudo('keytool -importkeystore  -deststorepass {0} -destkeypass {0} -srckeystore wildcard.p12 -srcstoretype '
                 'PKCS12 -srcstorepass {0} -destkeystore /opt/nexus/etc/ssl/keystore.jks'.format(keystore_pass))
            sudo('touch /home/{}/.ensure_dir/keystore_created'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to create keystore: ', str(err))
        sys.exit(1)


def download_packages():
    try:
        if not exists('/home/{}/.ensure_dir/packages_downloaded'.format(os_user)):
            run('mkdir packages')
            with cd('packages'):
                run('wget https://pkg.jenkins.io/debian/jenkins-ci.org.key')
                run('curl -v -u admin:admin123 -F "raw.directory=/" -F '
                    '"raw.asset1=@/home/{}/packages/jenkins-ci.org.key" '
                    '-F "raw.asset1.filename=jenkins-ci.org.key"  '
                    '"http://localhost:8081/service/rest/v1/components?repository=jenkins-hosted"'.format(os_user))
                run('wget http://mirrors.sonic.net/apache/maven/maven-{0}/{1}/binaries/apache-maven-'
                    '{1}-bin.zip'.format(maven_version.split('.')[0], maven_version))
                run('curl -v -u admin:admin123 -F "raw.directory=/" -F '
                    '"raw.asset1=@/home/{0}/packages/apache-maven-{1}-bin.zip" '
                    '-F "raw.asset1.filename=apache-maven-{1}-bin.zip"  '
                    '"http://localhost:8081/service/rest/v1/components?repository=jenkins-hosted"'.format(
                    os_user, maven_version))
                run('wget https://nodejs.org/dist/latest-v8.x/node-v8.15.0.tar.gz')
                run('curl -v -u admin:admin123 -F "raw.directory=/" -F '
                    '"raw.asset1=@/home/{}/packages/node-v8.15.0.tar.gz" '
                    '-F "raw.asset1.filename=node-v8.15.0.tar.gz"  '
                    '"http://localhost:8081/service/rest/v1/components?repository=jenkins-hosted"'.format(os_user))
                run('wget https://github.com/sass/node-sass/releases/download/v4.11.0/linux-x64-57_binding.node')
                run('curl -v -u admin:admin123 -F "raw.directory=/" -F '
                    '"raw.asset1=@/home/{}/packages/linux-x64-57_binding.node" '
                    '-F "raw.asset1.filename=linux-x64-57_binding.node"  '
                    '"http://localhost:8081/service/rest/v1/components?repository=jenkins-hosted"'.format(os_user))
            sudo('touch /home/{}/.ensure_dir/packages_downloaded'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to download packages: ', str(err))
        sys.exit(1)


def install_docker():
    try:
        if not exists('/home/{}/.ensure_dir/docker_installed'.format(os_user)):
            sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
            sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) '
                 'stable"')
            sudo('apt-get update')
            sudo('apt-cache policy docker-ce')
            sudo('apt-get install -y docker-ce={}~ce-0~ubuntu'.format(docker_version))
            sudo('usermod -a -G docker ' + os_user)
            sudo('update-rc.d docker defaults')
            sudo('update-rc.d docker enable')
            sudo('touch /home/{}/.ensure_dir/docker_installed'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to install docker: ', str(err))
        sys.exit(1)


def prepare_images():
    try:
        if not exists('/home/{}/.ensure_dir/images_prepared'.format(os_user)):
            put('files/Dockerfile', '/tmp/Dockerfile')
            sudo('docker build --file /tmp/Dockerfile -t pre-base .')
            sudo('docker login -u docker-nexus -p docker-nexus localhost:8083')
            sudo('docker tag pre-base localhost:8083/dlab-pre-base')
            sudo('docker push localhost:8083/dlab-pre-base')
            sudo('touch /home/{}/.ensure_dir/images_prepared'.format(os_user))
    except Exception as err:
        traceback.print_exc()
        print('Failed to download packages: ', str(err))
        sys.exit(1)


if __name__ == "__main__":
    ec2_resource = boto3.resource('ec2', region_name=args.region)
    ec2_client = boto3.client('ec2', region_name=args.region)
    efs_client = boto3.client('efs', region_name=args.region)
    route53_client = boto3.client('route53')
    tag_name = args.service_base_name + '-Tag'
    pre_defined_vpc = True
    pre_defined_subnet = True
    pre_defined_sg = True
    pre_defined_efs = True
    os_user = 'dlab-user'
    groovy_version = '2.5.1'
    nexus_version = '3.14.0-04'
    docker_version = '17.06.2'
    maven_version = '3.5.4'
    keystore_pass = id_generator()
    if args.action == 'terminate':
        if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
            remove_route_53_record(args.hosted_zone_id, args.hosted_zone_name, args.subdomain)
        if elastic_ip_exist():
            try:
                association_id = elastic_ip_exist(True, 'AssociationId')
                disassociate_elastic_ip(association_id)
            except:
                print("AWS Elastic IP address isn't associated with instance or there is an error "
                      "with disassociating it")
            release_elastic_ip()
        if ec2_exist():
            remove_ec2()
        if efs_exist():
            remove_efs()
        if sg_exist():
            remove_sgroups()
        if subnet_exist():
            remove_subnet()
        if vpc_exist():
            args.vpc_id = vpc_exist(True)
            remove_internet_gateways(args.vpc_id, args.service_base_name)
            remove_route_tables()
            remove_vpc(args.vpc_id)
    elif args.action == 'create':
        if not args.vpc_id and not vpc_exist():
            try:
                print('[CREATING AWS VPC]')
                args.vpc_id = create_vpc(args.vpc_cidr)
                enable_vpc_dns(args.vpc_id)
                rt_id = create_rt(args.vpc_id)
                pre_defined_vpc = False
            except:
                remove_internet_gateways(args.vpc_id, args.service_base_name)
                remove_route_tables()
                remove_vpc(args.vpc_id)
                sys.exit(1)
        elif not args.vpc_id and vpc_exist():
            args.vpc_id = vpc_exist(True)
            pre_defined_vpc = False
        print('AWS VPC ID: {}'.format(args.vpc_id))
        if not args.subnet_id and not subnet_exist():
            try:
                print('[CREATING AWS SUBNET]')
                args.subnet_id = create_subnet(args.vpc_id, args.subnet_cidr)
                if args.network_type == 'public':
                    enable_auto_assign_ip(args.subnet_id)
                print("[ASSOCIATING ROUTE TABLE WITH THE SUBNET]")
                rt = get_route_table_by_tag(args.service_base_name)
                route_table = ec2_resource.RouteTable(rt)
                route_table.associate_with_subnet(SubnetId=args.subnet_id)
                pre_defined_subnet = False
            except:
                try:
                    remove_subnet()
                except:
                    print("AWS Subnet hasn't been created or there is an error with removing it")
                if not pre_defined_vpc:
                    remove_internet_gateways(args.vpc_id, args.service_base_name)
                    remove_route_tables()
                    remove_vpc(args.vpc_id)
                sys.exit(1)
        if not args.subnet_id and subnet_exist():
            args.subnet_id = subnet_exist(True)
            pre_defined_subnet = False
        print('AWS Subnet ID: {}'.format(args.subnet_id))
        if not args.sg_id and not sg_exist():
            try:
                print('[CREATING AWS SECURITY GROUP]')
                allowed_ip_cidr = list()
                for cidr in args.allowed_ip_cidr.split(','):
                    allowed_ip_cidr.append({"CidrIp": cidr.replace(' ', '')})
                allowed_vpc_cidr_ip_ranges = list()
                for cidr in get_vpc_cidr_by_id(args.vpc_id):
                    allowed_vpc_cidr_ip_ranges.append({"CidrIp": cidr})
                ingress = format_sg([
                    {
                        "PrefixListIds": [],
                        "FromPort": 80,
                        "IpRanges": allowed_ip_cidr,
                        "ToPort": 80, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 22,
                        "IpRanges": allowed_ip_cidr,
                        "ToPort": 22, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 443,
                        "IpRanges": allowed_ip_cidr,
                        "ToPort": 443, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 8082,
                        "IpRanges": allowed_ip_cidr,
                        "ToPort": 8082, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 80,
                        "IpRanges": allowed_vpc_cidr_ip_ranges,
                        "ToPort": 80, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 443,
                        "IpRanges": allowed_vpc_cidr_ip_ranges,
                        "ToPort": 443, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    },
                    {
                        "PrefixListIds": [],
                        "FromPort": 8082,
                        "IpRanges": allowed_vpc_cidr_ip_ranges,
                        "ToPort": 8082, "IpProtocol": "tcp", "UserIdGroupPairs": []
                    }
                ])
                egress = format_sg([
                    {"IpProtocol": "-1", "IpRanges": [{"CidrIp": '0.0.0.0/0'}], "UserIdGroupPairs": [],
                     "PrefixListIds": []}
                ])
                tag = {"Key": tag_name, "Value": args.service_base_name}
                name_tag = {"Key": "Name", "Value": args.service_base_name + "-sg"}
                args.sg_id = create_security_group(args.service_base_name + '-sg', args.vpc_id, ingress, egress, tag,
                                                   name_tag)
                pre_defined_sg = False
            except:
                try:
                    remove_sgroups()
                except:
                    print("AWS Security Group hasn't been created or there is an error with removing it")
                    pass
                if not pre_defined_subnet:
                    remove_subnet()
                if not pre_defined_vpc:
                    remove_internet_gateways(args.vpc_id, args.service_base_name)
                    remove_route_tables()
                    remove_vpc(args.vpc_id)
                sys.exit(1)
        if not args.sg_id and sg_exist():
            args.sg_id = sg_exist(True)
            pre_defined_sg = False
        print('AWS Security Group ID: {}'.format(args.sg_id))

        if args.efs_enabled == 'True':
            if not args.efs_id and not efs_exist():
                try:
                    print('[CREATING AWS EFS]')
                    allowed_ip_cidr = list()
                    for cidr in args.allowed_ip_cidr.split(','):
                        allowed_ip_cidr.append({"CidrIp": cidr.replace(' ', '')})
                    allowed_vpc_cidr_ip_ranges = list()
                    for cidr in get_vpc_cidr_by_id(args.vpc_id):
                        allowed_vpc_cidr_ip_ranges.append({"CidrIp": cidr})
                    ingress = format_sg([
                        {
                            "PrefixListIds": [],
                            "FromPort": 2049,
                            "IpRanges": allowed_ip_cidr,
                            "ToPort": 2049, "IpProtocol": "tcp", "UserIdGroupPairs": []
                        },
                        {
                            "PrefixListIds": [],
                            "FromPort": 2049,
                            "IpRanges": allowed_vpc_cidr_ip_ranges,
                            "ToPort": 2049, "IpProtocol": "tcp", "UserIdGroupPairs": []
                        }
                    ])
                    egress = format_sg([
                        {"IpProtocol": "-1", "IpRanges": [{"CidrIp": '0.0.0.0/0'}], "UserIdGroupPairs": [],
                         "PrefixListIds": []}
                    ])
                    tag = {"Key": tag_name, "Value": args.service_base_name}
                    name_tag = {"Key": "Name", "Value": args.service_base_name + "-efs-sg"}
                    efs_sg_id = create_security_group(args.service_base_name + '-efs-sg', args.vpc_id, ingress, egress,
                                                      tag, name_tag)
                    args.efs_id = create_efs()
                    mount_target_id = create_mount_target(efs_sg_id)
                    pre_defined_efs = False
                    create_efs_tag()
                except:
                    try:
                        remove_efs()
                    except:
                        print("AWS EFS hasn't been created or there is an error with removing it")
                    if not pre_defined_sg:
                        remove_sgroups()
                    if not pre_defined_subnet:
                        remove_subnet()
                    if not pre_defined_vpc:
                        remove_internet_gateways(args.vpc_id, args.service_base_name)
                        remove_route_tables()
                        remove_vpc(args.vpc_id)
                    sys.exit(1)
            if not args.efs_id and efs_exist():
                args.efs_id = efs_exist(True)
                pre_defined_efs = False
            print('AWS EFS ID: {}'.format(args.efs_id))

        if not ec2_exist():
            try:
                print('[CREATING AWS EC2 INSTANCE]')
                ec2_id = create_instance()
            except:
                try:
                    remove_ec2()
                except:
                    print("AWS EC2 instance hasn't been created or there is an error with removing it")
                if not pre_defined_efs:
                    remove_efs()
                if not pre_defined_sg:
                    remove_sgroups()
                if not pre_defined_subnet:
                    remove_subnet()
                if not pre_defined_vpc:
                    remove_internet_gateways(args.vpc_id, args.service_base_name)
                    remove_route_tables()
                    remove_vpc(args.vpc_id)
                sys.exit(1)
        else:
            ec2_id = ec2_exist(True)

        if args.network_type == 'public':
            if not elastic_ip_exist():
                try:
                    print('[ALLOCATING AWS ELASTIC IP ADDRESS]')
                    allocate_elastic_ip()
                except:
                    try:
                        release_elastic_ip()
                    except:
                        print("AWS Elastic IP address hasn't been created or there is an error with removing it")
                    remove_ec2()
                    if not pre_defined_efs:
                        remove_efs()
                    if not pre_defined_sg:
                        remove_sgroups()
                    if not pre_defined_subnet:
                        remove_subnet()
                    if not pre_defined_vpc:
                        remove_internet_gateways(args.vpc_id, args.service_base_name)
                        remove_route_tables()
                        remove_vpc(args.vpc_id)
                    sys.exit(1)
            try:
                print('[ASSOCIATING AWS ELASTIC IP ADDRESS TO EC2 INSTANCE]')
                allocation_id = elastic_ip_exist(True)
                associate_elastic_ip(ec2_id, allocation_id)
                time.sleep(30)
            except:
                try:
                    association_id = elastic_ip_exist(True, 'AssociationId')
                    disassociate_elastic_ip(association_id)
                except:
                    print("AWS Elastic IP address hasn't been associated or there is an error with disassociating it")
                release_elastic_ip()
                remove_ec2()
                if not pre_defined_efs:
                    remove_efs()
                if not pre_defined_sg:
                    remove_sgroups()
                if not pre_defined_subnet:
                    remove_subnet()
                if not pre_defined_vpc:
                    remove_internet_gateways(args.vpc_id, args.service_base_name)
                    remove_route_tables()
                    remove_vpc(args.vpc_id)
                sys.exit(1)

        if args.network_type == 'public':
            ec2_ip_address = get_instance_ip_address_by_id(ec2_id, 'public_ip_address')
        else:
            ec2_ip_address = get_instance_ip_address_by_id(ec2_id, 'private_ip_address')

        if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
            try:
                print('[CREATING AWS ROUTE53 RECORD]')
                create_route_53_record(args.hosted_zone_id, args.hosted_zone_name, args.subdomain, ec2_ip_address)
            except:
                try:
                    remove_route_53_record(args.hosted_zone_id, args.hosted_zone_name, args.subdomain)
                except:
                    print("AWS Route53 record hasn't been created or there is an error with removing it")
                if args.network_type == 'public':
                    association_id = elastic_ip_exist(True, 'AssociationId')
                    disassociate_elastic_ip(association_id)
                    release_elastic_ip()
                remove_ec2()
                if not pre_defined_efs:
                    remove_efs()
                if not pre_defined_sg:
                    remove_sgroups()
                if not pre_defined_subnet:
                    remove_subnet()
                if not pre_defined_vpc:
                    remove_internet_gateways(args.vpc_id, args.service_base_name)
                    remove_route_tables()
                    remove_vpc(args.vpc_id)
                sys.exit(1)

        print("CONFIGURE CONNECTIONS")
        env['connection_attempts'] = 100
        env.key_filename = [args.key_path + args.key_name + '.pem']
        env.host_string = 'ubuntu@' + ec2_ip_address
        print("CONFIGURE LOCAL REPOSITORY")
        try:
            print('CREATING DLAB-USER')
            ensure_ssh_user('ubuntu', os_user)
            env.host_string = os_user + '@' + ec2_ip_address

            print('SETTING HOSTNAME')
            set_hostname()

            print('INSTALLING JAVA')
            install_java()

            print('INSTALLING GROOVY')
            install_groovy()

            print('CONFIGURING SSL CERTS')
            configure_ssl()

            print('INSTALLING NEXUS')
            install_nexus()

            print('INSTALLING NGINX')
            install_nginx()

            print('DOWNLOADING REQUIRED PACKAGES')
            download_packages()

            print('INSTALLING DOCKER')
            install_docker()

            print('PREPARING_DLAB_DOCKER_IMAGES')
            prepare_images()

            print('[SUMMARY]')
            print("AWS VPC ID: {0}".format(args.vpc_id))
            print("AWS Subnet ID: {0}".format(args.subnet_id))
            print("AWS Security Group ID: {0}".format(args.sg_id))
            print("AWS EC2 ID: {0}".format(ec2_id))
            print("AWS EC2 IP address: {0}".format(ec2_ip_address))
            if args.efs_id:
                print('AWS EFS ID: {}'.format(args.efs_id))
            if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
                print("DNS name: {0}".format(args.subdomain + '.' + args.hosted_zone_name))
        except:
            if args.hosted_zone_id and args.hosted_zone_name and args.subdomain:
                remove_route_53_record(args.hosted_zone_id, args.hosted_zone_name, args.subdomain)
            if args.network_type == 'public':
                association_id = elastic_ip_exist(True, 'AssociationId')
                disassociate_elastic_ip(association_id)
                release_elastic_ip()
            remove_ec2()
            if not pre_defined_efs:
                remove_efs()
            if not pre_defined_sg:
                remove_sgroups()
            if not pre_defined_subnet:
                remove_subnet()
            if not pre_defined_vpc:
                remove_internet_gateways(args.vpc_id, args.service_base_name)
                remove_route_tables()
                remove_vpc(args.vpc_id)
            sys.exit(1)

    else:
        print('Invalid action: {}'.format(args.action))