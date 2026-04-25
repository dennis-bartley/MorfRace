import tkinter as tk
from tkinter import filedialog, messagebox

from MorfRace import getCorrectedTime, rank
from GuiView import GuiView
from RosterValidator import RosterValidator
from Observer import Observer
from Style import *


geometry = "750x600"
column_names = ["sailno", "boatname", "boattype", "section", "rating", "owner", "harbor"]
col_names = ["Sailno", "Boat Name", "Boat Type", "Section", "Rating", "Owner", "Harbor"]

col_width = [5, 15, 15, 6, 6, 20, 12]
col_justify = [tk.RIGHT, tk.LEFT, tk.LEFT, tk.LEFT, tk.RIGHT, tk.LEFT, tk.LEFT]
num_cols = len(col_names)

class RosterView(GuiView):
    def __init__(self, controller, roster, title):
        super().__init__(controller, title, geometry)

        root = self.root
        
        self.controller = controller
        self.roster = roster
        self.validator = RosterValidator(roster , controller, column_names)    
        #Observer().register(self.updateNotification)
        root.protocol("WM_DELETE_WINDOW", self.window_exit)
    
        # --- Toolbar ---
        toolbar = tk.Frame(root, bg="#2c3e50", pady=6)
        toolbar.pack(fill=tk.X)
        
        menubar = tk.Menu(toolbar)
        # 2. Create the "File" menu and add commands
        file_menu = tk.Menu(menubar, tearoff=0)
        
        file_menu.add_command(label="New race", command=self.new_race_file)
        file_menu.add_command(label="Open race", command=self.open_race_file)
        file_menu.add_command(label="New roster", command=self.new_roster_file)
        file_menu.add_command(label="Save roster", command=self.save_roster_file)
        file_menu.add_separator() # Adds a horizontal line separator
        file_menu.add_command(label="Exit", command=self.window_exit) # Closes the window
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label = "add Row", command=self.add_row)  
        
        # 3. Add the "File" menu to the menu bar
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        root.config(menu=menubar)
        self.build_ui(col_names, menubar)
        
        self.selected_cell = [None]
        self.widgets = {}
        
        self.build_grid()

    
    def build_grid(self):
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

        # Data rows
        r = 1
        sailnos = self.roster.keys()
        for sailno in sailnos:
            boat = self.roster[sailno]
            row_bg = ROW_BG1 if r % 2 == 0 else ROW_BG2

            # Row number
            tk.Label(grid_frame, text=str(r), bg=HEADER_BG, fg=HEADER_FG,
                     font=HEADER_FONT, width=5, bd=1, relief=tk.FLAT).grid(
                row=r, column=0, sticky="nsew", padx=1, pady=1)

            for c in range(num_cols):
                index = column_names[c]
                value = boat[index]
                lbl = self.add_field(r, c+1, col_width, col_justify, value, row_bg)
                self.widgets[(r, c)] = (lbl, row_bg)

            r += 1
            
        self.rows = r

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
            
    def get_column_name(self, col):
        return col_names[col]
    
    def get_data_name(self, col):
        return  column_names[col]
    
    def get_column_num(self, name):
        for c in range(num_cols):
            if column_names[c] == name:
                return c 
            
        return None
    
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
        # Deselect previou
        '''
        if selected_cell[0] and selected_cell[0] in cell_labels:
            prev_lbl, prev_bg = cell_labels[selected_cell[0]]
            prev_lbl.config(bg=prev_bg, fg="#333")
        # Select new
        selected_cell[0] = (row, col)
        lbl, _ = cell_labels[(row, col)]
        lbl.config(bg=SEL_BG, fg=SEL_FG)
        '''
        pass
        
        
    def window_exit(self):
        quit()
        
    def new_race_file(self):
        self.controller.new_race()
        pass
    
    def new_roster_file(self):
        self.controller.new_file() 
    
    def save_roster_file(self):
        roster = self.get_roster_from_sheet()
        file_path = filedialog.asksaveasfilename(
            title="Save File",
            filetypes=(("Roster Files", "*.rst"), ("Roster File", "*.rst")))
        
        if ".rst" not in file_path:
            file_path = file_path + ".rst"
        self.controller.save_file(file_path, roster)
    
    # Open an existing race
    def open_race_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            filetypes=(("Race Files", "*.rac"), ("All files", "*.*")))
        self.controller.open_race(file_path)
    
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
        
    # construct a roster from the spreadsheet
    def get_roster_from_sheet(self):
        roster = {}
        for row in range(1, self.rows):
            sailno = self.getValue(row, self.get_column_num("sailno"))
            boat = {}
            for col in range(num_cols):
                value = self.getValue(row, col)
                boat[self.get_data_name(col)] = value
            roster[sailno] = boat
            
        return roster
        
    
    


