#!/usr/bin/env python3
"""
Demo script to run the Folders2CSV GUI application.
This script starts the tkinter GUI for the Audio Archive folder processing tool.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui import main
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error importing GUI module: {e}")
    print("Please ensure all required files are in the same directory:")
    print("- gui.py")
    print("- backend.py") 
    print("- main.py")
    
except Exception as e:
    print(f"Error starting application: {e}")
    import traceback
    traceback.print_exc()
