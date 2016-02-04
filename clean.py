"""""

clean.py

Brief: functions for identifying and cleaning up problematic street 
       name values, and for modifying all street names to match the
       same naming conventions used by the respective cities/county.

Data Philosophy: waste nothing; salvage everything.

--Code Guide--

    Line Continuation:

      Case 1: Backslash Inside Parentheses
        The '\' will be placed one column before the last parenthesis.
        The preference is based on keeping it "inside" the parentheses.
        All '\' inside the parentheses are placed uniformly.
      
      Example 1:
        def deep_scan(name,                         \
                      return_useables = False,      \
                      full_string = None,           \
                      report_result = report_result  ):

      Case 2: Backslash Outside Parentheses
        The '\' will be placed anywhere as needed, but all uniformly.

      Example 2:
        if (cleaned_name != name) and                 \
                (cleaned_name != "*highway_code") and \
                (cleaned_name != "*suite_code"):
      

        

Ronald Rihoo

"""""

import sys
from config import *
from definitions import *
from prepare import *
from log import grab_learned_names,      \
                handle_output,           \
                insert_known_parts,      \
                insert_useable_parts,    \
                learn_medial_name_parts, \
                store_processed_parts


__all__ = [ 'clean_string', 
            'remove_periods', 
            'update_name', 
            'verify_street_value' ]

'''

Auto-Configuration

'''

report_basics = grab_report_basics_preference()

report_input = grab_report_input_name_preference()

report_lateral_parts = grab_report_lateral_name_parts_preference()

report_result = grab_report_result_preference()

tabbed = grab_tabbed_output_preference()

learned_names = grab_learned_names()

# codes can be used to flag certain types of data for many purposes,
# such as passing them through without analysis or storing them and
# not passing them for insertion into the main data stream
codes = [ '*highway_code', '*interstate_code', '*suite_code' ]


'''

Data Provision

'''

def grab_codes():
    return codes


'''

General Working Functions

'''

# make a list with a single string value
def convert_to_list(name):
    street_name = []
    return street_name.append(name)

# split name apart into different fragments, count them, and 
# calculate the index for the last one
def fragment_and_count(name):
    fragment = name.split(' ')
    frag_num = len(fragment)
    last = (frag_num - 1)
    return fragment, frag_num, last

# deep scan findings report
def ds_report_findings(description):
    handle_output("....It's a potential " + description + ".")
    return

# change the first letter of a word to uppercase and return the 
# formatted word
def up(word, all_chars = False):
    if (all_chars):
        cased_word = word.upper()
    else:
        cased_word = word[0].upper() + word[1:]
    return cased_word


'''

Reporting Functions

'''

def handle_initial_reporting(name,                          \
                             fragment,                      \
                             frag_num, tabbed = tabbed,     \
                             report_basics = report_basics, \
                             report_input = report_input,    ):
    if (report_basics):
        report_initial_info(name, fragment, frag_num)
    elif (report_input):
        if tabbed:
            sys.stdout.write('\t')
        handle_output("Input" + name)
    return

# print the street name (for before updating it); print the 
# fragment list; print the quantity of fragments
def report_initial_info(name,           \
                        fragment,       \
                        frag_num,       \
                        tabbed = tabbed  ):
    if tabbed:
        sys.stdout.write('\t')
    handle_output("Input: " + name)

    if tabbed:
        sys.stdout.write('\t')
    handle_output(fragment)

    if tabbed:
        sys.stdout.write('\t')
    handle_output("Frag_num: " + str(frag_num))
    return

def report_result(name, tabbed = True):
    if tabbed:
        sys.stdout.write('\t')
    handle_output("Result: " + name)

# prints the learned-name list and adds the same print-out 
# to the event-log too
def report_learned_names(actual_parts = learned_names):
    handle_output("Learned: ")
    handle_output(actual_parts)
    # this separation will make the log analysis easier later
    handle_output("\n", False, False, 0)
    return

'''

Delegation Functions

'''

# manipulates problematic strings in multiple ways and calls 
# scanners onto them to find signs of string values that can 
# be fixed and/or salvaged 
def clean_string(string, char = ',', value_type = "street"):
    if (report_input) or (report_basics):
        handle_output('Input: ' + string)

    handle_output("Cleaning problematic '" + value_type + "' string value...")

    # create a list object of the string for comparison 
    # to a split object
    string_list = []
    string_list.append(string)

    split_string = string.split(char)

    cleaned_string = ''
    processed_names = ''
    processed_names_list = []

    # Handling given character (arg: char) issues
    if (split_string != string_list):
        handle_output("Found a '" + char + "' issue...")

        if (value_type == "street"):
            good_frag_index, bad_frag_index = split_and_scan(string, 
                                                             char)
        if (value_type == 'zipcode'):
            good_frag_index, bad_frag_index = split_and_scan(string, 
                                                             char, 
                                                             street = False, 
                                                             zipcode = True)
        handle_output('Output: ' + split_string[good_frag_index[0]] + ' (piping)')

        # Try just one good fragment, since only one good value can be
        # taken for now, 
        #
        # However, I propose that future plans should include to fuse
        # multiple good parts together in the correct way, as needed, 
        # which will require wider analytic capabilities (*1), and to
        # decide between two or more completely good fragment values
        # to keep as the best value (*2).
        #
        # Current Analytic Capacity Limitations
        #
        # 1. Multiple Valid Parts Improperly Separated by a Character.
        #
        #   if, 
        #       string == 'W, Arapaho, Road, TX, 75080'
        #   then, 
        #       only 'W' will be used, while the rest will be stored as
        #       identified, useful, and in need of further analysis
        #
        # A much wider analytic capacity is required for this function
        # to properly clean multiple comma (or other char) issues.
        #
        # 2. Multiple Valid Values Improperly Included Together and
        #    Separated by a Character.
        #
        #   if,
        #       string == 'W Arapaho Road, N Coit Road, TX, 75080'
        #   then,
        #       only 'W Arapaho Road' will be used, while the rest will
        #       be stored away for future analysis.
        # 
        # At this time, such problems have not been found in the Dallas
        # County OSM dataset that I have retrieved, so there is no need
        # to create the wider analytic procedures.
        #
        if good_frag_index != []:
            index = good_frag_index[0]
            if (value_type == 'street'):
                cleaned_string = split_and_fix(string, 
                                               char, 
                                               index, 
                                               basic = True)
            if (value_type == 'zipcode'):
                cleaned_string = split_and_fix(string, 
                                               char, 
                                               index, 
                                               zipcode = True)
        else:
            handle_output("No good fragments were found in this string.")

        if bad_frag_index != []: 
            handle_output("Attempting to identify the bad fragment and store "
                          "for manual inspection...")
            for index in bad_frag_index:
                processed_names = split_and_fix(string, 
                                                char, 
                                                index, 
                                                deep = True)
            # if the processed string is not empty or a code,
            # then append it to the processed_names list
            if (processed_names != '') and (processed_names[0] != '*'):
                processed_names_list.append(processed_names)

            # if one or more bad frags were processed,
            # then store them in the processed_parts log
            if (processed_names_list != []):
                store_processed_parts(processed_names_list, 
                                      known = True)
                handle_output("Bad fragment has been salvaged and stored in the "
                              "'useables' section of the log (some words could "
                              "be listed as 'unknown').")
        else:
            handle_output("No bad fragments were found in this string.")
    # Handling non-given-char issues
    else:
        handle_output("No '" + char + "' issues found.")
        if (value_type == 'street'):
            cleaned_string = deep_scan(string, full_string = string)
            if (cleaned_string != string) and (cleaned_string not in codes):
                handle_output("\n", newline = False)
                cleaned_string = update_name(cleaned_string, newline = False)
        if (value_type == 'zipcode'):
            good_frags, bad_frags = split_and_scan(string, 
                                                   char, 
                                                   street = False, 
                                                   zipcode = True)
            if (good_frags != []):
                cleaned_zipcode = split_and_fix(string, 
                                                char,
                                                good_frags, 
                                                zipcode = True)
            if (cleaned_string != string)         and   \
                    (cleaned_string not in codes) and   \
                    (cleaned_string != ''):
                handle_output("\n", newline = False)
                cleaned_string = update_name(cleaned_string, newline = False)

    return cleaned_string


'''

Data Scanning

'''

# verify if street name can be handled by the current state of the code
def verify_street_value(street_name,        \
                        ignore_case = False  ):
    if (ignore_case):
        return dallas_name_ignore_case_re.search(street_name)
    return dallas_name_convention_re.search(street_name)

def verify_zipcode_value(zipcode):
    return US_zipcode_re.search(zipcode)

# Split and Scan
#
# Detects the following type of errors: 
#
# "Avenue K, suite 700-285"
# "Forest Central Drive, Suite 300"
# "Noel Road, Suite 1370"
#
# Splits at the char from arg (comma, space, etc) and scans each 
# partition separately. This is a fragment-flagging mechanism used
# to find good fragments that require further scanning and fixing
# method to be called upon them. It also identifies bad fragments
# and handles them separately for scanning and storing.
#
# These are the problems that it tries to help solve: 
# 'Noel Road, Suite 1370' where only 'Noel Road' is expected
# and
# 'TX 75240' where only '75240' is expected
#
def split_and_scan(string, char, street = True, zipcode = False):
    # report state
    handle_output('Running split-and-scan...')
    
    # if string == "Noel Road, Suite 1370"
    # then line_list == [ 'Noel Road', 'Suite 1370' ]
    line_list = string.split(char)
    handle_output(line_list)

    # in the previous list example, last item == 'Suite 1370'
    # therefore, last index == 1
    last = (len(line_list) - 1)         # last index in word_list
    index = 0                           # word index

    # should be sets, due to the usage in this function; however,
    # some external functions require lists to be returned and other
    # functions smartly handle the lists
    index_of_good_frags = []            # track expected fragments
    index_of_bad_frags = []             # track unexpected fragments

    # operate on a list with more than one value; 
    # for example, [ "Noel Road", "Suite 1370" ]
    #           or [ 'TX', '75240' ]
    if ((type(line_list) == type([])) and (len(line_list) > 1)):
        # report state
        handle_output('Operating on a list with more than one value...')
        
        # search each fragment of the given string
        for line in line_list:
            
            ''' Street Name Values '''
            
            # if street name value, then expect fragments that have
            # multiple words/parts with spaces in between them
            #
            # Loop 1: 
            #   line == line_list[0], which is 'Noel Road',  index: 0
            # Loop 2:
            #   line == line_list[1], which is 'Suite 1370', index: 1
            if (street):
                # Loop 1:
                #   'Noel Road' will pass as a street value
                if (verify_street_value(line, ignore_case = True)):
                    # Loop 1:
                    #   index 0 will be appended in list of good frags
                    index_of_good_frags.append(index)
                # Loop 2:
                #   'Suite 1370' will pass as not a street value
                if (not verify_street_value(line, ignore_case = True)) and \
                                          (index not in index_of_good_frags):
                    # Loop 2:
                    #   index 1 will be appended in list of bad frags
                    index_of_bad_frags.append(index)

                # Further Dissection of the String for Analysis
                # 
                # This is because the verification method might have
                # failed and provided a false negative, so deeper
                # analysis of the fragment will provide a second chance
                # at seeing the good, useful parts and fixing them for
                # use later. This is still a fragment-flagging method.
                #
                # Loop 1:
                #   words == [ 'Noel', 'Road' ]
                #   fragment index == 0
                #
                # Loop 2:
                #   words == [ 'Suite', '1370' ]
                #   fragment index == 1
                words = line.split(' ')

                # Line Loop 1:
                #
                #   Word Loop 1:
                #       word == 'Noel'
                #       fragment index == 0
                #   Word Loop 2:
                #       word == 'Road'
                #       fragment index == 0
                # 
                # Line Loop 2:
                # 
                #   Word Loop 1:
                #       word == 'Suite'
                #       fragment index == 1
                #   Word Loop 2:
                #       word == '1370'
                #       fragment index == 1
                for word in words:
                    if (word in prefix):
                        index_of_good_frags.append(index)
                    if (word in suffix):
                        index_of_good_frags.append(index)


            ''' Zipcode Values '''
            
            # if zipcode value, then expect fragments that have one
            # word/part each; therefore, no spaces, as they have been
            # removed by the split at the beginning of the procedure.
            if (zipcode):
                # Recall: this is within a loop: line in line_list
                # Where:
                #   if,
                #       string == 'TX 75240'
                #   then,
                #       line_list == [ 'TX', '75240' ]
                #
                # Loop 1:
                #   line == 'TX', index == 0
                # Loop 2:
                #   line == '75240', index == 1

                # Loop 2: 
                #   '75240' will pass as a zipcode
                if (verify_zipcode_value(line)):
                    # Loop 2:
                    #   index 1 will be appended in good frags list
                    index_of_good_frags.append(index)
                if (not verify_zipcode_value(line)) and \
                       (index not in index_of_good_frags):
                    # Loop 1:
                    #   index 0 will be appended in bad frags list
                    index_of_bad_frags.append(index)

            # index tracking in the fragment loop; begins at 0
            index += 1

    # report state
    handle_output('Split-and-scan is complete.')
    return index_of_good_frags, index_of_bad_frags

# waste nothing; use every resource available
#
# this function scans and builds; however, due to its vast scanning 
# capabilities,I consider it to mostly be a scanner with an embedded 
# rebuilder
def deep_scan(name,                         \
              return_useables = False,      \
              full_string = None,           \
              report_result = report_result  ):
    # report state
    handle_output("Beginning deep scan...")

    # variables (lists are for the anticipation that multiple parts 
    # of the same type might exist here; such as two zipcodes)
    words = re.split('\W', name)
    wc = len(words)                     # word count

    # scanner status
    w2w_scan = False                    # word-by-word scan record

    # string value variables
    useables = {}                       # know what it is; can't use it
    unknown = []                        # don't know what it is
    fs = []                             # fake_string - rebuilt name
    housenumber = []
    suite = []
    city = []
    state = []
    zipcode = []

    # condition variables

    # prefix_stat -- 0 for 'does not exist yet'; 1 for 'it has been set'
    ps = 0
    # suffix stat -- 0 for 'does not exist yet'; 1 for 'it has been set'
    ss = 0
    # actual name parts stat -- 0 for none; 1 to infinite for quantity
    ns = 0
    # for keeping track of the words in the fragment during for loops
    index = 0

    # new suffix (for switching out with the old one)
    s = ''
    # description of the name part based on findings -- for reporting 
    # findings to the analyst
    descr = ''
    # final result variable
    result = ''

    # out-of-scope signals
    highway = False                     # highway marking
    suite_designation = False           # suite marking

    # basic info about the fragment going through analysis
    handle_output("Fragment: " + name)
    handle_output("Word Count: " + str(wc))

    
    ''' Quick Highway Address Scan '''

    handle_output("Starting the Quick Highway scan...")
    
    potential_zipcode = False

    for part in name.split(' '):
        if (US_zipcode_re.search(part)):
            potential_zipcode = True

    if not (potential_zipcode):
        if (highway_general_re.search(name)):
            descr = "highway name"
            handle_output("This string is a potential " + descr)
            highway = True
            result = "*highway_code"
        if (interstate_re.search(name)):
            descr = "interstate name"
            handle_output("This string is a potential " + descr)
            highway = True
            result = "*highway_code"

        if result == "*highway_code":
            handle_output("This address value has been deemed as a highway address"
                          " and will be inserted back into the data without"
                          " manipulation.")
    # report state
    handle_output("End of Quick Highway scan.")

    if descr == '':
        handle_output("Nothing has been found by the Quick Highway scan.")

    
    ''' Quick Suite Designation Scan '''
    
    # some strings that have a comma followed by a suite designation can
    # waste time and resources, especially in my OSM file, so let's take
    # care of it at the beginning and set the right signals 
    # (suite_designation = True) to bypass the rigorous scans
    if not highway:
        handle_output("Attempting the Quick Suite Designation scan...")
        first_letter = ''
        # hard-coded based off of my own dataset's errors; otherwise, 
        # this has to become a loop or a smart regex pattern test; or 
        # something better
        try: 
            # example, words == [ 'first', 'second', 'third' ]
            #                       [0]      [1]       [2]
            #          words[0][0] == 'f'
            #          words[1][0] == 's'
            if (words[0][0] != ''):
                first_letter = words[0][0]
            else:
                first_letter = words[1][0]
        except:
            # perhaps the first "letter" of the first "part" of the list
            # is an '' (empty string), for instance: 
            #                      
            # words == [ '', 'Suite', '1370' ]
            # 
            # -then it could have failed because of indexing issues. 
            # So, let's try the next list index item's first byte:
            try: first_letter = words[1][0]
            except: 
                # in case of failure, make sure we didn't catch anything 
                # funky before going to the next procedure
                first_letter = ''
                handle_output("The Quick Suite Designation scan could not identify "
                               "suite address information in this fragment.")
        if (first_letter != ''):
            # there's a much easier way to do this. This is just for 
            # the readability and ease
            if (first_letter == ' ' or 
                first_letter == 's' or 
                first_letter == 'S' or 
                first_letter == '#'    ):
                # -then the letter might possibly be a suite
                for word in words:
                    if (suite_re.search(word)):
                        # -then the fragment most likely contains only suite designations
                        print word
                        insert_known_parts(name)
                        suite_designation = True
                        result = '*suite_code'
                        handle_output("This fragment has been deemed as a suite designation and "
                                      "will be stored, but not inserted back into the data.")
            handle_output("The quick Suite Designation scan is now complete.")
    # reset the description string for re-use
    descr= ''

    
    ''' Word-by-Word Scan and Build '''
    
    if not highway and not suite_designation:
        # indicate that the word-by-word scan has occurred
        wbw_scan = True

        # report state
        handle_output("Running Word-by-Word scan and build...")

        # search every word
        for word in words:
          if (word != ''):  
            handle_output("Searching for '" + word + "'")
            if (word in expected_prefix):       descr = "prefix";                         w = up(word); fs.append(w);   ps = 1;     ds_report_findings(descr)
            if (word in expected_suffix):       descr = "suffix";                         s = up(word);                 ss = 1;     ds_report_findings(descr)
            if (word in prefix and ps == 0):    descr = "unconventional prefix";          w = up(word); fs.append(w);   ps = 1;     ds_report_findings(descr)
            if (word in suffix and ss == 0):    descr = "unconventional suffix";          s = up(word);                 ss = 1;     ds_report_findings(descr)
            if (word in learned_names):         descr = "part of a known street name";    w = up(word);                             ds_report_findings(descr)
            if (word not in learned_names):
              if (word[0] != word[0].upper()):
                w = up(word)
                if (w in learned_names):        descr = "part of a known street name";                                              ds_report_findings(descr)
            if (ss == 0):
              if (street_type_re.search(word)): descr = "mistyped suffix";                s = up(word);                             ds_report_findings(descr)
            if (index == 0):
              if (house_number_re.search(word)):descr = "housenumber";                    housenumber.append(word);                 ds_report_findings(descr)
            if (index != 0) and (len(word) < 5):
              if (suite_re.search(word)):       descr = "suite designation";              suite.append(word);                       ds_report_findings(descr)
            if (city_sweep_re.search(word)):    descr = "city";                           city.append(up(word));                    ds_report_findings(descr)
            if (state_sweep_re.search(word)):   descr = "state";                          state.append(up(word, all_chars = True)); ds_report_findings(descr)
            if (zipcode_re.search(word)):       descr = "zipcode";                        zipcode.append(word);                     ds_report_findings(descr)
            if (unk_digits_re.search(word)):    descr = "string of undesignated digits";  unknown.append(word);                     ds_report_findings(descr)
            if (descr == ''):
                unknown.append(word);
                # it might be part of the street name
                if (not digits_re.search(word))     and    \
                                (word not in suite) and    \
                                (word not in city)  and    \
                                (word not in state):
                    uw = up(word)
                    fs.append(uw)


            # add a medial part of the street name
            #if ((w in learned_names) or (word in learned_names)) and    \
            if ((word in learned_names) or (up(word) in learned_names)) and     \
                                ((not digits_re.search(word))           and    \
                                 (up(word) != s)                        and    \
                                 (word not in fs)                       and    \
                                 (up(word) not in fs)                   and    \
                                 (word not in suite)                    and    \
                                 (up(word) not in city)                 and    \
                                 (word.upper() not in state)):
                fs.append(up(word))
                ns +=1

            descr = ''
            index += 1
            continue

        # recall: fs stands for fake string
        #         fs is used to rebuild a healthy version of the string

        # add the suffix
        fs.append(s)
        result = ' '.join(fs)
        pass


    ''' Collect Identified and Unknown Processed Parts '''

    # put the identified parts in a packet and store them for review, 
    # as they are not useable here
    if (housenumber != []):
        # if there's only one item in the list, then store the item 
        # as a string
        if (len(housenumber) == 1):
            useables['housenumber'] = housenumber[0]
        # if there are more than one item in the list, 
        # then just store the whole list
        else:
            useables['housenumber'] = housenumber
    if (suite != []):
        if (len(suite) == 1):
            useables['suite'] = suite[0]
        else:
            useables['suite'] = suite
    if (city != []):
        if (len(city) == 1):
            useables['city'] = city[0]
        else:
            useables['city'] = city
    if (state != []):
        if (len(state) == 1):
            useables['state'] = state[0]
        else:
            useables['state'] = state
    if (zipcode != []):
        if (len(zipcode) == 1):
            useables['zipcode'] = zipcode[0]
        else:
            useables['zipcode'] = zipcode

    # store the unknown processed parts for human review
    if (unknown != []):
        store_processed_parts(unknown, known = False)

    # store the known processed parts for human review
    if (useables != {}):
        store_processed_parts(useables, 
                              name = full_string, 
                              passing_useables = True)


    ''' Produce Deep Scan Final Report '''
    
    # if Word-by-Word scan has been conducted, yet no known parts
    # have been found
    if (w2w_scan == True) and \
               (fs == []            and     \
                housenumber == []   and     \
                suite == []         and     \
                city == []          and     \
                state == []         and     \
                zipcode == []  ):
       handle_output('Nothing has been found by the Word-by-Word scan.')

    # notify analyst that the scan process is complete
    handle_output("Deep scan is complete.")

    # show/log final result
    if (report_result):
        handle_output("Result: " + result)

    # 
    if (return_useables == True):
        # if a fake string was produced, then a potentially good street
        # value is now in possession, so return it for use
        if (fs != []):
            if (useables == []):
                handle_output("Note: no useable parts were found.")
            return result, useables
    elif (return_useables == False):
        # if a fake string was produced, then a potentially good street 
        # value was produced, so return it
        if (fs != []):
            return result
        if (fs == []) and (highway == False) and (suite_designation == False):
            handle_output("Failed to find any street name results with "
                          "the deep scan.")

    return result


'''

Data Cleaning

'''


# look for periods, '.', in a string and remove them
def remove_periods(string, tabbed = tabbed):
    street_name = []
    street_name.append(string)

    period_problem_re = re.compile(r'[\.]')
    periods = 0

    if (period_problem_re.search(string)):
        handle_output('Found periods in string: ' + string)

    while (period_problem_re.search(string)):
        partial = string.split('.')

        if (partial != street_name):
            string = ''.join(partial)
            periods += 1

        handle_output('Cleaned value: ' + string)
    
    if (periods > 0):
        #if tabbed:
        #    sys.stdout.write('\t')
        handle_output('Periods: ' + str(periods) + ' (removed)')
        handle_output('\n', newline = False)

    return string


# change the format of the street name to the type expected; 
# example: 'Coit Road' -> 'Coit Rd'
def reformat_value(name, 
                   fragment, 
                   street_name, convention_dict, frag_index):
    for key in convention_dict:
        val = convention_dict[key]
        if fragment[frag_index] == key:
            partial = name.split(key)
            if (partial != street_name):
                name = val.join(partial)
    return name

# split string at a given character, char, then fix the good part 
# of the split
def split_and_fix(string, 
                  char, 
                  index, 
                  basic = False, 
                  deep = False,
                  zipcode = False):
    fragment = string.split(char)

    if (basic):
        cleaned_name = update_name(fragment[index])
        # for uniformity in reporting
        handle_output('\n', newline = False)
    if (deep):
        cleaned_name = deep_scan(fragment[index], full_string = string)
    if (zipcode):
        # hot fix
        cleaned_zip = fragment[index]
        return cleaned_zip

    return cleaned_name


# look for the possibility that the suffix might be in the prefix 
# position and switch it
def fix_misplacement(fragment, 
                     last, 
                     report_lateral = report_lateral_parts, 
                     tabbed = tabbed):
    # temporary copy of fragment; for a quick comparison at the end
    copy = fragment

    if (fragment[last] in expected_prefix):
        temp = fragment[0]                          # T = a
        fragment[0] = fragment[last]                # a = z
        fragment[last] = temp                       # z = T

        # log and print
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Prefix: " + fragment[0] + " (switched)")

    elif (fragment[last] not in expected_prefix):
        temp = fragment[0]                         # T = a
        for index in xrange(last):                 # a = b, b = c, ... 
            fragment[index] = fragment[index + 1]  # ... , x = y, y = z
        fragment[last] = temp                      # z = T

        # log and print event message
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Prefix: " + fragment[0] + " (switched)")
    
    # provide a new name and street_name (list-type of name), 
    # since the fragment list has been changed
    name = ' '.join(fragment)
    street_name = []
    street_name.append(name)    
    return name, fragment, street_name

# analyze and fix prefix
def audit_prefix(name, 
                 fragment, 
                 street_name, 
                 last, 
                 learned_name_parts = learned_names, 
                 reporting = True, 
                 report_lateral = report_lateral_parts, 
                 tabbed = tabbed):
    if (fragment[0] not in expected_prefix): 
        if (reporting):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("Prefix: " + fragment[0])

        if (fragment[0] not in expected_suffix) and (fragment[0] not in suffix):
            name = reformat_value(name, fragment, street_name, prefix, 0)
        elif (fragment[0] in expected_suffix) or (fragment[0] in suffix):
            name, fragment, street_name = fix_misplacement(fragment, last)
            name = reformat_value(name, fragment, street_name, prefix, 0)

        if (name.split()[0] == fragment[0]):
            if (fragment[0] not in learned_name_parts):
                learned_name_parts.add(fragment[0])
                if (report_lateral):
                    if tabbed:
                        sys.stdout.write('\t')
                    handle_output("....Warning: prefix dictionary may not have "
                                  "been sufficient to support: " + fragment[0])

        elif (fragment[0] in learned_name_parts):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("....Note: found this fragment in the learned "
                              "names list: " + fragment[0])

    else:
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Prefix: " + fragment[0] + " (expected)")

    return name, fragment, learned_name_parts

# analyze and fix suffix
def audit_suffix(name, 
                 fragment, 
                 street_name, 
                 last, 
                 learned_name_parts = learned_names, 
                 reporting = True, 
                 report_lateral = report_lateral_parts, 
                 tabbed = tabbed):
    if (fragment[last]) not in expected_suffix: 
        if (reporting):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("Suffix: " + fragment[last])

        name = reformat_value(name, fragment, street_name, suffix, last)
        street_name = name.split()

        if (street_name[len(street_name) - 1] == fragment[last]):
            if fragment[last] not in learned_name_parts:
                learned_name_parts.add(fragment[last])
                if (report_lateral):
                    if tabbed:
                        sys.stdout.write('\t')
                    handle_output("....Warning: suffix dictionary may not "
                                  "have been sufficient to support: " + 
                                  fragment[last])
        
        elif (fragment[last] in learned_name_parts):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("....Note: found this fragment in the learned "
                              "names list: " + 
                              fragment[last])
    else:
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Suffix: " + fragment[last] + " (expected)")

    return name, learned_name_parts

# fix the street name according to the set standards and try to learn 
# actual street name parts (a.k.a, the basic fix; versus the deep fix)
def update_name(name, 
                prefix = prefix, 
                suffix = suffix, 
                reporting = True, 
                report_result = report_result, 
                newline = True):
    # for list-type comparison later
    street_name = convert_to_list(name)

    # fragment: list of street name parts. frag_num: number of 
    # fragments. last: list index number of the last fragment
    fragment, frag_num, last = fragment_and_count(name)

    # print the given street name and its fragment list and quantity
    if (reporting):
        handle_initial_reporting(name, fragment, frag_num)

    # learn the medial name parts; the lateral (first and last) 
    # fragments will be handled later in the rest of the process
    learn_medial_name_parts(fragment)
    
    # last == (len(name) - 1). If length == 1, then there is no 
    # chance for a prefix/suffix.
    if (last > 0):
        # inspect and fix prefix
        name, fragment, actual_names = audit_prefix(name, 
                                                    fragment, 
                                                    street_name, 
                                                    last, 
                                                    reporting = reporting)
        # inspect and fix suffix
        name, actual_names = audit_suffix(name, 
                                          fragment, 
                                          street_name, 
                                          last, 
                                          reporting = reporting)
    
    # print the cleaned up, or unchanged, street name
    if (reporting):
        if (report_result):
            report_result(name)
        if (newline):
            handle_output("\n", True, True, 0)

    return name
