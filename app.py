from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import timedelta, datetime


import database
import model_loader
import utils

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

database.init_db()
utils.ensure_upload_folder()
model_loader.load_ml_model()

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if database.create_user(username, email, password):
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists', 'error')
            return redirect(url_for('signup'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = database.verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    return render_template('dashboard.html', username=username)

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory('upload', filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/image', methods=['GET', 'POST'])
@login_required
def image_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('image_upload'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('image_upload'))
        
        filename, filepath = utils.save_uploaded_file(file, 'image')
        
        if filename:
            prediction = model_loader.predict_image(filepath)
            
            user_id = session.get('user_id')
            prediction_id = database.save_prediction(
                user_id=user_id,
                filename=filename,
                file_type='image',
                prediction_result=prediction['result'],
                anomaly_type=prediction['anomaly_type'],
                anomaly_score=prediction['confidence_score']
            )
            
            session['last_prediction'] = {
                'prediction_id': prediction_id,
                'filename': filename,
                'file_type': 'image',
                'result': prediction['result'],
                'anomaly_type': prediction['anomaly_type'],
                'confidence_score': prediction['confidence_score'],
                'detection_time': datetime.now().strftime("%d %b %Y %H:%M")
            }
            
            return redirect(url_for('results'))
        else:
            flash('Invalid file format. Please upload an image file.', 'error')
            return redirect(url_for('image_upload'))
    
    return render_template('image.html')

@app.route('/video', methods=['GET', 'POST'])
@login_required
def video_upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(url_for('video_upload'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('video_upload'))
        
        filename, filepath = utils.save_uploaded_file(file, 'video')
        
        if filename:
            converted_filename = filename.rsplit('.', 1)[0] + '_converted.mp4'
            converted_filepath = os.path.join('upload', converted_filename)
            
            print(f"Converting video: {filename}")
            conversion_success = model_loader.convert_video_to_mp4(filepath, converted_filepath)
            
            if conversion_success and os.path.exists(converted_filepath):
                print(f"Video converted successfully: {converted_filename}")
                video_to_analyze = converted_filepath
                final_filename = converted_filename
            else:
                print("Conversion failed, using original video")
                video_to_analyze = filepath
                final_filename = filename
            
            prediction = model_loader.predict_video(video_to_analyze)
            
            frame_details_json = json.dumps(prediction['frame_details'])
            
            user_id = session.get('user_id')
            prediction_id = database.save_prediction(
                user_id=user_id,
                filename=final_filename,
                file_type='video',
                prediction_result=prediction['result'],
                anomaly_type=prediction['anomaly_type'],
                anomaly_score=prediction['confidence_score'],
                frame_details=frame_details_json
            )
            
            segments = utils.get_anomaly_segments(prediction['frame_details'])
            
            session['last_prediction'] = {
                'prediction_id': prediction_id,
                'filename': final_filename,
                'file_type': 'video',
                'result': prediction['result'],
                'anomaly_type': prediction['anomaly_type'],
                'confidence_score': prediction['confidence_score'],
                'detection_time': datetime.now().strftime("%d %b %Y %H:%M"),
                'total_frames': prediction['total_frames'],
                'analyzed_frames': prediction['analyzed_frames'],
                'abnormal_frames_count': prediction['abnormal_frames_count'],
                'frame_details': prediction['frame_details'],
                'segments': segments
            }
            
            return redirect(url_for('results'))
        else:
            flash('Invalid file format. Please upload a video file.', 'error')
            return redirect(url_for('video_upload'))
    
    return render_template('video.html')

@app.route('/results')
@login_required
def results():
    prediction_data = session.get('last_prediction')
    
    if not prediction_data:
        flash('No prediction data found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('results.html', prediction=prediction_data)

@app.route('/history')
@login_required
def history():
    user_id = session.get('user_id')
    predictions = database.get_user_predictions(user_id)
    
    predictions_list = []
    for pred in predictions:
        predictions_list.append({
            'id': pred['id'],
            'filename': pred['filename'],
            'file_type': pred['file_type'],
            'result': pred['prediction_result'],
            'anomaly_type': pred['anomaly_type'],
            'confidence_score': pred['anomaly_score'],
            'created_at': pred['created_at']
        })
    
    return render_template('history.html', predictions=predictions_list)

@app.route('/view_prediction/<int:prediction_id>')
@login_required
def view_prediction(prediction_id):
    prediction = database.get_prediction_by_id(prediction_id)
    
    if not prediction or prediction['user_id'] != session.get('user_id'):
        flash('Prediction not found', 'error')
        return redirect(url_for('history'))
    
    prediction_data = {
        'prediction_id': prediction['id'],
        'filename': prediction['filename'],
        'file_type': prediction['file_type'],
        'result': prediction['prediction_result'],
        'anomaly_type': prediction['anomaly_type'],
        'confidence_score': prediction['anomaly_score']
    }
    
    if prediction['file_type'] == 'video' and prediction['frame_details']:
        frame_details = json.loads(prediction['frame_details'])
        prediction_data['frame_details'] = frame_details
        prediction_data['total_frames'] = len(frame_details) * 10
        prediction_data['analyzed_frames'] = len(frame_details)
        abnormal_count = sum(1 for f in frame_details if not f['is_normal'])
        prediction_data['abnormal_frames_count'] = abnormal_count
        prediction_data['segments'] = utils.get_anomaly_segments(frame_details)
    
    session['last_prediction'] = prediction_data
    return redirect(url_for('results'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)