"""""

log.py

Brief: functions for logging and flagging

Log Hierarchy:

|
|----Master (.json)
       |
       |----Run_1 {}
       |     |
       |     |----events {}
       |     |      |
       |     |      |----event_1 []
       |     |      |
       |     |      |----event_2 []
       |     |      |
       |     |      |----event_n []
       |     |
       |     |----errors []
       |     |
       |     |----learnings (dir)
       |            |
       |            |----learned_names []
       |            |
       |            |----processed_parts {}
       |                   |
       |                   |----known_parts []
       |                   |
       |                   |----unknown_parts []
       |                   |
       |                   |----useable_parts {}
       |                          |
       |                          |----address_1 {}
       |                          |
       |                          |----address_2 {}
       |                          |
       |                          |----address_n {}
       |
       |----Run_2 {}
       |     |
       |     |----events {}
       |     |      |
       |     |      |----event_1 []
       |     |      |
       |     |      |----event_2 []
       :     :      : 


It would be wise to often change the directory name in the config.py file,
then copy the learned names list to the new directory.

Ronald Rihoo

"""""

import sys
import os
import time
import codecs
import json
from config import *
from clean import *


__all__ = [ 'grab_error_log', 
            'grab_event_log', 
            'grab_learned_names', 
            'grab_processed_names', 
            'handle_output', 
            'insert_useable_parts',
            'learn_medial_name_parts', 
            'load_learned_names_list', 
            'manage_directory', 
            'produce_logs', 
            'store_processed_parts' ]

'''

Auto-Configuration

'''

directory_name = grab_pathname()

console_output = grab_monitoring_preference()


'''

Variables

'''

learned_names = set()   # list of possible unique names learned during scans

known_parts = set()     # list of processed name parts that are identified as known value types (e.g: housenumber, city, state, zipcode, etc.)

unknown_parts = set()   # list of processed name parts that are identified as unknown value types (none of the scanners could identify the value type)

useable_parts = {}      # dictionary of dictionaries that hold useable address parts, which have been processed and identified as useable parts

processed_parts = {}    # dictionary holding the two lists of possible known and unknown street address parts that have been processed and stored for review

event_log = {}          # log of all normal event messages (including warnings)

event = []              # list of related event operations (as a packet); resets for each event after logging

error_log = []          # list of errors

op_count = 0            # operation counter

directory = grab_pathname()

'''

Data Provision (because global variables can raise hell)

'''

# return the name parts that were learned during scans
def grab_learned_names():
    return learned_names

# return the parts that have been processed, but as a package of all, rather than a list of packages (such as the one below)
def grab_processed_names():
    return processed_parts

# return the list of dictionaries that pack up one or more useable parts (housenumber, suite, city, state, zipcode, etc)
def grab_useable_parts():
    return useable_parts

# return event_log
def grab_event_log():
    return event_log

# return event_log
def grab_error_log():
    return error_log


'''

Flagging and Controlled Print

'''

# handle event logging and console output
def handle_output(message, unique = False, insert_event = False, newline = True, op_count = op_count, event = event, console_output = console_output):
    # add event message to the packet
    event.append(message)

    if (console_output):
      if (newline == True):
        print message
      if (newline == False):
        sys.stdout.write(message)

    # this becomes disabled only for messages that are meant to be under the same event as last
    if (unique):
      op_count += 1

    # insert event packet into event_log and clear event cursor
    if (insert_event):
      insert_event_log(str(op_count), event_log)

    return


'''

Learning

'''

# add the event log (array of strings) into the master_log dictionary and clear the event list
def insert_event_log(code, event_log, event = event):
    event_log[code] = event
    event = []
    return

def insert_known_parts(parts, knowns = known_parts):
    knowns.add(parts)
    return

def insert_unknown_parts(parts, unknowns = unknown_parts):
    unknowns.add(parts)
    return

def insert_useable_parts(parts, name = None):
    if name == None:
      n = 0
      for key in useable_parts:
        n += 1
      name = str(n)
    useable_parts[name] = parts
    return

def insert_processed_parts(known = known_parts, unknown = unknown_parts, useables = useable_parts, return_lists = False):
    known_parts_list = []
    unknown_parts_list = []

    for part in known:
      known_parts_list.append(part)
    for part in unknown:
      unknown_parts_list.append(part)

    processed_parts['known parts'] = known_parts_list
    processed_parts['unknown parts'] = unknown_parts_list
    processed_parts['useable parts'] = useables
    
    if return_lists:
      return known_parts_list, unknown_parts_list
    return

# load previously learned names from a saved list on the storage device
def load_learned_names_list(learned_names = learned_names, directory = directory):
    try: 
        handle_output("Loading learned names... ", newline = False)
        with open('learned/learned_names.json') as json_data:
          known_names = json.load(json_data)
          json_data.close()
        for name in (known_names['street name parts']):
          learned_names.add(name)
        handle_output("Done.")
    except:
        handle_output("Learned names could not be imported.")
        pass
    return

# learn actual parts of the street names, for improved error-checking; first and last frags are handled later.
# Ex: [ 'N', 'West', 'Shore', 'Rd' ] ->
def grab_names(fragment, report_names = False, return_names = False):
    last = (len(fragment) - 1)
    names_list = []
    for index in xrange(last - 1):
        if (index != 0) and (index != last):
            names_list.append(learned_names.add(fragment[index]))
    if report_names == True:
        handle_output("The following are the medial name parts: " + names_list)
    if return_names == True:
        return names_list
    return 

# learn names from a list
def learn_names(new_names, learned_names = learned_names):
    for name in new_names:
        learned_names.add(name)
    return

# store processed address parts for review by the human eye
def store_processed_parts(parts, known = False, known_parts = known_parts, unknown_parts = unknown_parts, name = 'unknown', passing_useables = False):
    if known and not passing_useables:
      for part in parts:
          known_parts.add(part)
    if not known and not passing_useables:
      for part in parts:
          unknown_parts.add(part)
    if passing_useables:
      useable_parts[name] = parts
    return

# in the case that there's a reasonable condition for assuming the string contains street name parts, then learn the parts
def learn_medial_name_parts(fragment):
    name_parts = [],
    if (len(fragment) > 2):
        name_parts = grab_names(fragment, return_names = True)
        if name_parts != []:
            learn_names(name_parts)
    return


'''

Logging

'''

# produce logs and handle the log directory
def produce_logs(dev = False):
    handle_output("Producing logs...")

    # make, or change to, the path specified in the args
    manage_directory('', 'logs')                         # directory_name is defined in log.py

    # creating a master log for this script (reusable as long in the same working directory during each run)
    log_all()

    if dev:
        # for the development phase and Udacity grader(s)
        log_errors(error_log)
        log_names(learned_names)
        log_processed_parts(known_parts, unknown_parts)

    handle_output("Logs produced.")

    return

# append all logs into the master log file
def log_all(event_log = event_log, error_log = error_log, learned_name_log = learned_names, processed_parts_log = processed_parts):
    filename = "master_log.json"

    master = {}
    run_log = {}
    name_log = []

    if error_log == []:
      error_log.append("No errors.")

    for name in learned_name_log:
      name_log.append(name)

    insert_processed_parts(known_parts, unknown_parts)

    run_log['event log'] = event_log
    run_log['error log'] = error_log
    run_log['learned name parts'] = name_log
    run_log['processed name parts'] = processed_parts

    master[time.strftime("%c")] = run_log

    with codecs.open(filename, "a") as fo:
        fo.write(json.dumps(master, indent=2)+"\n")
    return

# append errors in the error log
def log_errors(error_log):
    filename = "error_log.json"

    record = {}
    error_list = []

    for error in error_log:
      error_list.append(error)

    record[time.strftime("%c")] = error_list

    with codecs.open(filename, "a") as fo:
        fo.write(json.dumps(record, indent=2)+"\n")
    return

# store the learned names in a file (continuous log is for the development phase)
def log_names(names_log):
    filename = "learned_names.json"     # only one list, which is made for load and reuse
    logfile = "learning_log.json"       # log of every list that's exported, which is for testing and debugging

    record = {}
    name_list = []

    # store names for reuse
    for name in names_log:
        name_list.append(name)

    # to track changes in learning habits during development
    learning_log = {}
    learning_log[time.strftime("%c")] = name_list

    with codecs.open(logfile, "a") as fo:
        fo.write(json.dumps(learning_log, indent=2)+"\n")

    record['street name parts'] = name_list
    
    # learning should be universal across all OSM scans, so navigate outside of this OSM scan directory
    manage_directory('../..', 'learned')

    with codecs.open(filename, "w") as fo:
        fo.write(json.dumps(record, indent=2)+"\n")
    return

def log_processed_parts(known = known_parts, unknown = unknown_parts, useables = useable_parts, processed_parts = processed_parts):
    filename = "processed_parts.json"
    knowns_file   = "known_parts.json"
    unknowns_file = "unknown_parts.json"
    useables_file = "useable_parts.json"

    # update the 'processed_parts' dictionary with the known, unknown, and useable parts that have been stored in lists
    # also, return the known and unknowns lists to store in separate files. The useables is already a (global) list that's ready-to-go
    known_parts_list, unknown_parts_list = insert_processed_parts(known, unknown, return_lists = True)

    # store processed known and unknown parts in one file for review
    with codecs.open(filename, "w") as fo:
        fo.write(json.dumps(processed_parts, indent=2)+"\n")

    # to track changes in scanning and processing during development
    knowns_log = {}
    knowns_log[time.strftime("%c")] = known_parts_list

    with codecs.open(knowns_file, "a") as fo:
        fo.write(json.dumps(knowns_log, indent=2)+"\n")

    # to track changes in scanning processing during development
    unknowns_log = {}
    unknowns_log[time.strftime("%c")] = unknown_parts_list

    with codecs.open(unknowns_file, "a") as fo:
        fo.write(json.dumps(unknowns_log, indent=2)+"\n")

    # to track changes in scanning processing during development
    useables_log = {}
    useables_log[time.strftime("%c")] = useable_parts

    with codecs.open(useables_file, "a") as fo:
        fo.write(json.dumps(useables_log, indent=2)+"\n")
    return

'''

Work-Flow Organization

'''

# navigate to, or if it doesn't exist in the running directory, then make "directory" (argument 2)
def manage_directory(path = '', directory = ''):

    loop = 1

    # Allow user to change the name of the directory (to work in or create) from raw input
    #directory = raw_input('Directory name (for this run): ')
    #if (directory == ''):
    #      directory = 'street_name_analysis'

    handle_output("Managing working directory...")

    fullpath = os.path.realpath(path) + '/' + directory

    handle_output("....We're in " + os.path.realpath(''))

    if (path != ''):
        handle_output("Changing directory")
        os.chdir(path)                                                           # change directory based on path (in arg)
        handle_output("....Currently in " + os.path.realpath(''))

    while (loop <= 5):
        handle_output("Looking for " + fullpath)

        if not os.path.isdir(directory):                                         # if directory does not exist
            handle_output("....Directory does not exist.")                               # notify user; unless console_output == False ;)
            handle_output("....Attempting to make directory " + directory)
            os.makedirs(directory)                                               # make directory based on the desired directory
            os.chdir(directory)                                                  # change to directory
            handle_output("/" + directory + " has been successfully created.")
            loop = 6
        else:                                                                    # or else just change directory to it
            handle_output("....It exists.")
            handle_output("Changing to the path... ")
            os.chdir(directory)
            handle_output("....Now in " + os.path.realpath(''))

            if os.getcwd() != fullpath:
                    handle_output("Something went wrong. [Trial %d]" % loop)
                    loop = loop + 1
            else:
                    loop = 6                                                    # End the loop (job is done)
    return