import tkinter as tk
from tkinter import filedialog, messagebox

from OldGuiView import View
from RosterValidator import RosterValidator

# The class which handles the Roster spreadsheet
#
class RosterView(View):
    def __init__(self, controller, root, roster, title, geometry):
        super().__init__(controller, root, roster, title, geometry)
        self.controller = controller
        self.root = root
        self.roster = roster
        self.geometry = geometry

        self.column_names = ["sailno", "boatname", "boattype", "section", "rating", "owner", "harbor"]
        self.col_names = ["Sailno", "Boat Name", "Boat Type", "Section", "Rating", "Owner", "Harbor"]
        self.col_alignment = ["w", "w", "w", "w", "w", "w", "w"]
        rows = 10
        self.cols = len(self.col_names)
        #self.populate_initial_data(self.roster)
        self.validator = RosterValidator(self.controller, self.column_names)

    
        #toolbar = ttk.Frame(self)
        #toolbar.pack(side="top", fill="x")
        '''
        menubar = tk.Menu(self.master)
        # 2. Create the "File" menu and add commands
        file_menu = tk.Menu(menubar, tearoff=0)
        
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator() # Adds a horizontal line separator
        file_menu.add_command(label="Exit", command=self.master.destroy) # Closes the window
        
        # 3. Add the "File" menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)

        # 4. Configure the main window to use the menu bar
        self.master.config(menu=menubar)
        '''
        
        #self.build_ui(self.col_names, menubar)
        self.build_ui(self.col_names, None)
        #self.populate_initial_data(roster)


    def populate_initial_data(self, roster):
        
        # the roster is a dictionay keyed by sail number.
        # Each entry is a dictionary for that boat's information
        sailNumbers = list(roster.keys())
        
        self.widgets = {}
        irow = 1
        for sailno in sailNumbers:
            boat = roster[sailno]
            icol = 0
            for col in self.column_names:
                value = boat[col]
                entry_field = tk.Entry(self.master, relief="ridge", width=20)
                entry_field.grid(row=irow, column=icol, sticky="nsew")
                entry_field.insert(0, value)
                entry_field.bind('<Return>', self.on_enter_key)
                entry_field.bind("<Tab>", self.on_enter_key)
                entry_field.bind("<FocusOut>", self.on_lost_focus)
                self.widgets[(irow, icol)] = entry_field
                icol += 1
                
            irow += 1
        self.rows = irow  - 1
            
    def new_file(self):
        self.controller.new_race()
    
    def open_file(self):
        pass
    
    def save_file(self):
        # construct a roster from the spreadsheet
        roster = {}
        for row in range(self.rows):
            sailno = self.getValue(row+1, self.getColumnNum(self.column_names, 'sailno'))
            boat = {}
            col = 0
            for colName in self.column_names:
                boat[colName] = self.getValue(row+1, col)
                col += 1
            roster[sailno] = boat
            
        file_path = filedialog.asksaveasfilename(
            title="Save Roster File",
            defaultextension=".rst",
            filetypes=(("Roster Files", "*.rst"), ("All files", "*.*")))
        self.controller.save_file(file_path, roster)
        pass
    
    def on_enter_key(self, event):
        print("Roster View", event)
        widget = event.widget
        col = widget.grid_info()["column"]
        row = widget.grid_info()["row"]
        value = widget.get()
        print("on enter", row, col, value)
        if row is not None and col is not None:
            rc = self.validator.validate(self.column_names[col], value)
            if rc is not True:
                messagebox.showerror("Invalid entry", rc)
                
    def on_lost_focus(self, event):
        self.on_enter_key(event)

        

            
            
            
    
    


            
