# Folders2CSV

**Folders2CSV** is a Python Tkinter application designed for *12k Mastering*. It scans the `mastering` folder on external backup drives and generates a CSV file listing each subfolder along with its drive name. This tool streamlines cataloging and archiving audio project folders across multiple drives.

## Features

- **Automatic Drive Detection:** Finds connected external drives with "Audio Archive" naming.
- **Folder Scanning:** Scans the `mastering` folder on each selected drive.
- **CSV Export:** Generates or updates a CSV file with folder and drive names.
- **Duplicate Handling:** Avoids duplicate entries when updating an existing CSV.
- **User-Friendly GUI:** Simple interface for selecting drives and managing CSV files.
- **Status Logging:** Real-time progress and status updates in the app.

## Requirements

- **OS:** macOS (designed for Volumes drive structure)
- **Python:** 3.7+
- **Packages:** Standard library only (no external dependencies)

## Installation

1. [**Download Here**](https://github.com/nickdeupree/Folders2CSV/releases/download/1.0/Folders2CSV.zip)
2. Unzip the contents
3. Move app to /Applications
4. Launch Folders2CSV

## Usage

1. **Connect your external backup drives.**
2. **Launch the application**
3. **In the app:**
   - **Select or create a CSV file** (recommended location: `~/Downloads/mastering_folders.csv`).
   - **Select the drives** you want to scan.
   - **Click "Process Selected Drives"** to generate or update the CSV.

4. **The CSV will contain:**
   - `Folder Name`
   - `Drive Name`

## File Structure

- run_gui.py — Entry point for the GUI application.
- gui.py — Tkinter GUI logic.
- backend.py — Main backend logic for drive and CSV processing.
- backendHelpers.py — Helper functions for drive and folder operations.

## How It Works

- The app lists all connected drives matching the "Audio Archive" pattern.
- For each selected drive, it scans the `/Volumes/<Drive>/mastering` folder.
- All subfolders are listed and paired with their drive name.
- The results are saved to a CSV, avoiding duplicates if the file already exists.

## Troubleshooting

- **No drives found?**  
  Ensure your drives are mounted and named like "Audio Archive 1", etc.

---

**Developed for 12k Mastering.**  