"""""

clean.py

Brief:  functions for identifying and cleaning up problematic street name values,
        and for modifying all street names to match the same naming conventions 
        used by the respective cities/county. 

Data Philosophy: waste nothing; salvage everything.

Ronald Rihoo

"""""

import sys
from config import *
from definitions import *
from prepare import *
from log import grab_learned_names, handle_output, insert_known_parts, insert_useable_parts, learn_medial_name_parts, store_processed_parts


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

'''

General Working Functions

'''

# make a list with a single string value
def convert_to_list(name):
    street_name = []
    return street_name.append(name)

# split name apart into different fragments, count them, and calculate the index for the last one
def fragment_and_count(name):
    fragment = name.split(' ')
    frag_num = len(fragment)
    last = (frag_num - 1)
    return fragment, frag_num, last

# deep scan findings report
def ds_report_findings(description):
    handle_output("....It's a potential " + description + ".")
    return

# change the first letter of a word to uppercase and return the formatted word
def up(word):
    cased_word = word[0].upper() + word[1:]
    return cased_word


'''

Reporting Functions

'''

def handle_initial_reporting(name, fragment, frag_num, tabbed = tabbed, report_basics = report_basics, report_input = report_input):
    if (report_basics):
        report_initial_info(name, fragment, frag_num)
    elif (report_input):
        if tabbed:
            sys.stdout.write('\t')
        handle_output("Input" + name)
    return

# print the street name (for before updating it); print the fragment list; print the quantity of fragments
def report_initial_info(name, fragment, frag_num, tabbed = tabbed):
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

# prints the learned-name list and adds the same print-out to the event-log too
def report_learned_names(actual_parts = learned_names):
    handle_output("Learned: ")
    handle_output(actual_parts)
    handle_output("\n", False, False, 0)        # this separation will make the log analysis easier later
    return

'''

Delegation Functions

'''

# manipulates problematic strings in multiple ways and calls scanners onto them to find signs of street values that can be fixed and/or salvaged 
def clean_string(name):
    if (report_input):
        handle_output('Input: ' + name)
    handle_output("Cleaning problematic string value...")

    # create a list object of the street name for comparison to a split object
    street_name = []
    street_name.append(name)

    split_name = name.split(',')

    cleaned_name = ''
    processed_names = ''
    processed_names_list = []

    # Handling comma issues  --  note: needs to handle all problematic characters. I'm low on time
    if (split_name != street_name):
        handle_output('Found a comma issue...')
        good_frag_index, bad_frag_index = split_and_scan(name, ',')
        handle_output('Output: ' + split_name[good_frag_index[0]] + ' (piping)')
        # try just one good fragment, as I have not seen multiple comma errors yet, so there's only one good fragment each time in my own OSM file
        if good_frag_index != []:
            index = good_frag_index[0]
            cleaned_name = split_and_fix(name, ',', index, basic = True)
        else:
            handle_output("No good fragments were found in this string.")

        if bad_frag_index != []: 
            handle_output("Attempting to identify the bad fragment and store for manual inspection...")
            for index in bad_frag_index:
                processed_names = split_and_fix(name, ',', index, deep = True)
            if (processed_names != '') and (processed_names[0] != '*'):
                processed_names_list.append(processed_names)
            if (processed_names_list != []):
                store_processed_parts(processed_names_list, known = True)
                handle_output("Bad fragment has been salvaged and stored in the 'useables' section of the log (some words could be listed as 'unknown').")
        else:
            handle_output("No bad fragments were found in this string.")
    # Handling non-comma issues
    else:
        handle_output("No comma issues found.")
        cleaned_name = deep_scan(name, full_string = name)
        if (cleaned_name != name) and (cleaned_name != "*highway_code") and (cleaned_name != "*suite_code"):
            handle_output("\n", newline = False)
            cleaned_name = update_name(cleaned_name, newline = False)

    return cleaned_name


'''

Data Scanning

'''

# verify if street name can be handled by the current state of the code
def verify_street_value(street_name, ignore_case = False):
    if (ignore_case):
        return dallas_name_ignore_case_re.search(street_name)
    return dallas_name_convention_re.search(street_name)

# Detects the following type of errors: "Avenue K, suite 700-285"
#                                       "Forest Central Drive, Suite 300"
#                                       "Noel Road, Suite 1370"
#
# Splits at commas (or char from arg) and scans each partition separately
# This is the problem that it tries to help solve: "Noel Road, Suite 1370" 
def split_and_scan(string, char):
    handle_output('Running split-and-scan...')
    line_list = string.split(char)
    handle_output(line_list)
    last = (len(line_list) - 1)         # last index in word_list
    index = 0                           # word index

    index_of_good_frags = []
    index_of_bad_frags = []

    # operate on a list with more than one value; for example, [ "Noel Road", "Suite 1370" ]
    if ((type(line_list) == type([])) and (len(line_list) > 1)):
        handle_output('Operating on a list with more than one value...')
        for line in line_list:
            if (verify_street_value(line, ignore_case = True)):
                index_of_good_frags.append(index)

            words = line.split(' ')
            
            for word in words:
                if (word in prefix):
                    index_of_good_frags.append(index)
                if (word in suffix):
                    index_of_good_frags.append(index)
            
            if (not verify_street_value(line, ignore_case = True)) and (index not in index_of_good_frags):
                index_of_bad_frags.append(index)

            index += 1

    handle_output('Split-and-scan is complete.')
    return index_of_good_frags, index_of_bad_frags

# waste nothing; use every resource available
# scans and builds, but due to its massive scanning capabilities, I consider it to mostly be a scanner with an embedded rebuilder
def deep_scan(name, return_useables = False, full_string = None, report_result = report_result):
    handle_output("Beginning deep scan...")

    # Variables (lists are for the anticipation that multiple parts of the same type might exist here; such as two zipcodes)
    words = re.split('\W', name)
    wc = len(words)                     # word count

    # scanner status
    w2w_scan = False                    # flagging for whether the word-by-word scan has occurred

    # string value variables
    useables = {}                       # know what it is and it can be used in other parts, but just not here for the street name
    unknown = []                        # don't know what it is
    fs = []                             # fake_string - make a new string from the one given
    housenumber = []
    suite = []
    city = []
    state = []
    zipcode = []

    # condition variables
    ps = 0                              # prefix_stat -- 0 for 'does not exist yet'; 1 for 'it has been set'
    ss = 0                              # suffix stat -- 0 for "                  "; 1 for "               "
    ns = 0                              # actual name parts stat -- 0 for none; 1 to infinite for quantity
    index = 0                           # for keeping track of the words in the fragment during for loops

    s = ''                              # new suffix (for switching out with the old one)
    descr = ''                          # description of the name part based on findings -- for reporting findings to the analyst
    result = ''                         # final result variable

    # out-of-scope signals
    highway = False                     # highway marking
    suite_designation = False           # suite marking

    # basic info about the fragment going through analysis
    handle_output("Fragment: " + name)
    handle_output("Word Count: " + str(wc))

    
    ''' Quick Highway Address Scan '''

    handle_output("Starting the Quick Highway scan...")
    
    if (highway_general_re.search(name)):   descr = "highway name";      handle_output("This string is a potential " + descr); highway = True;  result = "*highway_code" 
    if (interstate_re.search(name)):        descr = "interstate name";   handle_output("This string is a potential " + descr); highway = True;  result = "*highway_code"

    if result == "*highway_code":
        handle_output("This address value has been deemed as a highway address and will be inserted back into the data without manipulation.")
    handle_output("End of Quick Highway scan.")

    if descr == '':
        handle_output("Nothing has been found by the Quick Highway Address scan.")

    
    ''' Quick Suite Designation Scan '''
    
    # some strings that have a comma followed by a suite designation can waste time and resources, especially in my OSM file
    # so let's take care of it at the beginning and set the right signals (suite_designation = True) to bypass the rigorous scans
    if not highway:
        handle_output("Attempting the Quick Suite Designation scan...")
        first_letter = ''
        # hard-coded based off of my own dataset's errors; otherwise, this has to become a loop or a smart regex pattern test (or something better)
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
            # perhaps the first "letter" of the first "part" of the list was an '' (empty string),
            # for instance, words == [ '', 'Suite', '1370' ] 
            # 
            # -then it could have failed because of indexing issues. So, let's try the next list index item's first byte:
            try: first_letter = words[1][0]
            except: 
                first_letter = '' # in case of failure, make sure we didn't catch anything funky before going to the next procedure
                handle_output("The Quick Suite Designation scan could not identify suite address information in this fragment.")
        if (first_letter != ''):
            # there's a much easier way to do this. I'm just doing this for the readability and ease
            if (first_letter == ' ' or first_letter == 's' or first_letter == 'S' or first_letter == '#'):
                for word in words:
                    if (suite_re.search(word)):
                        # the fragment most likely contains only suite designations
                        print word
                        insert_known_parts(name)
                        suite_designation = True
                        result = '*suite_code'
                        handle_output("This fragment has been deemed as a suite designation and will be stored, but not inserted back into the data.")
            handle_output("The quick Suite Designation scan is now complete.")
    # reset the description string for re-use
    descr= ''

    
    ''' Word-by-Word Scan and Build '''
    
    if not highway and not suite_designation:
        wbw_scan = True

        handle_output("Running Word-by-Word scan and build...")

        for word in words:
          if (word != ''):  
            handle_output('Searching for \'' + word + '\''  )
            if (word in expected_prefix):       descr = "prefix";                         w = up(word); fs.append(w);   ps = 1;     ds_report_findings(descr)
            if (word in expected_suffix):       descr = "suffix";                         s = up(word);                 ss = 1;     ds_report_findings(descr)
            if (word in prefix and ps == 0):    descr = "unconventional prefix";          w = up(word); fs.append(w);   ps = 1;     ds_report_findings(descr)
            if (word in suffix and ss == 0):    descr = "unconventional suffix";          s = up(word);                 ss = 1;     ds_report_findings(descr)
            if (word in learned_names):         descr = "part of a known street name";    w = up(word); fs.append(w);   ns +=1;     ds_report_findings(descr)
            if (word not in learned_names):
              if (word[0] != word[0].upper()):
                w = up(word)
                if (w in learned_names):        descr = "part of a known street name";                  fs.append(w);   ns +=1;     ds_report_findings(descr)
            if (ss == 0):
              if (street_type_re.search(word)): descr = "mistyped suffix";                s = up(word);                             ds_report_findings(descr)
            if (index == 0):
              if (house_number_re.search(word)):descr = "housenumber";                    housenumber.append(word);                 ds_report_findings(descr)
            if (index != 0) and (len(word) < 5):
              if (suite_re.search(word)):       descr = "suite designation";              suite.append(word);                       ds_report_findings(descr)
            if (city_sweep_re.search(word)):    descr = "city";                           city.append(word);                        ds_report_findings(descr)
            if (state_sweep_re.search(word)):   descr = "state";                          state.append(word);                       ds_report_findings(descr)
            if (zipcode_re.search(word)):       descr = "zipcode";                        zipcode.append(word);                     ds_report_findings(descr)
            if (unk_digits_re.search(word)):    descr = "string of undesignated digits";  unknown.append(word);                     ds_report_findings(descr)
            if (descr == ''):
                unknown.append(word);
                # it might be part of the street name
                if (not digits_re.search(word)):
                    w = up(word)
                    fs.append(w)
            descr = ''
            index += 1
            continue        
        fs.append(s)
        result = ' '.join(fs)
        pass


    ''' Collect Identified and Unknown Processed Parts '''

    # put the identified parts in a packet and store them for review, as they are not useable here
    if (housenumber != []):
        # if there's only one item in the list, then store the item as a string
        if (len(housenumber) == 1):
            useables['housenumber'] = housenumber[0]
        # if there are more than one item in the list, then just store the whole list
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
        store_processed_parts(useables, name = full_string, passing_useables = True)


    ''' Produce Deep Scan Final Report '''
    
    # if Word-by-Word scan has been conducted, yet no known parts have been found
    if (w2w_scan == True) and (fs == [] and housenumber == [] and suite == [] and city == [] and state == [] and zipcode == []):
        handle_output('Nothing has been found by the Word-by-Word scan.')

    # notify analyst that the scan process is complete
    handle_output("Deep scan is complete.")

    # show/log final result
    if (report_result):
        handle_output("Result: " + result)

    # 
    if (return_useables == True):
        # if a fake string was produced, then a potentially good street value is now in possession, so return it for use
        if (fs != []):
            if (useables == []):
                handle_output("Note: no useable parts were found.")
            return result, useables
    elif (return_useables == False):
        # if a fake string was produced, then a potentially good street value was produced, so return it
        if (fs != []):
            return result
        if (fs == []) and (highway == False) and (suite_designation == False):
            handle_output("Failed to find any street name results with the deep scan.")

    return result


'''

Data Cleaning

'''


# look for periods, '.', in a string and remove them
def remove_periods(name, tabbed = tabbed):
    street_name = []
    street_name.append(name)

    period_problem_re = re.compile(r'[\.]')
    periods = 0

    while (period_problem_re.search(name)):
        partial = name.split('.')

        if (partial != street_name):
            name = ''.join(partial)
            periods += 1
    
    if (periods > 0):
        if tabbed:
            sys.stdout.write('\t')
        handle_output("Periods: " + str(periods) + " (removed)")

    return name


# change the format of the street name to the type expected; example: 'Coit Road' -> 'Coit Rd'
def reformat_value(name, fragment, street_name, convention_dict, frag_index):
    for key in convention_dict:
        val = convention_dict[key]
        if fragment[frag_index] == key:
            partial = name.split(key)
            if (partial != street_name):
                name = val.join(partial)
    return name

# split string at a given character, char, then fix the good part of the split
def split_and_fix(string, char, index, basic = False, deep = False):
    fragment = string.split(char)

    if (basic):
        handle_output('\n', newline = False)            # for uniformity in reporting
        cleaned_name = update_name(fragment[index])
    if (deep):
        cleaned_name = deep_scan(fragment[index], full_string = string)

    return cleaned_name

# look for the possibility that the suffix might be in the prefix position and switch it
def fix_misplacement(fragment, last, report_lateral = report_lateral_parts, tabbed = tabbed):
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
        temp = fragment[0]                          # T = a
        for index in xrange(last):                  # a = b, b = c, ... 
            fragment[index] = fragment[index + 1]   # ... , x = y, y = z
        fragment[last] = temp                       # z = T

        # log and print event message
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Prefix: " + fragment[0] + " (switched)")
    
    # provide a new name and street_name (list-type of name), since the fragment list has been changed
    name = ' '.join(fragment)
    street_name = []
    street_name.append(name)    
    return name, fragment, street_name

# analyze and fix prefix
def audit_prefix(name, fragment, street_name, last, learned_name_parts = learned_names, reporting = True, report_lateral = report_lateral_parts, tabbed = tabbed):
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
                    handle_output("....Warning: prefix dictionary may not have been sufficient to support: " + fragment[0])

        elif (fragment[0] in learned_name_parts):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("....Note: found this fragment in the learned names list: " + fragment[0])

    else:
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Prefix: " + fragment[0] + " (expected)")

    return name, fragment, learned_name_parts

# analyze and fix suffix
def audit_suffix(name, fragment, street_name, last, learned_name_parts = learned_names, reporting = True, report_lateral = report_lateral_parts, tabbed = tabbed):
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
                    handle_output("....Warning: suffix dictionary may not have been sufficient to support: " + fragment[last])
        
        elif (fragment[last] in learned_name_parts):
            if (report_lateral):
                if tabbed:
                    sys.stdout.write('\t')
                handle_output("....Note: found this fragment in the learned names list: " + fragment[last])
    else:
        if (report_lateral):
            if tabbed:
                sys.stdout.write('\t')
            handle_output("Suffix: " + fragment[last] + " (expected)")

    return name, learned_name_parts

# fix the street name according to the set standards and try to learn actual street name parts (a.k.a, the basic fix; versus the deep fix)
def update_name(name, prefix = prefix, suffix = suffix, reporting = True, report_result = report_result, newline = True):
    # for list-type comparison later
    street_name = convert_to_list(name)

    # fragment: list of street name parts. frag_num: number of fragments. last: list index number of the last fragment
    fragment, frag_num, last = fragment_and_count(name)

    # print the given street name and its fragment list and quantity
    if (reporting):
        handle_initial_reporting(name, fragment, frag_num)

    # learn the medial name parts; the lateral (first and last) fragments will be handled later in the rest of the process
    learn_medial_name_parts(fragment)
    
    # last == (len(name) - 1). If length == 1, then there is no chance for a prefix/suffix.
    if (last > 0):
        # inspect and fix prefix
        name, fragment, actual_names = audit_prefix(name, fragment, street_name, last, reporting = reporting)
        # inspect and fix suffix
        name, actual_names = audit_suffix(name, fragment, street_name, last, reporting = reporting)
    
    # print the cleaned up, or unchanged, street name
    if (reporting):
        if (report_result):
            report_result(name)
        if (newline):
            handle_output("\n", True, True, 0)

    return name
