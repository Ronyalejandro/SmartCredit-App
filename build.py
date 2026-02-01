"""
Build script for SmartCredit App v0.1
Generates a standalone executable using PyInstaller.
"""
import os
import shutil
import subprocess
import sys

# Configuration
APP_NAME = "SmartCredit"
MAIN_SCRIPT = "main.py"
ICON_FILE = None  # Add path to .ico file if you have one
OUTPUT_DIR = "dist"
BUILD_DIR = "build"

def clean_previous_builds():
    """Remove previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    for dir_name in [OUTPUT_DIR, BUILD_DIR]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed {dir_name}/")
    
    # Remove spec file
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"   Removed {spec_file}")

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller not found!")
        print("   Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        return True

def build_executable():
    """Build the executable using PyInstaller"""
    print(f"\n🔨 Building {APP_NAME}...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",  # Single executable
        "--windowed",  # No console window (GUI mode)
        "--clean",
    ]
    
    # Add icon if available
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Add hidden imports for CustomTkinter
    cmd.extend([
        "--hidden-import", "customtkinter",
        "--hidden-import", "PIL._tkinter_finder",
    ])
    
    # Add data files (if needed in the future)
    # cmd.extend(["--add-data", "assets;assets"])
    
    cmd.append(MAIN_SCRIPT)
    
    # Execute build
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f"\n✅ Build successful!")
        print(f"   Executable: {OUTPUT_DIR}/{APP_NAME}.exe")
        return True
    else:
        print(f"\n❌ Build failed with code {result.returncode}")
        return False

def main():
    print("=" * 60)
    print(f"  SmartCredit v0.1 - Build Script")
    print("=" * 60)
    
    # Verify PyInstaller
    if not check_pyinstaller():
        return
    
    # Clean previous builds
    clean_previous_builds()
    
    # Build
    if build_executable():
        print("\n" + "=" * 60)
        print("  ✓ Build complete! Ready for distribution.")
        print("=" * 60)
        print(f"\nYou can find the executable in: {os.path.abspath(OUTPUT_DIR)}")
    else:
        print("\n⚠️  Build process encountered errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
