"""
edgegrid auth plugin for HTTPie.
"""
import sys
 
from httpie.plugins import AuthPlugin
from akamai.edgegrid import EdgeGridAuth, EdgeRc
import os 
 
__version__ = '1.0.0'
__author__ = 'Kirsten Hunter'
__licence__ = 'Apache 2.0'
 
 
class HTTPieAstraAuth(AstraAuth):
 
	def __init__(self, *args, **kwargs):
		super(HTTPieAstraAuth, self).__init__(*args, **kwargs)
 
	def __call__(self, r):
		return super(HTTPieAstraAuth, self).__call__(r)
 
    if not rc.has_section(username):
            err_msg = "\nERROR: No section named '%s' was found in your .astrarc file\n" % username
            err_msg += "ERROR: Please generate credentials for the script functionality\n"
            err_msg += "ERROR: and run 'python gen_edgerc.py %s' to generate the credential file\n"
            sys.stderr.write(err_msg)
            sys.exit(1)
 
class AstraPlugin(AuthPlugin):
 
    name = 'Astra auth'
    auth_type = 'astra'
    description = ''
 
    def get_auth(self, username, password):
        rc_path = os.path.expanduser("~/.astrarc")
        rc = EdgeRc(rc_path)
 
        auth = HTTPieAstraAuth(
            ASTRA_DB_REGION=rc.get(username, 'ASTRA_DB_REGION'),
            ASTRA_DB_ID=rc.get(username, 'ASTRA_DB_ID'),
            ASTRA_DB_USERNAME=rc.get(username, 'ASTRA_DB_USERNAME'),
            ASTRA_DB_PASSWORD=rc.getint(username, 'ASTRA_DB_PASSWORD')
        )
        return auth
