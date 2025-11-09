import sys
import json
import numpy as np
import pickle
import cv2
from numpy.linalg import norm
import os
import warnings

# Tắt tất cả warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import TensorFlow và tắt logging
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(0)

from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.layers import GlobalMaxPooling2D
from sklearn.neighbors import NearestNeighbors

# Redirect stderr để không in ra console
sys.stderr = open(os.devnull, 'w')

try:
    # Load pre-computed features
    feature_list = np.array(pickle.load(open("featurevector.pkl", "rb")))
    filenames = pickle.load(open("filenames.pkl", "rb"))

    # Load model
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    model.trainable = False

    model = tf.keras.Sequential([
        model,
        GlobalMaxPooling2D()
    ])

    def extract_feature(img_path, model):
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Could not read image: {img_path}")
        img = cv2.resize(img, (224, 224))
        img = np.array(img)
        expand_img = np.expand_dims(img, axis=0)
        pre_img = preprocess_input(expand_img)
        result = model.predict(pre_img, verbose=0).flatten()
        normalized = result / norm(result)
        return normalized

    def recommend(features, feature_list):
        neighbors = NearestNeighbors(n_neighbors=6, algorithm="brute", metric="euclidean")
        neighbors.fit(feature_list)
        distance, indices = neighbors.kneighbors([features])
        return indices, distance

    if len(sys.argv) < 2:
        result = {"error": "No image path provided"}
    else:
        image_path = sys.argv[1]
        
        # Extract features from uploaded image
        features = extract_feature(image_path, model)
        
        # Get recommendations
        indices, distances = recommend(features, feature_list)
        
        # Prepare results
        recommendations = []
        for i in range(len(indices[0])):
            # Chuẩn hóa đường dẫn
            image_path = filenames[indices[0][i]]
            # Loại bỏ các ký tự đặc biệt và chuẩn hóa
            image_path = image_path.replace('\\', '/')
            
            # Đảm bảo đường dẫn không có ký tự lạ
            image_path = image_path.strip()
            
            recommendations.append({
                "image": image_path,
                "similarity": float(1 / (1 + distances[0][i]))
            })
        
        result = {
            "recommendations": recommendations
        }
    
    # Restore stderr để in JSON
    sys.stderr = sys.__stderr__
    
    # In ONLY JSON, không có gì khác
    print(json.dumps(result))
    
except Exception as e:
    sys.stderr = sys.__stderr__
    print(json.dumps({"error": str(e)}))
    sys.exit(1)