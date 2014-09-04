'KnockKnock by Patrick Wardle is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License.'

import os
import sys
import json
import argparse
import traceback

#project imports
import file
import utils
import output
import command
import whitelist

#directory containing plugins
PLUGIN_DIR = "plugins/"

#args
args = None

#global plugin manager
PluginManager = None

#global plugin manager
pluginManagerObj = None

#main interface
def knocknock():

    #results
    results = []

    try:

        #init
        # ->logging, plugin manager, etc
        if not initKK():

            #dgb msg
            utils.logMessage(utils.MODE_ERROR, 'initialization(s) failed')

            #bail
            return False

        #dbg msg
        utils.logMessage(utils.MODE_INFO, 'initialization complete')

        #list plugins and bail
        if args.list:

            #display plugins
            listPlugins()

            #bail
            return True

        #scan for thingz
        results = scan(args.plugin)

        #make sure scan succeeded
        if None == results:

            #dbg msg
            utils.logMessage(utils.MODE_ERROR, 'scan failed')

            #bail
            return False

        #depending on args
        # filter out apple signed binaries, or whitelisted binaries, etc
        if not args.apple or not args.whitelist: #or args.signed:

            #iterate over all results
            # ->one for each startup item type
            for result in results:

                #list of files to be ignored
                ignoredFiles = []

                #list of commands to be ignored
                ignoredCommands = []

                #scan each startup object
                # ->if it should be ingored, add to ignore list
                for startupObj in result['items']:

                    #filter out files
                    # ->depending on args, singed by apple, whitelisted, etc
                    if isinstance(startupObj, file.File):

                        #by default, ignore signed by Apple
                        if not args.apple and startupObj.signedByApple():

                            #save
                            ignoredFiles.append(startupObj)

                        #by default, ignore whitelisted binaries
                        # ->ignore if already saved though
                        elif not args.whitelist and startupObj.isWhitelisted:

                            #save
                            ignoredFiles.append(startupObj)

                    #filter out commands
                    # ->just whitelisted ones
                    if isinstance(startupObj, command.Command):

                        #by default, ignore whitelisted commands
                        if not args.whitelist and startupObj.isWhitelisted:

                            #save
                            ignoredCommands.append(startupObj)

                    #now that we are done iterating
                    # ->subtract out all ignored files and command
                    result['items'] =  list(set(result['items']) - set(ignoredFiles) - set(ignoredCommands))

        #format output
        # ->normal output or JSON
        formattedResults = output.formatResults(results, args.json, args.post)

        #show em, if we need to
        if formattedResults != "":
            print formattedResults

    #top level exception handler
    except Exception, e:

        #dbg msg
        utils.logMessage(utils.MODE_ERROR, '\n EXCEPTION, %s() threw: %s' % (sys._getframe().f_code.co_name, e))

        #stack trace
        traceback.print_exc()

        #bail
        return False

    return True


#initialize knockknock
def initKK():

    #global args
    global args

    #global import
    global PluginManager

    #add knock knock's lib path to system path
    # ->ensures 3rd-party libs will be imported OK
    sys.path.insert(0, os.path.join(utils.getKKDirectory(), 'libs'))

    #now can import 3rd party lib
    # ->yapsy
    from yapsy.PluginManager import PluginManager

    #parse options/args
    # ->will bail (with msg) if usage is incorrect
    args = parseArgs()

    #init output/logging
    if not utils.initLogging(args.verbosity):

        #bail
        return False

    #dbg msg
    utils.logMessage(utils.MODE_INFO, 'initialized logging')

    #check version
    # ->only support Mavericks for now
    if not utils.isSupportedOS():

        #dbg msg
        utils.logMessage(utils.MODE_INFO, '%.1f is not a fully supported OS X version' % (utils.getOSVersion()))

        #bail
        #return False

    #dbg msg
    else:

        #dbg msg
        utils.logMessage(utils.MODE_INFO, '%.1f is a supported OS X version' % (utils.getOSVersion()))

    #load python <-> Objc bindings
    # ->might fail if non-Apple version of python is being used
    if not utils.loadObjcBindings():

        #dbg msg
        utils.logMessage(utils.MODE_ERROR, 'python <-> Objc bindings/module not installed\n       run via /usr/bin/python or install modules via \'pip install pyobjc\' to fix')

        #bail
        return False

    #load whitelists
    whitelist.loadWhitelists()

    #init plugin manager
    if not initPluginManager():

        #bail
        return False

    #dbg msg
    utils.logMessage(utils.MODE_INFO, 'initialized plugin manager')

    #giving warning about r00t
    if 0 != os.geteuid():

        #dbg msg
        utils.logMessage(utils.MODE_INFO, 'not running as r00t...some results may be missed')

    return True


#parse args
def parseArgs():

    #init parser
    parser = argparse.ArgumentParser()

    #arg, plugin name
    # ->optional
    parser.add_argument('-p', '--plugin', help='name of plugin')

    #arg, verbose
    # ->optional
    parser.add_argument('-v', '--verbosity', help='enable verbose output', action='store_true')

    #arg, display binaries signed by Apple
    # ->optional
    parser.add_argument('-a', '--apple', help='include Apple-signed binaries', action='store_true')

    #arg, display binaries that are whitelisted
    # ->optional
    parser.add_argument('-w', '--whitelist', help='include white-listed binaries', action='store_true')

    #arg, hide binaries that are signed (by anybody)
    # ->optional
    #parser.add_argument('-s', '--signed', help='exclude all signed binaries', action='store_true')

    #arg, list plugins
    # ->optional
    parser.add_argument('-l', '--list', help='list all plugins', action='store_true')

    #arg, output JSON
    # ->optional
    parser.add_argument('-j', '--json', help='produce output in JSON format', action='store_true')

    # offer to post json results elsewhere
    # ->optional
    parser.add_argument('-P', '--post', help='post json results to a webserver')

    #parse args
    return parser.parse_args()


#init plugin manager
def initPluginManager():

    #global
    global pluginManagerObj

    #create plugin manager
    pluginManagerObj = PluginManager()
    if not pluginManagerObj:

        #err msg
        utils.logMessage(utils.MODE_ERROR, 'failed to create plugin manager')

        #bail
        return False

    #set plugin path
    pluginManagerObj.setPluginPlaces([utils.getKKDirectory() + PLUGIN_DIR])

    #get all plugins
    pluginManagerObj.collectPlugins()

    return True


#list plugins
def listPlugins():

    #dbg msg
    utils.logMessage(utils.MODE_INFO, 'listing plugins')

    #interate over all plugins
    for plugin in pluginManagerObj.getAllPlugins():

        #dbg msg
        # ->always use print, since -v might not have been used
        print '%s -> %s' % (os.path.split(plugin.path)[1], plugin.name)

    return

#scanz!
def scan(pluginName):

    #results
    results = []

    #flag indicating plugin was found
    # ->only relevant when a plugin name is specified
    foundPlugin = False

    #full scan?
    if not pluginName:

        #dbg msg
        utils.logMessage(utils.MODE_INFO, 'beginning full scan')

    #plugin only
    else:

        #dbg msg
        utils.logMessage(utils.MODE_INFO, 'beginning scan using %s plugin' % pluginName)

    #interate over all plugins
    for plugin in pluginManagerObj.getAllPlugins():

        #results from plugin
        pluginResults = None

        #no plugin names means run 'em all
        if not pluginName:

            #dbg msg
            utils.logMessage(utils.MODE_INFO, 'executing plugin: %s' % plugin.name)

            #execute current plugin
            pluginResults = plugin.plugin_object.scan()

        #try to find match
        else:

            #get name of plugin file as name
            # ->e.g. /plugins/somePlugin.py -> 'somePlugin'
            currentPlugin = os.path.split(plugin.path)[1]

            #check for match
            if pluginName.lower() == currentPlugin.lower():

                #found it
                foundPlugin = True

                #dbg msg
                utils.logMessage(utils.MODE_INFO, 'executing requested plugin: %s' % pluginName)

                #execute plugin
                pluginResults = plugin.plugin_object.scan()


        #save plugin output
        if pluginResults:

            #plugins normally return a single dictionary of results
            if isinstance(pluginResults, dict):

                #save results
                results.append(pluginResults)

            #some plugins though can return a list of dictionaries
            # ->e.g. the launch daemon/agent plugin (one dictionary for each type)
            elif isinstance(pluginResults, list):

                #save results
                results.extend(pluginResults)

        #check if specific plugin was specified and found
        # ->if so, can bail
        if pluginName and foundPlugin:

                #bail
                break

    #sanity check
    # -> make sure if a specific plugin was specified, it was found/exec'd
    if pluginName and not foundPlugin:

        #err msg
        utils.logMessage(utils.MODE_ERROR, 'did not find requested plugin')

        #reset results
        results = None

    return results

#invoke main interface
if __name__ == '__main__':

    #main interface
    knocknock()

