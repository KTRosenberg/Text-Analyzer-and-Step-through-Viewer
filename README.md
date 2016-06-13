# Text-Analyzer-and-Step-through-Viewer
This project started as a word frequency/counter,
but I wanted to add the ability to step through a given text via command line,
jumping to specific lines and between instances of specific words.
Information such as "number of words in between current and previously-visited" instances and line numbers are displayed.
It is possible to display a chosen number of lines in the text at a time.
The project is a work-in-progress, and I intend to experiment with other ways to organize the necessary line/word information and 
see whether there is any improvements or advantages. I have included various sample files (some large and others smaller). 
The best option is to set all defaults and to select one of the files (or place your own in the directory.) Please enjoy.

Karl Toby Rosenberg

Text Analyzer (word counts, separation of instances of words, others) and Basic Text Viewer
ver 1.2_9_2

Dictionary and Word Frequency

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

current version June 12, 2016