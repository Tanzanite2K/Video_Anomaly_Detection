# Video Anomaly Detection in Surveillance Environments

## Overview

This project presents a Large-Scale Deep Learning Framework for Video Anomaly Detection in Surveillance Environments using weakly supervised learning techniques. The system is designed to automatically identify abnormal activities from surveillance videos by learning temporal and spatial patterns without requiring frame-level annotations.

The framework combines Multiple Instance Learning (MIL), I3D (Inflated 3D ConvNet), and MLP-based anomaly scoring to perform binary anomaly detection and multi-class classification across multiple anomaly categories.

---

## Features

* Weakly Supervised Video Anomaly Detection
* Multiple Instance Learning (MIL)
* I3D-based Spatio-Temporal Feature Extraction
* MLP-based Anomaly Classification
* Binary Anomaly Detection
* Multi-Class Classification (13 Anomaly Categories)
* Timestamp-Based Anomaly Localization
* Real-Time Video Processing Pipeline
* Frame Extraction & Temporal Segmentation
* Anomaly Scoring & Visualization
* Web-Based Interface for Detection

---

## Tech Stack

### Languages & Frameworks

* Python
* PyTorch
* TensorFlow
* Flask

### Libraries

* OpenCV
* NumPy
* Pandas
* Scikit-learn
* Matplotlib

### Frontend

* HTML
* CSS
* JavaScript

---

## Deep Learning Architecture

The proposed framework utilizes:

### 1. I3D (Inflated 3D ConvNet)

Used for extracting rich spatio-temporal features from surveillance video clips.

### 2. Multiple Instance Learning (MIL)

Enables weakly supervised learning by training the model using video-level labels instead of frame-level annotations.

### 3. MLP (Multi-Layer Perceptron)

Used for anomaly score prediction and final classification.

---

## Pipeline

```text
Video Input
   ↓
Frame Extraction
   ↓
Temporal Segmentation
   ↓
I3D Feature Extraction
   ↓
MIL Training
   ↓
MLP Anomaly Scoring
   ↓
Binary & Multi-Class Classification
   ↓
Timestamp Localization
   ↓
Output Visualization
```

---

## Dataset

The model is trained and evaluated on large-scale surveillance video datasets containing both normal and abnormal activities.

### Supported Anomaly Categories

* Abuse
* Arrest
* Arson
* Assault
* Burglary
* Explosion
* Fighting
* Robbery
* Shooting
* Shoplifting
* Stealing
* Vandalism
* Road Accidents

---

## Performance

* High anomaly detection accuracy
* Efficient temporal localization
* Robust performance on complex surveillance environments
* Effective learning using weak supervision

---

## Project Structure

```text
Video_Anomaly_Detection/
│
├── dataset/
├── models/
├── static/
├── templates/
├── uploads/
├── outputs/
├── app.py
├── train.py
├── predict.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Tanzanite2K/Video_Anomaly_Detection.git
cd Video_Anomaly_Detection
```

### Create Virtual Environment

```bash
python -m venv .venv311
```

### Activate Environment

#### Windows

```bash
.\.venv311\Scripts\Activate.ps1
```

#### Linux/Mac

```bash
source .venv311/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

### Train Model

```bash
python train.py
```

### Run Detection

```bash
python predict.py
```

### Start Flask Server

```bash
python app.py
```

---

## Research Contribution

This project focuses on improving large-scale surveillance intelligence through deep learning-based anomaly detection using weak supervision. The framework reduces dependency on expensive frame-level annotations while maintaining effective anomaly localization and classification performance.

---

## Interface 

<img width="1901" height="898" alt="image" src="https://github.com/user-attachments/assets/db574adb-5b68-4e22-9dac-125bab0a5edd" />
<img width="1899" height="904" alt="image" src="https://github.com/user-attachments/assets/28936185-570c-4ff0-989c-d3f856a92117" />
<img width="1502" height="913" alt="image" src="https://github.com/user-attachments/assets/e3634eb2-1c56-417f-8856-5de82275e0b9" />
<img width="1201" height="783" alt="image" src="https://github.com/user-attachments/assets/b1b335df-4127-441e-a7a4-caceafaf7371" />
<img width="1402" height="905" alt="image" src="https://github.com/user-attachments/assets/b8f392c2-d589-4e69-a94c-a2d659ab4e5d" />
<img width="645" height="843" alt="image" src="https://github.com/user-attachments/assets/636a14bc-f86c-4e80-895e-dc811f9c60e1" />


## Future Enhancements

* Real-Time CCTV Stream Detection
* Transformer-Based Temporal Modeling
* Attention Mechanisms for Improved Localization
* Cloud Deployment
* Edge AI Optimization
* Mobile Monitoring Dashboard

---

## Author

Karri Pavan Prabhas

---

## GitHub Repository

