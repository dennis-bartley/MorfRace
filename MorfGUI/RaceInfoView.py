import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from Info import getInfo
from Utils import get_full_path

'''
    This is a modal dialog that will prompt for information needed to score a rece
    
    It is a royal pain in the ass to do in tkinte
    It may be ugly, but it does seem to work

    The dialog returns a dictionary of race info
'''

class RaceInfoView(tk.Toplevel):
    def __init__(self, parent, title, prompt_labels, courses, seriesList, startTimes):
        super().__init__(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        self.entries = []
        self.courses = courses
        self.seriesList = seriesList
        self.startTimes = startTimes

        # Create a frame for the inputs
        input_frame = tk.Frame(self)
        input_frame.pack(padx=10, pady=10)
        self.input_frame = input_frame

        
        # Create labels and entry widgets in a loop fpr simple entry fields
        rows = {0:(0,0), 1:(0,2), 2:(1,0), 3:(1,2), 4:(2,0), 4:(2,2), 5:(3,0), 6:(3,2)}
        for i, label_text in enumerate(prompt_labels):
            irow, icol = rows[i]
            tk.Label(input_frame, text=label_text).grid(row=irow, column=icol, pady=5, sticky='e')
            entry = tk.Entry(input_frame)
            entry.grid(row=irow, column=icol+1, pady=icol+1, padx=5)
            self.entries.append(entry)
            
        irow += 1
        
        # set up the Series drop down list
        seriesEntries = sorted(seriesList.keys())
        self.series = tk.StringVar(value="Select Series")
        entry = tk.Label(input_frame, text="Select series").grid(row=irow, column=0, pady=5)
        entry = tk.OptionMenu(input_frame, self.series, *seriesEntries, command=self.on_series).grid(row=irow, column=1, pady=5)
        self.entries.append(self.series)
        irow += 1
        
        # now a drop down for courses
        courses = sorted(courses.keys())
        self.course = tk.StringVar(value="Select Course")
        entry = tk.Label(input_frame, text="Select Course").grid(row=irow, column=0, pady=5)
        entry = tk.OptionMenu(input_frame, self.course, *courses, command=self.on_course).grid(row=irow, column=1, pady=5)
        self.entries.append(self.course)
        irow += 1
        
        # an entry field for the distance of a race. It will be automatically
        # filled when the course is chosen, and can be overriden if necessary
        self.dist = tk.StringVar(value="")
        tk.Label(input_frame, text="Distance").grid(row=irow, column=0, pady=5)
        entry = tk.Entry(input_frame)
        self.distEntry = entry
        entry.grid(row=irow, column=1, pady=5)
        self.entries.append(entry)
        
        # Headers for the start times for each section
        tk.Label(input_frame, text="Section").grid(row=3, column=2, pady=5)
        tk.Label(input_frame, text="Start Times").grid(row=3, column=3, pady=5)
        

        # Create OK and Cancel buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.grid(row=0, column=0, padx=5)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.grid(row=0, column=1, padx=5)

        # Set focus and bind close event
        self.grab_set() # grab all events while the dialog is open
        self.focus_set()
        self.wait_window(self) # wait here until the window is destroyed

    # Populate the start times when a series is selected
    def on_series(self, value):
        irow = 4
        sectionTimes = self.seriesList[value]
        for section in sectionTimes:
            startTime = self.startTimes[section]
            
            tk.Label(self.input_frame, text=section).grid(row=irow, column=2, pady=5)
            entry = tk.Entry(self.input_frame)
            entry.insert(0, startTime["startTime"])
            entry.grid(row=irow, column=3, pady=5)
            self.entries.append(entry)
            irow += 1
        
    # Populate the distance when a course is selected
    def on_course(self, value):
        length = self.courses[value]["length"]
        self.distEntry.delete(0, tk.END)
        self.distEntry.insert(0, length)
        
        
    def on_ok(self):
        # Get the input values from the entry widgets
        self.result = [entry.get() for entry in self.entries]
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


# Function to show the dialog and return the results
def showInfoDialog(root):
    (club, series, startTimes, courses) = getInfo(get_full_path("Morfrace.inf"))
    
    seriesList = {"Perf": ["J9", "S7", "S6", "S5", "S4"],
                  "Comp": ["J9", "S7", "S6", "S5", "S4"],
                  "Lady": ["J9", "S4", "S5", "S7", "S6"],
                  "Long": ["J9", "S4", "S5", "S7", "S6"],
                  "BEER": ["J1", "B4", "B3", "B2", "B7", "B1", "B9", ]
                  }
    
    # Bring up the dialog here
    dialog = RaceInfoView(root, "Race Information", 
            ["Race Title", "Date", "RC Boat", 
             "Wind", "Seas"], courses, seriesList, startTimes)
    
    # After the dialog is closed, the script continues here
    result = dialog.result
    if result is not None: 
        raceTitle, date, raceCommittee, wind, seas, series, course, distance = dialog.result[0:8]
        starts = dialog.result[8:]
        
        try:
            # Make sure the date is in proper format
            datetime.strptime(date,  "%d-%b-%y")
        except:
            messagebox.showerror("Error", "Invalid date: %s. Should be like 12-Aug-26" % 
                                 date, parent = root)
            return None
            
        
        '''
             To produce the section/start times dictionary, merge the entries in the 
             seriesList with the starts returned from the dialog
        '''
        seriesSections = seriesList[series]
        startTimes = {}
        for index in range(len(starts)):
            startTimes[seriesSections[index]] = starts[index]
        
        # Construct the resulting disctionalry
        
        rc = {"title": raceTitle,
                  "Race": raceTitle,
                  "Series": series,
                  "Date": date.strip(),
                  "Course": course,
                  "Distance": distance,
                  "RC Boat": raceCommittee,
                  "Wind": wind,
                  "Seas": seas,
                  "startTimes" : startTimes,
                  } 
                  
    else:
        #print("Dialog cancelled")
        rc = None
        
    return rc

