__author__ = 'patrick w'

'''
	login and logout hooks allow a script or command to be executed during login/logout

    this plugin (which should be run as root) parses the login/logout plist file to extract any such hooks
'''

#project imports
import utils
import command

#plugin framwork import
from yapsy.IPlugin import IPlugin

#login window file
LOGIN_WINDOW_FILE = '/private/var/root/Library/Preferences/com.apple.loginwindow.plist'

#for output, item name
LOGIN_HOOK_NAME = 'Login Hook'

#for output, description of items
LOGIN_HOOK_DESCRIPTION = 'Command that is executed at login'

#for output, item name
LOGOUT_HOOK_NAME = 'Logout Hook'

#for output, description of items
LOGOUT_HOOK_DESCRIPTION = 'Command that is executed at logout'

#plugin class
class scan(IPlugin):

	#init results dictionary
	# ->item name, description, and list
	def initResults(self, name, description):

		#results dictionary
		return {'name': name, 'description': description, 'items': []}

	#invoked by core
	def scan(self):

		#results
		results = []

		#dbg
		utils.logMessage(utils.MODE_INFO, 'running scan')

		#init results
		# ->for for login hook
		results.append(self.initResults(LOGIN_HOOK_NAME, LOGIN_HOOK_DESCRIPTION))

		#init results
		# ->for logout hook
		results.append(self.initResults(LOGOUT_HOOK_NAME, LOGOUT_HOOK_DESCRIPTION))

		#load plist
		plistData = utils.loadPlist(LOGIN_WINDOW_FILE)

		#make sure plist loaded
		if plistData:

			#grab login hook
			if 'LoginHook' in plistData:

				#save into first index of result
				results[0]['items'].append(command.Command(plistData['LoginHook']))

			#grab logout hook
			if 'LogoutHook' in plistData:

				#save into second index of result
				results[1]['items'].append(command.Command(plistData['LogoutHook']))

		return results
