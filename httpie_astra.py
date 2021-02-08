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

__version__ = '1.0.0'
__author__ = 'Kirsten Hunter'
__licence__ = 'Apache 2.0'

class AstraAuth(AuthBase):
    def __init__(self, *args):
        return

    def __call__(self, r):
        return r

class HTTPieAstraAuth(AstraAuth):
    def __init__(self, USERNAME, ASTRA_DB_ID, ASTRA_DB_REGION, ASTRA_DB_USERNAME, ASTRA_DB_PASSWORD, ASTRA_DB_KEYSPACE, ASTRA_DB_TOKEN, ASTRA_DB_TOKEN_TIME):
        self.username = USERNAME,
        self.astra_db_id = ASTRA_DB_ID
        self.astra_db_region = ASTRA_DB_REGION
        self.astra_db_username = ASTRA_DB_USERNAME
        self.astra_db_password = ASTRA_DB_PASSWORD
        self.astra_db_keyspace = ASTRA_DB_KEYSPACE
        self.astra_db_token = ASTRA_DB_TOKEN
        self.astra_db_token_time = ASTRA_DB_TOKEN_TIME
        self.uuid = str(uuid.uuid4())

        return super(HTTPieAstraAuth, self).__init__()
                

    def __call__(self, r):
        now = datetime.timestamp(datetime.now())
        
        if (float(now)-float(self.astra_db_token_time)/(60)) > 30:
            headers = {
                'Content-Type': 'application/json',
                'Accept': '*/*'
            }
            payload = {'username':self.astra_db_username, 'password':self.astra_db_password}
            s = Session()
            resp = s.post("https://%s-%s.apps.astra.datastax.com/api/rest/v1/auth" % (self.astra_db_id, self.astra_db_region), 
                            data=json.dumps(payload), 
                            headers=headers)
            token = resp.json()['authToken']

            filename = os.path.expanduser("~/.astrarc")
            
            with open (filename, "r+") as myfile:
                data=myfile.read().replace('default','----DEFAULT----')
                myfile.close()
            with open (filename, "w") as myfile:
                myfile.write(data)
                myfile.close()

            rc = ConfigParser()
            rc.optionxform = str
            rc.read(filename)
            configfile = open(filename,'w')
            section = ''.join(self.username).replace('default','----DEFAULT----')
            rc.set(section, "ASTRA_DB_TOKEN", token)
            rc.set(section, "ASTRA_DB_TOKEN_TIME", str(datetime.timestamp(datetime.now())))
            self.astra_db_token = token
            with open(filename, 'w') as configfile:
	            rc.write(configfile)

            configfile.close()

            # Undo the ConfigParser work around
            with open (filename, "r") as myfile:
                data=myfile.read().replace('----DEFAULT----','default')
                myfile.close()
            with open (filename, "w") as myfile:
                myfile.write(data)
                myfile.close()
        # Now that we've got our token we can make the call
        r = super(HTTPieAstraAuth, self).__call__(r)
        r.url = r.url.replace("http:","https:")
        r.headers['Content-Type'] = "application/json"
        r.headers['x-cassandra-token'] = self.astra_db_token
        r.headers['x-cassandra-request-id'] = self.uuid
        r.url = r.url.replace("localhost","%s-%s.apps.astra.datastax.com/api" % (self.astra_db_id, self.astra_db_region))
        if ('KS') in r.url:
            r.url = r.url.replace('KS', self.astra_db_keyspace)
        
        if "json" in json.dumps(r.body):
            json_body = json.loads(r.body)
            if "json" in json_body:
                json_body = json_body["json"]
            r.body = json.dumps(json_body)
        if (r.body):
            r.body = r.body.replace("UUID", self.uuid)
        
        
        return r
 
class AstraPlugin(AuthPlugin):
    name = 'Astra auth'
    auth_type = 'astra'
    description = ''
    def get_auth(self, username, password):
        filename = os.path.expanduser("~/.astrarc")
        rc = ConfigParser(allow_no_value=True)
        rc.read(filename)
        
        if not rc.has_section(username):
            err_msg = "\nERROR: No section named '%s' was found in your .astrarc file\n" % username
            err_msg += "ERROR: Please generate credentials for the script functionality\n"
            err_msg += "ERROR: and run 'python gen_astrarc.py %s' to generate the credential file\n"
            sys.stderr.write(err_msg)
            sys.exit(1)

        auth = HTTPieAstraAuth(
            USERNAME = username,
            ASTRA_DB_ID=rc.get(username, 'astra_db_id'),
            ASTRA_DB_REGION=rc.get(username, 'astra_db_region'),
            ASTRA_DB_USERNAME=rc.get(username, 'astra_db_username'),
            ASTRA_DB_PASSWORD=rc.get(username, 'astra_db_password'),
            ASTRA_DB_KEYSPACE=rc.get(username, 'astra_db_keyspace'),
            ASTRA_DB_TOKEN=rc.get(username, 'astra_db_token'),
            ASTRA_DB_TOKEN_TIME=rc.get(username, 'astra_db_token_time')
        )
        return auth

    def __call__(self, r):
        

        return r


