# -*- mode: python ; coding: utf-8 -*-
# PyInstaller Build Specification for Attendance System
# Generated: May 28, 2026
# This file configures how PyInstaller packages the Flask attendance application

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# ============================================================================
# CONFIGURATION: Collect data files from packages
# ============================================================================

datas = [
    # Include HTML templates
    ('templates', 'templates'),
    
    # Include static assets (CSS, JS, images)
    ('static', 'static'),
    
    # Include upload directory (may be empty initially)
    ('static/uploads', 'static/uploads'),
]

print("[DEBUG] Collecting TensorFlow data files...")
datas += collect_data_files('tensorflow')

print("[DEBUG] Collecting DeepFace data files...")
datas += collect_data_files('deepface')

print("[DEBUG] Data files to include:")
for src, dst in datas:
    print(f"  {src} -> {dst}")

# ============================================================================
# CONFIGURATION: Hidden imports for problematic libraries
# ============================================================================

# These are imports that PyInstaller cannot automatically detect
hiddenimports = [
    # Core dependencies
    'flask',
    'werkzeug',
    'werkzeug.security',
    
    # Computer vision
    'cv2',
    'cv2.cv2',
    'PIL',
    'PIL.Image',
    
    # AI/ML - The heavy ones
    'tensorflow',
    'tensorflow.python',
    'tensorflow.python.keras',
    'tensorflow.python.keras.backend',
    'tensorflow.python.platform',
    'tensorflow.python.util',
    'tensorflow_core',
    'tensorflow_core.python',
    
    'deepface',
    'deepface.commons',
    'deepface.models',
    
    'retinaface',
    'retina_face',
    
    # Data processing
    'numpy',
    'scipy',
    'scipy.spatial',
    'scipy.spatial.distance',
    'pandas',
    
    # Other utilities
    'h5py',
    'protobuf',
    'requests',
    'sqlite3',
]

# Add all submodules from TensorFlow (comprehensive)
print("[DEBUG] Collecting TensorFlow submodules...")
try:
    tf_submodules = collect_submodules('tensorflow')
    hiddenimports += tf_submodules
    print(f"  Added {len(tf_submodules)} TensorFlow submodules")
except Exception as e:
    print(f"  Warning: Could not collect TensorFlow submodules: {e}")

# Add all submodules from DeepFace
print("[DEBUG] Collecting DeepFace submodules...")
try:
    deepface_submodules = collect_submodules('deepface')
    hiddenimports += deepface_submodules
    print(f"  Added {len(deepface_submodules)} DeepFace submodules")
except Exception as e:
    print(f"  Warning: Could not collect DeepFace submodules: {e}")

# Add all submodules from OpenCV
print("[DEBUG] Collecting OpenCV submodules...")
try:
    cv2_submodules = collect_submodules('cv2')
    hiddenimports += cv2_submodules
    print(f"  Added {len(cv2_submodules)} OpenCV submodules")
except Exception as e:
    print(f"  Warning: Could not collect OpenCV submodules: {e}")

# Remove duplicates
hiddenimports = list(set(hiddenimports))
print(f"\n[DEBUG] Total hidden imports: {len(hiddenimports)}")

# ============================================================================
# CONFIGURATION: Analysis stage
# ============================================================================

a = Analysis(
    ['app.py'],  # Entry point
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],  # Custom hooks directory (optional)
    hooksconfig={},
    runtime_hooks=[],  # Custom runtime hooks
    excludedimports=[
        # Exclude modules that cause issues
        'django',
        'matplotlib',
        'ipython',
        'jupyter',
        'pytest',
    ],
    noarchive=False,
)

# ============================================================================
# CONFIGURATION: Python Archive (PYZ)
# ============================================================================

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ============================================================================
# CONFIGURATION: Executable
# ============================================================================

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WorkHubAI',  # Output executable name
    debug=False,  # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression if available
    console=True,  # Show console window (helpful for debugging)
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ============================================================================
# CONFIGURATION: Collection (onedir = folder-based distribution)
# ============================================================================

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WorkHubAI'  # Output directory name
)

# ============================================================================
# NOTES FOR DEVELOPERS
# ============================================================================
# 
# Build Command:
#   pyinstaller build_attendance.spec --clean --noconfirm
#
# Output Location:
#   dist/attendance/  (folder-based distribution)
#
# Files to Manually Add After Build:
#   1. Pre-trained models (if bundling):
#      - Copy ~/.deepface/weights to dist/attendance/deepface_models
#   
#   2. Launcher scripts:
#      - Create attendance_launcher.bat
#      - Create attendance_runner.vbs (for hidden console)
#
# Environment Variables (set before building if needed):
#   - PYTHONOPTIMIZE: Set to 1 or 2 for optimization
#   - FFLAGS: Set for compiler optimization
#
# Build Time: ~15-25 minutes
# Final Size: ~1.1-1.5 GB
#
# ============================================================================
