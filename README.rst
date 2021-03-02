httpie-astra
============

Astra plugin for `HTTPie <https://github.com/jkbr/httpie>`_.


Installation
------------

To install from sources:

.. code-block:: bash

    $ python setup.py install

If using python 3 on Mac, replace python with python3:

.. code-block:: bash

    $ python3 setup.py install

Or, if you like, you can just use pip:

.. code-block:: bash

    $ pip install httpie-astra


Usage
-----

The Astra plugin relies on a .astrarc credentials file that will be created in your home directory and organized by [section] following the format below. Each [section] can contain a different credentials set allowing you to store all of your credentials in a single file. 

.. code-block:: bash

		[default]
		ASTRA_DB_REGION = *******
		ASTRA_DB_ID = *********************
		ASTRA_DB_USERNAME = *********
		ASTRA_DB_PASSWORD = *********
		ASTRA_DB_KEYBASE = tutorial
		ASTRA_DB_TOKEN = xxxx
		ASTRA_DB_TOKEN_TIME = X

		[section1]
		ASTRA_DB_REGION = *******
		ASTRA_DB_ID = *********************
		ASTRA_DB_USERNAME = *********
		ASTRA_DB_PASSWORD = *********
		ASTRA_DB_KEYBASE = tutorial
		ASTRA_DB_TOKEN = xxxx
		ASTRA_DB_TOKEN_TIME = X
		

Once you have the credentials set up, here is an example of what an Astra Call call would look like:

.. code-block:: bash

	% http --auth-type astra -a default: :/rest/v2/schemas/keyspaces
	or
	% http :/graphql/tutorial query='query { products(value: { id: "65cad0df-4fc8-42df-90e5-4effcd221ef7" }) { values { id name description price created } } }'


When you run the command, if your authentication token has expired it will refresh it for you.

I have made a change to how httpie processes json data.  To pass JSON in the request, just use something like this:

.. code-block:: bash

	http --auth-type astra -a default: POST :/rest/v2/schemas/keyspaces/KS/tables \
	json:='{"name":"products","ifNotExists":true,"columnDefinitions": [\
	{"name":"id","typeDefinition":"uuid","static":false}, {"name":"name","typeDefinition":"text","static":false}, \
	{"name":"description","typeDefinition":"text","static":false}, {"name":"price","typeDefinition":"decimal","static":false}, \
	{"name":"created","typeDefinition":"timestamp","static":false}],"primaryKey": {"partitionKey":["id"]},"tableOptions":{"defaultTimeToLive":0}}'

Note that you can create a configuration file to simplify the command further

File: ~/.config/httpie/config.json

.. code-block:: JSON

   	 {
		"default_options": [
			"--style=fruity",
			"--auth-type=astra",
			"--auth=default:" 
		]
	 }	

