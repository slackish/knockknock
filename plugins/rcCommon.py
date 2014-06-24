__author__ = 'patrick w'

'''
rc.common

    the /etc/rc.common file contains commands that are executed at boot

    this plugin (very basically) parses this file, extacting all commands (not in functions)

'''

import os
import glob

#project imports
import utils
import command

#plugin framework import
from yapsy.IPlugin import IPlugin

#path to rc.common
RC_COMMON_FILE = '/etc/rc.common'

#for output, item name
RC_COMMON_NAME = 'RC Common'

#for output, description of items
RC_COMMON_DESCRIPTION = 'Commands founds within the rc.common file'

#plugin class
class scan(IPlugin):

	#init results dictionary
	# ->plugin name, description, and list
	def initResults(self, name, description):

		#results dictionary
		return {'name': name, 'description': description, 'items': []}

	#invoked by core
	def scan(self):

		#commands
		commands = []

		#dbg msg
		utils.logMessage(utils.MODE_INFO, 'running scan')

		#init results dictionary
		results = self.initResults(RC_COMMON_NAME, RC_COMMON_DESCRIPTION)

		#get all commands in rc.common
		# ->note, commands in functions will be ignored...
		#   of course, if the function is invoked, this invocation will be displayed
		commands = utils.parseBashFile(RC_COMMON_FILE)

		#iterate over all commands
		# ->instantiate command obj and save into results
		for extractedCommand in commands:

			#instantiate and save
			results['items'].append(command.Command(extractedCommand))

		return results






