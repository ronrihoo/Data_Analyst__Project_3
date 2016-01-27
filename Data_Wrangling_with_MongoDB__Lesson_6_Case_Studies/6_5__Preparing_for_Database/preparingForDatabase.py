#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        el = {}
        handled = []
        created_dict = {}
        pos_list = []
        node_refs = []
        address = {}
        lat = None
        lon = None
        
        for att in element.attrib:
          # all the other attributes
          # pos attributes
          if att == "lat":
            lat = float(element.attrib[att])
            handled.append(att)
          elif att == "lon":
            lon = float(element.attrib[att])
            handled.append(att)
          elif att not in CREATED:
            el[att] = element.attrib[att]
            handled.append(att)
          # "created" attributes
          elif att in CREATED:
            created_dict[att] = element.attrib[att]
            handled.append(att)
            pass
        

        # Pos : { lat:v, lon:v}
        pos_list.append(lat)
        pos_list.append(lon)
        
        if pos_list != []:
          el['pos'] = pos_list
        
        # "created" dictionary
        if created_dict != {}:
          el['created'] = created_dict
        
        # Type
        el['type'] = element.tag

        for tag in element:

          if tag.tag == "nd":
              value = tag.attrib[tag.keys()[0]]
              node_refs.append(value)

          if tag.tag == "tag":
              tag_key = tag.attrib[tag.keys()[0]]

              # Take care of the "addr:" and "addr:...:..." parts
              t = tag_key.split('addr:') 
              if t[0] != tag_key:
                try: 
                    assert t[1].split(':')[1]
                    handled.append(tag_key)
                except: 
                    address[t[1]] = tag.attrib['v']
                    handled.append(tag_key)

              # Grab other parts
              x = tag.attrib['k']

              if x not in handled:
                if problemchars.search(x):
                  print "problematic key found and abandoned"
                else: 
                  el[x] = tag.attrib['v']
                  pass

        if (node_refs != []):
          el['node_refs'] = node_refs
        
        if (address != {}):
          el['address'] = address
        
        node = el
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map('example.osm', True)
    #pprint.pprint(data)
    
    correct_first_elem = {
        "id": "261114295", 
        "visible": "true", 
        "type": "node", 
        "pos": [41.9730791, -87.6866303], 
        "created": {
            "changeset": "11129782", 
            "user": "bbmiller", 
            "version": "7", 
            "uid": "451048", 
            "timestamp": "2012-03-28T18:31:23Z"
        }
    }
    assert data[0] == correct_first_elem
    assert data[-1]["address"] == {
                                    "street": "West Lexington St.", 
                                    "housenumber": "1412"
                                      }
    assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369", 
                                    "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()
