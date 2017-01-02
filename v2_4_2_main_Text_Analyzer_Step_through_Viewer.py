#!/usr/bin/env python3

import sys
import os
import time

import random

from abc import ABCMeta, abstractmethod

"""
Step-through Text and Word Viewer

Author: Karl Toby Rosenberg

Version 2_4_2, December 2016

"Text Analyzer and Step-through Viewer" is a utility to navigate an input text 
and examine the usage, repetition, and proximity of words.

The viewer can jump forwards and backwards in an input text by line or
between instances of particular words to see distances between those word 
instances. 
"""

# module-level constants:

PROGRAM_BANNER = ("+============================================+\n"
                  "| Welcome!                                   |\n"
                  "+============================================+\n")
                  
# directory of the program file
PROGRAM_HOME = os.path.dirname(os.path.realpath(__file__))

# for user input and control options in text_step and word_step functions
ENTER = ''
W_NEXT_INST = '>'
W_PREV_INST = '<'
INSTRUCTIONS = frozenset(['qa', "help"])
YES = NEXT_LINE = DEFAULT = 1
NO = QUIT = FIRST = 0
NO_MOVE = ERROR = -1
NO_OP = "NOOP"

# for accessing word_analysis list
WORD_COUNT   = 0
LINE_NUMBERS = 1
ITH_WORD_IN_TEXT = 2
ITH_CHAR_ON_LINE = 3
# UNUSED
# ICHARINTEXT = 4

# ASCII values for alphabetic characters 
A_LO = 65
Z_LO = 90
A_UP = 97
Z_UP = 122

#############################


def binary_min_line_above_search(line_numbers, low, high, starting_line):
    """
    given a starting line number and a list of valid line numbers,
    finds and returns the index of the nearest line number greater or 
    equal to the starting line
    
    param:
        list[int] line_numbers (list of line number candidates)
        int, low (lowest index to search)
        int, high (highest index to search)
        int, starting_line (the line from which to start the search for 
            the nearest later line)
    return:
        int, the index of the valid line search, -1 if no such line exists
    """
    index_first_valid_line = high
    if line_numbers[index_first_valid_line] == starting_line:
        return index_first_valid_line
    while low <= high:
        mid = (low + high)//2
        test_line = line_numbers[mid]
        
        if test_line == starting_line:
            return mid
        elif test_line < starting_line:
            low = mid + 1
        #if test_line > starting_line
        elif (line_numbers[index_first_valid_line] >= test_line
                  and mid <= index_first_valid_line):
            index_first_valid_line = mid
            high = mid - 1
            
    if line_numbers[index_first_valid_line] < starting_line:
        return -1
    return index_first_valid_line
    
def binary_max_line_below_search(line_numbers, low, high, starting_line):
    """
    given a starting line number and a list of valid line numbers,
    finds and returns the index of the nearest line number less than or 
    equal to the starting line
    
    param:
        list[int] line_numbers (list of line number candidates)
        int, low (lowest index to search)
        int, high (highest index to search)
        int, starting_line (the line from which to start the search for 
            the nearest earlier line)
    return:
        int, the index of the valid line search, -1 if no such line exists
            in the correct range
    """
    index_first_valid_line = low
    if line_numbers[index_first_valid_line] == starting_line:
        return index_first_valid_line
    while low <= high:
        mid = (low + high)//2
        test_line = line_numbers[mid]
        
        if test_line == starting_line:
            return mid
        elif test_line > starting_line:
            high = mid - 1
        # if test_line < starting_line
        elif (line_numbers[index_first_valid_line] <= test_line 
                  and mid >= index_first_valid_line):
            index_first_valid_line = mid
            low = mid + 1
            
    if line_numbers[index_first_valid_line] > starting_line:
        return -1
    return index_first_valid_line
    
    
def clean_word(word):
    """
    returns string with
    all non-alphabetical characters from given string (word) omitted

    param: 
        string, word
    return:
        string, cleaned (None if nothing to clean)
    """
    
    if word is None:
        return None
    
    cleaned = []
    cmp = 0
    for char in word:
        cmp = ord(char)
        if (cmp >= A_LO and cmp <= Z_LO) or (cmp >= A_UP and cmp <= Z_UP):
            cleaned.append(char)
    return ''.join(cleaned)
    
    
def is_valid_char(char, in_word_punct):
    """
    checks whether a given character is alphabetical or a valid non-alphabetical character,
    returns True if valid, else returns False

    param: 
        string, char (character to check)
        dictionary, in_word_punct (dictionary 
    return:
        boolean (True if the character is alphabetical, False otherwise)
    """
    
    val = ord(char)
    if ((val >= A_LO and val <= Z_LO) or (val >= A_UP and val <= Z_UP) 
            or char in in_word_punct):
        return True
    return False
    
    
def print_step_instructions():
    """
    displays the commands for text_step and word_step functions
    """
    print("TEXT STEP COMMANDS:\n"
          "    -enter a positive number n to display the next n lines\n"
          "    -a negative number -n to move to a specific line number n\n"
          "    -the < and > character keys to skip to\n"
          "         the previous or next instance of a word\n"
          "    -qa to display the commands again\n"
          "    -0 to leave text step for this file\n"
          "--------------------------------------------------")
    
    
def word_step(text_as_lines, word_analysis, starting_line, choice='>'):
    """
    skips to instances of the chosen word within the text,
    displays number of words skipped with each movement,
    displays position of each word instance with respect to the "list" of all
    words in the text

    enter '<' or '>' to skip to the previous or next instance of the chosen word

    param:
        list, text_as_lines
            the entire input text divided into lines,
            where line i is stored in text_as_lines[i-1]
        list, word_analysis
            information pertaining to a specific word in the text:
            word_analysis[0]
                int (number of instances of the given word in the text)
            word_analysis[1]
                list[int] (for each instance of the given word,
                stores--in order--the line numbers on which the word occurred)
            word_analysis[2]
                list[int] 
                    (interpret the text as a list of words, 
                    where word i is the ith word in the text,
                    this list stores the word index i for each instance of the 
                    given word
            word_analysis[3]
                list[int]
                    (interpret the text as a list of strings where each string 
                    is a line in the text with indices 0-length_of_line-1,
                    this list stores the index of the first character of the 
                    given word for each instance of the word, 
                    with respect to its line. 
                    Access this list with word_analysis[1])

            word_analysis   =   [
                                    1, 
                                    [line_count-1], 
                                    [word_i],
                                    [pos_on_line]
                                ]
        int, starting_line (the current line in the text)

    param (opt.): 
            string, choice:
                for now word_step is entered only from text_step when the 
                '<' or '>' command is entered 
                    (to step to the previous or the next instance),
                but the default choice value is now '>'
    return:
        (string, int) 2-tuple (command, current line number)
            used so text_step line number and next command are 
            consistent with changes and commands in word_step
            (pending command and line number)
    """
    
    line_nums   = word_analysis[LINE_NUMBERS]
    word_i      = word_analysis[ITH_WORD_IN_TEXT]
    pos_on_line = word_analysis[ITH_CHAR_ON_LINE] 

    # track current line
    current_line = starting_line
    # track ith instance of word
    w_inst_index = 0
    # number of word instances
    num_word_inst = len(word_i)
    
    """
    find first instance of word at/after or at/before starting line
    """
    # store result of searches (index of a desired word instance)
    found = -1
    # if the starting line is not the first line and 
    # the command is to find the next word instance
    if choice == W_NEXT_INST:
        if starting_line > 1:
            # binary search for the index of the first valid line at or 
            # after starting_line
            found = binary_min_line_above_search(line_nums, 0, 
                                                 len(line_nums) - 1,
                                                 starting_line)
                                                 
            # return (0, 0) if the end of the file has been reached
            # (no more instances later in the text) to exit
            if found == -1:
                print("Last instance reached\n---------------------")
                return NO_OP, 0
        else:
            current_line = line_nums[0]
    # if the command is to find the previous word instance
    elif choice == W_PREV_INST:
        if starting_line > 1:
            # binary search for the index of the first valid line
            # at or below starting_line
            found = binary_max_line_below_search(line_nums, 0, 
                                                 len(line_nums) - 1,
                                                 starting_line)
                                                 
            # if no earlier word instance is found,
            # move to the first one in the text
            if found == -1 or current_line < line_nums[found]:
                print("No instance earlier, starting at first instance\n")
                current_line = line_nums[0]
        else:
            print("No instance earlier, starting at first instance\n")
            current_line = line_nums[0]
    
    # set the current word instance index and
    # set the current line to be the instance's line
    if found >= 0:
        # set the word and line start positions to
        # the beginning of the line containing the word instance
        w_inst_index = found
        current_line = line_nums[w_inst_index]

    ################
    
    # True if the latest command is valid
    legal_command = True
    # command
    choice = ''
    
    # exit from the loop when an attempt is made
    # to move to move beyond the final instance of the word
    # (considered the end of the text in word_step)
    while w_inst_index < num_word_inst:
        # print the current line
        print(text_as_lines[current_line-1], end='')

        # display the marker for the current instance of the word,
        # display the number of words between current and previous
        # instances of the word
        if legal_command:
            # display the word marker (preceded by proper number of spaces)
            # under the current text line
            print('{0:>{1:d}}{2:d}'.format('^- w', 
                                           pos_on_line[w_inst_index]+4,
                                           word_i[w_inst_index]))

            # display the number of words between the current word instance and
            # the previous word instance reached
            if choice == W_NEXT_INST:
                print('{0}{1:d}'.format("words skipped forwards: ", 
                                        (word_i[w_inst_index]
                                        - word_i[w_inst_index-1] - 1)))
            elif choice == W_PREV_INST:
                print('{0}{1:d}'.format("words skipped backwards: ", 
                                        (word_i[w_inst_index+1]
                                        - word_i[w_inst_index] - 1)))
                                        
        legal_command = True
        # display current line number
        choice = input("L" + str(current_line) + ">> ").strip()
        print()

        """
        CHECK COMMANDS
        """
        # move to next word instance
        if choice == W_NEXT_INST:

            # if the next word instance index equals 
            # the number of word instances in the text,
            # then the end of the text has been reached, no-op
            if w_inst_index + 1 == num_word_inst:
                print("Last instance reached\n---------------------")
                # no-op command
                choice = NO_MOVE
            else:
                #increment the word instance index
                w_inst_index += 1
                # move to the next line
                current_line = line_nums[w_inst_index]

        # move to previous word instance
        elif choice == W_PREV_INST:
            # if not at the first instance of the word,
            # decrement the word instance index
            if w_inst_index == 0:
                # otherwise if the first word instance has already been reached,
                # reset the word index and line start positions to 
                # the beginning of the current line
                print("First instance reached\n----------------------")
                # no-op command
                choice = NO_MOVE
            else:
                w_inst_index -= 1
                # move to the next line
                current_line = line_nums[w_inst_index]
        
        # enter, exit word_step and proceed to the next line
        elif choice == ENTER:
            # return a step of 1 (move to next line) and the current line number
            return "1", current_line
        # display instructions
        elif choice in INSTRUCTIONS:
            print_step_instructions()
        else: 
            # if the command is a valid integer,
            # return a step of int(choice), print (choice) lines
            try:
                return str(int(choice)), current_line
            # if exception, the command is illegal,
            # continue and prompt for input again
            except:
                legal_command = False
                print("INVALID command")
                continue
                
def text_step(text_as_lines, word_analysis=None):
    """
    step-through lines in the text,
        enter a positive number n to display and step forward by n lines
        enter a negative number -n to skip to line number |-n|
        enter '<' or '>' to skip to the previous or 
        next instance of the chosen word (see word_step() )
        (whose word_analysis list is passed to text_step() )
        enter "qa" to display the instructions
        enter 0 to exit
    param:
        list, text_as_lines
            the entire input text divided into lines,
            where line i is stored in text_as_lines[i-1]
    param (opt.):(can only move between word instances with a word_analysis)
        list, word_analysis
            information pertaining to a specific word in the text:
            word_analysis[0]:
                int (number of instances of the given word in the text)
            word_analysis[1]
                list[int] 
                    (for each instance of the given word, stores--in order--the 
                    line numbers on which the word occurred)
            word_analysis[2]
                list[int] 
                    (interpret the text as a list of words, 
                    where word i is the ith word in the text,
                    this list stores the word index i for each instance of 
                    the given word)
            word_analysis[3]
                list[int] 
                    (interpret the text as a list of strings where each string 
                    is a line in the text with indices 0-length_of_line-1,
                    this list stores the index of the first character of 
                    the given word for each instance of the word, 
                    with respect to its line. 
                    Access this list with word_analysis[1])

            word_analysis   =   [
                                    1, 
                                    [line_count-1], 
                                    [word_i],
                                    [pos_on_line]
                                ]
    return:
         0 (QUIT) upon success, 
        -1 (ERROR) upon an error e.g. in word step
    """
    

    #################################

    if text_as_lines is None:
        return ERROR
        
    total_lines = len(text_as_lines)

    # lines displayed in a row
    cur_step = 0
    # maximum number of steps in a row / alternate command option
    step = 1
    # line position in text file
    line_pos = 0
    
    word_step_is_on = True
    if word_analysis is None:
        word_step_is_on = False
    else:
        line_nums = word_analysis[1]
        w_inst = word_analysis[2]
        pos_on_line = word_analysis[3]

    # current line number (displayed)
    current_line_l = 0
    
    # display the instructions upon first call of function
    if text_step.first_time:
        print_step_instructions()
        text_step.first_time = False


    # accept commands until the end of the text has been reached
    while current_line_l < total_lines:
        # print the current line
        print(text_as_lines[current_line_l], end='')

        # increment the number of lines that have been displayed in a row
        cur_step += 1
        # increment the line number
        current_line_l +=1
        # print the next line if there are more lines to display in a row
        if cur_step < step:
            continue
        # otherwise CHECK COMMANDS
        else:
            # wrap the command prompt and associated checks with a try/except
            # block to handle illegal commands
            while True:
                try:
                    # display the current line number,
                    # prompt for the next command
                    step = input("L" + str(current_line_l) + ">> ").strip()
                    # reset the lines-displayed-in-a-row counter
                    cur_step = 0

                    # move to the next or previous instance of a word
                    if step == W_NEXT_INST or step == W_PREV_INST:
                        if not word_step_is_on:
                            print("No word specified\n")
                            continue
                        ########## with testing enabled, 
                        # can enter and exit with return value printouts
                        try:
                            # call word_step to handle movement to instances of 
                            # specific words,
                            # returns a tuple (command, line_number) 
                            #     so text_step can update the current line
                            #     and try the next command
                            control = word_step(text_as_lines, word_analysis, 
                                             current_line_l, step)
                                             
                            if control[0] == NO_OP:
                                continue
                                
                            current_line_l = control[1]

                            # print("EXITING WORD_STEP with current_line = ", current_line_l, " return value = ", step)
                        except Exception as e:
                            # print(e)
                            print("CRITICAL ERROR, WORD STEP FAILED")
                            return ERROR
                        ##########
                        step = control[0]
                    # enter, move to the next line and print it
                    elif step == ENTER:
                        step = 1
                        break
                    # display the instructions
                    elif step in INSTRUCTIONS:
                        print_step_instructions()
                        continue
                        
                    # otherwise interpret the command as an integer
                    # check if valid int, causes an error if not
                    step_as_int = int(step)
                    
                    # if the command is a negative number,
                    # interpret it as a command to jump to a 
                    # specific line number abs(step)
                    if step[0] == "-":
                        current_line_l = int(step[1:])-1
                        step = 1
                        break
                    # if the command is a positive number,
                    # interpret it as the number of lines
                    # to print in succession
                    elif step_as_int > 0:
                        step = step_as_int
                        break
                    # if the command is 0, quit with a return value of 0
                    else:
                        return QUIT
                        
                # upon an exception / if command unrecognized,
                # loop around and prompt for a new command
                except Exception as e2:
                    # print(e2)
                    print("INVALID command")
                    continue
    # before returning from the function, 
    # display the final line number if the end of the final has been reached
    print('\nEnd of file reached after L{0:d}\n'.format(current_line_l))
    return QUIT

# function attribute,
# True if function call is the first one of the current session
text_step.first_time = True

def calc_word_analysis(text_file, 
                       in_word_punct=frozenset(["'", '-', u"’"]),
                       eq_words={"can't":["can", "not"], 
                                 "cannot":["can", "not"],
                                 "won't":["will", "not"],
                                 "shouldn't":["should", "not"],
                                 "you'd":["you", "would"],
                                 "you'll":["you", "will"],
                                 "you're":["you", "are"]
                       },
                       save_sequence=False
                       ):
    """
    calculates word frequencies given a text string,
    can find additional (optional) information, ignore trivial words,
    ignore words above a certain length,
    other possibilities are a work-in-progress

    param: 
        file, text_file (the file object representing the chosen text)
    param (opt.):
        frozenset[string], in_word_punct 
            (set of punctuation and marks used as part of words)
        dictionary, eq_words (dictionary of words to consider as 
            other words or combinations of words)
            NOTE: Currently unused
        boolean, save_sequence (whether to save a list of references to 
                                all words, duplicates included, 
                                in the order they are seen in the input text)
    return: 
        dictionary analysis_dict[string:[...]]
        (of word_analysis dictionary and optional dictionaries)
            list, word_analysis (access with analysis_dict["word analysis"])
            information pertaining to a specific word in the text,
            access with analysis_dict["word analysis"]
            word_analysis[0] (word_analysis[WORD_COUNT])
                int (number of instances of the given word in the text)
            word_analysis[1] (word_analysis[LINE_NUMBERS])
                list of int (for each instance of the given word,
                stores--in order--the line numbers where the word exists)
            word_analysis[2] (word_analysis[ITH_WORD_IN_TEXT])
                list of int (understand the entire text as a list of words, 
                    where word i is the ith word in the text,
                    this list stores the word index i for each instance of 
                    the given word)
            word_analysis[3] (word_analysis[ITH_CHAR_ON_LINE])
                list of int (understand the entire text as a list of strings 
                    where each string is a line in the text with indices 
                    0-length_of_line-1,
                    this list stores the index of the first character of 
                    the given word for each instance of the word, 
                    with respect to its line.

            word_analysis      [
                                    1, 
                                    [line_count-1], 
                                    [word_i],
                                    [pos_on_line]
                               ]

            UNUSED/UNCALCULATED (May reuse later):    
            word_analysis[4]:
                list of int (interpret the entire text as a single 
                string with indices 0-length_of_text-1,
                this list stores the index of the first character of 
                the given word for each instance of the word)
        
            list[int] text_as_lines (access with analysis_dict["text as lines"])
                the entire input text divided into lines,
                where line i is stored in text_as_lines[i-1]
            list[string] word list (access with analysis_dict["word list"])
                access list of words with analysis_dict[1]
            list[string] (the sequence of words, duplicates included, that
                          appear in the input text, access with
                          analysis_dict["word sequence"])
            int, number of words (access with analysis_dict["total words"])

            Temporarily removed / work-in-progress options 
            (NOTE: will redo outside function):
                gender: (access with analysis_dict["gender stat"]
                    access counts with [m] and [f]
                    access percentages with [%_m] and [%_f]
                    access percent of words identifiable as 
                    masculine or feminine with [%_indentifiable]
                mood: (access with analysis_dict["mood stat"])
                    access counts with [:D] and [D:]
                    access percentages with [%_:D] and [%_D:]
                    access percent of words identifiable as happy or sad 
                    with [%_indentifiable]

    """
    if text_file is None or in_word_punct is None:
        return None
        
    # dictionary of lists and dictionaries to return
    analysis_dict = {}
    # word analysis dictionary of word count and lists
    # (variables declared at top of file simplify access for user)
    word_analysis = {}
    # word list
    word_list = []
    
    if save_sequence:
        # word sequence (duplicates allowed)
        word_seq = []
        # save reference to word_seq.append
        word_seq_append_ = word_seq.append

    # dictionary of gender word counts (-1 counts if unused)
    # gender_stat = {'m':-1, 'f':-1}
    # dictionary of mood stat counts (-1 counts if unused)
    # mood_stat = {':D':-1, 'D:':-1}
    
    # save reference to word_list.append
    word_list_append_ = word_list.append
    # save reference to str.lower()
    lower_ = str.lower
    # save reference to str.isalpha()
    isalpha_ = str.isalpha
    
    # create a new list to store each character to be combined into a word
    new_word = []
    # save reference to new_word.append
    new_word_append_ = new_word.append
    
    #for each line L store the line at index L in text_as_lines
    text_as_lines = []
    text_as_lines_append_ = text_as_lines.append

    # given text, create a word frequency dictionary of words in 
    # all_text stripped of invalid punctuation,
    # records word positions, line positions, number of words between 
    # instances of a given word
    # for use with text_step and word_step
    
    ###########################################################  
    # track the number of characters reached so far 
    # with respect to the current line
    char_count_line = -1

    # UNUSED
    # track the number of characters reached so far 
    # with respect to the whole text
    # char_count_text = -1

    # counter tracks whether multiple punctuation marks appear in a row,
    # used to allow for words with "inside punctuation" 
    # (e.g. good-natured has a hyphen)
    # but does not allow words with multiple punctuation or non-alphabetical
    # characters in a row
    double_punct = 0
    # marks a word as alphabetical
    has_alpha = False
    # save a puffer of punctuation marks to allow for in-word punctuation
    # without adding punctuation immediately after the word
    punct_buffer = []
    # save reference to punct_buffer.append
    punct_buffer_append_ = punct_buffer.append
    # count the line number according to '\n' characters in text
    line_count = 1

    # count the number of words found
    word_i = 0

    # word start index with respect to lines
    pos_on_line = 0

    # UNUSED
    # word start index with respect to text
    # pos_in_text = 0

    # read the first line
    line = text_file.readline()
    # iterate as long as another line exists in the text
    while line:
        # store the line in the text
        text_as_lines_append_(line)
        # iterate through each character in the input text
        for char in line:
            char_count_line += 1

            # UNUSED
            # char_count_text += 1
                
            # if char is new-line, 
            if char == '\n':
                # reset the number of characters reached
                # with respect to the line
                char_count_line = -1
                # increment the line count
                line_count += 1
    
            # proceed immediately to the next character
            # if the char is not alphabetic, continue to the next character
            # or if the current word under 
            # construction has no alphabetic characters
            # (words must begin with an alphabetic character)
            if not has_alpha and not isalpha_(char):
                continue
    
            # treat alphabetic characters
            if isalpha_(char):
                # if the current word under construction
                # has no alphabetical characters so far (is empty),
                # mark the starting position of the word,
                # mark the word as alphabetic
                if not has_alpha:
                    pos_on_line = char_count_line

                    # UNUSED
                    # pos_in_text = char_count_text

                    has_alpha = True
                # if characters are waiting in the punctuation buffer,
                # first append them to the word under construction,
                # then clear the buffer
                if len(punct_buffer) > 0:
                    new_word_append_(''.join(punct_buffer))
                    del punct_buffer[:]
                # append the current alphabetic character 
                # to the word under construction
                new_word_append_(lower_(char))
                # reset the punctuation-in-a-row counter to 0
                # since the alphabetic character ends the streak 
                double_punct = 0
            #treat valid punctuation/characters
            elif char in in_word_punct:
                # if the punctuation-in-a-row counter is 0,
                # append the current punctuation/valid non-alphabetic mark 
                # to the punctuation buffer
                # and increment the punctuation-in-a-row counter
                # -punctuation is not added immediately in case, for example,
                # the current character is a hyphen,
                # which can be safely added in the middle of a word,
                # but cannot be added at the end of one.
                # The hyphen is not added to the end of a word,
                # as the word is considered complete before it can be 
                # (incorrectly) added.
                if double_punct == 0:
                    punct_buffer_append_(char)
                double_punct += 1

            # the current word has been completed if:
            # the punctuation-in-a-row counter is set to 2
            # (words cannot have multiple punctuation marks in a row)
            # or the character is not alphabetic or
            # an otherwise valid punctuation mark or character
            if double_punct == 2 or not is_valid_char(char, in_word_punct):
        
                # clear the punctuation buffer
                del punct_buffer[:]
                # reset the punctuation-in-a-row count
                double_punct = 0
                # reset has_alpha to prepare 
                # for the next round of valid word-checking
                has_alpha = False
                # (an additional check) to 
                # make sure that the new word has a valid length
                if len(new_word) > 0:
                    # a new word has been completed, increment the word counter
                    word_i += 1
                    # saved the characters in new_word as a joined_word
                    joined_word = sys.intern(''.join(new_word))
            
                    # if the new word has not been added to the dictionary
                    # and the word is alphabetical,
                    # add an entry for the word in the word list
                    # and in the dictionary with a count of 1
                    if joined_word not in word_analysis:

                        # WORD ANALYSIS CONTENTS:
                        # - integer representing the total word count 
                        # for the given word,
                        # - list of line numbers on which the word appears
                        # - list of the positions of each instance of the word 
                        # with respect to the list of words in the entire text
                        # - list of the positions of the first char 
                        # for each instance of the word 
                        # with respect to the entire text,
                        # - list of the positions of the first char 
                        # for each instance of the word
                        # with respect to the current line in the text

                        # add an entry for the joined_word
                        if char == '\n':
                            # if the current character is a new-line character,
                            # the line-count is off by +1
                            word_analysis[joined_word] =    [
                                                                1, 
                                                                [line_count-1], 
                                                                [word_i], 
                                                                [pos_on_line]#,
                                                                #[pos_in_text] 
                                                            ]
                        else:
                            word_analysis[joined_word] =    [
                                                                1, 
                                                                [line_count], 
                                                                [word_i], 
                                                                [pos_on_line]#,
                                                                #[pos_in_text]
                                                            ]

                        # add new word to word list
                        word_list_append_(joined_word)
                    # else if the new word has already been 
                    # added to the dictionary,
                    # increment the frequency count
                    # and add or update other information for that word
                    else:
                        # access the in-progress word data
                        word_data = word_analysis[joined_word]
                        # increment the word frequency count
                        word_data[WORD_COUNT] += 1
                        # append the next valid line number
                        if char == '\n':
                            word_data[LINE_NUMBERS].append(line_count-1)
                        else:
                            word_data[LINE_NUMBERS].append(line_count)
                
                        # append the ith word value for the 
                        # current instance of the word
                        word_data[ITH_WORD_IN_TEXT].append(word_i)
                        # append the starting position/index of the 
                        # current word instance with respect to the current line
                        word_data[ITH_CHAR_ON_LINE].append(pos_on_line)

                        # UNUSED
                        # append the starting position/index of the
                        # current word instance with respect to the whole text
                        # word_data[ICHARINTEXT].append(pos_in_text)
                    if save_sequence:
                        word_seq_append_(joined_word)
                # reset the word string
                del new_word[:]
        # try to read the next line
        line = text_file.readline()

    # The following checks whether there are any trailing characters
    # words are missed if the input file does not have an ending new-line
    # Rather than add an extra conditional in the main loop,
    # I add duplicated code (it's a trade-off)
    if len(new_word) > 0:
        # a new word has been completed, increment the word counter
        word_i += 1
        # saved the characters in new_word as a joined_word
        joined_word = sys.intern(''.join(new_word))

        # if the new word has not been added to the dictionary 
        # and the word is alphabetical,
        # add an entry for the word in the word list 
        # and in the dictionary with a count of 1
        if joined_word not in word_analysis:

            # WORD ANALYSIS CONTENTS:
            # - integer representing the total word count 
            # for the given word,
            # - list of line numbers on which the word appears
            # - list of the positions of each instance of the word 
            # with respect to the list of words in the entire text
            # - list of the positions of the first char 
            # for each instance of the word 
            # with respect to the entire text,
            # - list of the positions of the first char 
            # for each instance of the word
            # with respect to the current line in the text
            
            # add an entry for the joined_word
            if char == '\n':
                # if the current character is a new-line character, 
                # the line-count is off by +1
                word_analysis[joined_word] =    [
                                                    1, 
                                                    [line_count-1], 
                                                    [word_i], 
                                                    [pos_on_line]#,
                                                    #[pos_in_text] 
                                                ]
            else:
                word_analysis[joined_word] =    [
                                                    1, 
                                                    [line_count], 
                                                    [word_i], 
                                                    [pos_on_line]#,
                                                    #[pos_in_text]
                                                ]

            # add new word to word list
            word_list_append_(joined_word)

        # else if the new word has already been added to the dictionary,
        # increment the frequency count and other information for that word
        else:
            # access the in-progress word data
            word_data = word_analysis[joined_word]
            # increment the word frequency count
            word_data[WORD_COUNT] += 1
            # append the next valid line number
            if char == '\n':
                word_data[LINE_NUMBERS].append(line_count-1)
            else:
                word_data[LINE_NUMBERS].append(line_count)
    
            # append the ith word value for the current instance of the word
            word_data[ITH_WORD_IN_TEXT].append(word_i)
            # append the starting position/index of the current word instance
            # with respect to the current line
            word_data[ITH_CHAR_ON_LINE].append(pos_on_line)
        if save_sequence:
            word_seq_append_(joined_word)



    # if the text does not end with a new-line character
    # append a guard new-line character 
    if len(text_as_lines) > 0:
        final_line_index = len(text_as_lines) - 1 
        len_final_line = len(text_as_lines[final_line_index])
        if len_final_line > 0:
            text_as_lines[final_line_index] += '\n'
        else:
            text_as_lines[final_line_index] = '\n'
    else:
        text_as_lines_append_('\n')

    """
    #################################### 
    UNUSED, will likely be re-implemented as WordInfo command objects

    #if no words, return early
    if len(word_analysis) == 0:
        analysis_dict["word analysis"] = word_analysis
        #text divided into a list of lines
        analysis_dict["text as lines"] = text_as_lines
        #word list
        analysis_dict["word list"] = word_list
        #gender statistics
        # analysis_dict["gender stat"] = gender_stat
        #mood statistics
        # analysis_dict["mood stat"] = mood_stat
        return analysis_dict
    """
    
    """
    
    #if a maximum word length is set,
    #overwrite the word_analysis dictionary with a dictionary that
    #omits words of length greater than max_len
    if max_len > 0:
        temp_dict = {}
        #iterate through the words and copy only entries of valid length
        for key in word_analysis:
            if len(lower_(key)) <= max_len:
                temp_dict[key] = word_analysis[key]
        #overwrite the word_analysis dictionary
        word_analysis = temp_dict
        
        #print(word_analysis)
        #print('maxlen-ed\n')
        
    #if trivial words are to be omitted
    #overwrite the word_analysis dictionary with a dictionary that
    #omits trivial words, where trivial words are defined in the 
    # input list trivial_list
    #(or the default list if trivial_list is empty)
    if trivial == 0:
        if len(trivial_list) == 0:
            trivial_list = ['a', 'an', 'the', 'it', 'its', "it's", 'is', 'I', 
                            'you', 'he', 'she', 'we', 'our'
            ]
        temp_dict = {}
        #iterate through the words and copy only non-trivial entries
        for key in word_analysis:
            if key not in trivial_list:
                temp_dict[key] = word_analysis[key]
        #overwrite the word_analysis dictionary
        word_analysis = temp_dict
        
        #print(word_analysis)
        #print('detrivialized\n')
        
    #if gender terms are to be counted:
    if gender:
        gender_stat['m'] = 0
        gender_stat['f'] = 0
        gender = ''
        #if no list of gender terms specified, the default list is used
        if len(gender_terms) == 0:
            gender_terms = {
                            "he":'m', "him":'m', "his":'m', "gentleman":'m', 
                            "she":'f', "her":'f', "hers":'f', "lady":'f'
            }
        #iterate through the keys in the word frequency dictionary,
        #increment the count for each masculine or feminine word
        for key in word_analysis:
            if key in gender_terms:
                gender = gender_terms[key]
                if gender == 'm':
                    gender_stat['m'] += 1
                else:
                    gender_stat['f'] += 1
        #percent of text identified as masculine
        gender_stat['%_m'] = (gender_stat['m'] / len(word_analysis))*100
        #percent of text identified as feminine
        gender_stat['%_f'] = (gender_stat['f'] / len(word_analysis))*100
        #percent of text identified as either masculine or feminine
        gender_stat['%_indentifiable'] = (((gender_stat['m'] + gender_stat['f']) 
                                         / len(word_analysis))
                                         *100)
                                         
        #print(gender_stat)
        # print('gendered\n')
        
    if mood:
        mood_stat[':D'] = 0
        mood_stat['D:'] = 0
        mood = ''
        #if no list of mood terms specified, the default list is used
        if len(mood_terms) == 0:
            mood_terms = {
                            "yay":':D', "wonderful":':D', "splendid":':D', 
                            "lovely":':D', "aw":'D:', "terrible":'D:', 
                            "horrific":'D:', "unfortunately":'D:'
            }
        #iterate through the keys in the word frequency dictionary,
        #increment the count for each happy or sad word
        for key in word_analysis:
            if key in mood_terms:
                mood = mood_terms[key]
                if mood == ':D':
                    mood_stat[':D'] += 1
                else:
                    mood_stat['D:'] += 1
        #percent of text identified as happy
        mood_stat['%_:D'] = (mood_stat[':D'] / len(word_analysis))*100
        #percent of text identified as sad
        mood_stat['%_D:'] = (mood_stat['D:'] / len(word_analysis))*100
        #percent of text identified as either happy or sad
        mood_stat['%_indentifiable'] = (((mood_stat[':D'] + mood_stat['D:']) 
                                       / len(word_analysis))
                                       *100)
                                       
        #print(mood_stat)
        #print('mooded\n')
        
    #add specific dictionaries to the analysis dictionary for output
    """
    # populate analysis_dict
    
    # information per unique word
    analysis_dict["word analysis"] = word_analysis
    # text divided into a list of lines
    analysis_dict["text as lines"] = text_as_lines
    # word list
    analysis_dict["word list"] = word_list
    if not save_sequence:
        word_seq = []
    # all words in sequence
    analysis_dict["word sequence"] = word_seq
        
    # number of words in text
    analysis_dict["total words"] = word_i
    
    # gender statistics
    # analysis_dict["gender stat"] = gender_stat
    # mood statistics
    # analysis_dict["mood stat"] = mood_stat
    
    #return the analysis dictionary
    return analysis_dict
    
    
def display_word_list(analysis_dict):
    """
    displays the list of unique words found in the text
    
    param:
        dictionary, analysis_dict
    return:
        boolean (True if a valid analysis dictonary passed, False otherwise)
    """
    if analysis_dict is None:
        return False
    
    print("////All Words in List////")
    all_words = analysis_dict["word list"]
    # track the longest word
    w_longest = []
    len_longest = 0
    for w in all_words:
        if len(w) > len_longest:
            del w_longest[:]
            w_longest.append(w)
            len_longest = len(w)
        elif len(w) == len_longest:
            w_longest.append(w)
        print(w)
    print('--------------------------------------------------\n')
    return True
    
    
def get_file_names(display=False):
    """
    creates a list of file names in the current working directory,
    optionally displays index, file name pairs
    
    param (opt.):
        boolean, display (If True, displays index, file name pairs)
    
    return:
        list file_options (list of file info)
    """
    options = os.listdir(".")
    if display:
        file_options = []
        print("\nFILES:")
        count = 1
        for name in options:
            if os.path.isfile(name):
                print(str(count) + ' ' + name)
                count += 1
                file_options.append(name)
        print("--------------------------------------------------")
    else:
        file_options = [name for name in options if os.path.isfile(name)]
        
    return file_options
    
def display_directories():
    """
    displays all available sub-directories
    """
    options = os.listdir(".")
    print("\nSUBDIRECTORIES:")
    for dir in options:
        if os.path.isdir(dir) and not dir.startswith("."):
            print(dir)
    print("--------------------------------------------------")
    
    
def get_encoding(key):
    """
    gets the encoding name string corresponding to the "string as int" key
    
    param:
        string, key (the encoding number key used in the program or the
            name of the encoding type)
    return:
        string, encoding (name of encoding)
            (If the key unrecognized, returns the key itself)
    """
    if key == ENTER or key == '1' or key == None or key.lower() == "ascii":
        return "ascii"
    elif key == '2' or key.lower() == "utf-8":
        return "utf-8"
    elif key == '3' or key.lower() == "mac-roman":
        return "mac-roman"
    else:
        return key
        
        
def get_num_file_info_args():
    """
    returns the number of file : encoding pairs specified as command line args
    
    return:
        int, num_file_args, 
        -1 upon error (incorrect number of args)
        0 if no args
    """
    length = len(sys.argv)-1
    correct_num = length%2 == 0
    if correct_num:
        return (length)
    else:
        return -1
        
        
def display_file_info_cache_options(file_info_cache):
    """
    displays the files available in the file_info_cache
    
    param:
        list of 2-tuples (string, string), file_info_cache 
            (file info tuples containing 
            absolute file path name, encoding name pairs)
    return:
        boolean (True if saved files available, False otherwise)
    """
    
    if file_info_cache is None or len(file_info_cache) == 0:
        print("No saved files\n")
        return False

    length = len(file_info_cache)
    print("\nSAVED FILES:")
    for i in range(0, length):
        print("{:d} {:}".format(i+1, os.path.basename(file_info_cache[i][0])))
    print("--------------------------------------------------")
    return True
    
def add_command_line_arg_file_info(file_info_cache):
    """
    adds command line argument file info to the file info cache
    
    param:
        list of 2-tuples (string, string), file_info_cache 
            (file info tuples containing 
            absolute file path name, encoding name pairs)
    return:
        boolean (True if a file_info_cache passed, False otherwise)
    """
    if file_info_cache is None:
        return False
        
    args = sys.argv
    length = len(args)
    for i in range(1, length, 2):
        if not add_absolute_file_info(file_info_cache, 
                                      (os.path.abspath(args[i]), args[i+1])):
            print("Failed to add " + str(os.path.basename(args[i])))
    return True
    
    
def add_absolute_file_info(file_info_cache, file_info):
    """
    keeps absolute file path names and encoding tuples
    for processing at any time in any directory
    
    param:
        list of 2-tuples (string, string), file_info_cache 
            (file info tuples) containing 
            absolute file path name, encoding name pairs
        2-tuple (string, string), file_info
            (contains an absolute file path name, encoding name pair)
    return:
        boolean True if successful, False otherwise
            (NOTE: does not guarantee that file will be opened and read 
            successfully when accessed)
    """
    if file_info_cache is None or file_info is None:
        return False
        
    absolute = file_info[0]
    if os.path.exists(absolute) and os.path.isfile(absolute):
        file_info_cache.append(file_info)
        return True
    return False
    
def add_file_info_from_file(file_info_cache, 
                            file_name="reserved_input_info.txt", 
                            delimiter=' '):
    """
    reads the reserved input info file,
    processes each line (absolute_file_path_name, encoding_type) into a tuple,
    and stores each tuple in the reserved file info cache so files can be
    pre-loaded from any directory and selected later
    
    param:
        list of 2-tuples (string, string), (the reserved file info tuples)
            containing absolute file path name, encoding name pairs
    param (opt.):
        string, file_name (the name of the reserved input file info file)
        string, delimiter (the delimiter used in the reserved input file
            to separate absolute file path name and encoding name)
    return:
        boolean (True if reserved file info read correctly, False otherwise)
    """
    
    if file_info_cache is None:
        return False
        
    if os.path.exists(file_name) and os.path.isfile(file_name):
        with open(file_name, 'r') as info:
            for line in info:
                file_info = line.split(delimiter)
                file_info[1] = file_info[1].strip()
                add_absolute_file_info(file_info_cache,
                                      (file_info[0], file_info[1]))
    return True
    
    
def select_text_file(file_info_cache=None):
    """
    Open a file for reading
    
    param (opt.):
        list of 2-tuple (string, string), file_info_cache
            (containing absolute file names and encoding numbers)
    return:
        file descriptor for reading, None upon exit or error (given file_info)
    """
    
    first_prompt = True
    # try to open a file (specified with an index) and its encoding
    while True:
        # display files in current directory
        if first_prompt:
            file_options = get_file_names(display=True)
            first_prompt = False
            
        option = input("Select a File:\n"
                       "    '<index>' to select a file in"
                       " the current working directory\n"
                       "    'r <index>' to select a reserved file\n"
                       "    'cd <path>' to change the working directory\n"
                       "    'ls' to show the files in the current working"
                       " directory\n"
                       "    'lsr' to show reserved files\n"
                       "    'dir' to list all sub-directories\n"
                       "    '0' to quit\n").strip()
                       
        if option.startswith("cd"):
            first_prompt = set_directory(option)
            if first_prompt == None:
                return None
        elif option == "ls":
            file_options = get_file_names(display=True)
        elif option == "lsr":
            display_file_info_cache_options(file_info_cache)
        elif option == "dir":
            display_directories()
        elif option == "0":
            return None
        elif not option.isdigit() and not option.startswith("r "):
            print("INVALID option")
        else:
            try:
                if option.startswith("r "):
                    if file_info_cache is None:
                        print("No saved files")
                        continue
                    which_list = file_info_cache
                    index = int(option[2:])-1
                    file_name = which_list[index][0]
                    encoding_key = file_info_cache[index][1]
                else:
                    which_list = file_options
                    index = int(option)-1
                    if index < 0 or index > len(which_list):
                        raise IndexError()
                    file_name = which_list[index]
                    encoding_key = input("Enter the encoding of the file: "
                                         "(enter or 1 for ascii default), "
                                         "(2 for utf-8), "
                                         "(3 for mac-roman), "
                                         "specify otherwise: ")
            except IndexError:
                print("ERROR: invalid index\n")
            except:
                print("ERROR: invalid access\n")
            else:
                try:
                    text_file = open(file_name, 'r', 
                                     encoding=get_encoding(encoding_key))
                except Exception as e:
                    print("ERROR: unable to open the file\n")
                    # print(e)
                else:
                    return text_file
                    
                    
def set_directory(command=None):
    """
    for setting the current working directory while running the program
    
    param: (opt.) 
        string, path=None (either prompt user first time or use the arg path)
    return:
        boolean (whether the directory was changed)
    """
    prev_wd = os.getcwd()
    
    while True:
        try:
            if not command:
                print("Currently in\n{:}".format(os.getcwd()))
                option = input("cd Commands:\n" 
                               "    'cd <path>' to change directory\n"
                               "    'h' to select the utility home directory\n"
                               "    enter to select the current directory\n"
                               "    'p' to select the previous directory\n"
                               "    'ls' to list all files\n"
                               "    'dir' to list all sub-directories\n"
                               "    '0' to quit\n").strip()
            else:
                option = command
                command = None
                
            if option == ENTER:
                return os.getcwd() == prev_wd
            elif option == 'h':
                os.chdir(PROGRAM_HOME)
            elif option == 'p':
                os.chdir(prev_wd)
                return True
            elif option.startswith("cd "):
                os.chdir(option[3:].strip())
            elif option == "ls":
                get_file_names(display=True)
            elif option == "dir":
                display_directories()
            elif option == "0":
                return None
            else:
                print("INVALID option")
        except Exception as e:
            print("ERROR, directory not found\n")
            # print(e)
            
            
def calculate_word_info(analysis_dict, output_dict, choices_set):
    """
    NOTE: TESTING THIS FUNCTIONALITY, not used much yet
    
    saves desired information based on analysis dictionary 
    in an output dictionary (that is passed to the function--a side-effect)
    
    param:
        dictionary, analysis_dict 
            (the text analysis dictionary containing information to print)
        dictionary, output_dict
            (the dictionary in which to store lists containing desired info)
        set[WordInfo], choices_set (each element calculates desired info)
    return:
        boolean True if calculation is run successfully, False otherwise 
    """
    
    if analysis_dict is None or output_dict is None or len(choices_set) == 0: 
        return False
        
    for kind in choices_set:
        output_dict[kind.key] = kind.calculate(analysis_dict)
    
    return True

    """
    count = 0
    line_number = 0
    format_start = '{:<' + str(len_longest) + '} {:>'
    # format and output each word paired with its count nicely
    for word in sorted(word_analysis.keys()):
        count = word_analysis[word][WORD_COUNT]
        print(str( format_start + str(len(str(count))) + '}').format(word, count))
        
    print("\nNumber of unique words found: " + str(len(all_words)) + '\n')
    if len(w_longest) > 1:
        print("Longest words: {:} Length in characters: {:d}\n\n".format(w_longest, len_longest))
    else:
        print("Longest word: {:} Length in characters: {:d}\n\n".format(w_longest[0], len_longest))
        
    # TODO <------------------------------
    """
    
class WordInfo(metaclass=ABCMeta):
    """
    serves as an abstract base class for all classes with a calculate
    method that acts upon an analysis dictionary
    """
    @abstractmethod
    def calculate(self):
        """
        must be implemented in sub-classes
        """
        pass
        
class LongestInfo(WordInfo):
    """
    figures which word(s) is/are the longest in the text,
    returns the word (or multiple ties) as a list
    """
    def __init__(self):
        """
        sets the class key as "word longest"
        """
        self.key = "word longest"
        
    def calculate(self, analysis_dict):
        """
        find the longest word(s)
        param:
            dictionary, analysis_dict (created from the text)
        return:
            list[string] (the longest word(s))
        """
        
        all_words = analysis_dict["word list"]
        w_longest = []
        len_longest = 0
        for w in all_words:
            if len(w) > len_longest:
                del w_longest[:]
                w_longest.append(w)
                len_longest = len(w)
            elif len(w) == len_longest:
                w_longest.append(w)
        return w_longest
        
class LenXInfo(WordInfo):
    """
    creates a list containing the sub-set of words in the text that
    have a given length
    """
    def __init__(self, length):
        """
        sets the class key as the concatenation of "word length" 
        and the desired word length, saves the desired length
        
        param:
            int, length (desired length for words to find)
        """
        self.key = "word length " + str(length)
        self.length = length
        
    def calculate(self, analysis_dict):
        """
        find the words of length "length"
        param:
            dictionary analysis_dict (created from the text)
            int length (of desired words)
        return:
            list of string (the word(s) with length "length")
        """
        all_words = analysis_dict["word list"]
        l = self.length
        w_len = []
        for w in all_words:
            if len(w) == l:
                w_len.append(w)
        return w_len

class WordDistCalc(WordInfo):
    """
    creates a dictionary that for each word (or word in a given sub-list)
    stores a list of int distances between each instance of the word in the
    relevant text
    """
    def __init__(self, word_sublist=None):
        """
        sets the class key, 
        stores the sub-list of words for later calculation
    
        param (opt.):
            list[string], word_sublist 
                (sub-list of words whose distances are desired)
        """
        self.key = "word dist"
        self.word_sublist = word_sublist
        
    def calculate(self, analysis_dict):
        """
        for each word in the relevant text, or optionally only the words
        specified in the word sub-list, creates a list[int] of distances
        between instances of the word, stores all lists in a dictionary
        with a word:list[int] mapping
    
        param:
            dictionary analysis_dict (created from the text)
            int length (of desired words)
        return:
            dictionary[string, list[int]] (mapping of word to instance distances)
         
        """
        if analysis_dict is None:
            return None
            
        if self.word_sublist is None:
            words = analysis_dict["word list"]
        else:
            words = self.word_sublist
            
        word_analysis = analysis_dict["word analysis"]
        dists = {}
        for word in words:
            try:
                word_pos_i = word_analysis[word][ITH_WORD_IN_TEXT]
            except KeyError:
                pass
            else:
                l = len(word_pos_i)
                dists[word] = [word_pos_i[i] - word_pos_i[i-1] - 1
                               for i in range(1, l)]
        return dists
        
class WordNeighbors(WordInfo):
    """
    creates a dictionary that, for each word, stores a list
    of words that appeared one position 
    before, and another list of words that appeared one position after
    the same dictionary can be combined with information from across
    multiple texts
    """
    def __init__(self, neighbors=None):
        """
        sets the class key, 
        stores the neighbors dictionary for later population or update
    
        param (opt.):
            dictionary[string][int][string], neighbors 
                (maps a word to two lists: 
                one for a list of words one position before,
                and another for a list of words that appear one position after)
        """
        self.key = "word neighbors"
        self.neighbors = neighbors
        
    def calculate(self, analysis_dict):
        """
        builds or updates the neighbors dictionary for previous and next
        word lists per word
    
        param:
            dictionary analysis_dict (created from the text)
            int length (of desired words)
        return:
            dictionary[string][int][string] neighboring words graph
         
        """
        if analysis_dict is None:
            return None
        if self.neighbors is None:
            neighbors = {}
        else:
            neighbors = self.neighbors
            
        word_seq = analysis_dict["word sequence"]
        length = len(word_seq)
        prev = None
        next = None
        for i in range(length):
            word = word_seq[i]
            try:
                next = word_seq[i+1]
            except IndexError:
                next = None
                
            try:
                neighbors[word][0].append(prev)
                neighbors[word][1].append(next)
            except KeyError:
                neighbors[word] = [[prev], [next]]
                
            prev = word
                
        return neighbors

def get_message_itr_naive(word_neighbors, thresh):
    """
    creates a generator for a message created by traversing
    random neighboring words in the word neighbors graph
    (naive testing)
    
    param:
        list[string], word_list (list of unique words in the current text)
        int, thresh (number of words to generate for the sequence)
    yield:
        string, next word in the generates sequence
    """
    selector = random.SystemRandom()
    
    key = selector.choice(list(word_neighbors.keys()))
    for i in range(thresh):
        if key is None:
            return
        else:
            yield key
            
        next_neighbors = word_neighbors[key][1]
        key = selector.choice(next_neighbors)
    
    
def test_info_classes(analysis_dict, word_graph=None):
    """
    TESTING WordInfo command objects
    """
    output_dict = {}
    # calculate_word_info(analysis_dict, output_dict, 
                        # set([LongestInfo(), LenXInfo(1)]))
    # calculate_word_info(analysis_dict, output_dict,
                        # set([WordDistCalc(["be"])]))
                        
    if word_graph is None:
        calculate_word_info(analysis_dict, output_dict,
                            set([WordNeighbors()]))
    else:
        calculate_word_info(analysis_dict, output_dict,
                            set([WordNeighbors(neighbors=word_graph)]))
                            
                            
    word_neighbors = output_dict["word neighbors"]
    
    # total_words = analysis_dict["total words"]
    
    gen = get_message_itr_naive(word_neighbors, 10)
    
    for word in gen:
        print(word, end=" \n")
        
    print(len(word_neighbors))
    
    
"""
START MAIN
"""
def main():
    """
    Handles the main instruction sequence for receiving input and
    calling relevant procedures to start text step and word step
    
    reads files from reserved file, checks for additional files
    specified in command line arguments, prompts for specific file choice,
    calculate information for use with text step and word step
    
    multiple files can be checked in the same program run
    """
    
    print(PROGRAM_BANNER, end='')
    
    print("Current working directory: {:}".format(os.getcwd()))
    
    file_info_cache = []
    num_info_args = get_num_file_info_args()
    if num_info_args > 0:
        add_command_line_arg_file_info(file_info_cache)
    elif num_info_args < 0:
        print("Invalid number of arguments")
        
    add_file_info_from_file(file_info_cache)
    
    choose_file = True
    
    # testing:
    # word_graph = {}
    
    while choose_file:
        success = True
        try:
            # file selection
            text_file = select_text_file(file_info_cache)
            
            if text_file is None:
                break
                
            # call calc_word_analysis(),
            # save the analysis dict that it returns
            analysis_dict = calc_word_analysis(text_file, save_sequence=True)
        except Exception as e:
            print("ERROR: cannot read file")
            print(e)
            success = False
        finally:
            if text_file is None:
                success = False
            else:
                text_file.close()
                
        if success:
            
            # test_info_classes(analysis_dict, word_graph=word_graph)
            
            print("////TEXT STEP VIEWER////\n")
            
            word_analysis = analysis_dict["word analysis"]
            word_list     = analysis_dict["word list"]
            text_as_lines = analysis_dict["text as lines"]
            
            prompt = True
            while prompt:
                word = input("Commands:\n"
                             "    Enter a word from the text to step between "
                             "instances of it\n"
                             "    Enter a blank to step through the text only\n"
                             "    'lw' to list the words found in the text\n"
                             "    '1' to choose a new file\n"
                             "    '0' to exit\n"
                             "").strip().lower()
                if word == 'lw':
                    display_word_list(analysis_dict)
                elif word == '1':
                    prompt = False
                elif word == '0':
                    choose_file = False
                    prompt = False
                elif word == ENTER:
                    text_step(text_as_lines, None)
                elif word in word_list:
                    text_step(text_as_lines, word_analysis[word])
                else:
                    print("Error: word cannot be found\n")
    sys.exit("Goodbye!") 
    
    
# starting point
if __name__ == "__main__":
    try:
        main()
    except EOFError:
        pass
        