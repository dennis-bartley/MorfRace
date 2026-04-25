import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from OldGuiView import View

#
# The class which handles the Roster spreadsheet
#


class RosterView(View):
    def __init__(self, controller, master, roster, geometry):
        super().__init__(master, controller, roster, geometry);
        self.controller = controller
        self.master = master
        self.roster = roster
        self.geometry = geometry
        self.pack(fill="both", expand=True)

        self.col_names = ["Sailno", "Boat Name", "Boat Type", "Owner", "Section", "Rating", ]
        self.col_alignment = ["w", "w", "w", "w", "w", "w"]
        self.rows = 10
        self.cols = len(self.col_names)
        self._editing = None  # (row_id, col_idx, entry_widget)
        self._build_ui()
        self._populate_initial_data(self.roster)

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x")
        
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


        # Container with scrollbars
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            container,
            columns=[self._col_name(i) for i in range(self.cols)],
            show="headings",
            selectmode="browse"
        )
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        # Configure columns and headers
        for i in range(self.cols):
            name = self.col_names[i]
            self.tree.heading(name, text=name, anchor="nw")
            self.tree.column(name, width=20, anchor=self.col_alignment[i], stretch=True)

        # Bindings
        self.tree.bind("<Double-1>", self._begin_edit)
        self.tree.bind("<Return>", self._begin_edit_return)
        self.tree.bind("<Escape>", lambda e: self._end_edit(cancel=True))
        self.tree.bind("<Button-1>", self._maybe_end_edit)
        self.tree.bind("<KeyPress>", self._nav_keys)

    def _populate_initial_data(self, roster):
        values = []
        
        keys = list(roster.keys())
        
        
        for r in keys:
            row = []
            element = roster[r]
            sailno = element["sailno"]
            boatname = element["boatname"]
            boattype = element["boattype"]
            section = element["section"]
            owner = element["owner"]
            rating = element["rating"]
            self.tree.insert("", tk.END, values=(sailno, boatname, boattype, owner, section, rating))

            
        self.tree.insert("", "end", values=values)

    # ----- Editing -----
    def _begin_edit_return(self, event):
        # Start edit on selected cell via Enter
        focus = self.tree.focus()
        if not focus:
            return
        col = self.tree.identify_column(event.x)  # unreliable on Return
        # Fallback: start edit on first visible column
        self._begin_edit_on(focus, 0)

    def _begin_edit(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)  # e.g., '#3'
        col_idx = int(col_id.replace("#", "")) - 1
        self._begin_edit_on(row_id, col_idx)

    def _begin_edit_on(self, row_id, col_idx):
        if not row_id:
            return
        self._end_edit(cancel=False)

        # Cell bbox
        col_name = self._col_name(col_idx)
        try:
            x, y, w, h = self.tree.bbox(row_id, col_name)
        except Exception:
            return
        if w <= 0 or h <= 0:
            return

        # Current value
        values = list(self.tree.item(row_id, "values"))
        current = values[col_idx] if col_idx < len(values) else ""

        # Create Entry overlay
        entry = ttk.Entry(self.tree)
        entry.insert(0, current)
        entry.select_range(0, tk.END)
        entry.focus_set()

        def commit(event=None):
            new_val = entry.get()
            self._set_cell(row_id, col_idx, new_val)
            self._end_edit(cancel=False)

        def cancel(event=None):
            self._end_edit(cancel=True)

        entry.bind("<Return>", commit)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", commit)

        entry.place(x=x, y=y, width=w, height=h)
        self._editing = (row_id, col_idx, entry)

    def _end_edit(self, cancel=True):
        if not self._editing:
            return
        row_id, col_idx, entry = self._editing
        try:
            if not cancel:
                # Commit already handled by commit callback
                pass
        finally:
            entry.destroy()
            self._editing = None

    def _set_cell(self, row_id, col_idx, value):
        values = list(self.tree.item(row_id, "values"))
        # Ensure list has enough columns
        if len(values) < self.cols:
            values += [""] * (self.cols - len(values))
        values[col_idx] = value
        self.tree.item(row_id, values=values)

    def _maybe_end_edit(self, event):
        # End edit when clicking elsewhere
        if self._editing:
            # If click stays on same cell, let _begin_edit handle
            self._end_edit(cancel=False)

    # ----- Navigation -----
    def _nav_keys(self, event):
        if not self.tree.focus():
            return
        if event.keysym in ("Tab", "Right"):
            self._move_selection(dx=1, dy=0)
            return "break"
        if event.keysym in ("Left",):
            self._move_selection(dx=-1, dy=0)
            return "break"
        if event.keysym in ("Up",):
            self._move_selection(dx=0, dy=-1)
            return "break"
        if event.keysym in ("Down",):
            self._move_selection(dx=0, dy=1)
            return "break"

    def _move_selection(self, dx=0, dy=0):
        focus = self.tree.focus()
        if not focus:
            return
        # Determine current column by last edited or default 0
        col_idx = 0
        if self._editing:
            col_idx = self._editing[1]
        col_idx = max(0, min(self.cols - 1, col_idx + dx))

        # Move row
        try:
            row_idx = int(focus)
        except ValueError:
            row_idx = self.tree.index(focus)
        row_idx = max(0, min(self.rows - 1, row_idx + dy))
        new_row_id = str(row_idx)
        self.tree.focus(new_row_id)
        self.tree.selection_set(new_row_id)
        self._begin_edit_on(new_row_id, col_idx)

    # ----- Row/Column management -----
    def add_row(self):
        new_iid = str(self.rows)
        self.tree.insert("", "end", iid=new_iid, values=[""] * self.cols)
        self.rows += 1
        self.tree.focus(new_iid)
        self.tree.selection_set(new_iid)

    def delete_selected_row(self):
        focus = self.tree.focus()
        if not focus:
            return
        idx = int(focus)
        self.tree.delete(focus)
        # Reindex remaining rows for simple numeric iids
        all_ids = self.tree.get_children("")
        for i, iid in enumerate(all_ids):
            if iid != str(i):
                self.tree.item(iid, tags=("reindex",))
        # Rebuild to keep consistent iids
        data = [self.tree.item(iid, "values") for iid in all_ids]
        self.tree.delete(*all_ids)
        for i, vals in enumerate(data):
            self.tree.insert("", "end", iid=str(i), values=vals)
        self.rows = len(data)

    def add_column(self):
        self.cols += 1
        name = self._col_name(self.cols - 1)
        current = list(self.tree["columns"])
        current.append(name)
        self.tree.configure(columns=current)
        self.tree.heading(name, text=name, anchor="W")
        self.tree.column(name, width=100, anchor="center", stretch=True)
        for iid in self.tree.get_children(""):
            values = list(self.tree.item(iid, "values"))
            values.append("")
            self.tree.item(iid, values=values)

    def delete_last_column(self):
        if self.cols <= 1:
            return
        last_name = self._col_name(self.cols - 1)
        current = list(self.tree["columns"])
        current.remove(last_name)
        self.tree.configure(columns=current)
        for iid in self.tree.get_children(""):
            values = list(self.tree.item(iid, "values"))
            if values:
                values.pop()
            self.tree.item(iid, values=values)
        self.cols -= 1

    # ----- CSV I/O -----
    def new_sheet(self):
        if not self._confirm_discard():
            return
        for iid in self.tree.get_children(""):
            self.tree.delete(iid)
        self.rows = 20
        self.cols = 8
        self.tree.configure(columns=[self.col_names(i) for i in range(self.cols)])
        for i in range(self.cols):
            name = self.col_names(i)
            self.tree.heading(name, text=name, anchor=self.col_alignment[i])
            self.tree.column(name, width=100, anchor="nw", stretch=True)
        self._populate_initial_data()

    def open_file(self):
        pass

    def save_file(self):
        pass
    
    def new_file(self):
        pass
        
    # ----- Utilities -----
    def _col_name(self, idx):
        return self.col_names[idx]

    def _confirm_discard(self):
        pass
    