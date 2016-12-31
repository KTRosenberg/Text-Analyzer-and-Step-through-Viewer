# Text-Analyzer-and-Step-through-Viewer (Main version v2_4_2)
The project is a utility to navigate an input text and examine the usage, 
repetition, and proximity of words.
The viewer can jump forwards and backwards in an input text by line or 
between instances of particular words to see distances between those 
word instances. I wish to develop the program into a tool for 
more text analysis as I learn more about areas such as
natural language processing. (For example, one might compare authors' word
use or examine one's own writing styles with the tool.)

Version 2_4_2, December 2016

By Karl Toby Rosenberg

## Instructions

### Running the program:
    # in the command line:

    # plain start:
    
    $ python3 v2_4_2_main_Text_Analyzer_Step_through_Viewer.py test_11.txt

    # specify files to add to the reserved files list: 
    # (Use absolute file path names here unless the file is in the program directory)
    
    $ python3 v2_4_2_main_Text_Analyzer_Step_through_Viewer.py test_11.txt 
    <file_name> <encoding_name e.g. ascii> ... <file_name_k> <encoding_name_k>

    # (I will shorten the name of the exectable)
    
### Choosing File(s), Setting-up Working Directory:
- The program displays a list of files in the current working directory
 paired with convenience indices
 
 #### You are prompted to select a file via a number of commands: (NOTE: sample files included)

- \<*index*> to select the file corresponding to the index (then specify the encoding, e.g. 1 for ascii or ascii)
- __r__ \<*index*> to select a reserved file
 * The program keeps a reserved files list/cache so even if you change
 directory while running the program, the reserved files can be opened.
 *(abs_file_name:encoding_name)* pairs specified as command line arguments are added to the list,
 as well as *(abs_file_name:encoding_name)* pairs listed in a local *reserved_input_info.txt*
 file (one pair for each line, separated by a space)
 The file name and separator between file and encoding (in the file) can be
 changed by passing optional arguments to the relevant function: 
  __add_file_info_from_file()__
- __cd__ \<*path*> to change directory
 * This works similarly to the traditional cd command
 - cd sub-commands:
    * __cd__ \<*path*> to continue to change directory
    * __h__ to select the utility's starting home directory
    * __enter__ to confirm the current directory and return to file selection
    * __p__ to cancel (even after changing directory without confirming)
    * __ls__ to list all available files in the current directory
    * __dir__ to list all immediate sub-directories
    * __0__ to quit the program
- __ls__ to list all available files in the current directory
- __lsr__ to list all available files in the reserved files list
- __dir__ to list all immediate sub-directories
- __0__ to quit the program 

### Text Step and Word Step:
You are then prompted to start using the text step functionality:
- enter a word that appears in the text to be able to step
between instances of the word, press enter or an empty line to
ignore this functionality 
- You can always exit the stepper with __0__ to
choose a(nother) word or select another file
Commands to enter:
- a number *n* to step forwards in the text by *n* lines
- a negative number *-n* to move to a specific line number *n*
NOTE: moving to a line beyond the end of the text will exit text step
and prompt for a new word or file

- __<__ and __>__ to skip to the previous or next instance of the given word
 the program will move to the correct line and
 indicate the position of the word instance, as well as display
 the number of words between the new and previous instance and the 
 word number of the new instance (word *i* in the entire text)
- __qa__ or __help__ to display the instructions
- __0__ to leave text step for this file 
 (and have the option to choose another word or file, or to list the words in the current file with __lsw__)

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Additional Notes

### Possible Explorations:
Tracking distance relationships between different words as opposed to 
instances of a specific word only would be interesting.
This would likely require a more complex system with various graphs 
and many more calculations. I might try to use databases and/or play with
a different language (perhaps C) as outlined below (under the Version 3>
heading) Reading the text in smaller chunks may help, as might being
more careful about what information is stored as a value for a string key
(having pointer arithmetic might help here too.)
I would also like to turn this program into something that can be more easily 
used for comparing texts (e.g. authors' word use habits in terms of distances). 
I will probably need to compile a sub-set of words (definitely omitting
ones such as "a" and "the") related to a specific topic (e.g. philosophical
terms when looking at philosophers' writing).
It would be good if the program could be developed to have educational or 
self-analysis applications to some extent. The newer directory changing, 
file-reserving, and other features are making the program easier 
to test and use, so the preliminary steps are in-progress.

### Work-in-Progress Functionality:
- WordInfo class
    * extend from the abstract WordInfo class to create a "command" for
    calculating information based on the analysis dictionary 
    (created from the input text). Assign the derived class a key
    for retrieval from an output dictionary and implement a calculate method
    that works upon the analysis dictionary. Simple test examples include
    finding the longest words in the text or finding all words with a given
    length 

### Test and Old Versions
Version 3> 
- stores positions of the beginning of each line 
(the index of the starting character with respect to the entire text),
- does NOT store the text in a list, reads from file for every line output
- requires check for both DOS/Windows and 
UNIX/UNIX-like system new-lines (\r\n, \n)
A problem: This uses seek(), which reads in terms of bytes. Python
char strings are of variable length and do not represent actual
sizes in bytes in the text. I need to encode any non-ASCII character,
and doing so is noticeably slower than when encoding isn't done. 
In other words, there is a tradeoff between speed and memory use.
Options:
- Use ASCII-only text so len(Python char) is one byte
(This might not a good limitation to have.)
- Use another language for the text input and parsing phase (Perhaps C,
which has char primitives, though there would be additional challenges
related to non-ASCII support. I have been experimenting with the idea
in the hash-table C project.)
- Something completely different...

Miscellaneous idea:
- If I am able to create a system that saves memory by not loading the entire
text into memory, then I might choose to store chunks of the text, 
rather than none at all. For example, for very large texts I could use something
similar to demand paging to save only a constant piece of a text at any 
given point.
