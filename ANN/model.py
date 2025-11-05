from keras.models import load_model
from django.conf import settings
import os
import numpy as np
import json
import base64
import io
from datetime import datetime

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
    return 'Malignant' if prediction[0][0] < 0.5 else 'Benign'


def train_model(data):
    print(data)
    features = np.array([
        data['radius1'], data['texture1'], data['perimeter1'], data['area1'], data['smoothness1'],
        data['compactness1'], data['concavity1'], data['concave_points1'], data['symmetry1'], data['fractal_dimension1'],
        data['radius2'], data['texture2'], data['perimeter2'], data['area2'], data['smoothness2'],
        data['compactness2'], data['concavity2'], data['concave_points2'], data['symmetry2'], data['fractal_dimension2'],
        data['radius3'], data['texture3'], data['perimeter3'], data['area3'], data['smoothness3'],
        data['compactness3'], data['concavity3'], data['concave_points3'], data['symmetry3'], data['fractal_dimension3']
    ]).reshape(1, -1)

    target = np.array([data['target']])
    if data['target'] == 'M':
        target = np.array([4])
    else:
        target = np.array([2])

    model.fit(features, target, epochs=50, batch_size=32)

    static_dirs = getattr(settings, "STATICFILES_DIRS", [])
    if static_dirs:
        assets_root = static_dirs[0]
    else:
        assets_root = os.path.join(settings.BASE_DIR, "assets")
    os.makedirs(assets_root, exist_ok=True)
    out_path = os.path.join(assets_root, "classifier_model.h5")
    model.save(out_path)

    model_params = {
        'weights': [],
        'architecture': model.to_json()
    }
    
    for layer in model.layers:
        layer_weights = layer.get_weights()
        if layer_weights: 
            model_params['weights'].append({
                'layer_name': layer.name,
                'weights': [w.tolist() for w in layer_weights]
            })
    
    buffer = io.BytesIO()
    model.save(buffer, save_format='h5')
    model_bytes = buffer.getvalue()
    params_base64 = base64.b64encode(model_bytes).decode('utf-8')
    
    return {
        'params_json': json.dumps(model_params),
        'params_base64': params_base64,
        'timestamp': datetime.now().isoformat()
    }