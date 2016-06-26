#!/usr/bin/env python3

import sys
import os
import time

#alphabetic constants
__a = 65
__z = 90
__A = 97
__Z = 122

#constants for user input options in text_step and word_step functions
__ENTER = ''
__W_NEXT_INST = '>'
__W_PREV_INST = '<'
__INSTRUCTIONS = 'qa'
__YES = __NEXT_LINE = 1
__NO = __QUIT = __FIRST = 0
__NOMOVE = -1

"""
Karl Toby Rosenberg

Text Analyzer (word counts, separation of instances of words, others) and Basic Text Viewer
ver 1.2_9_2

-Dictionary and Word Frequency

-Step-through-text-viewer:
    Steps through text x lines at a time (1 by default), displays line number
    jumps to specific lines,
    skips to specific instances of a chosen word 
    at/after or at/before current line position (forwards and backwards)
        displays the word instance's position/index in the text,
        displays number of words skipped (forwards or backwards)
    If end of file reached 
    (either through a line skip or through an attempt to step forward after 
    the last instance of a word has already been reached),
    exits (prompts to enter a new word to "track"),
    If no instance of the chosen word found before the current line,
    moves directly to the first instance
    
    possible not to remove extra punctuation (less accurate)
    possible to remove specified (trivial words)
    mood/gender word counts possible
    to-do: implement way for the user to specify the 
    mood/gender/trivial words and replace the default placeholder lists

current version June 12, 2016
"""
#############################

"""
binary_min_line_above_search

given a starting line number and a list of valid line numbers,
finds and returns the index of the nearest line number greater or equal to the starting line
returns -1 if there is no such valid line in the correct range
"""
def binary_min_line_above_search(line_numbers, low, high, starting_line):
    #print("SEARCHING FOR LINE NUMBER >=", starting_line, ' ', line_numbers)
    mid = 0
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
        else: #if line_numbers[mid] > starting_line
            if line_numbers[index_first_valid_line] > test_line:
                index_first_valid_line = mid
            high = mid - 1
    if line_numbers[index_first_valid_line] < starting_line:
        return -1
    return index_first_valid_line

"""
binary_max_line_below_search

given a starting line number and a list of valid line numbers,
finds and returns the index of the nearest line number less than or equal to the starting line
returns -1 if there is no such valid line in the correct range
"""
def binary_max_line_below_search(line_numbers, low, high, starting_line):
    #print("SEARCHING FOR LINE NUMBER <=", starting_line, ' ', line_numbers)
    mid = 0
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
        else: #if line_numbers[mid] < starting_line
            if line_numbers[index_first_valid_line] < test_line:
                index_first_valid_line = mid
            low = mid + 1
    if line_numbers[index_first_valid_line] > starting_line:
        return -1
    return index_first_valid_line

"""
clean_word

returns string with
all non-alphabetical characters from given string (word) omitted

params: string word
return: string cleaned
"""
def clean_word(word):
    cleaned = []
    cmp = 0
    for char in word:
        cmp = ord(char)
        if (cmp >= __a and cmp <= __z) or (cmp >= __A and cmp <= __Z):
            cleaned.append(char)
    return ''.join(cleaned)

"""
is_valid_char

checks whether a given character is alphabetical or a valid non-alphabetical character,
returns True if valid, else returns False
"""
def is_valid_char(char, in_word_punct):
    val = ord(char)
    if (val >= __a and val <= __z) or (val >= __A and val <= __Z) or char in in_word_punct:
        return True
    return False

"""
print_instructions

displays the commands for text_step and word_step functions
"""
def print_instructions():
    print("TEXT STEP COMMANDS:\n\
    -enter a number n to step by n lines\n\
    -a number -n to skip to a specific line number\n\
    -the < and > character keys to skip to\n\
     the previous and next instance of a word\n\
    -qa to display the commands again\n\
    -0 to quit\n")

"""
word_step

params: string all_text
        list new_line_positions (indices of new-line characters in all_text)
        list word_count (contains information about the chosen word):
            [0], contains word frequency count
            [1], contains list [ints] of line numbers for each instance of the word
            [2], contains list of list[ints] with miscellaneous information:
                [2][0] contains list[ints] of number of words between instance (i) and instance (i + 1) of the word
                [2][1] contains list[ints]  (for each instance of the given word) the integer i representing the instance's position in the entire text
                [2][2] contains list[ints]: indices of starting character for each instance (i) of the word
            [freq, [line_nums], [[w_between_inst],[w_before_inst],[pos_word_inst]] ]
        starting line, the current line number in the text (when the function is called)
optional param: choice
        for now word_step is entered only from text_step when the '<' or '>' command 
        (to step to the previous or the next instance) is entered, but the default choice is now '>'
"""
def word_step(all_text, new_line_positions, word_count, starting_line, choice='>'):
    #initialize default values/store relevant lists

    #track ith instance of word
    w_inst_index = 0
    #list of line numbers where the chosen word appears
    line_numbers = word_count[1]
    current_line = line_numbers[0]
    #by default move to the first word instance in the text
    w_pos = line_start = 0
    if line_numbers[0] > 1:
        w_pos = line_start = new_line_positions[line_numbers[0]-2] + 1
    #positions of the word instances relative to the whole text
    pos_word_inst = word_count[2][2]
    #number of word instances
    num_word_inst = len(pos_word_inst)
    #number of words between word instances
    num_words_between = word_count[2][0]

    """
    find first instance of word at/after or at/before starting line
    """
    #store result of searches (index of a desired word instance)
    found = -1
    #if the starting line is not the first line and the command is to find the next word instance
    if starting_line > 1 and choice == __W_NEXT_INST:
        #binary search for first valid line at or after starting_line
        found = binary_min_line_above_search(line_numbers, 0, len(line_numbers) - 1, starting_line)

        #return (0, 0) if the end of the file has been reached (no more instances later in the text) to exit
        if found == -1:
            print("End of file reached\n")
            return 0, 0
    #if the command is to find the previous word instance
    elif choice == __W_PREV_INST:
        #binary search for first valid line at or below starting_line
        found = binary_max_line_below_search(line_numbers, 0, len(line_numbers) - 1, starting_line)

        #if no earlier word instance is found, move to the first one in the text
        if found == -1:
            print("no instance earlier, starting at first instance\n")
    
    #if a word instance index has been found and the line is not the first
    #(If the line is the first, then the default values have already been set and do not need to be changed)
    if found >= 0 and line_numbers[found] > 1:
        #set the word and line start positions to the beginning of the line holding the word instance
        w_inst_index = found
        w_pos = line_start = new_line_positions[line_numbers[w_inst_index]-2] + 1
        current_line = line_numbers[w_inst_index]

    ################
    
    #True if the latest command is valid
    legal_command = True
    #command
    choice = ''
    
    #exit from the loop when an attempt is made
    #to move to move beyond the final instance of the word
    #(considered the end of the text in word_step)
    while w_inst_index < num_word_inst:
        #print each character on the current line until a new-line character is encountered
        if all_text[w_pos] != '\n':
            print(all_text[w_pos],end='')
            w_pos += 1
            continue

        #display the marker for the current instance of the word, display number of words between current
        #and previous instance of the word
        if legal_command:
            #display the word marker (preceded by proper number of spaces) under the current text line
            print('\n' + ' '*(pos_word_inst[w_inst_index] - line_start) + '^- w ' + str(word_count[2][1][w_inst_index]))
            #display the number of words between the current word instance and the previous word instance reached
            if choice == __W_NEXT_INST:
                print("words skipped forwards: " + str(num_words_between[w_inst_index]))
            elif choice == __W_PREV_INST:
                print("words skipped backwards: " + str(num_words_between[w_inst_index + 1]))

        legal_command = True
        #display current line number
        choice = input("L" + str(current_line) + ">> ")
        print()

        """
        CHECK COMMANDS
        """
        #move to next word instance
        if choice == __W_NEXT_INST:
            #increment the word instance index
            w_inst_index += 1

            #if the word instance index equals 
            #the number of word instances in the text,
            #then the end of the text has been reached, break from loop
            if w_inst_index == num_word_inst:
                break

            #if the next line to visit is not the first line in the text,
            #set the word and line start positions to the beginning of the line holding the next word instance
            if line_numbers[w_inst_index] > 1:
                w_pos = line_start = new_line_positions[line_numbers[w_inst_index]-2] + 1
                current_line = line_numbers[w_inst_index]
            #if the next word instance is still on the the first line,
            #set the word and line start positions to the beginning of the first line in the text
            else:
                w_pos = line_start = 0
                current_line = 1

        #move to previous word instance
        elif choice == __W_PREV_INST:
            #if not at the first instance of the word,
            #decrement the word instance index
            if w_inst_index > 0:
                w_inst_index -= 1

                #if the previous line to visit is not the first line in the text,
                #set the word and line start positions to the beginning of the line holding the previous word instance
                if line_numbers[w_inst_index] > 1:
                    w_pos = line_start = new_line_positions[line_numbers[w_inst_index]-2] + 1
                    current_line = line_numbers[w_inst_index]
                #if the previous word instance is still on the the first line,
                #set the word and line start positions to the beginning of the first line in the text
                else:
                    w_pos = line_start = 0
                    current_line = 1
            #otherwise if the first instance of the word has already been reached,
            #reset word index and line start positions to beginning of current line
            else:
                print("First instance reached")
                w_pos = line_start = 0
                if line_numbers[0] > 1:
                    w_pos = line_start = new_line_positions[line_numbers[0]-2] + 1
                #dummy command
                choice = __NOMOVE
        #enter, exit word_step and proceed to the next line
        elif choice == __ENTER:
            #return a step of 1 (move to next line) and the current line number
            return 1, current_line
        #display instructions
        elif choice == __INSTRUCTIONS:
            print_instructions()
        else: 
            #if the command is a valid integer,
            #return a step of int(choice),print (choice) lines
            try:
                return int(choice), current_line
            #if exception, the command is illegal,
            #continue and prompt for input again
            except:
                legal_command = False
                continue
    #if the end of the file has been reached, return 0 0 to text_step (0 is the command to exist text_step)
    print("End of file reached\n")
    return 0, 0

"""
text_step

params: string all_text
        list new_line_positions (indices of new-line characters in all_text)
        list word_count (contains information about the chosen word):
            [0], contains word frequency count
            [1], contains list [ints] of line numbers for each instance of the word
            [2], contains list of list[ints] with miscellaneous information:
                [2][0] contains list[ints] of number of words between instance (i) and instance (i + 1) of the word
                [2][1] contains list[ints]  (for each instance of the given word) the integer i representing the instance's position in the entire text
                [2][2] contains list[ints]: indices of starting character for each instance (i) of the word
        [freq, [line_nums], [[w_between_inst],[w_before_inst],[pos_word_inst]] ]
"""
def text_step(all_text, new_line_positions, word_count):

    #print(word_count)
    
    #append a new-line marker to the end of the text
    all_text += '\n'
    #save the length of the text
    text_length = len(all_text)
    #lines displayed in a row
    cur_step = 0
    #maximum number of steps in a row / alternate command option
    step = 1
    #position in text file
    pos = 0
    #list of information pertaining to word
    all_word_inst = word_count[2][2]
    #list of number(s) of words between current and previous instances of chosen word
    words_between = word_count[2][0]
    #line numbers on which words appear
    line_counts = word_count[1]
    #current line number (displayed)
    current_line = 0
    
    #display the instructions upon first call of function
    if text_step.first_time:
        print_instructions()
        text_step.first_time = False

    #accept commands until the end of the text has been reached
    while pos < text_length:
        #print each character on the current line until a new-line character is encountered
        if all_text[pos] != '\n':
            print(all_text[pos],end='')
            pos += 1
        #if a new-line character has been encountered (the next line has been reached)
        #and the end of the text has not been reached
        elif pos < text_length:
            #increment the lines-displayed-in-a-row counter
            cur_step += 1
            #increment the line number
            current_line +=1
            #continue to print the next line if there are more lines to display in a row
            if cur_step < step:
                print('\n',end='')
                pos += 1
                continue
            #otherwise CHECK COMMANDS
            else:
                #wrap the command prompt and checks with a try/except loop to handle illegal commands
                while True:
                    try:
                        #display the current line number, prompt for the next command
                        step = input("\nL" + str(current_line) + ">> ")
                        #reset the lines-displayed-in-a-row counter
                        cur_step = 0

                        #move to the next or previous instance of a word
                        if step == __W_NEXT_INST or step == __W_PREV_INST:
                            ##########TRY/EXCEPT, enter and exit with return value printouts
                            try:
                                #print("ENTERING WORD_STEP")

                                #call word_step to handle movement to specific instances of words,
                                #returns a tuple (command, line_number) so text_step can update the current line
                                #and try the next command
                                step = word_step(all_text, new_line_positions, word_count, current_line, step)
                                current_line = step[1]

                                #print("EXITING WORD_STEP with current_line = ", current_line, "return value = ", step)
                            except:
                                print("WORD STEP FAILED")
                            ##########
                            #move to the starting position of the current line
                            pos = new_line_positions[current_line - 1]
                            step = step[0]
                        #enter, move to the next line and print it
                        elif step == __ENTER:
                            step = 1
                        #display the instructions
                        elif step == __INSTRUCTIONS:
                            print_instructions()
                            continue
                        #otherwise interpret the command as an integer
                        else:
                            step = int(step)
                        
                        #if the command is a positive number,
                        #interpret it as the number of lines to print in succession
                        if step > 0:
                            #move one position to the right of the new-line to continue printing
                            pos += 1
                        #if the command is a negative number,
                        #interpret it as a command to jump to a specific line number |step|
                        elif step < 0:
                            #if the jump is to line 1, reset the current line and position to their default values
                            if step == -1:
                                current_line = 0
                                pos = 0
                            #for all other lines, set the correct starting positions of the chosen line
                            else:
                                #the positions for the current line are
                                #offset from the positions of the new-line characters in the previous line
                                current_line = -1*(step)-1 
                                pos = new_line_positions[-1*(step + 2)] + 1
                            step = 1
                        #if the command is 0, quit with a return value of 0
                        else:
                            return __QUIT
                        #if no error has occurred, break from the try/except loop
                        break
                    #upon an exception, prompt for a new command
                    except:
                        continue
    #before returning from the function, display the final line number if the end of the final has been reached
    print("End of file reached at L" + str(current_line) + '\n')

#function attribute,
#True if function call is the first one of the current session
text_step.first_time = True

"""
TO-DO text_step / word_step functions / information storage:
experiment with different ways of tracking and storing line numbers and positions
for example: 
    -Store entire lines as text strings in a list [line 1, line 2, etc.] 
        instead of new-line character positions.
    -Instead of of assigning each word a list that stores only the specific line numbers where instance i of a particular word may be found,
        assign a buffer containing 0s and 1s for each line in the text,
        where 0 means that a word is not on a line, and 1 means that a word is on a line.
        For 0s, store a tuple (0, i) where i is the index of the line number (in the line_numbers list for the word]
        of the next instance of the given word.
            The following example would have a line_numbers array [5, 7, 8]
        For 1s, store a tuple (1, i, j, k) where i is the ith occurrence of the word 
            (I could store the "words in between current and previous instance" j value in a third position in the tuple,
            as well as other information in a 4th position k such as the word position (location of first char))
        This would make it easier to find proper indices, but more space would be necessary.
text: 10 lines
word_info:  [(0,0), (0,0), (0,0), (0,0), (1,1,0,k), (0,1), (1,2,1,k), (1,3,0,k), (0,0), (0,0)]
line_info: [starting_positions of first chars in lines...]
    Since the values in (lines) would be set in order, it may be good to omit trailing 0s:
            [(0,0), (0,0), (0,0), (0,0), (1,1,0,k), (0,1), (1,2,1,k), (1,3,0,k)]

#word_info:    [(0,0), (0,0), (0,0), (0,0), (1,1,0,k), (0,1), (1,2,1,k), (1,3,0,k)]                                                         ^-current_line = 6
#line_numbers: [5, 7, 8]

        #find next valid line where word appears (possibly on the current line): 
        #current_line is now 6,
        #current_pos is index of the first char in the line (with respect to the entire text)
        
        #first check whether the current line number is represented in word_info,
        #if not, the current line and no lines after it are valid
        if current_line > len(word_info):
            print("End of file reached")
            return
        
        #otherwise, check whether an instance of the word already exists on the current line
        w_inst_exists = word_info[current_line-1][0] #1 if exists, 0 if does not exist
        if w_inst_exists:
            current_pos = line_info[current_line-1]
        else:
            #extra variables for more clarity
            next_line_index = word_info[current_line-1][1] # 1 from (0, 1)
            current_line = line_numbers[1] #find the next line number where an instance of the word can be found, 7
            current_pos = line_info[current_line - 1] #set current position in text to start of the line

        #to prepare for the next command, move to the previous or next line afterwards
        #depending on whether the command was to move to the next or previous instance of the word

        #Note: to find the previous valid line, 
        #subtract 1 from the value at index 1 in (0, 1), which results 0
        #if the result is -1, then there is no previous valid line
        #move to the first valid line
        
        #no searching (binary or other search) is necessary
    
I would just like to experiment with this idea, though all of the reading/writing may introduce too many inefficiencies
and could be even worse than the current implementation that uses binary search,
though list indexing may be simpler to read. I also have to consider what I would do when a single word appears multiple times on
a single line. One tuple may not be enough in the above possible system without even more indices being stored.
It may be good to try iterating through lines (where full lines are stored at indices in a line[] list
"""


"""
calc_w_frequency

calculates word frequencies given a text string,
can find additional (optional) information

params: string all_text
optional params: pass 1 or 0 to specify option, or specify a list of words for a list parameter
    clean: clean text/words
    max_len: omit words of length greater than max_len
    trivial: omit trivial words
    trivial_list: specifies a list of trivial words
    gender: count words with male or female qualities, 
        stores another dictionary in list of dictionaries returned from function,
        contains counts and percentages for male and female,
    gender_terms: specifies a list of gender words
    mood: count words with happy or sad qualities
        stores another dictionary in list of dictionaries returned from function,
        contains counts and percentages for happy and sad
    mood_terms: specifies a list of happy or sad words
    in_word_punct: list of acceptable in-word punctuation
    
return: list analysis_list of word_freq dictionary and optional dictionaries
    word counts and miscellaneous word/text information for each word:
        access word count dictionary with with analysis_list[0]
        select a word with analysis_list[0][chosen_word]
            [0], contains word frequency count
            [1], contains list [ints] of line numbers for each instance of the word
            [2], contains list of list[ints] with miscellaneous information:
                [2][0] contains list[ints] of number of words between instance (i) and instance (i + 1) of the word
                [2][1] contains list[ints]  (for each instance of the given word) the integer i representing the instance's position in the entire text
                [2][2] contains list[ints]: indices of starting character for each instance (i) of the word
        [freq, [line_nums], [[w_between_inst],[w_before_inst],[pos_word_inst]] ]
    word list:
        access list of words with analysis_list[1]
    gender:
        access counts with (analysis_list[2])[m] and (analysis_list[2])[f]
        access percentages with (analysis_list[2])[%_m] and (analysis_list[2])[%_f]
        access percent of words identifiable as masculine or feminine with (analysis_list[2])[%_indentifiable]
    mood:
        access counts with (analysis_list[3])[:D] and (analysis_list[3])[D:]
        access percentages with  (analysis_list[3])[%_:D] and (analysis_list[3])[%_D:]
        access percent of words identifiable as happy or sad with (analysis_list[3])[%_indentifiable]
"""
def calc_w_frequency(
all_text, 
clean=0, 
max_len=0, 
trivial=1, trivial_list=[], 
gender=0, gender_terms=[], 
mood=0, mood_terms=[], 
in_word_punct=["'", '-', u"’"],
eq_words={"can't":["can", "not"], "cannot":["can", "not"], "won't":["will", "not"], "shouldn't":["should", "not"]}
):
    all_text += '\n'
    
    #output list to return
    analysis_list = []
    #word list
    word_list = []
    #word frequency dictionary
    word_freq = {}
    #dictionary of gender word counts (-1 counts if unused)
    gender_stat = {'m':-1, 'f':-1}
    #dictionary of mood stat counts (-1 counts if unused)
    mood_stat = {':D':-1, 'D:':-1}

    #save reference to word_list.append
    _word_list_append = word_list.append
    #save reference to str.lower()
    _lower = str.lower
    #save reference to str.isalpha()
    _is_alpha = str.isalpha    
    #create a new empty string word
    new_word = []
    #save reference to new_word.append
    _new_word_append = new_word.append

    #track indices of new line characters
    new_line_pos = []
    _new_line_pos_append = new_line_pos.append

    #given text, create a word frequency dictionary of words in all_text stripped of invalid punctuation,
    #records word positions, line positions, number of words between instances of a given word
    #for use with text_step and word_step
    if clean:
        char_count = -1
        #counter tracks whether multiple punctuation marks appear in a row,
        #used to allow words with interior punctuation (e.g. hyphen: good-natured) 
        #but does not allow words with multiple punctuation or non-alphabetical characters in a row
        double_punct = 0
        #marks a word as alphabetical
        has_alpha = False
        #save a puffer of punctuation marks to allow for in-word punctuation
        #without adding punctuation immediately after the word
        punct_buffer = []
        #save reference to punct_buffer.append
        _punct_buffer_append = punct_buffer.append
        #count the line number according to '\n' characters in text
        line_count = 1
        
        #unused
        #count the number of preceding words  (distance from start)
        #total_dist = 0
        
        #count the number of words found
        word_i = 0
        #word start index
        start_at = 0

        #iterate through each character in the input text
        for char in all_text:
            #track the number of characters reached so far
            char_count += 1
            
            #if char is new-line, 
            if char == '\n':
                #append the position of the new-line to the new_line_pos list,
                _new_line_pos_append(char_count)
                #increment the line count
                line_count += 1
            
            #if the char is not alphabetic,
            #continue to the next character if the current word under construction
            #has no alphabetic characters (words must begin with an alphabetic character)
            if has_alpha == False and _is_alpha(char) == False:
                continue
            
            #treat alphabetic characters
            if _is_alpha(char):
                #if the current word under construction
                #has no alphabetical characters so far (is empty),
                #mark the starting position of the word, mark the word as alphabetic
                if has_alpha == False:
                    start_at = char_count
                    has_alpha = True
                #if character are waiting in the punctuation buffer,
                #first append them to the word under construction, then clear the buffer
                if len(punct_buffer) > 0:
                    _new_word_append(''.join(punct_buffer))
                    del punct_buffer[:]
                #append the current alphabetic character to the word under construction
                _new_word_append(_lower(char))
                #reset the punctuation-in-a-row counter to 0 since the alphabetic character ends the streak 
                double_punct = 0
            #treat valid punctuation/characters
            elif char in in_word_punct:
                #if the punctuation-in-a-row counter is 0,
                #append the current punctuation/valid non-alphabetic mark to the punctuation buffer
                #and increment the punctuation-in-a-row counter
                #-punctuation is not added immediately in case, for example,
                #the current character is a hyphen, which can be safely added in the middle of a word,
                #but cannot be added at the end of one.
                #The hyphen is not added to the end of a word, as the word is considered complete before it can be (incorrectly) added.
                if double_punct == 0:
                    _punct_buffer_append(char)
                double_punct += 1

            #the current word has been completed if:
            #the punctuation-in-a-row counter is set to 2 (words cannot have multiple punctuation marks in a row)
            #or the character is not alphabetic or an otherwise valid punctuation mark or character
            if double_punct == 2 or is_valid_char(char, in_word_punct) == False:
                
                #clear the punctuation buffer
                del punct_buffer[:]
                #reset the punctuation-in-a-row count
                double_punct = 0
                #reset has_alpha to prepare for the next round of valid word-checking
                has_alpha = False
                #(an additional check) make sure that the new word has a valid length
                if len(new_word) > 0:
                    #a new word has been completed, increment the word counter
                    word_i += 1
                    #saved the characters in new_word as a joined_word
                    joined_word = ''.join(new_word)

                    """
                    Silly feature?
                    #check for equivalent words, EX: won't = will not by default
                    if len(eq_words) > 0 and joined_word in eq_words:
                        for word in eq_words[joined_word]:
                            if word not in word_freq:
                                _word_list_append(word)
                                word_freq[word] = 1
                            else:
                                word_freq[word] += 1 
                        continue
                    """
                    
                    #if the new word has not been added to the dictionary and the word is alphabetical,
                    #add an entry for the word in the word list and in the dictionary with a count of 1
                    if joined_word not in word_freq:
                        #add new word to word list
                        _word_list_append(joined_word)

                        #track word frequency count,
                        #line numbers,
                        #number of words between instances of word,
                        #the position of the word in the text
                        #(the ith word as opposed to the position of the first character with respect to the whole text)
                        #starting_position

                        #add an entry for the joined_word
                        if char == '\n':
                            #if the current character is a new-line character, the line-count is off by +1
                            word_freq[joined_word] = [1, [line_count-1], [[0], [word_i], [start_at]]]
                        else:
                            word_freq[joined_word] = [1, [line_count], [[0], [word_i], [start_at]]]

                        """
                        #OLD DISTANCE-BASED
                        if char == '\n':
                            word_freq[joined_word] = [1, [line_count-1], [[0], [total_dist], [start_at]]]
                        else:
                            word_freq[joined_word] = [1, [line_count], [[0], [total_dist], [start_at]]]
                        """
                    #else if the new word has already been added to the dictionary,
                    #increment the frequency count and other information for that word
                    else:
                        #access the in-progress word data
                        word_data = word_freq[joined_word]
                        #increment the word frequency count
                        word_data[0] += 1
                        #append the next valid line number
                        if char == '\n':
                            word_data[1].append(line_count-1)
                        else:
                            word_data[1].append(line_count)
                        #access the list of ith word numbers for the current word
                        ith_w_in_text = word_data[2][1]
                        #append the number of words between the current and previous instance of the word
                        #(calculated with (current ith instance of word in text) - (previous ith instance of word in text + 1)
                        (word_data[2][0]).append(word_i - (ith_w_in_text[len(ith_w_in_text)-1] + 1))
                        #append the ith word value for the current instance of the word
                        (word_data[2][1]).append(word_i)
                        #append the starting position/index of the current word instance with respect to the whole text
                        (word_data[2][2]).append(start_at)

                        """
                        #OLD DISTANCE-BASED
                        prev_dist = word_data[2][1]
                        (word_data[2][0]).append(total_dist - (prev_dist[len(prev_dist)-1] + 1))
                        (word_data[2][1]).append(total_dist)
                        (word_data[2][2]).append(start_at)
                        """
                    #total_dist += 1

                #reset the word string
                del new_word[:]
        #print(word_freq)
        print('cleaned\n')
    #else create a word frequency dictionary of words in all_text including punctuation
    else:
        #hasalpha_w is true if the current word under construction has an alphabetical character
        #this prevents non-words such as a hyphen '-' from being recognized as words
        hasalpha_w = False
        #save reference to str.isspace()
        _is_space = str.isspace
        #iterate through each character in the input text
        for char in all_text:
            #if the current word under construction has no alphabetical characters
            #and the character is alphabetical, set hasalpha_w to True 
            if hasalpha_w == False and _is_alpha(char):
                hasalpha_w = True
            #if the character has no whitespace and is not the empty string,
            #add the character to the word under construction
            if _is_space(char) == False and char != '':
                _new_word_append(_lower(char))
            #else check whether the current string is a completed word
            else:
                #check the current string only if it has at least one alphabetical character
                if hasalpha_w:
                    joined_word = ''.join(new_word)
                    #if the new word has not been added to the dictionary,
                    #add an entry for the word in the word list and in the dictionary with a count of 1
                    if joined_word not in word_freq:
                        _word_list_append(joined_word)
                        word_freq[joined_word] = [1]
                    #else if the new word has already been added to the dictionary,
                    #increment the frequency count for that word
                    elif joined_word in word_freq:
                        word_freq[joined_word][0] += 1
                #reset the word string
                del new_word[:]
                hasalpha_w = False
        #print(word_freq)
        print('not cleaned\n')

    ###############################
    #print(tempL)

    #if no words, quit
    if len(word_freq) == 0:
        return analysis_list

    #if a maximum word length is set,
    #overwrite the word_freq dictionary with a dictionary that
    #omits words of length greater than max_len
    if max_len > 0:
        temp_dict = {}
        #iterate through the words and copy only entries of valid length
        for key in word_freq:
            if len(_lower(key)) <= max_len:
                temp_dict[key] = word_freq[key]
        #overwrite the word_freq dictionary
        word_freq = temp_dict

        #print(word_freq)
        print('maxlen-ed\n')
    
    #if trivial words are to be omitted
    #overwrite the word_freq dictionary with a dictionary that
    #omits trivial words, where trivial words are defined in the input list trivial_list
    #(or the default list if trivial_list is empty)
    if trivial == 0:
        if len(trivial_list) == 0:
            trivial_list = ['a', 'an', 'the', 'it', 'its', "it's", 'is', 'I', 'you', 'he', 'she', 'we', 'our']
        temp_dict = {}
        #iterate through the words and copy only non-trivial entries
        for key in word_freq:
            if key not in trivial_list:
                temp_dict[key] = word_freq[key]
        #overwrite the word_freq dictionary
        word_freq = temp_dict

        #print(word_freq)
        print('detrivialized\n')

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
        for key in word_freq:
            if key in gender_terms:
                gender = gender_terms[key]
                if gender == 'm':
                    gender_stat['m'] += 1
                else:
                    gender_stat['f'] += 1
        #percent of text identified as masculine
        gender_stat['%_m'] = (gender_stat['m'] / len(word_freq))*100
        #percent of text identified as feminine
        gender_stat['%_f'] = (gender_stat['f'] / len(word_freq))*100
        #percent of text identified as either masculine or feminine
        gender_stat['%_indentifiable'] = ((gender_stat['m'] + gender_stat['f']) / len(word_freq))*100

        #print(gender_stat)
        print('gendered\n')

    if mood:
        mood_stat[':D'] = 0
        mood_stat['D:'] = 0
        mood = ''
        #if no list of mood terms specified, the default list is used
        if len(mood_terms) == 0:
            mood_terms = {
                            "yay":':D', "wonderful":':D', "splendid":':D', "lovely":':D',
                            "aw":'D:', "terrible":'D:', "horrific":'D:', "unfortunately":'D:'
                         }
        #iterate through the keys in the word frequency dictionary,
        #increment the count for each happy or sad word
        for key in word_freq:
            if key in mood_terms:
                mood = mood_terms[key]
                if mood == ':D':
                    mood_stat[':D'] += 1
                else:
                    mood_stat['D:'] += 1
        #percent of text identified as happy
        mood_stat['%_:D'] = (mood_stat[':D'] / len(word_freq))*100
        #percent of text identified as sad
        mood_stat['%_D:'] = (mood_stat['D:'] / len(word_freq))*100
        #percent of text identified as either happy or sad
        mood_stat['%_indentifiable'] = ((mood_stat[':D'] + mood_stat['D:']) / len(word_freq))*100

        #print(mood_stat)
        print('mooded\n')

    #add the word list to the output list
    analysis_list.append(word_list)
    #add the remaining dictionaries to the output list
    analysis_list.append(word_freq)
    analysis_list.append(gender_stat)
    analysis_list.append(mood_stat)
    analysis_list.append(new_line_pos)
    #return the analysis list
    return analysis_list

"""
configure

choose settings for analysis

returns the list of choices
"""
def configure():
    #list of option strings for prompt, answers to questions stored as 1 or 0 in choices_list
    prompt_list = [            
                    "Clean text? (enter or 1/0) ",
                    "Specify a maximum word length? (enter 0 for no limit or a positive number) ", 
                    "Include trivial words? (enter or 1/0) ", 
                    "Analyze gender? (enter or 1/0) ", 
                    "Analyze mood? (enter or 1/0) "
                    ]
    #list of default on/off choices for calc_w_frequency function
    choices_list = [0, 0, 0, 0, 0]
    #cycle through options in prompt,
    #set all settings by updating the values in choice_list according to the user's choices
    count = 0
    for option in prompt_list:
        valid_choice = False
        while valid_choice == False:
            choice = input(option).lower()
            if choice == __ENTER:
                choices_list[count] = 1
                valid_choice = True
            elif choice.isnumeric():
                choices_list[count] = int(choice)
                valid_choice = True
            elif choice == '0':
                valid_choice = True
            else:
                print("Please select a valid option\n")
        count += 1

    #return the updated list of choices
    return choices_list

"""""""""""""""""""""
MAIN
"""""""""""""""""""""
def main():

    """
    USER OPTIONS:
    set directory, function options, and file - default options available
    """

    choices_list = []
    input_incomplete = True

    #confirm or set the working directory
    while input_incomplete:
        option = input("Specify a working directory. Press enter for the default directory: ")
        if option == __ENTER:
            try:
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            except:
                option = input("ERROR, would you like to retry? (1 or enter/0): ")
                if option == __ENTER or option == '1':
                    continue
                sys.exit("quitting")
        else:
            try:
                os.chdir(option)
            except:
                print("Directory invalid, please select the default working directory or choose a valid directory\n")
                continue
        print(os.getcwd())
    
        #set text analysis options to default or configure them
        while input_incomplete:
            option = input("Set all to default? (enter or 1/0): ")
            if option == __ENTER or option == '1':
                choices_list.extend([1,0,1,1,1])
            elif option == '0':
                choices_list.extend(configure())
            else:
                print("Please choose a valid option.\n")
                continue
            input_incomplete = False

    """
    FILE SELECTION, OPEN FILE FOR READING
    """
    #original test files for first versions of program,
    #user may attempt to select any file in the current working directory
    text_options = ["Hamlet.txt", "test.txt", "test_2.txt", "test_3.txt"]
    #stores the input text file
    text_file = ''
    
    #option/loop checks
    try_new_file = False
    choose_file = True
    
    #file selection prompt
    option = input("Enter '1' or the enter key to choose a file,\notherwise enter '0' or another key to choose the default file (must be named 'default.txt'): ")

    #default file selection
    if option != __ENTER and option != '1':
        try:
            text_file = open("default.txt", 'r')
            choose_file = False
        except:
            print("Unable to open the default file, please specify a file:")
            choose_file = True
            time.sleep(1)
    else:
        try_new_file = True

    if choose_file:
        #display files in current directory
        print("\nFILES:\n")
        file_options = next(os.walk(os.getcwd()))[2]
        count = 0
        for file_name in file_options:
            print(str(count) + ' ' + file_name)
            count += 1
        print("\n")
    
    #try to open a file (specified with an index) and its encoding
    while choose_file:

        if try_new_file:
            option = ''
        else:
            option = input("Would you like to try a different file? (enter or 1/0 or any other entry): ")

        if option == '' or option == '1':
            option = input("Enter the index of a file in the current working directory: ")
            _encoding = input("Enter the encoding of the file, (enter or 1 for ascii default), (2 for utf-8), (3 for mac-roman), specify otherwise: ") 
            if _encoding == '' or _encoding == '1':
                _encoding = "ascii"
            elif _encoding == '2':
                _encoding = "utf-8"
            elif _encoding == '3':
                _encoding = "mac-roman"
            try:
                text_file = open(file_options[int(option)], 'r', encoding=_encoding)
            except:
                print("ERROR: unable to open the file\n")
            else:
                choose_file = False
        else:
            sys.exit("quitting")
        try_new_file = False

    #try to read the text file
    all_text = ''
    try:
        all_text = text_file.read()
    except:
        sys.exit("ERROR")

    text_file.close()

    #def calc_w_frequency(all_text, clean=0, max_len=0, trivial=1, trivial_list=[], gender=0, gender_terms=[], mood=0, mood_terms=[]):

    #call calc_w_frequency() and save the analysis list that it returns
    analysis_list = calc_w_frequency(all_text, choices_list[0], choices_list[1], choices_list[2], [], choices_list[3], [], choices_list[4], [])  

    """
    OUTPUT DISPLAY
    """
    if len(analysis_list) == 0:
        print("Nothing\n")
        sys.exit(0)
    
    print("////test clean_word function, given \"PEACE,\" ////\n\n")
    print(clean_word("PEACE,") + '\n')
    print('\n\n')

    #print(analysis_list)

    print("////All Words in List////\n\n")
    all_words = analysis_list[0]
    #track the longest word
    w_longest = 0
    len_longest = 0
    for w in all_words:
        if len(w) > len_longest:
            w_longest = w
            len_longest = len(w)
        print(w)
    print('\n\n')

    print("////All Word Counts////\n\n")
    
    word_counts = analysis_list[1]
    count = 0
    line_number = 0
    format_start = '{:<' + str(len_longest) + '} {:>'
    #format words and counts nicely
    for word in sorted(word_counts.keys()):
        count = word_counts[word][0]
        #line_numbers = word_counts[word][1]
        """
        #disabled distance between and average distance display counts (too many values to display at once)
        dist_btwn = word_counts[word][2][0]
        total = 0
        avg_dst = -1
        for num_w in dist_btwn:
            total += num_w
        if len(dist_btwn) > 0:
            #avg_dst = total/len(dist_btwn)
        """

        """
        print(str( format_start + str(len(str(count))) + '}{:>}{:>}').format(
            word, 
            count, 
            ', line#s:' + ''.join((' ' + str(line)) for line in line_numbers),
            ', w_btwn:' + ''.join((' ' + str(num_w)) for num_w in dist_btwn))
            )
        """
        """
        print(str( format_start + str(len(str(count))) + '}{:>}').format(
            word, 
            count, 
            ',\n avg_dst_btwn:' + ''.join(' ' + str(avg_dst)))
            )
        """
        print(str( format_start + str(len(str(count))) + '}').format(word, count))
        
    print("\nNumber of unique words found: " + str(len(all_words)) + '\n')
    print("Longest word: ",w_longest,' ',str(len_longest), '\n\n')

    if len(analysis_list) > 0 and choices_list[3] > 0:
        print("////Gender Information////\n\n")
        gender_stat = analysis_list[2]
    
        print("number of words identified as masculine: " + str(gender_stat['m']) + '\n')
        print("percent of text identified as masculine: " + str(gender_stat['%_m']) + '\n')
        print("number of words identified as feminine: " + str(gender_stat['f']) + '\n')
        print("percent of text identified as feminine:  " + str(gender_stat['%_f']) + '\n')
        print("percent of text identified as either masculine or feminine: " + str(gender_stat['%_indentifiable']) + '\n\n')

    if len(analysis_list) > 1 and choices_list[4] > 0:
        print("////Mood Information////\n\n")
        mood_stat = analysis_list[3]

        print("number of words identified as happy: " + str(mood_stat[':D']) + '\n')
        print("percent of text identified as happy: " + str(mood_stat['%_:D']) + '\n')
        print("number of words identified as sad:   " + str(mood_stat['D:']) + '\n')
        print("percent of text identified as sad:   " + str(mood_stat['%_D:']) + '\n')
        print("percent of text identified as either happy or sad: " + str(mood_stat['%_indentifiable']) + '\n\n')

    #step through the text and between instances of a chosen word that appears in the text
    #(currently only with a cleaned text)
    if choices_list[0] == 1:
        print("////Step through Text////\n")
        prompt = True
        while prompt:
            #print(word_counts)
            word = input("Please select a word (enter 0 to quit): ").lower()
            if word == '0':
                prompt = False
            elif word in word_counts:
                text_step(all_text, analysis_list[4], word_counts[word])
            else:
                print("Error: word cannot be found\n") 

#main function
if __name__ == "__main__":
    try:
        main()
    #allow control+d
    except EOFError:
        pass
