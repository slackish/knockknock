import json

#project imports
import utils

#whitelist files
WHITE_LISTED_FILES = 'whitelists/whitelistedFiles.json'

#white list commands
WHITE_LISTED_COMMANDS = 'whitelists/whitelistedCommands.json'

#global white list
# ->hashes/info of known good files
whitelistedFiles = []

#global white list
# ->commands
whitelistedCommands = []

#load whitelists
def loadWhitelists():

	#global files
	global whitelistedFiles

	#global commands
	global whitelistedCommands

	#open/load whitelisted files
	with open(utils.getKKDirectory() + WHITE_LISTED_FILES) as file:

		#load
		whitelistedFiles = json.load(file)

	#open/load whitelisted commands
	with open(utils.getKKDirectory() + WHITE_LISTED_COMMANDS) as file:

		#load
		# ->note, commands are in 'commands' array
		whitelistedCommands = json.load(file)['commands']