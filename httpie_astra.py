"""
astra auth plugin for HTTPie.
"""
import sys

from httpie.plugins import AuthPlugin
from configparser import ConfigParser
from requests.auth import AuthBase
from requests import Request, Session
from datetime import datetime
import os, uuid, requests, json
import sys, os
import re
import argparse
import configparser
from os.path import expanduser


__version__ = '1.0.0'
__author__ = 'Kirsten Hunter'
__licence__ = 'Apache 2.0'

class AstraAuth(AuthBase):
    def __init__(self, *args):
        return

    def __call__(self, r):
        return r

class HTTPieAstraAuth(AstraAuth):
    def __init__(self, USERNAME, ASTRA_DB_ID, ASTRA_DB_REGION, ASTRA_DB_KEYSPACE, ASTRA_DB_APPLICATION_TOKEN, ASTRA_DB_ADMIN_TOKEN):
        self.username = USERNAME,
        self.astra_db_id = ASTRA_DB_ID
        self.astra_db_region = ASTRA_DB_REGION
        self.astra_db_keyspace = ASTRA_DB_KEYSPACE
        self.astra_db_application_token = ASTRA_DB_APPLICATION_TOKEN
        self.astra_db_admin_token = ASTRA_DB_ADMIN_TOKEN
        self.uuid = str(uuid.uuid4())

        return super(HTTPieAstraAuth, self).__init__()
                

    def __call__(self, r):
        now = datetime.timestamp(datetime.now())
        
        # Now that we've got our token we can make the call
        r = super(HTTPieAstraAuth, self).__call__(r)
        r.url = r.url.replace("http:","https:")
        r.headers['Content-Type'] = "application/json"
        r.headers['Authorization'] = "Bearer %s" % (self.astra_db_admin_token)
        r.headers['x-cassandra-token'] = self.astra_db_application_token
        r.headers['x-cassandra-request-id'] = self.uuid
        if self.astra_db_id:
            r.url = r.url.replace("localhost","%s-%s.apps.astra.datastax.com/api" % (self.astra_db_id, self.astra_db_region))
        else:
            r.url = r.url.replace("localhost","api.astra.datastax.com")
        
        if ('KS') in r.url:
            r.url = r.url.replace('KS', self.astra_db_keyspace)
        
        if "json" in json.dumps(r.body):
            json_body = json.loads(r.body.replace('"\n"',''))
            if "json" in json_body:
                json_body = json_body["json"]
            r.body = json.dumps(json_body)
        if (r.body):
            r.body = r.body.replace("UUID", self.uuid)
        print(r.body)
        print(r.headers)
        
        
        return r
 
class AstraPlugin(AuthPlugin):
    name = 'Astra auth'
    auth_type = 'astra'
    description = ''

    def setCreds(self, username):
            # Process the original .astrarc file
            home = expanduser("~")
            origConfig = configparser.ConfigParser()
            filename = "%s/.astrarc" % home

            fields = ['ASTRA_DB_REGION','ASTRA_DB_ID','ASTRA_DB_KEYSPACE', 'ASTRA_DB_APPLICATION_TOKEN', 'ASTRA_DB_ADMIN_TOKEN']

            section_name = username
            section_name_pretty = username
            if section_name.lower() == "default":
                section_name = "----DEFAULT----"
                section_name_pretty = "default"
            else:
                section_name = username
                section_name_pretty = username

            # If this is a new file, create it
            
            if not os.path.isfile(filename):
                print ("+++ Found credentials file: %s" % filename)
                origConfig.read(filename)

            else:
                print ("+++ Creating new credentials file: %s" % filename)
                open(filename, 'a+').close()
                print ("Datastax Astra Credentials")
                print
                print ("This script will create or update a configuration section")
                print ( "in the local ~/.astrarc credential file.")
                print ("Would you like to copy/paste the configuration block from the website (1)")
                print ("or fill in the values individually(2)?")

                print ("Please make a selection (1/2):")
                choice = input("Input type:").strip()
                value = {}
    
                if (choice == "2"):
                    print ("Please fill in the following fields for your database:")
                    print
                    for field in fields:
                        value[field] = input(field + ": ")

                if (choice == "1"):
                    err_msg = "\WARNING: No section named '%s' was found in your .astrarc file\n" % username
                    err_msg += "Let's grab your configuration from the Astra Website.\n"
                    err_msg += "Please log into your Astra instance at https://astra.datastax.com,\n"
                    err_msg += "and select the database you want to use.\n\n"
                    err_msg += "Now, click on the dark blue 'Connect' button under 'Settings'\n"
                    err_msg += "On the lower right, there is a black box with 'export' commands.\n"
                    err_msg += " Copy that whole block.\n"
                    err_msg += "Paste the content below, then CTRL-D or CMD-D:\n"
                    sys.stderr.write(err_msg)
                    while True:
                        try:
                            line = input("")
                        except EOFError:                    
                            break
                        line = line.replace('export ', '')
                        key, contents = line.upper().split("=")
                        value[key] = contents.lower()
                        if "app_token" in line:
                            break
                    
                    print ("Please enter your API Admin user token:")
                    line = input("")
                    value["ASTRA_DB_APPLICATION_TOKEN"] = line

                    print ("Please enter your Database Administrator user token:")
                    line = input("")
                    value["ASTRA_DB_ADMIN_TOKEN"] = line
                print (value)
                
               
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

            # Open the ~/.astrarc file for writing
            Config = configparser.ConfigParser(defaults = defaults)
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

            auth = HTTPieAstraAuth(
                USERNAME = username,
                ASTRA_DB_ID=value["ASTRA_DB_ID"],
                ASTRA_DB_REGION=value["ASTRA_DB_REGION"],
                ASTRA_DB_KEYSPACE=value["ASTRA_DB_KEYSPACE"],
                ASTRA_DB_APPLICATION_TOKEN=value["ASTRA_DB_APPLICATION_TOKEN"],
                ASTRA_DB_ADMIN_TOKEN=value["ASTRA_DB_ADMIN_TOKEN"]             )
            return auth
 
    def get_auth(self, username, password):
        filename = os.path.expanduser("~/.astrarc")
        rc = ConfigParser(allow_no_value=True)
        rc.read(filename)
        print ("Getting auth")
        if not rc.has_section(username):
            return self.setCreds(username)

        try:
            auth = HTTPieAstraAuth(
                ASTRA_DB_ID = (rc.get(username, 'astra_db_id')) if (rc.has_option(username, 'astra_db_id')) else None,
                USERNAME=username,
                ASTRA_DB_REGION = (rc.get(username, 'astra_db_region')) if (rc.has_option(username, 'astra_db_region')) else "",
                ASTRA_DB_KEYSPACE = (rc.get(username, 'astra_db_keyspace')) if (rc.has_option(username, 'astra_db_keyspace')) else "",
                ASTRA_DB_APPLICATION_TOKEN=(rc.get(username, 'astra_db_application_token')) if (rc.has_option(username, 'astra_db_application_token')) else "",
                ASTRA_DB_ADMIN_TOKEN=(rc.get(username, 'astra_db_admin_token')) if (rc.has_option(username, 'astra_db_admin_token')) else "",

            )
        except:
            auth=HTTPieAstraAuth(
                USERNAME = username,
                ASTRA_DB_APPLICATION_TOKEN=rc.get(username, 'astra_db_application_token', None),
                ASTRA_DB_ID=None,
                ASTRA_DB_REGION=None,
                ASTRA_DB_KEYSPACE=None,
                ASTRA_DB_ADMIN_TOKEN=rc.get(username, 'astra_db_admin_token', vars=DefaultOption(config, section, ASTRA_DB_ADMIN_TOKEN=None))
            )
            print(auth)
        return auth

    def __call__(self, r):
        

        return r


