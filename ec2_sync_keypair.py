#!/usr/bin/python

import boto.ec2
import argparse

# Setup Usage and args
parser = argparse.ArgumentParser(description= 'Import Public Key into AWS Regions')

parser.add_argument('-k', '--key', metavar='KeyPairName',
                                            dest='keypair_name',
                                            action='store',
                                            required=True,
                                            help='KeyPair Name')
parser.add_argument('-p', '--pub', metavar='PublicKeyFile',
                                            dest='public_key_file',
                                            action='store',
                                            required=True,
                                            help='Public Key File')
args = parser.parse_args()

print args.keypair_name
print args.public_key_file

"""
Synchronize SSH keypairs across all EC2 regions.

keypair_name    The name of the keypair.
public_key_file The path to the file containing the
								public key portion of the keypair.
"""
fp = open(args.public_key_file)
material = fp.read()
fp.close()

for region in boto.ec2.regions():
  print 'Importing key to %s region' %region.name
  ec2 = region.connect()

  # Try to list the keypair.  If it doesn't exist
  # in this region, then import it.
  try:
    key = ec2.get_all_key_pairs(keynames=[args.keypair_name])[0]
    print 'Keypair(%s) already exists in %s' % (args.keypair_name,
																										region.name)
  except ec2.ResponseError, e:
    if e.code == 'InvalidKeyPair.NotFound':
      print 'Importing keypair(%s) to %s' % (args.keypair_name,
																									 region.name)
      ec2.import_key_pair(args.keypair_name, material)
