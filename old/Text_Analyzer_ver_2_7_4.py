#!/usr/bin/env python3

"""
Karl Toby Rosenberg

Dictionary and Word Frequency Testing

June 2016
"""

import sys
import os

"""
clean_word

returns string with
all non-alphabetical characters from given string (word) omitted

params: string word
return: string cleaned
"""
def clean_word(word):
    cleaned = ''
    for char in word:
        if char.isalpha():
            cleaned += char
    return cleaned

def is_valid_char(char, in_word_punct):
    val = ord(char)
    if (val >= 65 and val <= 90) or (val >= 97 and val <= 122) or char in in_word_punct:
        return True
    return False

"""
calc_w_frequency

calculates word frequencies given a text string,
can find additional (optional) information

params: string all_text
    optional params: pass 1 or 0 to specify option, or specify a list of words for a list parameter
    clean: omit punctuation
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
return: list analysis_list of word_freq dictionary and optional dictionaries
    word counts:
        access word frequency dictionary with with analysis_list[0]
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
in_word_punct=["'", '-'], 
eq_words={"can't":["can", "not"], "cannot":["can", "not"], "won't":["will", "not"], "shouldn't":["should", "not"]},
lengths=1
):
    all_text += '\n'
    
    #output list to return
    analysis_list = []
    #word list
    word_list = []
    #word frequency dictionary
    word_freq = {}
    #dictionary of gender word counts
    gender_stat = {'m':0, 'f':0}
    #dictionary of mood stat counts
    mood_stat = {':D':0, 'D:':0}
    
    length_stat = {"_max":['',0], "_min":['',0]}

    """
    I read that saving references to repeatedly used functions such as the following
    improves efficiency, but that could have been for older versions of Python. Is there any more
    information available?
    """
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
    #given text, create a word frequency dictionary of words in all_text stripped of punctuation
    if clean:
        #counter tracks whether multiple punctuation marks appear in a row,
        #used to allow words with interior punctuation (e.g. hyphen: good-natured) 
        #but does not allow words with multiple punctuation or non-alphabetical characters in a row
        double_punct = 0
        has_alpha = False
        
        punct_buffer = []
        #save reference to punct_buffer.append
        _punct_buffer_append = punct_buffer.append

        #iterate through each character in the input text
        for char in all_text:
            #print(char, double_punct, ''.join(new_word))

            #for each alphabetical character,
            #reset the punctuation counter,
            #add the character to the current word
            if has_alpha == False and _is_alpha(char) == False:
                continue
            if _is_alpha(char):
                has_alpha = True
                if len(punct_buffer) > 0:
                    _new_word_append(''.join(punct_buffer))
                    del punct_buffer[:]
                _new_word_append(_lower(char))
                double_punct = 0
            elif char in in_word_punct:
                if double_punct == 0:
                    _punct_buffer_append(char)
                double_punct += 1
            #the current word is complete if:
            #the punctuation counter is set to 2
            #or the character is not alphabetical or an example of a valid punctuation mark
            if double_punct == 2 or is_valid_char(char, in_word_punct) == False:
                del punct_buffer[:]
                #reset the punctuation count
                double_punct = 0
                #reset has_alpha
                has_alpha = False
                if len(new_word) > 0:
                    joined_word = ''.join(new_word)
                    #reset the word string
                    del new_word[:]
                    #check for equivalent words, EX: won't = will not by default
                    if len(eq_words) > 0 and joined_word in eq_words:
                        for word in eq_words[joined_word]:
                            if word not in word_freq:
                                _word_list_append(word)
                                word_freq[word] = 1
                            else:
                                word_freq[word] += 1 
                        continue
                    #if the new word has not been added to the dictionary and the word is alphabetical,
                    #add an entry for the word in the word list and in the dictionary with a count of 1
                    if joined_word not in word_freq:
                        _word_list_append(joined_word)
                        word_freq[joined_word] = 1
                    #else if the new word has already been added to the dictionary,
                    #increment the frequency count for that word
                    else:
                        word_freq[joined_word] += 1

                


        print(word_freq)
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
                        word_freq[joined_word] = 1
                    #else if the new word has already been added to the dictionary,
                    #increment the frequency count for that word
                    elif joined_word in word_freq:
                        word_freq[joined_word] += 1
                #reset the word string
                del new_word[:]
                hasalpha_w = False
        print(word_freq)
        print('not cleaned\n')

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

        print(word_freq)
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

        print(word_freq)
        print('detrivialized\n')

    #if gender terms are to be counted:
    if gender:
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

        print(gender_stat)
        print('gendered\n')

    if mood:
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

        print(mood_stat)
        print('mooded\n')

    #add the word list to the output list
    analysis_list.append(word_list)
    if lengths:
        word_freq["lengths"] = length_stat
    #add each dictionary to the output list
    analysis_list.append(word_freq)
    if gender:
        analysis_list.append(gender_stat)
    else:
        analysis_list.append({})
    if mood:
        analysis_list.append(mood_stat)
    else:
        analysis_list.append({})
    analysis_list.append(length_stat)
    #return the analysis list
    return analysis_list


def configure():
    #list of option strings for prompt
    prompt_list = [            
                    "Remove punctuation from words? (enter or 1/0) ",
                    "Specify a maximum word length? (enter 0 for no limit or a positive number) ", 
                    "Include trivial words? (enter or 1/0) ", 
                    "Analyze gender? (enter or 1/0) ", 
                    "Analyze mood? (enter or 1/0) ",
                    "Track max/min length word? (enter or 1/0)"
                    ]
    #list of default on/off choices for calc_w_frequency function
    choices_list = [0, 0, 0, 0, 0, 0]

    for option in prompt_list:
        valid_choice = False
        while valid_choice == False:
            choice = input(option).lower()
            if choice == '':
                choices_list[count] = 1
                valid_choice = True
            elif choice.isnumeric():
                choices_list[count] = int(choice)
                valid_choice = True
            elif choice == '0':
                valid_choice = True
            else:
                print("Please select a valid option\n")

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

    while input_incomplete:
        option = input("Specify a working directory. Press enter for the default directory: ")
        if option == '':
            try:
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
            except:
                option = input("ERROR, would you like to retry? (1 or enter/0): ")
                if option == '' or option == '1':
                    continue
                sys.exit("quitting")      
        else:
            try:
                os.chdir(option)
            except:
                print("Directory invalid, please select the default working directory or choose a valid directory\n")
                continue
        print(os.getcwd())

        while input_incomplete:
            option = input("Set all to default? (enter or 1/0): ")
            if option == '' or option == '1':
                choices_list.extend([1,0,1,1,1,1])
            elif option == '0':
                choices_list.extend(configure())
            else:
                print("Please choose a valid option.\n")
                continue
            input_incomplete = False

    """
    FILE SELECTION, OPEN FILE FOR READING
    """
    #available texts in creator's working directory
    text_options = ["Hamlet.txt", "test.txt", "test_2.txt", "test_3.txt"]
    text_file = ''
    try_new_file = False
    loop = True

    option = input("Enter '1' or the enter key for the default file,\notherwise enter '0' or other key to specify a file: ")

    if option == '' or option == '1':
        try:
            text_file = open(text_options[2], 'r')
            loop = False
        except:
            print("Unable to open the default file\n")
            loop = True
    else:
        loop = True
        try_new_file = True

    print("\nFILES:\n")
    file_options = next(os.walk(os.getcwd()))[2]
    count = 0
    for file_name in file_options:
        print(str(count) + ' ' + file_name)
        count += 1
    print("\n")

    while loop:

        if try_new_file:
            option = ''
        else:
            option = input("Would you like to try a different file? (enter or 1/0 or any other entry): ")

        if option == '' or option == '1':
            option = input("Enter the index of a file in the current working directory: ")
            _encoding = input("Enter the encoding of the file, (enter or 1 for ascii default), 2 for utf-8, specify otherwise: ") 
            if _encoding == '' or _encoding == '1':
                _encoding = "ascii"
            elif _encoding == '2':
                _encoding = 'utf-8'
            try:
                text_file = open(file_options[int(option)], 'r', encoding=_encoding)
            except:
                print("ERROR: unable to open the file\n")
            else:
                loop = False
        else:
            sys.exit("quitting")
        try_new_file = False

    all_text = ''
    try:
        all_text = text_file.read()
    except:
        print("ERROR")
        sys.exit("ERR")

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

    print(analysis_list)

    print("////All Words in List////\n\n")
    all_words = analysis_list[0]
  
    for w in all_words:
        print(w)
    print('\n\n')

    print("////All Word Counts////\n\n")
    word_counts = analysis_list[1]
    if  choices_list[5] > 0:
        longest = word_counts["_max"]
        shortest = word_counts["_min"]
        format_start = '{:<' + str(longest[0]) + '} {:>'
    #format words and counts nicely
    for word in sorted(word_counts.keys()):
        count = word_counts[word]
        print(str( format_start + str(len(str(count))) + '}').format(word, count))
    print("\nNumber of unique words found: " + str(len(all_words)) + '\n\n')
    if choices_list[5] > 0:
        print("Longest  word: ", longest[0], ' ', longest[1], '\n')
        print("Shortest word: ", shortest[0], ' ', shortest[1], '\n')

    if  choices_list[3] > 0:
        print("////Gender Information////\n\n")
        gender_stat = analysis_list[2]
    
        print("number of words identified as masculine: " + str(gender_stat['m']) + '\n')
        print("percent of text identified as masculine: " + str(gender_stat['%_m']) + '\n')
        print("number of words identified as feminine: " + str(gender_stat['f']) + '\n')
        print("percent of text identified as feminine:  " + str(gender_stat['%_f']) + '\n')
        print("percent of text identified as either masculine or feminine: " + str(gender_stat['%_indentifiable']) + '\n\n')

    if  choices_list[4] > 0:
        print("////Mood Information////\n\n")
        mood_stat = analysis_list[3]

        print("number of words identified as happy: " + str(mood_stat[':D']) + '\n')
        print("percent of text identified as happy: " + str(mood_stat['%_:D']) + '\n')
        print("number of words identified as sad: " + str(mood_stat['D:']) + '\n')
        print("percent of text identified as sad:  " + str(mood_stat['%_D:']) + '\n')
        print("percent of text identified as either happy or sad: " + str(mood_stat['%_indentifiable']) + '\n\n')
if __name__ == "__main__":
    main()