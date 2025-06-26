import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
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
        
        self.create_widgets()
        self.refresh_drives()
    
    def create_widgets(self):
        # Configure ttk styles for flat appearance
        style = ttk.Style()
        style.configure("TLabelframe", borderwidth=0, relief="flat")
        style.configure("TCheckbutton", focuscolor="none")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # CSV File Selection Section
        csv_frame = ttk.LabelFrame(main_frame, padding="10")
        csv_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        csv_frame.columnconfigure(1, weight=1)
        
        ttk.Label(csv_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.csv_entry = ttk.Entry(csv_frame, textvariable=self.csv_file_path, state="readonly")
        self.csv_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(csv_frame, text="Browse Existing", command=self.browse_existing_csv).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(csv_frame, text="Create New", command=self.create_new_csv).grid(row=0, column=3)
        
        # Drives Selection Section
        drives_frame = ttk.LabelFrame(main_frame, text="Audio Archive Drives", padding="10")
        drives_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        drives_frame.columnconfigure(0, weight=1)
        drives_frame.rowconfigure(1, weight=1)
        
        # Drives header with refresh button
        drives_header = ttk.Frame(drives_frame)
        drives_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        drives_header.columnconfigure(0, weight=1)
        
        ttk.Label(drives_header, text="Select drives to process:").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(drives_header, text="Refresh", command=self.refresh_drives).grid(row=0, column=1, sticky=tk.E)
        
        # Drives listbox with scrollbar
        listbox_frame = ttk.Frame(drives_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        # Canvas with focus border removed
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
        
        # Frame to hold the checkboxes
        self.drives_checkboxes_frame = ttk.Frame(self.drives_canvas)
        self.canvas_window = self.drives_canvas.create_window((0, 0), window=self.drives_checkboxes_frame, anchor="nw")
        
        # Bind canvas resize to update scrollregion
        self.drives_checkboxes_frame.bind("<Configure>", self.on_drives_frame_configure)
        self.drives_canvas.bind("<Configure>", self.on_drives_canvas_configure)
        
        # Process Section
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        process_frame.columnconfigure(0, weight=1)
        
        self.process_button = ttk.Button(process_frame, text="Process Selected Drives", command=self.process_drives)
        self.process_button.grid(row=0, column=0, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(process_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, pady=(0, 5))
   
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text area with scrollbar
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_text_frame.columnconfigure(0, weight=1)
        status_text_frame.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(status_text_frame, height=6, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        
        # Configure main frame row weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        self.log_message("Application started. Please select or create a CSV file.")
    
    def on_drives_frame_configure(self, event):
        """Update canvas scroll region when frame size changes"""
        self.drives_canvas.configure(scrollregion=self.drives_canvas.bbox("all"))
    
    def on_drives_canvas_configure(self, event):
        """Update canvas window width when canvas is resized"""
        canvas_width = event.width
        self.drives_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
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
                self.log_message(f"Selected existing CSV: {os.path.basename(file_path)}")
    
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
            self.log_message(f"New CSV file will be created: {os.path.basename(file_path)}")
            # Validate the path even for new files
            self.validate_csv_selection(file_path)
    
    def refresh_drives(self):
        """Refresh the list of available Audio Archive drives"""
        self.log_message("Refreshing drives list...")
        
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
        
        if self.available_drives:
            self.log_message(f"Found {len(self.available_drives)} Audio Archive drives")
        else:
            self.log_message("No Audio Archive drives found")
    
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
        
        self.log_message(f"Processing {len(self.selected_drives)} selected drives...")
        
        # Disable process button and start progress
        self.process_button.config(state="disabled")
        self.progress_var.set("Processing drives...")
        
        # Run processing in separate thread
        thread = threading.Thread(target=self.process_drives_thread)
        thread.daemon = True
        thread.start()
    
    def process_drives_thread(self):
        """Process drives in a separate thread"""
        try:
            def progress_callback(message):
                self.root.after(0, lambda: self.log_message(message))
            
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
            self.progress_var.set("Processing complete!")
            self.log_message(f"✓ {message}")
            messagebox.showinfo("Success", message)
        else:
            self.progress_var.set("Processing failed")
            self.log_message(f"✗ {message}")
            messagebox.showerror("Error", message)
    
    def processing_error(self, error_msg):
        """Called when processing encounters an error"""
        self.process_button.config(state="normal")
        self.progress_var.set("Error occurred")
        self.log_message(f"✗ Error: {error_msg}")
        messagebox.showerror("Error", f"An error occurred: {error_msg}")
    
    def log_message(self, message):
        """Add a message to the status log"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    # Backend interface methods
    def get_available_drives(self):
        """Get list of available Audio Archive drives"""
        return Folders2CSVBackend.get_available_drives()
    
    def validate_csv_selection(self, csv_path):
        """Validate the selected CSV file"""
        if csv_path:
            is_valid, message, count = Folders2CSVBackend.validate_csv_file(csv_path)
            if is_valid:
                self.log_message(f"CSV validation: {message}")
            else:
                self.log_message(f"CSV validation failed: {message}")
                messagebox.showerror("Invalid CSV", message)
            return is_valid
        return False


def main():
    root = tk.Tk()
    Folders2CSVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
