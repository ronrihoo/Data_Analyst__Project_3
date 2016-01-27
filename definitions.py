"""""

definitions.py

Brief:  incomplete specifications of Dallas County conventions for naming transportation paths,
        in the form of regular expressions, arrays, and dictionaries. Also, never-to-be-complete
        sets of definitions for problems, because only testing for expectations is not enough.

Note: there is a methodology much easier than this, that I have in the laterals of my mind and
      have already written some of the code for here. I will implement it as an add-on in a future 
      update, provided that I don't become too busy.

Ronald Rihoo

"""""

import re


'''''

Street Data Shaping

(prepare.py)

'''''

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


'''''

Dallas County Street-Naming Conventions

Expected Prefix and Suffix Values

'''''

expected_prefix = [ "N", "S", "E", "W" ]

expected_suffix = [ "St",   "Ave",  "Blvd", "Dr",   "Ct", 
                    "Pl",   "Sq",   "Ln",   "Rd",   "Tr", 
                    "Pkwy", "Cmns", "Cir",  "Ctr",  "Way",  
                    "Expressway", "Highway", "Freeway",         # these three should be in their own list
                  ]

prefix = {
            "North"     : "N",
            "South"     : "S",
            "West"      : "W",
            "East"      : "E",
         }

# lower-cased or other types included as needed
suffix = {  "Street"    : "St",
            "Avenue"    : "Ave",
            "Boulevard" : "Blvd",
            "Drive"     : "Dr",
            "dr"        : "Dr",
            "Court"     : "Ct",
            "Place"     : "Pl",
            "Square"    : "Sq",
            "Lane"      : "Ln",
            "Road"      : "Rd",
            "Trail"     : "Tr",
            "Parkway"   : "Pkwy",
            "Commons"   : "Cmns",
            "Circle"    : "Cir",
            "Center"    : "Ctr",
         }


'''''

Dallas County Street-Naming Conventions

Regular Expressions

'''''

# common street names, such as "Arapaho Rd" or "N Arapaho Rd"
dallas_name_convention_re = re.compile(r'(((?P<direction>^[N,S,E,W](([o,a,e][r,u,s][t]([h]?))?) )?))(?P<name_parts>((([0-9]+)(st|[n,r]d|th) )?)(([A-Z]([a-z]+) )+)?)(?P<street_type>[A-Z]([a-z]+)$)')
dallas_name_ignore_case_re = re.compile(r'(((?P<direction>^[N,S,E,W](([o,a,e][r,u,s]|[t]([t]?))?) )?))(?P<name_parts>([A-Z](([a-z]+)?) )+)(?P<street_type>[A-Z]([a-z]+)$)', re.IGNORECASE)


'''''

Problematic Street Name Conditions (For Dallas County)

'''''

# starting with digits that are immediately followed by a space; unapplicable characters anywhere; zip codes at the end
problem_conditions_re = re.compile(r'(^[0-9]+ )|([=\+/&<>;"\?%#$@\,\t\r]+)|( [0-9]{4,5}$)|( [0-9]+[\-][0-9]+$)')
problem_address_parts_re = re.compile(r'(?P<house_number>^[0-9]+ )|(?P<suite>(( ?)(([s,S][u,U]?[i,I]?[t,T]?[e,E]?#?)|(#))[0-9]+))|(?P<zip_code> [0-9]+[\-][0-9]+$)')
problem_chars_nums_re = re.compile(r'(?P<bad_char>[=\+/&<>;"\?%#$@\,\t\r]+)|(?P<bad_num>(( [0-9]{4})|( [0-9]{6,}))$)')

# problems against the Dallas County street naming conventions
prefix_problems_re = re.compile(r'(^([n,s,e,w]|[N,S,E,W])([o,a,e])([r,u,s])([a-z]{1,2}) )')
suffix_problems_re = re.compile(r'[ ](((([a-z]+)|[a-z][a-z]|([A-Z]([a-z]+))))$)')
period_problem_re = re.compile(r'[\.]')

# State Highway: SH ###
highway_texas_re = re.compile(r'(^(([N,S,E,W]?)( ?)([t,T][x,X])( ?))([0-9]{1,3}))$')
highway_general_re = re.compile(r'(^(([N,S,E,W]?)((orth|outh|ast|est)?)( ?)([a-z,A-Z]{2,3}) ?))(([a-z,A-Z]-)?([0-9]{1,3})([n,N,s,S,e,E,w,W]?))$', re.IGNORECASE)

# I-### or I-###E
interstate_re = re.compile(r'(^([a-z,A-Z]{2} ))(([a-z,A-Z]-)?([0-9]{1,3}))')


'''''

Other Problematic Street Names (an unfair section title, but I have to get this project done for now)

'''''

# Detect the following type of street value errors: "5223 alpha road dallas tx 75240" 
#                                                   "5229 alpha road dallas tx 75240"
#
# Dissecting the error: { 'housenumber' : '5223', 'street name' : 'alpha road', 'city' : 'dallas', 'state': 'tx', 'zipcode': '75240' }
#
# So someone or something (a bot) input all of that for the 'street name',--unbelievable!

# scan for 'housenumber' -- limited because of zipcode issue
house_number_re = re.compile(r'(?P<house_number>(((^[^a-zA-z]+))([0-9]{1,4})( ?)))')

# scan for city (Dallas)
city_sweep_re = re.compile(r'(?P<city>(( ?)[d,D][a,A][l,L][l,L][a,A][s,S]( ?)))')

# scan for state (Texas)
state_sweep_re = re.compile(r'(?P<state>((((,?)( ?)(,?)))([t,T][x,X])(,? ?)))')
state_good_punct_re = re.compile(r'(?P<state>(, [t,T][x,X] ))')
state_bad_punct_re = re.compile(r'(?P<state>( [t,T][x,X])( ?))')

# scan for zipcode (US)
zipcode_re = re.compile(r'(?P<zip_code>( ?([0-9]{5})([\-]?)(([0-9]+)?)$))')

# unknown/undesignated long digits
unk_digits_re = re.compile(r'(?P<long_digits>( ?(([0-9]{6,}))( ?)))')

digits_re = re.compile(r'[0-9]+')


# Detect the following errors: "Avenue K, suite 700-285"
#                              "Forest Central Drive, Suite 300"
#                              "Noel Road, Suite 1370"
#                              "Preston Road #500E"
#
# scan for suite - 'suite', '#', suite number, suite letter as a sub-suite address
suite_re = re.compile(r'(?P<suite>([s,S][u,U][i,I]?[t,T]?([e,E]?|([e,E] )?)))|((?P<suite_number>(#?)([0-9]+))(?P<suite_extention>((-[0-9]+)?))(?P<suite_letter>(([a-z,A-Z]$))?))')


'''''

Street Type

Regular Expressions

'''''

street_type_re = re.compile(r'Road|Street|Avenue|Boulevard|Drive|Court|Place|Square|Lane|Trail|Parkway|Cmmons|Circle|Center', re.IGNORECASE)
