import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'upload'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Upload folder created at {UPLOAD_FOLDER}")

def allowed_file(filename, file_type):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    return False

def save_uploaded_file(file, file_type):
    if file and allowed_file(file.filename, file_type):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{unique_id}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return filename, filepath
    return None, None

def get_file_path(filename):
    return os.path.join(UPLOAD_FOLDER, filename)

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_anomaly_segments(frame_details):
    segments = []
    current_segment = None
    
    for frame in frame_details:
        if not frame['is_normal']:
            if current_segment is None:
                current_segment = {
                    'start': frame['timestamp'],
                    'end': frame['timestamp'],
                    'anomaly_type': frame['anomaly_type']
                }
            else:
                current_segment['end'] = frame['timestamp']
        else:
            if current_segment is not None:
                segments.append(current_segment)
                current_segment = None
    
    if current_segment is not None:
        segments.append(current_segment)
    
    return segments

def delete_old_files(days=7):
    current_time = datetime.now()
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        if (current_time - file_modified).days > days:
            os.remove(filepath)