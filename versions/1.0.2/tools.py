import os
import subprocess
from datetime import datetime
version = "1.0.1"

def ensure_assets_dir():
    """Creates the 'assets' directory if it does not exist."""
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    return assets_dir

def run_paint_tool():
    """Creates the .ico file with today's date and opens it in Paint."""
    assets_dir = ensure_assets_dir()
    
    # Get current date in YYYY-MM-DD format
    today_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"pnttl.{today_date}.ico"
    file_path = os.path.join(assets_dir, file_name)
    
    # Create an empty file if it doesn't exist yet
    if not os.path.exists(file_path):
        open(file_path, "wb").close()
    
    print(f"Opening MS Paint for file: {file_path}")
    
    try:
        # Launch MS Paint with the created file
        subprocess.run(["mspaint", file_path])
    except FileNotFoundError:
        print("Error: Microsoft Paint (mspaint.exe) could not be found on this system.")

def print_version():
    global version
    """Displays the application version."""
    print(version)
    input("Press enter to exit if you're in Python's original app.")

def main():
    print("===================================")
    print("      TOOL SELECTION MENU         ")
    print("===================================")
    print("1. Paint")
    print("2. Version")
    print("===================================")
    
    user_choice = input("Which tool would you like to select? ").strip().lower()
    
    if user_choice in ["1", "paint"]:
        run_paint_tool()
    elif user_choice in ["2", "version"]:
        print_version()
    else:
        print("Invalid selection. Please choose either 'Paint' or 'Version'.")

if __name__ == "__main__":
    main()
