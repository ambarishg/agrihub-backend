import os
import time
from config.configs import CONFIGS

def delete_recent_files(directory, hours):
    # Convert hours to seconds
    time_threshold = time.time() - (hours * 3600)
    
    # Iterate through files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Check if it's a file (not a directory)
        if os.path.isfile(file_path):
            # Get the file's last modification time
            file_mod_time = os.path.getmtime(file_path)
            
            # Check if the file was modified within the last N hours
            if file_mod_time <= time_threshold:
                try:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

# Example usage
directory_path = CONFIGS.UPLOAD_DIR  # Replace with your directory path
hours_to_check = 4  # Replace with N hours
delete_recent_files(directory_path, hours_to_check)
