# Text-Analyzer-and-Step-through-Viewer (Main version is v2_4)
This project started as a word frequency/counter,
but I wanted to add the ability to step through a given text via command line,
jumping to specific lines and between instances of specific words.
Information such as "number of words in between current and previously-visited" instances and line numbers are displayed.
It is possible to display a chosen number of lines in the text at a time.
The project is a work-in-progress, and I intend to experiment with other ways to organize the necessary line/word information and 
see whether there is any improvements or advantages. I have included various sample files (some large and others smaller). 
The best option is to set all defaults and to select one of the files (or place your own in the directory.) Please enjoy.

Karl Toby Rosenberg

Text Analyzer (word counts, separation of instances of words, others) and Text Viewer
current test ver 3, July 6, 2016


Implementations of main and test versions:

1> store positions of new-line characters (the index of the characters with respect to the entire list), read characters until new-lines are reached

2_2 and _4> store the text as lines (0 through L-1) in a list

3> store positions of the beginning of each line (the index of the starting character with respect to the entire text),
does NOT store the list, reads directly from file object
implementation required check for both DOS/Windows and UNIX/UNIX-like system new-lines (\r\r, \n),

-I have to see whether seek() buffers most of the types of files I am using,
and I also have to see how it behaves when seeking backwards through a file.
The program does not modify the text file or store the full text.
-ASCII-only supported for sure, but I believe that I have correctly implemented
a way to track the positions of unicode characters, but the additional encoding
slows the program more. I will see whether there are better ways of achieving the same effect.
Otherwise version 3 is definitely best left as an ASCII-encoding-only version.
Additional testing is probably best.
(v1 and v2_2 are more tolerant for now)

-NOTE: I believe that I made it possible for unicode character positions to be recorded
correctly. This needs additional testing.


Step-through-text-viewer:

-Steps through text x lines at a time (1 by default), displays line number
jumps to specific lines

-skips to specific instances of a chosen word 
at/after or at/before current line position (forwards and backwards)

-displays the word instance's position/index in the text,
displays number of words skipped (forwards or backwards)

-If end of file reached 
(either through a line skip or through an attempt to step forward after 
the last instance of a word has already been reached),
exits (prompts to enter a new word to "track")

-If no instance of the chosen word found before the current line,
moves directly to the first instance

-possible not to remove extra punctuation (less accurate)
possible to remove specified (trivial words)
mood/gender word counts possible

to-do: implement way for the user to specify the 
mood/gender/trivial words and replace the default placeholder lists

current version 2_4 July 6, 2016