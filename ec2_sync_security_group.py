#!/usr/bin/python

import boto.ec2
import argparse

# Setup Usage and args
parser = argparse.ArgumentParser(description= 'Add Specified Securty Groups \
                                               all AWS Regions and open     \
                                               SSH Port ')

parser.add_argument('-s', '--sec', metavar='SecurityGroupName',
                                            dest='security_group_name',
                                            action='store',
                                            required=True,
                                            help='Security Group Name')
args = parser.parse_args()
print args.security_group_name

# Setup some variables
ssh_port=22
cidr='0.0.0.0/0'

"""
Synchronize Security Group Names across all EC2 regions.

security_group_name    The name of the Security Group.
"""
for region in boto.ec2.regions():
  print 'Creating Security Group in %s region' %region.name
  ec2 = region.connect()

  # Check to see if specified security group already exists in this region
  # If we get an InvalidGroup.NotFound error back from EC2,
  # it means that it doesn't exist and we need to create it.
  try:
    group = ec2.get_all_security_groups(groupnames=
                                                [args.security_group_name])[0]
  except ec2.ResponseError, e:
    if e.code == 'InvalidGroup.NotFound':
      print 'Creating Security Group: %s' % args.security_group_name
      # Create a security group to control access to instance via SSH.
      group = ec2.create_security_group(args.security_group_name,
                                         'Lakitu First Server Security Group')
    else:
      raise

    # Add a rule to the security group to authorize SSH traffic
    # on the specified port.
    try:
        group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print 'Security Group: %s already authorized' \
                                                     %args.security_group_name
        else:
            raise

