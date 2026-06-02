from deepface import DeepFace
import numpy as np
import cv2
import tempfile
import os
from retinaface import RetinaFace
import time
from scipy.spatial.distance import cosine

# ================= FACE DETECTORS =================
# Primary: Haar Cascades (fast) - for real-time video
# Fallback: RetinaFace (accurate) - when Haar misses or low confidence

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Initialize RetinaFace once globally (expensive operation)
print("[INIT] Loading RetinaFace model (one-time initialization)...")
try:
    retinaface_detector = RetinaFace.build_model()
    print("[OK] RetinaFace model loaded")
except Exception as e:
    print(f"[WARN] RetinaFace loading failed: {e}")
    retinaface_detector = None

# Model cache for ensemble recognition
AVAILABLE_MODELS = ["Facenet512", "ArcFace", "VGGFace2"]
ENABLE_MULTI_MODEL_ENSEMBLE = True  # Use multiple models for better accuracy


# ================= FACE QUALITY ASSESSMENT =================
def assess_face_quality(face_img):
    """
    Assess quality of face image for recognition
    Returns: (quality_score, issues) where quality_score is 0-100
    Issues: list of detected problems (blur, angle, etc)
    """
    try:
        issues = []
        quality_score = 100
        
        if face_img is None or face_img.size == 0:
            return 0, ["Invalid image"]
        
        # 1. CHECK BLUR (Laplacian variance method)
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:  # Very blurry
            issues.append("Blur")
            quality_score -= 30
        elif laplacian_var < 200:  # Somewhat blurry
            issues.append("Slight Blur")
            quality_score -= 15
        
        # 2. CHECK BRIGHTNESS (mean intensity)
        mean_intensity = np.mean(gray)
        if mean_intensity < 50:  # Too dark
            issues.append("Too Dark")
            quality_score -= 25
        elif mean_intensity > 200:  # Too bright/overexposed
            issues.append("Overexposed")
            quality_score -= 20
        
        # 3. CHECK CONTRAST (standard deviation)
        contrast = np.std(gray)
        if contrast < 30:  # Low contrast
            issues.append("Low Contrast")
            quality_score -= 15
        
        # 4. CHECK FACE SIZE (relative to image)
        h, w = face_img.shape[:2]
        face_area_ratio = (h * w) / (160 * 160) if h > 0 and w > 0 else 0
        if h < 40 or w < 40:  # Face too small in frame
            issues.append("Face Too Small")
            quality_score -= 20
        
        quality_score = max(0, min(100, quality_score))
        return quality_score, issues
    
    except Exception as e:
        print(f"[ERROR] Quality assessment error: {e}")
        return 50, ["Assessment Error"]


# ================= FACE PREPROCESS =================
def preprocess_face(face):
    try:
        # Resize to standard size
        face = cv2.resize(face, (160, 160))

        # IMPROVED PREPROCESSING: Multi-step lighting normalization
        # 1. Convert to LAB (separates color from lighting)
        lab = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        
        # 2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # More aggressive parameters for better face illumination
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_channel = clahe.apply(l_channel)
        
        # 3. Optional: Apply bilateral filter to smooth while preserving edges
        # This reduces noise while keeping important features sharp
        l_channel = cv2.bilateralFilter(l_channel, 5, 75, 75)
        
        # 4. Merge back
        lab = cv2.merge([l_channel, a, b])
        face = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # 5. Optional: Mild histogram equalization for overall improvement
        # face = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
        # h, s, v = cv2.split(face)
        # v = cv2.equalizeHist(v)
        # face = cv2.merge([h, s, v])
        # face = cv2.cvtColor(face, cv2.COLOR_HSV2BGR)

        return face
    except Exception as e:
        print(f"[ERROR] Preprocess Error: {e}")
        return face


# ================= DETECT ALL FACES (HYBRID: Fast Haar + Accurate RetinaFace) =================
def detect_all_faces(img, use_retinaface=False):
    """
    Detect all faces in image using hybrid approach for speed + accuracy
    
    Default: Uses Haar Cascades (very fast, ~10-20ms)
    Fallback: Uses RetinaFace (slower, ~100-200ms but more accurate)
    
    Args:
        img: Input image
        use_retinaface: Force RetinaFace detection
    
    Returns: List of dictionaries with face coordinates and crops
    """
    try:
        if img is None or img.size == 0:
            return []
        
        faces_list = []
        
        # STRATEGY 1: Use fast Haar Cascades for real-time detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        haar_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(haar_faces) > 0:
            # Successfully detected with Haar - fast and good enough
            for (x, y, w, h) in haar_faces:
                face_crop = img[y:y+h, x:x+w]
                faces_list.append({
                    'facial_area': (x, y, x+w, y+h),
                    'face_crop': face_crop,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h,
                    'detector': 'Haar'
                })
            return faces_list
        
        # STRATEGY 2: Fallback to RetinaFace if Haar didn't find anything
        # This is slower but catches difficult angles/lighting
        if retinaface_detector is not None or use_retinaface:
            try:
                faces_data = RetinaFace.detect_faces(img, model=retinaface_detector)
                
                if isinstance(faces_data, dict) and len(faces_data) > 0:
                    for face_key, face_data in faces_data.items():
                        if isinstance(face_data, dict) and 'facial_area' in face_data:
                            facial_area = face_data['facial_area']
                            x1, y1, x2, y2 = facial_area
                            
                            padding = 10
                            x1 = max(0, x1 - padding)
                            y1 = max(0, y1 - padding)
                            x2 = min(img.shape[1], x2 + padding)
                            y2 = min(img.shape[0], y2 + padding)
                            
                            face_crop = img[y1:y2, x1:x2]
                            faces_list.append({
                                'facial_area': (x1, y1, x2, y2),
                                'face_crop': face_crop,
                                'x': x1,
                                'y': y1,
                                'w': x2 - x1,
                                'h': y2 - y1,
                                'detector': 'RetinaFace'
                            })
                    return faces_list
            except Exception as e:
                    print(f"[ERROR] RetinaFace fallback failed: {e}")
        
        return faces_list
    
    except Exception as e:
        print(f"[ERROR] Face detection error: {e}")
        return []


# ================= DETECT FACE (HYBRID: Fast Haar + Accurate RetinaFace) =================
def detect_face(img):
    """
    Detect largest face in image using hybrid approach
    Returns single largest face crop for processing
    """
    try:
        if img is None or img.size == 0:
            return None
        
        # Use hybrid detection
        faces = detect_all_faces(img, use_retinaface=False)
        
        if len(faces) > 0:
            # Return largest face
            largest_face = max(faces, key=lambda f: f['w'] * f['h'])
            return largest_face['face_crop']
        
        return None
    
    except Exception as e:
        print(f"[ERROR] detect_face error: {e}")
        return None


# ================= GET EMBEDDING (ENHANCED WITH QUALITY CHECK) =================
def get_embedding(face_img):
    """
    Convert face image to embedding using DeepFace with Facenet512 model
    Handles both file paths and numpy arrays
    Returns: 512-dimensional numpy array (Facenet512)
    
    Note: Using Facenet512 (512-dim) for better accuracy
    Can also use ArcFace (128-dim) for speed if needed
    """
    temp_file = None
    try:
        # ENHANCED: Check face quality first
        quality_score, issues = assess_face_quality(face_img)
        if quality_score < 30:
            print(f"[WARN] Low quality face ({quality_score}%): {issues}")
        elif quality_score < 60:
            print(f"[WARN] Fair quality face ({quality_score}%): {issues}")
        
        face_img = preprocess_face(face_img)

        # DeepFace.represent expects a file path, not numpy array
        # Save temp file if passed as numpy array
        if isinstance(face_img, np.ndarray):
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            cv2.imwrite(temp_file.name, face_img)
            face_path = temp_file.name
        else:
            face_path = face_img

        # Use Facenet512 model for better accuracy (512-dimensional)
        # Facenet512 returns 512-dimensional embeddings
        result = DeepFace.represent(
            img_path=face_path,
            model_name="Facenet512",
            detector_backend="skip",  # We already detected face
            enforce_detection=False  # Trust our detection
        )

        if not result or len(result) == 0:
            print(f"[ERROR] No embedding generated")
            return None
        
        emb = result[0]["embedding"]
        emb_array = np.array(emb, dtype=np.float32)
        
        # Verify we got expected embedding dimensions
        if len(emb_array) not in [128, 512]:
            print(f"[WARN] Expected 128 or 512-dim embedding, got {len(emb_array)}-dim")
        
        # CRITICAL FIX: L2-normalize the embedding (unit vector)
        # This is essential for proper distance calculation
        # Most face recognition systems expect normalized embeddings
        emb_norm = np.linalg.norm(emb_array)
        if emb_norm > 0:
            emb_array = emb_array / emb_norm  # Normalize to unit vector
        
        return emb_array

    except Exception as e:
        print(f"[ERROR] Embedding Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up temp file
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except:
                pass


# ================= GET MULTI-MODEL EMBEDDINGS (ENSEMBLE) =================
def get_multi_model_embeddings(face_img):
    """
    Generate embeddings using multiple models for ensemble recognition
    More accurate but slower than single model
    Returns: dict with {model_name: embedding_array}
    """
    try:
        embeddings = {}
        temp_file = None
        
        face_img = preprocess_face(face_img)
        
        if isinstance(face_img, np.ndarray):
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            cv2.imwrite(temp_file.name, face_img)
            face_path = temp_file.name
        else:
            face_path = face_img
        
        # Try each model
        for model_name in AVAILABLE_MODELS:
            try:
                result = DeepFace.represent(
                    img_path=face_path,
                    model_name=model_name,
                    detector_backend="skip",
                    enforce_detection=False
                )
                
                if result and len(result) > 0:
                    emb = np.array(result[0]["embedding"], dtype=np.float32)
                    # Normalize
                    emb_norm = np.linalg.norm(emb)
                    if emb_norm > 0:
                        emb = emb / emb_norm
                    embeddings[model_name] = emb
                    print(f"   [OK] {model_name} embedding ({len(emb)}-dim)")
            except Exception as e:
                print(f"   [WARN] {model_name} failed: {e}")
                continue
        
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        return embeddings
    
    except Exception as e:
        print(f"[ERROR] Multi-model embedding error: {e}")
        return {}


# ================= ENCODE FACE =================
def encode_face(image_path):
    try:
        img = cv2.imread(image_path)

        if img is None:
            return None

        face = detect_face(img)

        if face is None:
            return None

        return get_embedding(face)

    except Exception as e:
        print("[ERROR] Encoding Error:", e)
        return None


# ================= RECOGNITION WITH SIMILARITY (ENHANCED WITH MULTIPLE METRICS) =================
def recognize_face(frame, known_encodings, ids):
    """
    Recognize a face in the frame against known encodings
    ENHANCED: Uses both L2 distance and cosine similarity for better accuracy
    Returns (matched_intern_id, similarity_percentage) or (None, 0) if no match found
    Threshold: 60% similarity (0.40 distance for ArcFace 128-dim vectors)
    """
    try:
        face = detect_face(frame)

        if face is None:
            return None, 0
        
        # Check face quality
        quality_score, quality_issues = assess_face_quality(face)

        current = get_embedding(face)

        if current is None:
            return None, 0

        min_dist = float("inf")
        max_cosine_sim = -1.0
        matched_id = None
        matched_similarity = 0
        valid_matches = 0

        for i, known in enumerate(known_encodings):
            # Skip invalid encodings
            if known is None or len(known) == 0:
                continue
            
            # CRITICAL FIX: L2-normalize stored encodings if not already normalized
            # Old encodings may not be normalized, so normalize on-the-fly
            known_norm = np.linalg.norm(known)
            if known_norm > 1.1:  # If norm significantly > 1, it's not normalized
                known_normalized = known / known_norm
            else:
                known_normalized = known  # Already normalized or small
            
            # Ensure shapes match (both 128-dim and 512-dim supported)
            if len(known_normalized) != len(current):
                print(f"[WARN] Shape mismatch for {ids[i]}: {len(known_normalized)} vs {len(current)} dims")
                continue

            try:
                # ENHANCED: Calculate both metrics
                # 1. L2 Distance (Euclidean distance between normalized vectors)
                dist = np.linalg.norm(known_normalized - current)
                
                # 2. Cosine Similarity (angle between vectors)
                # Ranges from -1 (opposite) to 1 (identical)
                cos_sim = 1 - cosine(known_normalized, current)
                
                valid_matches += 1

                if dist < min_dist:
                    min_dist = dist
                    max_cosine_sim = cos_sim
                    matched_id = ids[i]
            except Exception as e:
                print(f"[WARN] Distance calc error for {ids[i]}: {e}")
                continue

        # Debug output
        if valid_matches > 0:
            print(f"[DEBUG] Face comparison: Best L2={min_dist:.4f}, Cosine={max_cosine_sim:.4f}, Valid={valid_matches}")
        else:
            print(f"[WARN] No valid encodings to compare against")

        # ENHANCED: Use both metrics for final decision
        # Convert L2 distance to similarity percentage
        max_distance = 1.4  # For L2-normalized vectors
        l2_similarity = max(0, 100 * (1 - min_dist / max_distance))
        
        # Convert cosine similarity to percentage (cosine ranges from -1 to 1)
        cosine_similarity_percent = max(0, 100 * (max_cosine_sim + 1) / 2)
        
        # Average the two metrics for more robust decision
        matched_similarity = (l2_similarity + cosine_similarity_percent) / 2
        
        print(f"[DEBUG] L2: {l2_similarity:.1f}%, Cosine: {cosine_similarity_percent:.1f}%, Avg: {matched_similarity:.1f}%")
        
        # ADAPTIVE THRESHOLD based on quality
        if quality_score >= 70:
            threshold = 58  # High quality faces: lower threshold
        elif quality_score >= 50:
            threshold = 60  # Medium quality: standard threshold
        else:
            threshold = 65  # Low quality: higher threshold to avoid false matches
        
        print(f"[DEBUG] Quality: {quality_score}%, Threshold: {threshold}%")

        # 60-65% SIMILARITY THRESHOLD (adaptive)
        if matched_similarity >= threshold:
            print(f"[OK] Face matched: {matched_id} (similarity: {matched_similarity:.1f}%, dist: {min_dist:.4f})")
            return matched_id, matched_similarity
        else:
            print(f"[NOMATCH] No match. Best similarity: {matched_similarity:.1f}% (threshold: {threshold}%)")

        return None, matched_similarity

    except Exception as e:
        print(f"[ERROR] Recognition Error: {e}")
        return None, 0