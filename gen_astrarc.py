#! /usr/bin/env python

# This script will generate a ~/.astrarc credentials file based on
# the provided variables
#
# Usage: python gen_astrarc.py 

""" Copyright 2021 DataStax Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys, os
import re
import argparse
import configparser
from os.path import expanduser

# This script will create a configuration section with the name of the client in your 
# ~/.astrarc credential store. 

fields = ['ASTRA_DB_REGION','ASTRA_DB_ID','ASTRA_DB_USERNAME','ASTRA_DB_PASSWORD','ASTRA_DB_KEYBASE']

parser = argparse.ArgumentParser(description='After authorizing your client \
	in the {OPEN} API Administration tool, export the credentials and process \
	them with this script.')
parser.add_argument('--config_section', '-s', action='store', 
	help='create or update config section with this section name.')
args= parser.parse_args()

# Set up section headers
if args.config_section:
	section_name = args.config_section
	section_name_pretty = args.config_section
	if section_name.lower() == "default":
		section_name = "----DEFAULT----"
		section_name_pretty = "default"
else:
	section_name = "----DEFAULT----"
	section_name_pretty = "default"

print ("Datastax Astra Credentials")
print
print ("This script will create or update a configuration section")
print ( "in the local ~/.astrarc credential file.")
print ("Would you like to copy/paste the configuration block from the website (1)")
print ("or fill in the values individually(2)?")

print ("Please make a selection (1/2):")
choice = input("Input type:")

if (choice == 2):

	print ("Please fill in the following fields for your database:")
	print
	value = {}
	for field in fields:
		value[field] = input(field + ": ")


	value['ASTRA_DB_TOKEN']= "X"
	value['ASTRA_DB_TOKEN_TIME'] = "X"
	fields.append('ASTRA_DB_TOKEN')
	fields.append('ASTRA_DB_TOKEN_TIME')

if (choice == 1):
	print ("I'll get this soon")	

# Process the original .astrarc file
home = expanduser("~")
origConfig = configparser.ConfigParser()
filename = "%s/.astrarc" % home

# If this is a new file, create it
if not os.path.isfile(filename):
	print ("+++ Creating new credentials file: %s" % filename)
	open(filename, 'a+').close()
else:
	print ("+++ Found credentials file: %s" % filename)
	
# Recommend default section name if not present
origConfig.read(filename)

if section_name_pretty in origConfig.sections():
	print (">>> Replacing section: %s" % section_name_pretty)
	replace_section = True
else:
	print ("+++ Creating section: %s" % section_name_pretty)
	replace_section = False

# Make sure that this is ok ~ any key to continue
try:
	input("\nPress Enter to continue or ctrl-c to exit.")
except SyntaxError:
	pass

# We need a line for the output to look nice
print 

# If we have a 'default' section hide it from ConfigParser
print ("Using {section_name_pretty}")
with open (filename, "r+") as myfile:
	data=myfile.read().replace('default','----DEFAULT----')
	myfile.close()
with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

# Open the ~/.edgerc file for writing
Config = configparser.ConfigParser()
Config.optionxform = str
Config.read(filename)
configfile = open(filename,'w')

# Remove a section that is being replaced
if replace_section: 
	print ("--- Removing section: %s" % section_name)
	Config.remove_section(section_name)

# Add the new section
print ("+++ Adding section: %s" % section_name)
Config.add_section(section_name)
for field in fields:
	Config[section_name][field] = value[field]

with open(filename, 'w') as configfile:
	Config.write(configfile)

configfile.close()

# Undo the ConfigParser work around
with open (filename, "r") as myfile:
	data=myfile.read().replace('----DEFAULT----','default')
	myfile.close()
with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

print ("\nDone. Please verify your credentials in ~/.astrarc")
print	
