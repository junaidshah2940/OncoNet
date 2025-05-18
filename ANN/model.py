from keras.models import load_model
from django.conf import settings
import os
import numpy as np

model_path = os.path.join(settings.BASE_DIR, 'assets', 'classifier_model.h5')

model = load_model(model_path)

def classify_data(data):
    features = np.array([
        data['radius1'], data['texture1'], data['perimeter1'], data['area1'], data['smoothness1'],
        data['compactness1'], data['concavity1'], data['concave_points1'], data['symmetry1'], data['fractal_dimension1'],
        data['radius2'], data['texture2'], data['perimeter2'], data['area2'], data['smoothness2'],
        data['compactness2'], data['concavity2'], data['concave_points2'], data['symmetry2'], data['fractal_dimension2'],
        data['radius3'], data['texture3'], data['perimeter3'], data['area3'], data['smoothness3'],
        data['compactness3'], data['concavity3'], data['concave_points3'], data['symmetry3'], data['fractal_dimension3']
    ]).reshape(1, -1)

    prediction = model.predict(features)
    return 'Malignant' if prediction[0][0] > 0.5 else 'Benign'
