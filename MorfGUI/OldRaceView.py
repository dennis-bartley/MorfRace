from datetime import timedelta

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

from OldGuiView import View
from RaceValidator import *
from Observer import Observer
from MorfRace import alphabetSoup




class RaceView(View):
    def __init__(self, controller, master, roster, title, geometry, toplevel):
        super().__init__(controller, master, roster, title, geometry,
                         toplevel= toplevel)
        self.controller = controller
        self.roster = roster
        self.validator = RaceValidator(roster , self.controller)
        
        Observer().register(self.updateNotification)
        master.protocol("WM_DELETE_WINDOW", self.window_exit)

        '''
        self.data_names = ["fleetSection", "fleetPosition", "sectionPosition", "sailno", "boatname",
                           "rating", "finishTime", "correctedTime", "boatType" , "owner"]
        '''
        
        self.data_names = ["section", "fleetPosition", "sectionPosition", "sailno", "boatname",
                           "rating", "finishTime", "correctedTime", "boattype" , "owner"]
        self.col_names = ["Section", "FleetPos", "SectionPos", "Sailno", "Boat Name", 
                          "Rating", "Finish", "Corrected", "Boat Type", "Owner", ]
        self.col_alignment = ["w", "w", "w", "e", "w", "e", "w", "w", "w"]
        self.rows = 20
        self.cols = len(self.col_names)

        #self.validator = RaceValidator(self.column_names)

    
        #toolbar = ttk.Frame(self)
        #toolbar.pack(side="top", fill="x")
        
        menubar = tk.Menu(self.master)
        # 2. Create the "File" menu and add commands
        file_menu = tk.Menu(menubar, tearoff=0)
        
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator() # Adds a horizontal line separator
        file_menu.add_command(label="Exit", command=self.master.destroy) # Closes the window
        
        edit_menu = tk.Menu(self.master, tearoff=0)
        edit_menu.add_command(label = "add Row", command=self.add_row)
        edit_menu.add_command(label="Score", command=self.score_race)
        
        
        # 3. Add the "File" menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.build_ui(self.col_names, menubar)
        # 4. Configure the main window to use the menu bar
        #self.window.config(menu=menubar)
        self.populate_data(None)
        
    def updateNotification(self, message):
        # update the roster
        self.roster = self.controller.getRoster()
        
    def window_exit(self):
        print("Got window exit")
        Observer().remove(self)
        
    def populate_data(self, race_results):        
        # race_results is a list of boats, each entry is a dictionary by field name
        self.widgets = {}
        self.rows = 20
        if race_results:
            self.rows = len(race_results)
            
        for irow in range(1,self.rows):
            for icol in range(len(self.data_names)):
                self.window.columnconfigure(icol, minsize=10)
                value = " "
                if (race_results):
                    boat = race_results[irow]
                    value = boat[self.data_names[icol]]
                self.addField(irow, icol, value)
                
                                        

    def findBoatName(self, boatName):
        # The roster is keyed by sailnumber.... iterate through the roster to find the boat name
        for sailno in self.roster.keys():
            boat = self.roster[sailno]
            if boat["boatname"] == boatName:
                return boat
        
        return None
    
    def populateRowFromBoat(self, boat, row):
        col = 0
        for colName in self.data_names:
            value  = ""
            if colName in boat:
                value = boat[colName]
                
            widget = self.widgets[(row, col)]
            widget.delete(0, tk.END)
            widget.insert(0, value)
    
            col += 1
                        
    def populateRowFromSailno(self, sailno, row):
        boat = self.roster[sailno]
        self.populateRowFromBoat(boat, row)
    
    def populateRowFromBoatname(self, boatname, row):
        boat = self.findBoatName(boatname)
        self.populateRowFromBoat(boat, row)
                
                
    def getColumnName(self, colNum):
        return self.col_names[colNum]
    
    def getColumnNum(self, colName):
        for col in range(len(self.col_names)):
            if self.col_names[col] == colName:
                return col 
        return None 
    
    def updateCorrectedTime(self, row):
            sailnoCol = self.getColumnNum("Sailno")
            sailno = self.getValue(row, sailnoCol).strip()
            finishCol = self.getColumnNum("Finish")
            finishTime = self.getValue(row, finishCol)
            if finishTime in alphabetSoup:
                self.setValue(row, self.getColumnNum("Corrected"), finishTime)
            else:
                rating = self.getValue(row, self.getColumnNum("Rating"))
                section = self.getValue(row, self.getColumnNum("Section"))
                # need to have both rating and section in order to calculated corrected time
                if rating != "" and section != "":
                    correctedTime = self.controller.calculateCorrectedTime(sailno, 
                                                    finishTime, rating, section)
                    if correctedTime is not None:
                        self.setValue(row, self.getColumnNum("Corrected"), correctedTime)
    

    def on_gain_focus(self, event):
        print("on gain focus", event)
        widget = event.widget
        self.currentCol = widget.grid_info()["column"]
        self.currentRow = widget.grid_info()["row"]
        value = widget.get().strip()
        self.currentValue = value
        
    def on_enter_key(self, event):
        print("On Enter", event)
        widget = event.widget
        value = widget.get().strip()
        if (value == self.currentValue):
            return
        
        col = widget.grid_info()["column"]
        row = widget.grid_info()['row']
        columnName = self.getColumnName(col)
        rc = self.validator.validate(columnName, value)
        if rc != True:
            messagebox.showerror(title="Invalid entry", 
                       message=rc,
                       parent = self.window)
            return 
        
        if columnName == "Sailno":
            self.populateRowFromSailno(value, row)
            widget = self.widgets[(row, self.getColumnNum("Finish"))]
            widget.focus_set()
            
        if columnName == "Boat Name":
            self.populateRowFromBoatname(value, row)
            widget = self.widgets[(row, self.getColumnNum("Finish"))]
            widget.focus_set()
            
        # The finishTime was updated, calculate corrected time
        if columnName in  ["Finish", "Section", "Rating"]:
            self.updateCorrectedTime(row)            

    def on_lost_focus(self, event):
        print("on lost focus", event.widget.grid_info())
        self.on_enter_key(event)
        
    def on_up_arrow(self, event):
        widget = event.widget
        col = widget.grid_info()["column"]
        row = widget.grid_info()["row"]
        if row >1:
            row -= 1
            newWidget = self.widgets[(row, col)]
            newWidget.focus_set()
        
    def on_down_arrow(self, event):
        widget = event.widget
        col = widget.grid_info()["column"]
        row = widget.grid_info()["row"]
        if row < (self.rows - 1):
            row += 1
            newWidget = self.widgets[(row, col)]
            newWidget.focus_set()
        
    def new_file(self):
        pass
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=(("Race Files", "*.rac"), ("All files", "*.*")))
        race = self.controller.open_file(file_path)
        (self.info, self.startTimes, results) = race
        self.populate_data(results)
            
    
    def save_file(self):
        try:
            # Make sure the race is scored before saving
            self.scoreit()
        except BaseException as e:
            messagebox.showerror(title="Error",
                                 message=e,
                                 parent=self.window)
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".rac",
                    filetypes=[("Race file","*.rac"),("Text Document","*.txt"),
                               ("Web file",".html")])
        results = self.getResults()
        self.controller.save_file(file_path, results)

        
    def add_row(self):
        self.rows += 1
        for col in range(len(self.data_names)):
            self.addField(self.rows, col, "")
        widget = self.widgets[(self.rows, 0)]
        widget.focus_set()
            
        
    def score_race(self):
        try:
            self.scoreit()
        except BaseException as e:
            messagebox.showerror(title="Error",
                                 message=e,
                                 parent=self.window)            
            
    def scoreit(self):
        boats = self.getBoats()
        rankedScores = self.controller.Score(boats)
        
        # the ranked scores are a dictionary by section
        # Each section is a list of boats ordered by rank in that section
        sections = sorted(rankedScores)
        row = 1
        for section in sections:
            boats = rankedScores[section]
            for boat in boats:
                self.setValue(row, self.getColumnNum("Section"), section)
                self.setValue(row, self.getColumnNum("SectionPos"), boat["sectionPosition"])
                self.setValue(row, self.getColumnNum("FleetPos"), boat["fleetPosition"])
                self.setValue(row, self.getColumnNum("Sailno"), boat["sailno"])
                self.setValue(row, self.getColumnNum("Boat Name"), boat["Boat Name"])
                self.setValue(row, self.getColumnNum("Rating"), boat["Rating"])
                self.setValue(row, self.getColumnNum("Finish"), boat["finishTime"])
                self.setValue(row, self.getColumnNum("Corrected"), boat["correctedTime"])
                self.setValue(row, self.getColumnNum("Boat Type"), boat["Boat Type"])
                self.setValue(row, self.getColumnNum("Owner"), boat["Owner"])
                row += 1
        
    def getBoats(self):
        boats = []
        for row in range(1, self.rows):
            sailno = self.getValue(row, self.getColumnNum("Sailno")).strip()
            if sailno != "":
                fleetSection = self.getValue(row, self.getColumnNum("Section"))
                (fleet, section) = self.getFleetSection(fleetSection)
                finish = self.getValue(row, self.getColumnNum("Finish"))
                boat = {"sailno": sailno,
                        "finishTime": finish,
                        "correctedTime": self.getValue(row, self.getColumnNum("Corrected")),
                        "penalty": finish if finish in alphabetSoup else "",
                        "Owner": self.getValue(row, self.getColumnNum("Owner")),
                        "Boat Name": self.getValue(row,self.getColumnNum("Boat Name")),
                        "fleet": fleet, "section": section,
                        "Rating": self.getValue(row, self.getColumnNum("Rating")),
                        "Boat Type": self.getValue(row, self.getColumnNum("Boat Type")),
                        }
                boats.append(boat)
        return boats
    
    # split the fleet and section ... this might be a bit fragile?
    # for our purposes, the flieet is the first character, followed by the section
    def getFleetSection(self, fleetSection):
        fleet =  fleetSection[0]
        section = fleetSection[1:]
        return(fleet, section)
        
    # Contsruct a results dictionary from the spreadsheet
    # results is a dictionary by section. Each section is a list of boats
    def getResults(self):
        nrows = 10
        sections={}
        
        for row in range(1,nrows):
            section = self.getValue(row, self.getColumnNum("Section"))
            sailno = self.getValue(row, self.getColumnNum("Sailno"))

            corrected = self.getValue(row, self.getColumnNum("Corrected"))
            if sailno != " ":
                penalty = None 
                finishTime = self.getValue(row, self.getColumnNum("Finish"))
                if (finishTime.strip() == ""):
                    # If there's not a finish time, then we can't score the boat
                    raise BaseException("No Finish Time for sail %s" % sailno)
                
                if finishTime in alphabetSoup:    
                    correctedTime = finishTime
                    penalty = finishTime
                else:
                    correctedTime = self.toTimeDelta(corrected)
                    
                boat = {"fleetPosition":int(self.getValue(row, self.getColumnNum("FleetPos"))),
                        "sectionPosition":int(self.getValue(row, self.getColumnNum("SectionPos"))),
                        "sailno": sailno, 
                        "boatname":self.getValue(row, self.getColumnNum("Boat Name")),
                        "rating":self.getValue(row, self.getColumnNum("Rating")), 
                        "finishTime":self.getValue(row, self.getColumnNum("Finish")),
                        "correctedTime": correctedTime,
                        "penalty": penalty,
                        "boatType":self.getValue(row, self.getColumnNum("Boat Type")),
                        "owner":self.getValue(row, self.getColumnNum("Owner")),
                        }
                
                if section not in sections:
                    sections[section] = []
                sections[section].append(boat)
        
        return sections
    
    def toTimeDelta(self, time):
        mmss = time.split(":")
        delta = timedelta(minutes=int(mmss[0]), seconds=int(mmss[1]))
        return delta
            
                

        
        