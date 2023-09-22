import os
import sys
import time
import shutil
from datetime import datetime
import argparse

def monitor_and_copy(monitorfile, destination):
    last_modified_time = None
    
    while True:
        # Check the file's modified time
        current_modified_time = os.path.getmtime(monitorfile)
        
        if last_modified_time is None:
            last_modified_time = current_modified_time

        # If the file has been modified since the last check
        if current_modified_time != last_modified_time:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            destination_file = os.path.join(destination, f"{os.path.basename(monitorfile)}_{timestamp}")
            shutil.copy2(monitorfile, destination_file)
            print(f"File changed! Copied to {destination_file}")
            
            # Update the last modified time
            last_modified_time = current_modified_time
        
        # Wait for a minute before checking again
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor a file and copy it if changed.")
    parser.add_argument('--monitorfile', required=True, help="Path to the file to monitor")
    parser.add_argument('--destination', required=True, help="Directory to copy the file to if changed")

    args = parser.parse_args()

    monitor_and_copy(args.monitorfile, args.destination)
