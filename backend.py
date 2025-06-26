
import os
import csv
from backendHelpers import BackendHelpers

class Folders2CSVBackend:
    """Backend interface for processing Audio Archive drives"""
    
    @staticmethod
    def get_available_drives():
        """
        Get list of available Audio Archive drives
        
        Returns:
            list: List of drive names that contain Audio Archive data
        """
        try:
            return BackendHelpers.getDrives()
        except Exception as e:
            print(f"Error getting drives: {e}")
            return []
    
    @staticmethod
    def process_drives_to_csv(selected_drives, csv_file_path, progress_callback=None):
        """
        Process selected drives and save/append to CSV file
        
        Args:
            selected_drives (list): List of drive names to process
            csv_file_path (str): Path to the CSV file to create/update
            progress_callback (callable): Optional callback for progress updates
            
        Returns:
            tuple: (success: bool, message: str, data_count: int)
        """
        try:
            data = []
            
            for i, drive in enumerate(selected_drives):
                if progress_callback:
                    progress_callback(f"Processing drive: {drive}")
                
                mastering_folder = BackendHelpers.getMasteringFolder(drive)
                if mastering_folder:
                    folder_data = BackendHelpers.getFolderContents(mastering_folder, drive)
                    if folder_data:
                        data.extend(folder_data)
                        if progress_callback:
                            progress_callback(f"Found {len(folder_data)} folders in {drive}")
                    else:
                        if progress_callback:
                            progress_callback(f"No folders found in {drive}")
                else:
                    if progress_callback:
                        progress_callback(f"No mastering folder found for drive: {drive}")
            
            if not data:
                return False, "No data found to save", 0
            
            # Sort by drive name
            data.sort(key=lambda x: x[1])
            
            # Check if file exists to determine if we should append or create new
            file_exists = os.path.exists(csv_file_path)
            existing_data = []
            
            if file_exists:
                # Read existing data to avoid duplicates
                try:
                    with open(csv_file_path, 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        next(reader, None)  # Skip header
                        existing_data = [(row[0], row[1]) for row in reader if len(row) >= 2]
                except Exception as e:
                    print(f"Warning: Could not read existing CSV file: {e}")
                    existing_data = []
            
            # Filter out duplicates
            existing_set = set(existing_data)
            new_data = [item for item in data if item not in existing_set]
            
            # Combine all data
            all_data = existing_data + new_data
            all_data.sort(key=lambda x: x[1])  # Sort by drive name
            
            # Write to CSV
            if progress_callback:
                progress_callback("Saving to CSV file...")
            
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Folder Name', 'Drive Name'])
                for folder, drive in all_data:
                    writer.writerow([folder, drive])
            
            total_folders = len(all_data)
            new_folders = len(new_data)
            
            if file_exists and new_folders > 0:
                message = f"CSV updated with {new_folders} new folders. Total: {total_folders} folders."
            elif file_exists and new_folders == 0:
                message = f"No new folders found. CSV contains {total_folders} folders."
            else:
                message = f"CSV created with {total_folders} folders."
            
            return True, message, total_folders
            
        except Exception as e:
            error_msg = f"Error processing drives: {str(e)}"
            print(error_msg)
            return False, error_msg, 0
    
    @staticmethod
    def validate_csv_file(csv_file_path):
        """
        Validate if the CSV file exists and has the correct format
        
        Args:
            csv_file_path (str): Path to the CSV file
            
        Returns:
            tuple: (is_valid: bool, message: str, folder_count: int)
        """
        if not csv_file_path:
            return False, "No CSV file specified", 0
        
        if not os.path.exists(csv_file_path):
            return True, "New CSV file will be created", 0
        
        try:
            with open(csv_file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                
                if not header or len(header) < 2:
                    return False, "Invalid CSV format: missing or incorrect header", 0
                
                if header[0].lower() not in ['folder name', 'folder'] or header[1].lower() not in ['drive name', 'drive']:
                    return False, "Invalid CSV format: incorrect column headers", 0
                
                # Count existing rows
                row_count = sum(1 for row in reader if len(row) >= 2)
                
                return True, f"Valid CSV file with {row_count} existing entries", row_count
                
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}", 0
    
    @staticmethod
    def get_drive_info(drive_name):
        """
        Get information about a specific drive
        
        Args:
            drive_name (str): Name of the drive
            
        Returns:
            dict: Drive information including folder count, mastering folder path, etc.
        """
        try:
            mastering_folder = BackendHelpers.getMasteringFolder(drive_name)
            if not mastering_folder:
                return {
                    'drive_name': drive_name,
                    'stripped_name': BackendHelpers.stripDriveName(drive_name),
                    'mastering_folder': None,
                    'folder_count': 0,
                    'status': 'No mastering folder found'
                }
            
            folder_data = BackendHelpers.getFolderContents(mastering_folder, drive_name)
            
            return {
                'drive_name': drive_name,
                'stripped_name': BackendHelpers.stripDriveName(drive_name),
                'mastering_folder': mastering_folder,
                'folder_count': len(folder_data) if folder_data else 0,
                'status': 'Ready' if folder_data else 'No folders found'
            }
            
        except Exception as e:
            return {
                'drive_name': drive_name,
                'stripped_name': BackendHelpers.stripDriveName(drive_name),
                'mastering_folder': None,
                'folder_count': 0,
                'status': f'Error: {str(e)}'
            }
