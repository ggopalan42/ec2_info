#!/usr/bin/python

import os
import time
import boto.ec2
import boto.manage.cmdshell
import sys
import argparse

# Setup Usage and args
parser = argparse.ArgumentParser(description='Connect to AWS isntance via SSH')

parser.add_argument('-i', '--ins', metavar='InstanceType', 
                                            dest='instance', 
                                            action='store', 
                                            default='t1.micro', 
                                            help='AWS Instance type to run on')
parser.add_argument('-a', '--ami', metavar='AMI_ID', 
                                            dest='ami_id', 
                                            action='store', 
                                            default='ami-1bd68a5e', 
                                            help='AWS AMI ID to use')
parser.add_argument('-n', '--no_terminate', dest='no_term', 
                                            action='store_true', 
                                            help='Do not terminate instance \
                                                          after exiting shell')
args = parser.parse_args()

# Get AMI ID and Instance Type from argument parser
ami=args.ami_id
instance_type=args.instance

key_name='lakitufirstserver-ec2-key'
key_extension='.pem'
key_dir='~/.ssh'
group_name='lakitufirstserver-security-group'
ssh_port=22
cidr='0.0.0.0/0'
tag='Lakitu'
user_data=None
login_user='ec2-user'
ssh_passwd=None

print 'Launching Instance Type %s using AMI ID %s' %(instance_type,ami)

"""
Launch an instance and wait for it to start running.
Returns a tuple consisting of the Instance object and the CmdShell
object, if request, or None.

ami        The ID of the Amazon Machine Image that this instance will
					 be based on.  Default is a 64-bit Amazon Linux EBS image.

instance_type The type of the instance.

key_name   The name of the SSH Key used for logging into the instance.
					 It will be created if it does not exist.

key_extension The file extension for SSH private key files.

key_dir    The path to the directory containing SSH private keys.
					 This is usually ~/.ssh.

group_name The name of the security group used to control access
					 to the instance.  It will be created if it does not exist.

ssh_port   The port number you want to use for SSH access (default 22).

cidr       The CIDR block used to limit access to your instance.

tag        A name that will be used to tag the instance so we can
					 easily find it later.

user_data  Data that will be passed to the newly started
					 instance at launch and will be accessible via
					 the metadata service running at http://169.254.169.254.

login_user The user name used when SSH'ing into new instance.  The
					 default is 'ec2-user'

ssh_passwd The password for your SSH key if it is encrypted with a
					 passphrase.
    """


cmd = None
    
# Create a connection to EC2 service.
# You can pass credentials in to the connect_ec2 method explicitly
# or you can use the default credentials in your ~/.boto config file
# as we are doing here.
ec2 = boto.ec2.connect_to_region('us-west-1')
print ec2

# Check to see if specified keypair already exists.
# If we get an InvalidKeyPair.NotFound error back from EC2,
# it means that it doesn't exist and we need to create it.
try:
  key = ec2.get_all_key_pairs(keynames=[key_name])[0]
except ec2.ResponseError, e:
  if e.code == 'InvalidKeyPair.NotFound':
    print 'Invalid Key Pair Specified' % key_name
  else:
    raise

# Check to see if specified security group already exists.
# If we get an InvalidGroup.NotFound error back from EC2,
# it means that it doesn't exist and we need to create it.
try:
  group = ec2.get_all_security_groups(groupnames=[group_name])[0]
except ec2.ResponseError, e:
  if e.code == 'InvalidGroup.NotFound':
    print 'Invalid Security Group specified' % group_name
  else:
    raise

# Now start up the instance.  The run_instances method
# has many, many parameters but these are all we need
# for now.
reservation = ec2.run_instances(ami,
                                key_name=key_name,
                                security_groups=[group_name],
                                instance_type=instance_type,
                                placement='us-west-1a',
                                user_data=user_data)

# Find the actual Instance object inside the Reservation object
# returned by EC2.

instance = reservation.instances[0]
print ("Starting %s Instance Type, id= %s" %(instance_type,instance.id))

# The instance has been launched but it's not yet up and
# running.  Let's wait for it's state to change to 'running'.
print ('Waiting for instance'),
while instance.state != 'running':
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(5)
    instance.update()
print 'done'

# Let's tag the instance with the specified label so we can
# identify it later.
instance.add_tag(tag)

# The instance is now running, let's try to programmatically
# SSH to the instance using Paramiko via boto CmdShell.

# The reason to sleep is looks like the SSH daemon in the instance
print "Going to sleep for 60 sec"
time.sleep(60)
print "Outta sleep"
    
key_path = os.path.join(os.path.expanduser(key_dir),
                        key_name+key_extension)
print 'Starting SSH Command Shell'
cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                key_path,
                                                user_name=login_user)
# Not too sure why I have to call ...sshclient twice.
# But first one always fails.
cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                key_path,
                                                user_name=login_user)

# Start an SSH Shell
cmd.shell()

# When done, terminate the instance
if not args.no_term:
  print ('Terminating Instance: %s ' %instance.id),
  instance.terminate()
  
  while instance.state == 'running':
    sys.stdout.write(".")
    sys.stdout.flush()
    time.sleep(5)
    instance.update()
  print 'Terminated'
else:
  print('Warning! Instance %s is not being terminated!' %instance.id)

