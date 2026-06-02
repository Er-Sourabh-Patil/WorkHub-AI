#!/usr/bin/env python
"""
AUTOMATED BUILD SCRIPT for Attendance System Executable
========================================================

This script automates the entire process of creating a standalone Windows executable
from the Flask attendance management application.

Usage:
    python build_executable.py
    
Features:
    - Cleans previous builds
    - Installs/verifies PyInstaller
    - Builds executable with all dependencies
    - Copies additional files
    - Creates launcher scripts
    - Generates final package

Output:
    dist/attendance/  - Complete standalone application
    
Estimated time: 20-30 minutes
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_NAME = "WorkHub AI"
PYINSTALLER_VERSION = "6.2.0"
PYTHON_MIN_VERSION = (3, 8)
BUILD_SPEC_FILE = "build_workhubai.spec"
EXECUTABLE_NAME = "WorkHubAI"
OUTPUT_DIR = "dist"
PACKAGE_DIR = f"{OUTPUT_DIR}/{EXECUTABLE_NAME}"

# ============================================================================
# COLORS FOR TERMINAL OUTPUT
# ============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}[*] {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

# ============================================================================
# STEP 1: PRE-BUILD CHECKS
# ============================================================================

def check_python_version():
    """Verify Python version compatibility"""
    print_section("Checking Python version")
    
    version = sys.version_info[:2]
    if version < PYTHON_MIN_VERSION:
        print_error(f"Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}+ required, got {version[0]}.{version[1]}")
        return False
    
    print_success(f"Python {version[0]}.{version[1]} detected")
    return True

def check_build_environment():
    """Verify all required files exist"""
    print_section("Checking build environment")
    
    required_files = [
        'app.py',
        'config.py',
        'database.py',
        'face_utils.py',
        'camera_api.py',
        'requirements.txt',
        'templates',
        'static',
    ]
    
    missing = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
            print_error(f"Missing: {file_path}")
        else:
            print_success(f"Found: {file_path}")
    
    return len(missing) == 0

def check_dependencies():
    """Verify all Python dependencies are installed"""
    print_section("Checking Python dependencies")
    
    try:
        import flask
        print_success("Flask installed")
        
        import cv2
        print_success("OpenCV installed")
        
        import numpy
        print_success("NumPy installed")
        
        import tensorflow
        print_success("TensorFlow installed")
        
        import deepface
        print_success("DeepFace installed")
        
        return True
    except ImportError as e:
        print_error(f"Missing dependency: {e}")
        print_warning("Run: pip install -r requirements.txt")
        return False

# ============================================================================
# STEP 2: PREPARATION
# ============================================================================

def clean_previous_builds():
    """Remove previous build artifacts"""
    print_section("Cleaning previous builds")
    
    dirs_to_remove = [
        'build',
        'dist',
        '.pyinstaller_cache',
        '__pycache__',
        '.pytest_cache',
    ]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print_info(f"Removing: {dir_name}")
            try:
                shutil.rmtree(dir_name)
                print_success(f"Removed: {dir_name}")
            except Exception as e:
                print_warning(f"Could not remove {dir_name}: {e}")

def install_pyinstaller():
    """Ensure PyInstaller is installed"""
    print_section("Setting up PyInstaller")
    
    try:
        import PyInstaller
        print_success(f"PyInstaller {PyInstaller.__version__} already installed")
        
        if PyInstaller.__version__ != PYINSTALLER_VERSION:
            print_warning(f"PyInstaller version mismatch (expected {PYINSTALLER_VERSION})")
            print_info("Updating PyInstaller...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                f'pyinstaller=={PYINSTALLER_VERSION}',
                '--upgrade', '--quiet'
            ])
            print_success(f"PyInstaller updated to {PYINSTALLER_VERSION}")
        
        return True
    except ImportError:
        print_info("Installing PyInstaller...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install',
                f'pyinstaller=={PYINSTALLER_VERSION}',
                '--quiet'
            ])
            print_success(f"PyInstaller {PYINSTALLER_VERSION} installed")
            return True
        except Exception as e:
            print_error(f"Failed to install PyInstaller: {e}")
            return False

# ============================================================================
# STEP 3: BUILD EXECUTABLE
# ============================================================================

def build_executable():
    """Build the executable using PyInstaller"""
    print_section("Building executable (this may take 15-25 minutes)")
    
    if not os.path.exists(BUILD_SPEC_FILE):
        print_error(f"Build specification file not found: {BUILD_SPEC_FILE}")
        return False
    
    print_info("Starting PyInstaller build process...")
    print_warning("This process is resource-intensive and may take a while...")
    
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        BUILD_SPEC_FILE,
        '--clean',
        '--noconfirm'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print_success("Executable build completed successfully!")
            return True
        else:
            print_error("PyInstaller build failed!")
            return False
    
    except Exception as e:
        print_error(f"Build execution error: {e}")
        return False

# ============================================================================
# STEP 4: POST-BUILD PROCESSING
# ============================================================================

def copy_additional_files():
    """Copy additional files to the distribution package"""
    print_section("Copying additional files")
    
    if not os.path.exists(PACKAGE_DIR):
        print_error(f"Package directory not found: {PACKAGE_DIR}")
        return False
    
    # Create required directories
    directories = [
        'database',
        'logs',
        'models',
    ]
    
    for dir_name in directories:
        dir_path = os.path.join(PACKAGE_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        print_success(f"Created directory: {dir_path}")
    
    # Copy README if exists
    if os.path.exists('README.txt'):
        dest = os.path.join(PACKAGE_DIR, 'README.txt')
        shutil.copy('README.txt', dest)
        print_success("Copied: README.txt")
    else:
        # Create default README
        create_default_readme(os.path.join(PACKAGE_DIR, 'README.txt'))
    
    return True

def create_default_readme(filepath):
    """Create a default README file"""
    readme_content = f"""WORKHUB AI v1.0
===============

SYSTEM REQUIREMENTS:
- Windows 7/8/10/11 (64-bit)
- 4 GB RAM (8 GB recommended)
- 2 GB free disk space (3-4 GB with models)
- Webcam/Camera (optional, for live attendance)

INSTALLATION & USAGE:
1. Extract this folder to your desired location
2. Run: workhubai_launcher.bat
3. Open browser to: http://localhost:5000
4. Complete setup at: http://localhost:5000/setup

FIRST RUN:
- First launch will download AI models (~2 GB)
- This may take 5-10 minutes on first run
- Subsequent launches will be faster

TROUBLESHOOTING:
- Port 5000 in use? Edit config.py and change port
- Camera not detected? Check Windows privacy settings
- Models not downloading? Ensure internet connection active

DATABASE:
- Database file: database/attendance.db
- Backup regularly for data safety
- Single instance only (no concurrent access)

For support, refer to the main project documentation.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    with open(filepath, 'w') as f:
        f.write(readme_content)
    
    print_success("Created: README.txt")

def create_launcher_scripts():
    """Create batch and VBS launcher scripts"""
    print_section("Creating launcher scripts")
    
    # Batch launcher (simple)
    bat_launcher = f"""@echo off
REM WorkHub AI Launcher
REM This script launches the WorkHub AI application

cd /d "%~dp0"
set PYTHONHOME=%cd%

echo Starting {PROJECT_NAME}...
echo Opening http://localhost:5000

start "" WorkHubAI.exe

REM Give it a moment to start
timeout /t 2 /nobreak

REM Open browser
start http://localhost:5000
"""
    
    bat_path = os.path.join(PACKAGE_DIR, 'workhubai_launcher.bat')
    with open(bat_path, 'w') as f:
        f.write(bat_launcher)
    
    print_success(f"Created: workhubai_launcher.bat")
    
    # VBS launcher (hidden console)
    vbs_launcher = """' WorkHub AI - Silent Launcher
' This script launches the WorkHub AI application without showing console window

CreateObject("WScript.Shell").Run CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\\WorkHubAI.exe", 0, False
"""
    
    vbs_path = os.path.join(PACKAGE_DIR, 'workhubai_runner.vbs')
    with open(vbs_path, 'w') as f:
        f.write(vbs_launcher)
    
    print_success(f"Created: workhubai_runner.vbs")
    
    return True

def create_config_template():
    """Create a config template for user customization"""
    print_section("Creating configuration template")
    
    config_template = """# Attendance System - Configuration Override File
# Uncomment and modify settings as needed

# Port Configuration
# FLASK_PORT = 5000

# Database Configuration  
# DATABASE_PATH = './database/attendance.db'

# Application Settings
# DEBUG_MODE = False
# AUTO_RELOAD = False

# Camera Settings
# CAMERA_FPS = 30
# FRAME_SKIP = 2

# Face Recognition Thresholds
# SIMILARITY_THRESHOLD = 60
# DETECTION_FRAMES = 5
"""
    
    config_path = os.path.join(PACKAGE_DIR, 'config_override.txt')
    with open(config_path, 'w') as f:
        f.write(config_template)
    
    print_success("Created: config_override.txt")
    return True

# ============================================================================
# STEP 5: VERIFICATION
# ============================================================================

def verify_build():
    """Verify the build was successful"""
    print_section("Verifying build")
    
    exe_path = Path(PACKAGE_DIR) / f"{EXECUTABLE_NAME}.exe"
    
    if not exe_path.exists():
        print_error(f"Executable not found: {exe_path}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print_success(f"Executable created: {exe_path}")
    print_info(f"Executable size: {size_mb:.1f} MB")
    
    # Check for required directories
    required_dirs = ['templates', 'static']
    for dir_name in required_dirs:
        dir_path = Path(PACKAGE_DIR) / dir_name
        if not dir_path.exists():
            print_error(f"Missing directory: {dir_path}")
            return False
        print_success(f"Directory present: {dir_name}")
    
    return True

def calculate_total_size():
    """Calculate total package size"""
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(PACKAGE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                pass
    
    total_mb = total_size / (1024 * 1024)
    total_gb = total_mb / 1024
    
    if total_gb >= 1:
        return f"{total_gb:.2f} GB ({file_count} files)"
    else:
        return f"{total_mb:.1f} MB ({file_count} files)"

# ============================================================================
# STEP 6: FINAL REPORTING
# ============================================================================

def print_build_report():
    """Print final build report"""
    print_header(f"BUILD COMPLETE - {PROJECT_NAME}")
    
    package_path = os.path.abspath(PACKAGE_DIR)
    total_size = calculate_total_size()
    
    print(f"""
{Colors.GREEN}{Colors.BOLD}[SUCCESS] BUILD SUCCESSFUL{Colors.ENDC}

[OUTPUT] Output Location:
   {package_path}

[INFO] Package Information:
   Total Size: {total_size}
   Executable: {EXECUTABLE_NAME}.exe
   
[USAGE] How to Use:
   1. Navigate to: {package_path}
   2. Double-click: attendance_launcher.bat
   3. Open browser to: http://localhost:5000
   4. Complete setup
   
[FIRST-RUN] First Run:
   - Models will auto-download (~5-10 min)
   - Ensure internet connection
   - Be patient with initial startup
   
[FILES] Files Included:
   - WorkHubAI.exe (main executable)
   - workhubai_launcher.bat (easy launcher)
   - workhubai_runner.vbs (silent launcher)
   - README.txt (instructions)
   - database/ (empty directory for database)
   - logs/ (for application logs)
   
[NEXT] Next Steps:
   1. Test the executable
   2. Create an installer (optional)
   3. Distribute to users
   
{Colors.YELLOW}[IMPORTANT] Important Notes:{Colors.ENDC}
   - First launch takes longer (models download)
   - Keep port 5000 available
   - Ensure write permissions for database
   - Test thoroughly before distribution
   
""")

def print_troubleshooting():
    """Print troubleshooting guide"""
    print(f"""
{Colors.CYAN}TROUBLESHOOTING GUIDE{Colors.ENDC}

[ERROR] Application Won't Start:
   1. Check firewall allows access to port 5000
   2. Verify Python was properly packaged
   3. Check Windows antivirus didn't quarantine
   4. Try changing port in config

[ERROR] Models Not Loading:
   1. Ensure internet connection on first run
   2. Check disk space (need ~2-3 GB free)
   3. Check user has write permissions
   4. Try manual model download

[ERROR] Camera Not Working:
   1. Check Windows privacy settings
   2. Allow app to access camera
   3. Try with different camera
   4. Verify OpenCV installation

[ERROR] Port Already in Use:
   1. Edit config.py in package directory
   2. Change FLASK_PORT value
   3. Restart application

For more help, check: EXECUTABLE_CONVERSION_TECHNICAL_ANALYSIS.md
""")

# ============================================================================
# MAIN BUILD PROCESS
# ============================================================================

def main():
    """Main build orchestration"""
    
    print_header(f"ATTENDANCE SYSTEM - EXECUTABLE BUILD")
    print_info(f"Building {PROJECT_NAME} v1.0")
    print_info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Step 1: Pre-build checks
    print("\n" + "=" * 70)
    print("PHASE 1: PRE-BUILD CHECKS".center(70))
    print("=" * 70)
    
    if not check_python_version():
        print_error("Python version check failed")
        sys.exit(1)
    
    if not check_build_environment():
        print_error("Build environment incomplete")
        sys.exit(1)
    
    if not check_dependencies():
        print_error("Python dependencies missing")
        sys.exit(1)
    
    # Step 2: Preparation
    print("\n" + "=" * 70)
    print("PHASE 2: PREPARATION".center(70))
    print("=" * 70)
    
    clean_previous_builds()
    
    if not install_pyinstaller():
        print_error("PyInstaller installation failed")
        sys.exit(1)
    
    # Step 3: Build
    print("\n" + "=" * 70)
    print("PHASE 3: BUILD EXECUTABLE".center(70))
    print("=" * 70)
    
    if not build_executable():
        print_error("Build failed")
        sys.exit(1)
    
    # Step 4: Post-build
    print("\n" + "=" * 70)
    print("PHASE 4: POST-BUILD PROCESSING".center(70))
    print("=" * 70)
    
    if not copy_additional_files():
        print_error("Failed to copy additional files")
        sys.exit(1)
    
    if not create_launcher_scripts():
        print_error("Failed to create launcher scripts")
        sys.exit(1)
    
    create_config_template()
    
    # Step 5: Verification
    print("\n" + "=" * 70)
    print("PHASE 5: VERIFICATION".center(70))
    print("=" * 70)
    
    if not verify_build():
        print_error("Build verification failed")
        sys.exit(1)
    
    # Final Report
    elapsed_time = time.time() - start_time
    print(f"\n✓ Total build time: {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    
    print_build_report()
    print_troubleshooting()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nBuild cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
