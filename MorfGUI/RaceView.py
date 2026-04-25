from datetime import timedelta

import tkinter as tk
from tkinter import filedialog, messagebox

from GuiView import GuiView
from RaceInfoView import showInfoDialog
from RaceValidator import RaceValidator
from Observer import Observer
from MorfRace import alphabetSoup
from Style import *
from Utils import get_full_path

HEADER_BG = "Blue"
geometry = "950x600"

data_names = ["section", "fleetPosition", "sectionPosition", "sailno", "boatname",
                   "rating", "finishTime", "correctedTime", "boattype" , "owner"]
data_names_from_rac = ["fleetSection", "fleetPosition", "sectionPosition", "sailno", "boatname",
                   "rating", "finishTime", "correctedTime", "boatType" , "owner"]
col_names = ["Section", "FleetPos", "SectionPos", "Sailno", "Boat Name", 
                  "Rating", "Finish", "Corrected", "Boat Type", "Owner", ]
translate_names = {"section": "fleetSection", "boattype":"boattype"}
col_justify = [tk.LEFT, tk.RIGHT, tk.RIGHT, tk.RIGHT, tk.LEFT,
               tk.RIGHT, tk.RIGHT, tk.RIGHT, tk.LEFT, tk.LEFT]
col_width = [6, 10, 10, 6, 15, 6, 8, 8, 14, 16]
rows = 20
num_cols = len(col_names)


class RaceView(GuiView):
    def __init__(self, controller, roster, file_name, title):
        super().__init__(controller, title, geometry)
        
        self.rows = rows
        self.roster = roster
        self.validator = RaceValidator(roster, controller)
        Observer().register(self.updateNotification)
        
        menubar = tk.Menu(self.root)
        # 2. Create the "File" menu and add commands
        file_menu = tk.Menu(menubar, tearoff=0)
        
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator() # Adds a horizontal line separator
        file_menu.add_command(label="Exit", command=self.root.destroy) # Closes the window
        
        edit_menu = tk.Menu(self.root, tearoff=0)
        edit_menu.add_command(label = "add Row", command=self.add_row)
        edit_menu.add_command(label="Score", command=self.score_race)
        
        # 3. Add the "File" menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.build_ui(col_names, menubar)
        
        self.selected_cell = [None]
        self.widgets = {}
        
        # Openining an existing file?
        race_results = None
        self.info = None
        if file_name:
            try: 
                race_data = controller.open_file(file_name)
                (self.info, self.startTimes, race_results) = race_data
                self.root.title(file_name)
            except Exception as e:
                messagebox.showerror(title="Failed to open", 
                       message="Can't open %s: %s:" % (file_name, e),
                       parent = self.main_frame)

        self.build_grid(race_results)
        
        # If it's a new file, get the information about the race
        if not self.info:
            self.info = showInfoDialog(self.root)        
            if self.info is not None:
                self.startTimes = self.info["startTimes"]
                controller.set_info(self.info)
            
        
    def build_grid(self, race_results):
        # Clear existing grid
        grid_frame = self.grid_frame
        status_var = self.status_var
        canvas = self.canvas
        
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.widgets.clear()
        self.selected_cell[0] = None


        # Column headers
        tk.Label(grid_frame, text="#", bg=HEADER_BG, fg=HEADER_FG,
                 font=HEADER_FONT, width=5, relief=tk.FLAT,
                 bd=1, padx=4).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        for c in range(num_cols):
            name = col_names[c]
            lbl = tk.Label(grid_frame, text=name, bg=HEADER_BG, fg=HEADER_FG,
                           font=HEADER_FONT, width=col_width[c], relief=tk.FLAT, bd=1)
            lbl.grid(row=0, column=c + 1, sticky="nsew", padx=1, pady=1)
            
        # set the number of rows to default if this is a new race, else the number of boats in the results
        self.rows = rows
        if race_results:
            self.rows = len(race_results)

            
        # Data rows
        for r in range(1, self.rows):
            row_bg = ROW_BG1 if r % 2 == 0 else ROW_BG2
            
            if race_results:
                boat = race_results[r-1]

            # Row number
            tk.Label(grid_frame, text=str(r), bg=HEADER_BG, fg=HEADER_FG,
                     font=HEADER_FONT, width=5, bd=1, relief=tk.FLAT).grid(
                row=r, column=0, sticky="nsew", padx=1, pady=1)

            for c in range(num_cols):
                # if this is an exusting file, use the entr from the boat, else blank
                value = " "
                if race_results:
                    value = boat[data_names_from_rac[c]]
                lbl = self.add_field(r, c+1, col_width, col_justify, value, row_bg)
                self.widgets[(r, c)] = (lbl, row_bg)


            r += 1

        # Update scroll region
        grid_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        status_var.set(f"Grid built: {r} rows × {num_cols} cols")
        
    def add_field(self, row, col, col_width, col_justify, value, bg):
        entry_field = tk.Entry(self.grid_frame, width = col_width[col-1],
                               font = FONT, bg=bg, bd=1, relief=tk.FLAT, cursor="hand2",
                               justify=col_justify[col-1])
        entry_field.grid(row=row, column=col, sticky='e')
        entry_field.insert(0, value)

        
        entry_field.bind('<Return>', self.on_enter_key)
        entry_field.bind("<Tab>", self.on_enter_key)
        entry_field.bind("<FocusOut>", self.on_lost_focus)
        entry_field.bind("<FocusIn>", self.on_gain_focus)
        entry_field.bind("<Up>", self.on_up_arrow)
        entry_field.bind("<Down>", self.on_down_arrow)
        entry_field.bind("<Button-1>", self.on_click)
        return entry_field
    
    def get_column_name(self, col):
        return col_names[col]
    
    def get_column_num(self, colName):
        for col in range(len(col_names)):
            if col_names[col] == colName:
                return col 
        return None 
        
    def on_enter_key(self, event):
        widget = event.widget
        value = widget.get().strip()
        #if (value == self.currentValue):
        #    return
        
        col = widget.grid_info()["column"]
        row = widget.grid_info()['row']
        columnName = self.get_column_name(col-1)
        rc = self.validator.validate(columnName, value)
        if rc != True:
            messagebox.showerror(title="Invalid entry", 
                       message=rc,
                       parent = self.main_frame)
            return 
        
        if columnName == "Sailno":
            self.populateRowFromSailno(value, row)
            col = self.get_column_num("Finish")
            (widget, bg) = self.widgets[(row, col)]
            widget.focus_set()
            
        if columnName == "Boat Name":
            self.populateRowFromBoatname(value, row)
            (widget, bg) = self.widgets[(row, self.get_column_num("Finish") + 1)]
            widget.focus_set()
            
        # The finishTime was updated, calculate corrected time
        # if there is section, rting, and finish time
        if columnName in  ["Finish", "Section", "Rating"]:
            section = self.getValue(row, self.get_column_num("Section")).strip()
            rating =  self.getValue(row, self.get_column_num("Rating")).strip()
            finish =  self.getValue(row, self.get_column_num("Finish")).strip()
            if (len(section) > 0 and len(rating) > 0 and len(finish) > 0):                    
                self.updateCorrectedTime(row)      
            
            
    def findBoatName(self, boatName):
        # The roster is keyed by sailnumber.... iterate through the roster to find the boat name
        for sailno in self.roster.keys():
            boat = self.roster[sailno]
            if boat["boatname"] == boatName:
                return boat
            
    def populateRowFromBoat(self, boat, row):
        col = 0
        for colName in data_names:
            value  = ""
            if colName in boat:
                value = boat[colName]
                
            (widget, bg) = self.widgets[(row, col)]
            widget.delete(0, tk.END)
            widget.insert(0, value)
    
            col += 1
            
    def populateRowFromSailno(self, sailno, row):
        boat = self.roster[sailno]
        self.populateRowFromBoat(boat, row)
    
    def populateRowFromBoatname(self, boatname, row):
        boat = self.findBoatName(boatname)
        self.populateRowFromBoat(boat, row)
    
    def on_lost_focus(self, event):
        pass
    
    def on_gain_focus(self, evemt):
        pass
    
    def on_up_arrow(self, event):
        widget = event.widget
        col = widget.grid_info()["column"]
        row = widget.grid_info()["row"]
        if row >1:
            row -= 1
            (newWidget, bg)  = self.widgets[(row, col-1)]
            newWidget.focus_set()
    
    def on_down_arrow(self, event):
        widget = event.widget
        col = widget.grid_info()["column"]
        row = widget.grid_info()["row"]
        if row < (self.rows - 1):
            row += 1
            (newWidget, bg) = self.widgets[(row, col-1)]
            newWidget.focus_set()
            
    def on_click(self, event):
        #print(event)
        '''
        # Deselect previous
        if selected_cell[0] and selected_cell[0] in cell_labels:
            prev_lbl, prev_bg = cell_labels[selected_cell[0]]
            prev_lbl.config(bg=prev_bg, fg="#333")
        # Select new
        selected_cell[0] = (row, col)
        lbl, _ = cell_labels[(row, col)]
        lbl.config(bg=SEL_BG, fg=SEL_FG)
        '''
        
        self.status_var.set(f"Selected: {0} {1}")  
        
    def new_file(self):
        pass
    
    def save_file(self):
        try:
            # Make sure the race is scored before saving
            self.scoreit()
        except BaseException as e:
            messagebox.showerror(title="Error",
                                 message=e,
                                 parent=self.main_frame)
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".rac",
                    initialdir=get_full_path(""),
                    filetypes=[("Race file","*.rac"),("Text Document","*.txt"),
                               ("Web file",".html")])
        results = self.getResults()
        self.controller.save_file(file_path, results)
        pass
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=(("Race Files", "*.rac"), ("All files", "*.*")))
        race = self.controller.open_file(file_path)
        (self.info, self.startTimes, results) = race
        self.widgets = {}
        self.build_grid(results)
    
    def add_row(self):
        r = self.rows + 1
        row_bg = ROW_BG1 if (r+1) % 2 == 0 else ROW_BG2
        
        # Row number
        tk.Label(self.grid_frame, text=str(r-1), bg=HEADER_BG, fg=HEADER_FG,
                font=HEADER_FONT, width=5, bd=1, relief=tk.FLAT).grid(
                row=r, column=0, sticky="nsew", padx=1, pady=1)
        value = " "
        for c in range(num_cols):
            self.add_field(r, c+1, col_width, col_justify, value, row_bg)
        
        self.grid_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        
        self.rows += 1
        self.status_var.set(f"Grid built: {self.rows-1} rows × {num_cols} cols")
    
    
    def score_race(self):
        try:
            self.scoreit()
        except BaseException as e:
            messagebox.showerror(title="Error",
                                 message=e,
                                 parent=self.message_box)       
            
    def updateNotification(self, message):
        # update the roster
        self.roster = self.controller.getRoster()

    
    def updateCorrectedTime(self, row):
        sailnoCol = self.get_column_num("Sailno")
        sailno = self.getValue(row, sailnoCol).strip()
        finishCol = self.get_column_num("Finish")
        finishTime = self.getValue(row, finishCol)
        if finishTime in alphabetSoup:
            self.setValue(row, self.get_column_num("Corrected"), finishTime)
        else:
            rating = self.getValue(row, self.get_column_num("Rating"))
            section = self.getValue(row, self.get_column_num("Section"))
            # need to have both rating and section in order to calculated corrected time
            if rating != "" and section != "":
                correctedTime = self.controller.calculateCorrectedTime(sailno, 
                                                finishTime, rating, section)
                if correctedTime is not None:
                    self.setValue(row, self.get_column_num("Corrected"), correctedTime)
                    
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
                self.setValue(row, self.get_column_num("Section"), section)
                self.setValue(row, self.get_column_num("SectionPos"), boat["sectionPosition"])
                self.setValue(row, self.get_column_num("FleetPos"), boat["fleetPosition"])
                self.setValue(row, self.get_column_num("Sailno"), boat["sailno"])
                self.setValue(row, self.get_column_num("Boat Name"), boat["Boat Name"])
                self.setValue(row, self.get_column_num("Rating"), boat["Rating"])
                self.setValue(row, self.get_column_num("Finish"), boat["finishTime"])
                self.setValue(row, self.get_column_num("Corrected"), boat["correctedTime"])
                self.setValue(row, self.get_column_num("Boat Type"), boat["Boat Type"])
                self.setValue(row, self.get_column_num("Owner"), boat["Owner"])
                row += 1
        
    def getBoats(self):
        boats = []
        for row in range(1, self.rows):
            sailno = self.getValue(row, self.get_column_num("Sailno")).strip()
            if sailno != "":
                fleetSection = self.getValue(row, self.get_column_num("Section"))
                (fleet, section) = self.getFleetSection(fleetSection)
                finish = self.getValue(row, self.get_column_num("Finish"))
                boat = {"sailno": sailno,
                        "finishTime": finish,
                        "correctedTime": self.getValue(row, self.get_column_num("Corrected")),
                        "penalty": finish if finish in alphabetSoup else "",
                        "Owner": self.getValue(row, self.get_column_num("Owner")),
                        "Boat Name": self.getValue(row,self.get_column_num("Boat Name")),
                        "fleet": fleet, "section": section,
                        "Rating": self.getValue(row, self.get_column_num("Rating")),
                        "Boat Type": self.getValue(row, self.get_column_num("Boat Type")),
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
        sections={}
        
        for row in range(1,self.rows):
            section = self.getValue(row, self.get_column_num("Section"))
            sailno = self.getValue(row, self.get_column_num("Sailno"))

            corrected = self.getValue(row, self.get_column_num("Corrected"))
            if sailno != " ":
                penalty = None 
                finishTime = self.getValue(row, self.get_column_num("Finish"))
                if (finishTime.strip() == ""):
                    # If there's not a finish time, then we can't score the boat
                    raise BaseException("No Finish Time for sail %s" % sailno)
                
                if finishTime in alphabetSoup:    
                    correctedTime = finishTime
                    penalty = finishTime
                else:
                    correctedTime = self.toTimeDelta(corrected)
                    
                boat = {"fleetPosition":int(self.getValue(row, self.get_column_num("FleetPos"))),
                        "sectionPosition":int(self.getValue(row, self.get_column_num("SectionPos"))),
                        "sailno": sailno, 
                        "boatname":self.getValue(row, self.get_column_num("Boat Name")),
                        "rating":self.getValue(row, self.get_column_num("Rating")), 
                        "finishTime":self.getValue(row, self.get_column_num("Finish")),
                        "correctedTime": correctedTime,
                        "penalty": penalty,
                        "boatType":self.getValue(row, self.get_column_num("Boat Type")),
                        "owner":self.getValue(row, self.get_column_num("Owner")),
                        }
                
                if section not in sections:
                    sections[section] = []
                sections[section].append(boat)
        
        return sections
    
    def toTimeDelta(self, time):
        mmss = time.split(":")
        delta = timedelta(minutes=int(mmss[0]), seconds=int(mmss[1]))
        return delta
    
    
    
    