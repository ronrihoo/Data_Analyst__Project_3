"""""

prepare.py

Brief: extract, analyze, clean, and shape OSM XML data for conversion
       to the JSON format, which will be imported into MongoDB for analysis.

Ronald Rihoo

"""""

import codecs                                # ... log.py
import json                                  # ... log.py
import xml.etree.cElementTree as ET          # ... clean.py  (also by analyzeusers.py)
from config import *
from definitions import *
from clean import *
from log import *


__all__ = [ 'process_map',
            'shape_element']

'''

Auto- Configuration

'''

filename = grab_filename()

directory_name = grab_pathname()

error_log = grab_error_log()

report_input = grab_report_input_name_preference()

report_errors = grab_report_errors_preference()

'''

Variables

'''

# keys for "created" data
CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


'''

Functions

'''

# grab OSM XML data, make sense of it, clean it, and shape it up for the JSON format
def shape_element(element):
    # for collecting all of the shaped parts of each element passed through
    node = {}

    # the dictionary that will fall under "created"
    created_dict = {}

    # the array that will include the lat and lon
    pos_list = []

    node_refs = []

    address = {}

    # the lat and lon values will be handled carefully, because appending
    # them to a list could mean that they'll be placed in random order.
    lat = None
    lon = None  

    # for passing error codes
    err_code = 0
  
    # only concerned with "node" and "way" tags
    if element.tag == "node" or element.tag == "way" :
        for attr in element.attrib:
          if attr == "lat":
            lat = float(element.attrib[attr])
          elif attr == "lon":
            lon = float(element.attrib[attr])
          elif attr not in CREATED:
            node[attr] = element.attrib[attr]
          elif attr in CREATED:
            created_dict[attr] = element.attrib[attr]
            pass
        
        # [ lat, lon ], append "lat" first, then "lon"
        if lat != None:
          pos_list.append(lat)
        else:
          err_code = -1

        if lon != None:
          pos_list.append(lon)
        else:
          err_code += 2

        if err_code < 0:
          print "warning: lat is missing"
        elif err_code > 1:
          print "warning: lon is missing"
        
        # 'pos' : [ lat, lon ]
        if pos_list != []:
          node['pos'] = pos_list
        
        # 'created' : { ... }
        if created_dict != {}:
          node['created'] = created_dict
        
        # 'type' : 'node' (or 'way')
        node['type'] = element.tag

        # now analyzing the tags that fall under the element
        for tag in element:
          # store the value attribute of a tag in node_refs, where tag type is "nd," as such: <nd ref="2636086179"/>
          if tag.tag == "nd":
              value = tag.attrib[tag.keys()[0]]       # or ... tag.attrib['ref'], but it's not as safe
              node_refs.append(value)
          # where tag type is "tag," as such: <tag k="addr:city" v="Chicago"/>
          if tag.tag == "tag":
              tag_key = tag.attrib['k']           # ex: "addr:city" from <tag k="addr:city" v="Chicago"/>
              tag_val = tag.attrib['v']           # ex: "Chicago"   from <tag k="addr:city" v="Chicago"/>

              # Remove the "addr:" and "addr:...:..." parts from the tag_key strings
              if not lower.search(tag_key):
                if lower_colon.search(tag_key):
                  s = tag_key.split('addr:')

                  # if the tag key has been successfully reshaped by the split, then handle it; otherwise, do nothing.
                  # s[0], because what's sought after is an array like ['', 'housename']; therefore, an array like ['cuisine'] would fail.
                  if s[0] != tag_key:
                    # example: s[1] in ['', 'street'] == 'street'
                    # add the new key to the 'address' dictionary, which came with a value that also needs to be added
                    if s[1] == "street":
                      # prevent a potentially messy and unexpected value to go through, so that it won't pollute the script's learning environment
                      verified = False
                      cleaned = False
                      escape = False
                      val = remove_periods(tag_val)
                      name_verification = verify_street_value(val)
                      try:
                        if (name_verification.group()): 
                          if (report_input): 
                            handle_output(name_verification.group())
                        verified = True
                      except: 
                          # try again, but with case ignored. (AaBbCcDd...)
                          name_verification = verify_street_value(val, ignore_case = True)
                          verified = True
                          try: 
                            if (name_verification.group()): 
                              if (report_input): 
                                handle_output(name_verification.group() + " (case problem)")
                          except:
                              verified = False                  # 'verified' takes the operation back to its regular flow, so it has to be false from here
                              updated_val = clean_string(val)
                              if (updated_val == val):
                                cleaned = False
                                handle_output("\n", newline = False)
                              if (updated_val != val):
                                cleaned = True
                                if (type(updated_val) == type([])):
                                  updated_val = ' '.join(updated_val)
                                #handle_output("Result: " + updated_val)
                                handle_output("\n", newline = False)
                              # not going to deal with changing highway addresses right now, so just pass it as is
                              if (updated_val == "*highway_code"):
                                escape = True                      # bypass the cleaning state
                                address[s[1]] = val
                      if (verified == True and cleaned == False):
                        # if the street name is clean enough (according to the set re's), then pass it to get inspected and updated as needed
                        updated_val = update_name(val)
                        address[s[1]] = updated_val       # This should turn out like: { 'street' : 'N Coit Rd' }
                      # if the street name has already been cleaned, then just pass it for storage
                      elif (cleaned == True):
                        address[s[1]] = updated_val
                      elif (escape):
                        # do nothing
                        pass
                      else:
                        # add to error list
                        error_log.append(tag_val)

                        # handle output and logging
                        if (report_errors):
                          handle_output("Error: street name value \"" + tag_val + "\" is a problematic string and will not be processed.\n", True, True)     
                    
                    else:
                      # if tag key is not "street", then it does not need to first be updated in this project
                      address[s[1]] = tag_val
                  # if splitting "addr:" from the key didn't do anything and it has a second colon, then it's to be treated normally
                  elif s[0] == tag_key:
                    # in the case of problematic characters, do nothing with it and move along
                    if problemchars.search(s[0]):
                      pass
                    # otherwise, add it directly to the node dictionary, where it belongs.
                    else: 
                      node[s[0]] = tag.attrib['v']
                      pass
              # this will add attributes from tags like: <tag k="building" v="yes"/>
              elif lower.search(tag_key): 
                node[tag_key] = tag.attrib['v']

        if (node_refs != []):
          node['node_refs'] = node_refs
        
        if (address != {}):
          node['address'] = address
        
        return node
    else:
        return None

# parse through XML data; analyze and reformat the data for JSON; then write it to a JSON file
def process_map(input_filename = filename, neat_format = False):
    # generate a relative JSON filename
    output_filename = "{0}.json".format(input_filename)
    data = []
    
    manage_directory('', directory_name)

    handle_output('Opening output stream...')

    # open a file handle; update data; write data to storage and screen, then return to run() 
    with codecs.open(output_filename, "w") as file_handle:
        input_data = ET.iterparse('../../' + input_filename)
        
        handle_output("Beginning the analysis process...")
        handle_output("\n", newline=False)

        for _, element in input_data:
            updated_element = shape_element(element)

            if (updated_element):
                # cater to the console screen
                data.append(updated_element)

                # cater to the storage device
                if (neat_format):
                    file_handle.write(json.dumps(updated_element, indent=2)+"\n")
                else:
                    file_handle.write(json.dumps(updated_element) + "\n")
    
    if (data == []):
        handle_output("Ended process with no data.")
        handle_output("\n", newline = 0)                # separated for ease of log analysis

    handle_output("The analysis process is now complete.")
    return data
