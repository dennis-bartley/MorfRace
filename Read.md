Welcome to the Morf Race program

This package includes a GUI interface to enter race data and update the roster file

It uses Python version 3

The Tkinter packge must be installed to use the GUI

if tkinter is not installed you can:

   apt-get install python3-tk

   or pip install tkinter
   
The data files are kept in the Data directory. This includes individual race files
as well as the roster, and inf files. Results are also placed in the Data directory

The .inf file contains information about the scoring method, course lengths, section start times, 
and series 

to run the GUI, there is a script MorfGui

MorfGui <roster file>

It presume the roster file name is MorfRace.rst
You can use a different roster for Beer cans for instance


