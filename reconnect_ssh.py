#!/usr/bin/python

import os
import time
import boto
import boto.manage.cmdshell

key_name='lakitufirstserver-ec2-key'
key_extension='.pem'
key_dir='~/.ssh'

# Create a connection to EC2 service.
# You can pass credentials in to the connect_ec2 method explicitly
# or you can use the default credentials in your ~/.boto config file
# as we are doing here.
ec2 = boto.connect_ec2()

# Get the instances
reservation=ec2.get_all_instances()

# Then get the instance ID of the last running instance
for r in reservation:
  if r.instances[0].state == 'running':  #PS: Not sure why using instances[0] here
    instance=r.instances[0]

key_path = os.path.join(os.path.expanduser(key_dir), key_name+key_extension)
print key_path
cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                        key_path,
                                                        user_name='ec2-user')
print cmd

line=cmd.run("cat /proc/cpuinfo")
print type(line)

for l in line:
  print type(l)
  print l

