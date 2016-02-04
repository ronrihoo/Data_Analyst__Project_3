"""""

config.py

Ronald Rihoo

"""""

__all__ = [ 'grab_filename', 
			'grab_pathname', 
			'grab_monitoring_preference', 
			'grab_report_basics_preference',
			'grab_report_errors_preference', 
			'grab_report_input_name_preference', 
			'grab_report_lateral_name_parts_preference',
			'grab_report_result_preference',
			'grab_report_zipcode_preference',
			'grab_tabbed_output_preference' ]

'''

Configuration

'''

## File and Directory Settings

# name of OSM file
filename = "map_smaller"

# name of folder that will be created and used for storing 
# multiple log files
directory_name = filename + "_dir"


''' Event Monitoring and Tracking '''

# Event Monitoring
#
# When 'True', the event messages will print out to the screen 
# according to the settings that follow. Logging will occur either 
# way. Even though this setting will not affect logging, the following
# settings will.
#
# When 'False', all of the below settings will be irrelevant to the 
# screen output. However, the settings that follow will affect the 
# logging process.
#
monitor_events = True

# Reporting Basics
#
# This includes three items: 
#		- the input name given
#		- each word in the given name, within a list
#		- the number of words (or frags for fragments) in the name
#
# In the following example, produces the flagged parts of the output:
#
#	 Input: North Coit Road 		<---
#	 ['North', 'Coit', 'Road']		<---
#	 Frag_num: 3					<---
#	 Prefix: North
#	 Suffix: Road
#	 Result: N Coit Rd
#
report_basics = True


# Reporting Input Value
#
# This is an alternative to reporting the basics and could be used
# when less event information is desired for printing out on the screen
# during runtime. It can be useful for easier comparison between the 
# input value and the output value (result).
#
# This includes only one item: 
#		- the input name given
#
# In the following example, it produces the flagged part of the output:
#
#	 Input: North Coit Road 		<---
#	 Prefix: North
#	 Suffix: Road
#	 Result: N Coit Rd
#
report_input = False


# Reporting Lateral Name Parts
#
# Prints out the prefix and suffix of the provided street name, for
# visual inspection of the values to gain more insight over the data.
#
# This includes two items: 
#		- the prefix of the input name given
#		- the suffix of the input name given
#
# In the following example, produces the flagged parts of the output:
#
#	 Input: North Coit Road
#	 Prefix: North					<---
#	 Suffix: Road  					<---
#	 Result: N Coit Rd
#
report_lateral_name_parts = True


# Reporting the Street Result
#
# Shows the result of the reformatting/cleaning process.
#
# This includes only one item: 
#		- the resulting string after reformatting the given input name
#
# In the following example, it produces the flagged part of the output:
#
#	 Input: North Coit Road
#	 Prefix: North
#	 Suffix: Road
#	 Result: N Coit Rd 				<---
#
report_result = True


# Reporting the Zipcode Scans and Cleaning Results
#
# This includes the following output:
# 
# 	Zipcode scanned and inserted into data with zero problems found
#	Zipcode: 75206 
#
# or
#
# Error: problematic zipcode found in the 'postcode' tag.
# 	Zipcode: TX 75074
#	Cleaned: 75074
#  
report_zipcode = True

# Reporting Errors
#
# This signal will induce the printing of error messages on the screen.
#
# All errors will be logged in .../log/error_log.json, regardless.
#
# This includes only one item: 
#		- the resulting string after reformatting the given input name
#
# Example:
# ...
# No good fragments were found in this string.
# No bad fragments were found in this string.
# 
# Error: street name value "TX 78" is a problematic string and will not
#		 be processed.
#
# Greenville Ave
# Input: Greenville Ave
# ['Greenville', 'Ave']
# ...
#
report_errors = True						# prints error messages


# Tabbed Output
# 
# For visual differentiation between regular and operational/troubled 
# activities, tabbing can be useful. In this case, the normal 
# reformatting activity, such as changing "North Arapaho Road" to 
# "N Arapaho Rd", will be tabbed, along with other minor contributions 
# to the process (removing periods; switching word placement). 
#
# Operational activities, such as switching directories and producing
# logs, will not be tabbed. Troubled activities, such as scanning 
# problematic strings, will not be tabbed either. This way, the analyst
# can more easily focus on either type of activity as needed during the 
# analysis and/or troubleshooting process.
# 
# Here is an example of tabbed output:
#
# ...
# Deep scan is complete.
# Result: *highway_code
#
#	  Input: Greenville Ave
#	  ['Greenville', 'Ave']
#	  frag_num: 2
#	  Prefix: Greenville
#	  ----Warning: prefix dictionary may not have been sufficient to support: Greenville
#	  Suffix: Ave (expected)
#	  Result: Greenville Ave
#
#	  Input: Greenville Ave
#	  ['Greenville', 'Ave']
#	  frag_num: 2
#	  ...
# ...
#
# An example of untabbed output:
#
# ...
# Nothing has been found by the Out-of-Scope scan.
# Running Word-by-Word scan and build...
# Searching for '5223'
# ----It's a potential housenumber.
# Searching for 'alpha'
# Searching for 'road'
# ----It's a potential mistyped suffix.
# Searching for 'dallas'
# ----It's a potential city.
# Searching for 'tx'
# ----It's a potential state.
# Searching for '75240'
# ----It's a potential zipcode.
# Deep scan is complete.
# Result: Alpha Road
#
# Input: Alpha Road
# ['Alpha', 'Road']
# frag_num: 2
# Prefix: Alpha
# ----Warning: prefix dictionary may not have been sufficient to support: Alpha
# Suffix: Road
# Result: Alpha Rd
#
# Cleaning problematic string value...
# No comma issues found.
# Beginning deep scan...
# ...
#
tabbed = True

# Prevent duplicate printing of the input name
if (report_basics == True): report_input = False


'''

Data Provision

'''

## File and Directory Handling
def grab_filename():
    return filename

def grab_pathname():
    return directory_name


## Event Monitoring and Tracking

def grab_monitoring_preference():
    return monitor_events

def grab_report_basics_preference():
	return report_basics

def grab_report_input_name_preference():
	return report_input

def grab_report_lateral_name_parts_preference():
	return report_lateral_name_parts

def grab_report_result_preference():
	return report_result

def grab_report_zipcode_preference():
	return report_zipcode

def grab_report_errors_preference():
	return report_errors

def grab_tabbed_output_preference():
	return tabbed