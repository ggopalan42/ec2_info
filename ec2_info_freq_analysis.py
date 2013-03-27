#!/usr/bin/python
import os, time, sys, ConfigParser, argparse

# This program spawns EC2 Instances:
#  1) Of various types as specified in the array EC2_Types
#  2) On various regions as specified in EC2_Regions
#  3) On various availability zones as specified in EC2_AvailZones
#
# It then runs the set of commands specified in EC2_InstanceCommands
# and logs the output to a file in the format: AWS_EC2_Info_<date>_<time>.log
#

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

# Set defaults. Defaults will be overridden if a config file is specified
# Or if the default config file (ec2_info_default_config.cfg) exists in current
# directory
EC2_InfoFlags=[
                'aes',
                'hypervisor'
              ]

# Default config file. Later to be passed in as arg
config_file='ec2_info_minimal_config.cfg'

# Setup Config Parser and read in Config file
config=ConfigParser.ConfigParser()

# If the config file exists, read it in
if os.path.exists(config_file):
  config.read(config_file)

  # Get LoopCount
  LoopCount=  int(config.get('EC2_LOOP_COUNT','LoopCount'))

  # Get AMI IDs
  EC2_AmiIdLst= config.items('EC2_AMI_ID')
  EC2_ConfigAmis={}
  for k, v in EC2_AmiIdLst:
    # Remove all white spaces from AMI_ID string and assign
    EC2_ConfigAmis[k]=v.replace(' ','')
    EC2_AMI_IDS=EC2_ConfigAmis

  # Get Regions and Avail Zones
  EC2_AvailZonesLst= config.items('EC2_AvailZones')
  EC2_ConfigRegions=[]
  EC2_ConfigZones={}
  for k, v in EC2_AvailZonesLst:
    EC2_ConfigRegions.append(k)
    # Remove all white spaces from avail zone string, or run_instances barfs
    EC2_ConfigZones[k]=v.replace(' ','').split(',')
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
# Else run from default specified in this program after supplying a big warning
else:
  print '******** WARNING: Config file does not exist. **********'
  print '******** A lot of instances are going get fired off ****'
  print '**** Abort script if you don\'t want to spend that kind of money ****'
  raw_input('Press Enter to Continue . . . ')

# print EC2_AMI_IDS
# print EC2_Regions
# print EC2_AvailZones
# print EC2_InstanceTypes
# print EC2_InstanceCommands
# sys.exit ('Done!')

# End setup and start main program

# Create a log file name in format: ec2_info_<year>-<month>-<day>-<Hr>_<Min>
log_file_name='ec2_info_'+time.strftime('%Y-%m-%d-%H_%M')+'.log'
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
				ami_id = EC2_AMI_IDS[aws_region]
				print 'Launching & logging for %s type at %s' %(inst_type, aws_avail_zone)
				print >>log_file, '-------------------------------------------------'
				print >>log_file, '-------- Loop Count: %d -----------' %loop_cnt
				print >>log_file, '-------- AWS Region: %s -----------' %aws_region
				print >>log_file, '-------- Avail Zone: %s -----------' %aws_avail_zone
				print >>log_file, '-------- Instance Type: %s --------' %inst_type
				print >>log_file, '-------- AMI ID: %s ---------------' %ami_id
				print >>log_file, '-------------------------------------------------'
				instance,cmd = launch_instance(ami=ami_id, 
                                       availability_zone=aws_avail_zone, 
                                       instance_type=inst_type)

				# Run shell commands and collect the output
				print 'Running shell commands'
				for sh_cmd in EC2_InstanceCommands:
					print >>log_file, '------- Now running command: '+sh_cmd+' -------'
					ret_tup = cmd.run(sh_cmd)
					for line in ret_tup:
						print >>log_file, line
					print >>log_file, '\n'

        # Terminate the instance
				print ('Terminating Instance: %s ' %instance.id)
				instance.terminate()

				while instance.state == 'running':
					sys.stdout.write('.')
					sys.stdout.flush()
					time.sleep(5)
					instance.update()
				print 'Terminated'
      # End for inst_types
    # End for aws_avail_zone
  # End for aws_region
# End for loop_count

# Close the log file
log_file.close()

