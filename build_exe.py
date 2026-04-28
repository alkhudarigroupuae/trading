import os
import subprocess
import sys

def build_executable():
    print("==================================================")
    print("🚀 Alkhudari Trading Engine - EXE Builder")
    print("==================================================")
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print("✅ PyInstaller is installed.")
    except ImportError:
        print("⚠️ PyInstaller not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # The command to build the exe
    # We need to include templates and static folders for Flask to work
    
    build_command = [
        "pyinstaller",
        "--name=Alkhudari_TradeEngine",
        "--onefile",
        "--add-data=templates;templates", # Windows uses ; not :
        "--add-data=static;static",
        "--hidden-import=engineio.async_drivers.threading",
        "--hidden-import=flask_sqlalchemy",
        "--hidden-import=yfinance",
        "--hidden-import=requests",
        "run_simple.py"
    ]
    
    print("\n⏳ Building the .exe file... This may take a few minutes.")
    print("Command:", " ".join(build_command))
    
    # Note: This script MUST be run on the Windows VPS itself to generate a Windows .exe
    if os.name == 'nt': # If running on Windows
        subprocess.call(build_command)
        print("\n✅ Build Complete! You will find Alkhudari_TradeEngine.exe in the 'dist' folder.")
    else:
        print("\n❌ ARCHITECTURE WARNING:")
        print("You are currently running on macOS/Linux. PyInstaller can only build a Windows .exe if it is run ON a Windows machine.")
        print("Please copy this project to your Windows VPS first, then run this script: `python build_exe.py`")

if __name__ == "__main__":
    build_executable()