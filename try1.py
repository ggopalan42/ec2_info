#!/usr/bin/python
import os, time, sys
import ConfigParser

# This program spawns EC2 Instances:
#  1) Of various types as specified in the array EC2_Types
#  2) On various regions as specified in EC2_Regions
#  3) On various availability zones as specified in EC2_AvailZones
#
# It then runs the set of commands specified in EC2_InstanceCommands
# and logs the output to a file in the format: AWS_EC2_Info_<date>_<time>.log
#

from ec2_launch_instance import launch_instance

# Default AMI to use.
# 
EC2_AMI_ID = 'ami-1bd68a5e'

LoopCount = 1

# Setup ec2 instance query arrays
EC2_Regions=[
               'ap-northeast-1',     # Asia Pacific (Tokyo)
               'ap-southeast-1',     # Asia Pacific (Singapore)
               'ap-southeast-2',     # Asia Pacific (Sydney)
               'eu-west-1',          # Europe West (Ireland)
               'sa-east-1',          # South America East (Sao Paulo)
               'us-east-1',          # US East (Virginia)
               'us-west-1',          # US West 1 (N. California)
               'us-west-2'           # US West 2 (Oregon)
            ]

"""
EC2_Regions=[
               ec2.ap-northeast-1.amazonaws.com,  # Asia Pacific (Tokyo)
               ec2.ap-southeast-1.amazonaws.com,  # Asia Pacific (Singapore)
               ec2.ap-southeast-2.amazonaws.com,  # Asia Pacific (Sydney)
               ec2.eu-west-1.amazonaws.com,       # Europe West (Ireland)
               ec2.sa-east-1.amazonaws.com,     # South America East (Sao Paulo)
               ec2.us-east-1.amazonaws.com,       # US East (Virginia)
               ec2.us-west-1.amazonaws.com,       # US West 1 (N. California)
               ec2.us-west-2.amazonaws.com        # US West 2 (Oregon)
            ]
"""

# The Availability Zones in a dict since the the availability zones are
# not uniform across all AWS regions
EC2_AvailZones={
                 'ap-northeast-1':
                     ['ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c'],
                 'ap-southeast-1':
                     ['ap-southeast-1a', 'ap-southeast-1a'],
                 'ap-southeast-2':
                     ['ap-southeast-2a', 'ap-southeast-2a'],
                 'eu-west-1':
                     ['eu-west-1a','eu-west-1b','eu-west-1c'],
                 'sa-east-1':
                     ['sa-east-1a', 'sa-east-1b'],
                 'us-east-1':
                     ['us-east-1a','us-east-1b','us-east-1c','us-east-1d'],
                 'us-west-1':
                     ['us-west-1a', 'us-west-1c'],
                 'us-west-2':
                     ['us-west-2a', 'us-west-2b', 'us-west-2c' ]
               }

# Setup ec2 instance query arrays
EC2_InstanceTypes=[
                    't1.micro',            # Micro Instance
                    'm1.small',            # First Gen
                    'm1.medium',           # First Gen
                    'm1.large',            # First Gen
                    'm1.xlarge'            # First Gen
                  ]
"""
Other EC2_InstanceTypes for cut and paste
                    'm3.xlarge',           # Second Gen
                    'm3.2xlarge',          # Second Gen
                    'm2.xlarge',           # High-Memory
                    'm2.2xlarge',          # High-Memory
                    'm2.4xlarge',          # High-Memory
                    'c1.medium',           # High-CPU
                    'c1.xlarge',           # High-CPU
                    'cc2.8xlarge',         # Cluster Compute
                    'cr1.8xlarge',         # High Memory Cluster Compute
                    'cg1.4xlarge',         # Cluster GPU
                    'hi1.4xlarge',         # High IO
                    'hs1.8xlarge',         # High Storage
"""

EC2_InstanceCommands=[
                       'date',
                       'hostname',
                       '/sbin/ifconfig',
                       'netstat -nlt',
                       'uname -r',
                       'mount',
                       'df -k',
                       'cat /proc/meminfo',
                       'cat /proc/cpuinfo',
                       'traceroute www.stoke.com'
                     ]

config_file='ec2_info_default_config.cfg'
# Setup Config Parser and red in Config file
config=ConfigParser.ConfigParser()

print EC2_InstanceTypes
print EC2_InstanceCommands
# If the config file exists, read it in
if os.path.exists(config_file):
  config.read(config_file)

  # Get AMI ID and LoopCount
  EC2_AMI_ID= config.get('EC2_AMI_ID','AMI_ID')
  LoopCount=  config.get('EC2_LOOP_COUNT','LoopCount')

  # Get Regions and Avail Zones
  EC2_AvailZonesLst= config.items('EC2_AvailZones')
  EC2_ConfigRegions=[]
  EC2_ConfigZones={}
  for k, v in EC2_AvailZonesLst:
    EC2_ConfigRegions.append(k)
    EC2_ConfigZones[k]=v.split(',')
  # Set regions and avail zones read from config file to the defined arrays
  EC2_Regions=EC2_ConfigRegions
  EC2_AvailZones=EC2_ConfigZones

  # Get Instance types
  EC2_ConfigInstTypes= config.get('EC2_InstanceTypes','EC2_InstanceTypes')
  EC2_InstanceTypes = EC2_ConfigInstTypes.split('\n')

  # Get Instance Commands
  EC2_ConfigInstanceCommands= config.get('EC2_InstanceCommands',
                                                   'EC2_InstanceCommands')
  EC2_InstanceCommands = EC2_ConfigInstanceCommands.split('\n')
else:
  print '******** WARNING: Config file does not exist. **********'
  print 'A lot of instances are going get fired off'
  print 'Abort script if you don\'t want to spend that kind of money'

print EC2_InstanceTypes
print EC2_InstanceCommands

sys.exit('Done!')

# End setup and start main program

# Create a log file name in format: ec2_info_<year>-<month>-<day>-<Hr>_<Min>
# GG `log_file_name='ec2_info_'+time.strftime('%Y-%m-%d-%H_%M')+'.log'
log_file_name='ec2_null_'+time.strftime('%Y-%m-%d-%H_%M')+'.log'
print 'Logging all output to log file %s' %log_file_name 
log_file=open(log_file_name,'wt')       # Open the log file for writing in text mode

# Iterate for LoopCount
for loop_cnt in range(LoopCount):
  # Iterate through AWS regions
  for aws_region in EC2_Regions:
    # Iterate through AWS Availability Zones
    for aws_avail_zone in EC2_AvailZones[aws_region]:
      # Start iterating through Instance Types
			for inst_type in EC2_InstanceTypes: 
				# Launch an instance
				ami_id = EC2_DEFAULT_AMI_ID
				print 'Launching & logging for %s type' %inst_type
				print >>log_file, '-------------------------------------------------'
				print >>log_file, '-------- Loop Count: %d -----------' %loop_cnt
				print >>log_file, '-------- AWS Region: %s -----------' %aws_region
				print >>log_file, '-------- Avail Zone: %s -----------' %aws_avail_zone
				print >>log_file, '-------- Instance Type: %s --------' %inst_type
				print >>log_file, '-------- AMI ID: %s ---------------' %ami_id
				print >>log_file, '-------------------------------------------------'
				# GG instance,cmd = launch_instance(ami=ami_id, instance_type=inst_type)

				# Run shell commands and collect the output
				print 'Running shell commands'
				for sh_cmd in EC2_InstanceCommands:
					print >>log_file, '------- Now running command: '+sh_cmd+' -------'
					# GG ret_tup = cmd.run(sh_cmd)
					# GG for line in ret_tup:
						# GG print >>log_file, line
			  # GG print >>log_file, '\n'

				# Terminate the instance
				# GG print ('Terminating Instance: %s ' %instance.id)
				# GG instance.terminate()

				# GG while instance.state == 'running':
					# GG sys.stdout.write('.')
					# GG sys.stdout.flush()
					# GG time.sleep(5)
					# GG instance.update()
				print 'Terminated'
      # End for inst_types
    # End for aws_avail_zone
  # End for aws_region
# End for loop_count

# Close the log file
log_file.close()

