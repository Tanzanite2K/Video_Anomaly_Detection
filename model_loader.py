import numpy as np
import cv2
import pickle
from tensorflow.keras.models import load_model
import subprocess
import os

model = None
label_encoder = None

def convert_video_to_mp4(input_path, output_path):
    try:
        command = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            output_path
        ]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"FFmpeg conversion failed: {result.stderr.decode()}")
            return False
    except subprocess.TimeoutExpired:
        print("Video conversion timed out")
        return False
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg.")
        return False
    except Exception as e:
        print(f"Video conversion error: {str(e)}")
        return False

def load_ml_model():
    global model, label_encoder
    
    try:
        model = load_model('models/anomaly_detection_model.h5')
        print("Model loaded successfully")
        
        with open('models/label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        print("Label encoder loaded successfully")
        
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_resized = cv2.resize(img_gray, (48, 48))
    img_normalized = img_resized / 255.0
    img_reshaped = img_normalized.reshape(1, 48, 48, 1)
    return img_reshaped

def preprocess_frame(frame):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_resized = cv2.resize(frame_gray, (48, 48))
    frame_normalized = frame_resized / 255.0
    frame_reshaped = frame_normalized.reshape(1, 48, 48, 1)
    return frame_reshaped

def predict_image(image_path):
    try:
        processed_image = preprocess_image(image_path)
        
        predictions = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence_score = float(predictions[0][predicted_class_idx])
        
        predicted_label = label_encoder.inverse_transform([predicted_class_idx])[0]
        
        if predicted_label == 'NormalVideos':
            result = 'Normal'
            anomaly_type = 'Normal'
        else:
            result = 'Abnormal'
            anomaly_type = predicted_label
        
        all_scores = {label_encoder.inverse_transform([i])[0]: float(predictions[0][i]) 
                     for i in range(len(predictions[0]))}
        
        return {
            'result': result,
            'anomaly_type': anomaly_type,
            'confidence_score': confidence_score,
            'all_scores': all_scores
        }
    
    except Exception as e:
        print(f"Error in predict_image: {str(e)}")
        raise

def predict_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_details = []
        frame_count = 0
        analyzed_count = 0
        abnormal_count = 0
        
        anomaly_votes = {}
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % 10 == 0:
                processed_frame = preprocess_frame(frame)
                
                predictions = model.predict(processed_frame, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                confidence_score = float(predictions[0][predicted_class_idx])
                
                predicted_label = label_encoder.inverse_transform([predicted_class_idx])[0]
                
                is_normal = (predicted_label == 'NormalVideos')
                
                if not is_normal:
                    abnormal_count += 1
                    anomaly_votes[predicted_label] = anomaly_votes.get(predicted_label, 0) + 1
                
                timestamp = frame_count / fps if fps > 0 else 0
                
                frame_details.append({
                    'frame_number': frame_count,
                    'timestamp': timestamp,
                    'anomaly_type': 'Normal' if is_normal else predicted_label,
                    'confidence_score': confidence_score,
                    'is_normal': is_normal
                })
                
                analyzed_count += 1
            
            frame_count += 1
        
        cap.release()
        
        if abnormal_count > analyzed_count / 2:
            overall_result = 'Abnormal'
            dominant_anomaly = max(anomaly_votes.items(), key=lambda x: x[1])[0] if anomaly_votes else 'Unknown'
        else:
            overall_result = 'Normal'
            dominant_anomaly = 'Normal'
        
        overall_confidence = abnormal_count / analyzed_count if analyzed_count > 0 else 0
        
        return {
            'result': overall_result,
            'anomaly_type': dominant_anomaly,
            'confidence_score': overall_confidence,
            'total_frames': total_frames,
            'analyzed_frames': analyzed_count,
            'abnormal_frames_count': abnormal_count,
            'frame_details': frame_details
        }
    
    except Exception as e:
        print(f"Error in predict_video: {str(e)}")
        raise