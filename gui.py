import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
from backend import Folders2CSVBackend


class Folders2CSVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folders to CSV Converter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.csv_file_path = tk.StringVar()
        self.drives_var = tk.Variable()
        self.selected_drives = []
        self.available_drives = []  # Store actual drive names
        self.drive_checkboxes = []  # Store checkbox variables
        self.mode_var = tk.StringVar( )  # Toggle between add_drives and view_csv
        
        self.drives_loaded = False
        self.search_text = tk.StringVar(value="")
        self.csv_data = []  # Store CSV data for viewing

        # Load saved configuration
        self.load_saved_config()

        self.create_widgets()
        self.refresh_drives()
        
    
    def create_widgets(self):
        self.create_main_frame()
        self.create_csv_file_section()
        self.create_mode_toggle_section()
        self.create_add_drives_section()
        self.create_view_csv_section()
        
        # Configure main frame row weights
        self.main_frame.rowconfigure(3, weight=1)
        
        # Initially show only the add drives mode
        self.on_mode_changed()
        
        # Set initial button layout
        self.update_csv_buttons()

    def create_main_frame(self):
        # Configure ttk styles for flat appearance
        style = ttk.Style()
        
        style.configure("TLabelframe", borderwidth=0, relief="flat")
        style.configure("TCheckbutton", focuscolor="none")
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        self.main_frame.columnconfigure(1, weight=1)

    def create_csv_file_section(self):
        csv_frame = ttk.LabelFrame(self.main_frame, padding="10")
        csv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        csv_frame.columnconfigure(1, weight=1)
        
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_file_path, state="readonly")
        self.csv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Store button references so we can show/hide them
        self.browse_button = ttk.Button(csv_frame, text="Browse Existing", command=self.browse_existing_csv)
        self.create_button = ttk.Button(csv_frame, text="Create New", command=self.create_new_csv)

    def create_mode_toggle_section(self):
        mode_frame = ttk.Frame(self.main_frame)
        mode_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        radio_container = ttk.Frame(mode_frame)
        radio_container.grid(row=0, column=0, columnspan=2)
        
        ttk.Radiobutton(radio_container, text="Add Drives", variable=self.mode_var, value="add_drives", command=self.on_mode_changed).grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(radio_container, text="View CSV", variable=self.mode_var, value="view_csv", command=self.on_mode_changed).grid(row=0, column=1)

    def create_add_drives_section(self):
        self.add_drives_frame = ttk.Frame(self.main_frame)
        self.add_drives_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.add_drives_frame.columnconfigure(0, weight=1)
        self.add_drives_frame.rowconfigure(0, weight=1)

        drives_frame = ttk.LabelFrame(self.add_drives_frame, text="Select Drives", padding="10")
        drives_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        drives_frame.columnconfigure(0, weight=1)
        drives_frame.rowconfigure(1, weight=1)

        drives_header = ttk.Frame(drives_frame)
        drives_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        drives_header.columnconfigure(0, weight=1)

        ttk.Label(drives_header, text="Select drives to process:").grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(drives_header, text="Refresh", command=self.refresh_drives).grid(row=0, column=1, sticky=tk.E)
        
        listbox_frame = ttk.Frame(drives_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        self.drives_canvas = tk.Canvas(
            listbox_frame,
            height=200,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            takefocus=0)
        self.drives_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        drives_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.drives_canvas.yview)
        drives_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.drives_canvas.config(yscrollcommand=drives_scrollbar.set)
        
        self.drives_checkboxes_frame = ttk.Frame(self.drives_canvas)
        
        self.canvas_window = self.drives_canvas.create_window((0, 0), window=self.drives_checkboxes_frame, anchor="nw")
        
        self.drives_checkboxes_frame.bind("<Configure>", self.on_drives_frame_configure)
        
        self.drives_canvas.bind("<Configure>", self.on_drives_canvas_configure)
        
        process_frame = ttk.Frame(self.add_drives_frame)
        process_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        process_frame.columnconfigure(0, weight=1)
        
        self.process_button = ttk.Button(process_frame, text="Process Selected Drives", command=self.process_drives)
        self.process_button.grid(row=0, column=0, pady=(0, 10))


    def create_view_csv_section(self):
        self.view_csv_frame = ttk.Frame(self.main_frame)
        self.view_csv_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W), pady=(0, 10))
        self.view_csv_frame.columnconfigure(0, weight=1)
        self.view_csv_frame.rowconfigure(0, weight=0)  # search row
        self.view_csv_frame.rowconfigure(1, weight=1)  # data row

        search_container = ttk.LabelFrame(self.view_csv_frame, padding="10")
        search_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        search_container.columnconfigure(0, weight=1)
        search_label = ttk.Label(search_container, text="Search by Folder/Drive")
        search_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        search_entry = ttk.Entry(search_container, width=30, textvariable=self.search_text)
        search_entry.grid(row=1, column=0, sticky=(tk.W, tk.E))
        search_entry.bind('<KeyRelease>', self.on_search_entry_changed)

        data_frame = ttk.LabelFrame(self.view_csv_frame, padding="10")
        data_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W), pady=(0, 10))
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=0)  # header row
        data_frame.rowconfigure(1, weight=1)  # databox row
        databox_frame = ttk.Frame(data_frame)
        databox_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        databox_frame.columnconfigure(0, weight=1)
        databox_frame.rowconfigure(0, weight=1)
        
        # Store reference for later use
        self.databox_frame = databox_frame

    def update_csv_buttons(self):
        """Update CSV button layout based on current mode"""
        # Remove existing buttons first
        self.browse_button.grid_remove()
        self.create_button.grid_remove()
        
        if self.mode_var.get() == "add_drives":
            # Show both buttons in add drives mode
            self.browse_button.grid(row=0, column=2, padx=(0, 5), columnspan=1, sticky="")
            self.create_button.grid(row=0, column=3, columnspan=1, sticky="")
        else:  # view_csv mode
            # Show only browse button spanning both columns
            self.browse_button.grid(row=0, column=2, columnspan=2, sticky=(tk.W, tk.E))

    def on_mode_changed(self):
        """Handle switching between Add Drives and View CSV modes"""
        if self.mode_var.get() == "add_drives":
            self.add_drives_frame.grid()
            self.view_csv_frame.grid_remove()
            if not self.drives_loaded:
                self.refresh_drives()
                self.drives_loaded = True
        else:  # view_csv
            self.add_drives_frame.grid_remove()
            self.view_csv_frame.grid()
            # Load CSV data when switching to view mode
            if self.csv_file_path.get():
                self.load_and_display_csv_data()
        
        # Update button layout based on mode
        self.update_csv_buttons()
        
        self.root.update_idletasks()
        # Save the current mode to config
        self.save_config()

    def load_saved_config(self):
        """Load saved configuration (mode and CSV path)"""
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                    # Load saved mode
                    saved_mode = config.get('last_mode', 'add_drives')
                    if saved_mode in ['add_drives', 'view_csv']:
                        self.mode_var.set(saved_mode)
                    else:
                        self.mode_var.set('add_drives')
                    
                    # Load saved CSV path
                    saved_path = config.get('last_csv_path', '')
                    if saved_path and os.path.exists(saved_path):
                        self.csv_file_path.set(saved_path)
                    
                    return True
            else:
                # Set defaults if no config exists
                self.mode_var.set('add_drives')
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading saved config: {e}")
            self.mode_var.set('add_drives')
            return False

    def save_config(self):
        """Save current configuration (mode and CSV path)"""
        try:
            config_path = self.get_config_path()
            config = {
                'last_mode': self.mode_var.get(),
                'last_csv_path': self.csv_file_path.get()
            }
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")

    def get_config_path(self):
        """Get path to config file in Application Support dir"""
        app_support = os.path.expanduser('~/Library/Application Support')
        app_folder = os.path.join(app_support, 'Folders2CSV')
        if not os.path.exists(app_folder):
            os.makedirs(app_folder, exist_ok=True)
        return os.path.join(app_folder, 'config.json')
    
    def on_drives_frame_configure(self, event):
        """Update canvas scroll region when frame size changes"""
        self.drives_canvas.configure(scrollregion=self.drives_canvas.bbox("all"))
    
    def on_drives_canvas_configure(self, event):
        """Update canvas window width when canvas is resized"""
        canvas_width = event.width
        self.drives_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def set_mode(self, mode):
        """Set the current mode (add_drives or view_csv)"""
        self.mode_var.set(mode)
        self.save_mode_var(mode)
    
    def browse_existing_csv(self):
        """Browse for an existing CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Existing CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser('~/Downloads')
        )
        if file_path:
            if self.validate_csv_selection(file_path):
                self.csv_file_path.set(file_path)
                self.save_config()  # Save both mode and CSV path
                # Load data if we're currently in view mode
                if self.mode_var.get() == "view_csv":
                    self.load_and_display_csv_data()

    def create_new_csv(self):
        """Create a new CSV file"""
        file_path = filedialog.asksaveasfilename(
            title="Create New CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.expanduser('~/Downloads'),
            initialfile="mastering_folders.csv"
        )
        if file_path:
            self.csv_file_path.set(file_path)
            self.save_config()  # Save both mode and CSV path
            # Validate the path even for new files
            self.validate_csv_selection(file_path)
            # Clear data display for new files
            if self.mode_var.get() == "view_csv":
                self.csv_data = []
                self.display_csv_data()

    def load_and_display_csv_data(self):
        """Load CSV data and update the display"""
        csv_path = self.csv_file_path.get()
        if not csv_path:
            self.csv_data = []
            self.display_csv_data()
            return
        
        try:
            self.csv_data = Folders2CSVBackend.get_csv_contents(csv_path)
            self.display_csv_data()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load CSV file: {e}")
            self.csv_data = []
            self.display_csv_data()

    def display_csv_data(self):
        """Display the CSV data in the view section"""
        # Use the stored reference to databox_frame
        databox_frame = self.databox_frame
        
        if not databox_frame:
            return
        
        # Clear existing content
        for widget in databox_frame.winfo_children():
            widget.destroy()
        
        if not self.csv_data:
            ttk.Label(databox_frame, text="No data to display").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=10)
            return
        
        # Create scrollable canvas with same style as drives section
        canvas = tk.Canvas(
            databox_frame,
            height=300,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            takefocus=0
        )
        scrollbar = ttk.Scrollbar(databox_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Handle canvas resize
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Filter data based on search text
        search_term = self.search_text.get().lower()
        filtered_data = self.csv_data
        if search_term:
            filtered_data = [
                (folder, drive) for folder, drive in self.csv_data
                if search_term in folder.lower() or search_term in drive.lower()
            ]
                
        # Display data rows
        for i, (folder_name, drive_name) in enumerate(filtered_data):
            row_frame = ttk.Frame(scrollable_frame)
            row_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=1)
            row_frame.columnconfigure(0, weight=3)  # Match header column weight
            row_frame.columnconfigure(1, weight=2)  # Match header column weight
            
            ttk.Label(row_frame, text=folder_name, width=40).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
            ttk.Label(row_frame, text=drive_name, width=20).grid(row=0, column=1, sticky=tk.W)
        
        canvas.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        databox_frame.columnconfigure(0, weight=1)
        databox_frame.rowconfigure(0, weight=1)

    def on_search_entry_changed(self, event):
        """Handle search entry changes"""
        self.display_csv_data()  # Refresh display with filtered data

    def refresh_drives(self):
        """Refresh the list of available Audio Archive drives"""
        self.drives_loaded = False
        
        # Clear current checkboxes
        for widget in self.drives_checkboxes_frame.winfo_children():
            widget.destroy()
        self.drive_checkboxes.clear()
        
        # Get drives from backend
        self.available_drives = self.get_available_drives()
        
        # Create checkboxes for each drive
        for i, drive in enumerate(self.available_drives):
            drive_info = Folders2CSVBackend.get_drive_info(drive)
            display_text = f"{drive_info['stripped_name']} ({drive_info['folder_count']} folders)"
            
            # Create checkbox variable
            var = tk.BooleanVar()
            self.drive_checkboxes.append(var)
            
            # Create checkbox widget
            checkbox = ttk.Checkbutton(
                self.drives_checkboxes_frame,
                text=display_text,
                variable=var
            )
            checkbox.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
            
        # Update canvas scroll region
        self.drives_checkboxes_frame.update_idletasks()
        self.drives_canvas.configure(scrollregion=self.drives_canvas.bbox("all"))

        self.drives_loaded = True
    
    def process_drives(self):
        """Process the selected drives"""
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select or create a CSV file first")
            return
        
        # Get selected drives based on checkbox states
        selected_indices = [i for i, var in enumerate(self.drive_checkboxes) if var.get()]
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one drive to process")
            return
        
        # Get the actual drive names
        self.selected_drives = [self.available_drives[i] for i in selected_indices if i < len(self.available_drives)]
        
        
        # Disable process button and start progress
        self.process_button.config(state="disabled")
        
        # Run processing in separate thread
        thread = threading.Thread(target=self.process_drives_thread)
        thread.daemon = True
        thread.start()
    
    def process_drives_thread(self):
        """Process drives in a separate thread"""
        try:
            def progress_callback(message):
                print(message)
            
            success, message, count = Folders2CSVBackend.process_drives_to_csv(
                self.selected_drives, 
                self.csv_file_path.get(),
                progress_callback
            )
            
            # Update UI in main thread
            self.root.after(0, self.processing_complete, success, message, count)
        except Exception as e:
            self.root.after(0, self.processing_error, str(e))
    
    def processing_complete(self, success, message, count):
        """Called when processing is complete"""
        self.process_button.config(state="normal")
        
        if success:
            print(f"✓ {message}")
            messagebox.showinfo("Success", message)
            # Refresh CSV data if we're in view mode
            if self.mode_var.get() == "view_csv":
                self.load_and_display_csv_data()
        else:
            print(f"✗ {message}")
            messagebox.showerror("Error", message)
    
    def processing_error(self, error_msg):
        """Called when processing encounters an error"""
        self.process_button.config(state="normal")
        print(f"✗ Error: {error_msg}")
        messagebox.showerror("Error", f"An error occurred: {error_msg}")
    
    # Backend interface methods
    def get_available_drives(self):
        """Get list of available Audio Archive drives"""
        return Folders2CSVBackend.get_available_drives()
    
    def validate_csv_selection(self, csv_path):
        """Validate the selected CSV file"""
        if csv_path:
            is_valid, message, count = Folders2CSVBackend.validate_csv_file(csv_path)
            if is_valid:
                print(f"CSV validation: {message}")
            else:
                print(f"CSV validation failed: {message}")
                messagebox.showerror("Invalid CSV", message)
            return is_valid
        return False


def main():
    root = tk.Tk()
    Folders2CSVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
