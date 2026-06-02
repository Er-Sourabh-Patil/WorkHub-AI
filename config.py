import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# HANDLE PYINSTALLER PATHS
# ============================================================================

def get_base_dir():
    """Get the correct base directory for bundled files (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable (PyInstaller)
        return sys._MEIPASS
    else:
        # Running as normal Python script
        return os.path.abspath(os.path.dirname(__file__))

BASE_DIR = get_base_dir()

# Database
DATABASE = os.path.join(BASE_DIR, "database.db")

# Upload folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")
CAPTURED_FOLDER = os.path.join(BASE_DIR, "captured_faces")

# Security - Use environment variable for SECRET_KEY
# IMPORTANT: Change this in production!
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-12345")

# Session config
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# ================= FACE RECOGNITION CONFIG (ENHANCED) =================

# Base similarity threshold (adaptive based on quality)
FACE_RECOGNITION_THRESHOLD = 60  # Base threshold (%)

# Adaptive thresholds based on face quality
HIGH_QUALITY_THRESHOLD = 58    # Confidence > 70% quality
MEDIUM_QUALITY_THRESHOLD = 60  # Confidence 50-70% quality
LOW_QUALITY_THRESHOLD = 65     # Confidence < 50% quality

# Attendance marking parameters
DETECTION_STABILITY_FRAMES = 5  # Frames to confirm detection before marking attendance

# Face quality assessment thresholds
MIN_QUALITY_SCORE = 30          # Minimum acceptable quality (0-100)
BLUR_THRESHOLD = 100            # Laplacian variance threshold for blur detection
MIN_BRIGHTNESS = 50             # Minimum mean intensity
MAX_BRIGHTNESS = 200            # Maximum mean intensity
MIN_CONTRAST = 30               # Minimum standard deviation for contrast

# Multi-model ensemble recognition
ENABLE_MULTI_MODEL_ENSEMBLE = False  # Set to True for higher accuracy (slower)
AVAILABLE_MODELS = ["Facenet512", "ArcFace", "VGGFace2"]  # Models to use in ensemble

# Detection strategy
USE_RETINAFACE_FALLBACK = True   # Fallback to RetinaFace when Haar fails
FRAME_SKIP_INTERVAL = 2          # Process every nth frame (2 = every 2nd frame)

# Directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CAPTURED_FOLDER, exist_ok=True)