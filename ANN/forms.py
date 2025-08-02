from django import forms
from .models import BC

class DataInputForm(forms.ModelForm):
    class Meta:
        model = BC
        fields = [
            "patient_id", "radius1", "texture1", "perimeter1", "area1", "smoothness1", "compactness1", "concavity1", "concave_points1", "symmetry1", "fractal_dimension1",
            "radius2", "texture2", "perimeter2", "area2", "smoothness2", "compactness2", "concavity2", "concave_points2", "symmetry2", "fractal_dimension2",
            "radius3", "texture3", "perimeter3", "area3", "smoothness3", "compactness3", "concavity3", "concave_points3", "symmetry3", "fractal_dimension3",
        ]

    def __init__(self, *args, **kwargs):
        super(DataInputForm, self).__init__(*args, **kwargs)
        
        placeholder_map = {
            "patient_id": "e.g., 84000000",
            "radius1": "e.g., 17.99",
            "texture1": "e.g., 10.38",
            "perimeter1": "e.g., 122.8",
            "area1": "e.g., 1001.0",
            "smoothness1": "e.g., 0.1184",
            "compactness1": "e.g., 0.2776",
            "concavity1": "e.g., 0.3001",
            "concave_points1": "e.g., 0.1471",
            "symmetry1": "e.g., 0.2419",
            "fractal_dimension1": "e.g., 0.07871",

            "radius2": "e.g., 17.99",
            "texture2": "e.g., 10.38",
            "perimeter2": "e.g., 122.8",
            "area2": "e.g., 1001.0",
            "smoothness2": "e.g., 0.1184",
            "compactness2": "e.g., 0.2776",
            "concavity2": "e.g., 0.3001",
            "concave_points2": "e.g., 0.1471",
            "symmetry2": "e.g., 0.2419",
            "fractal_dimension2": "e.g., 0.07871",

            "radius3": "e.g., 17.99",
            "texture3": "e.g., 10.38",
            "perimeter3": "e.g., 122.8",
            "area3": "e.g., 1001.0",
            "smoothness3": "e.g., 0.1184",
            "compactness3": "e.g., 0.2776",
            "concavity3": "e.g., 0.3001",
            "concave_points3": "e.g., 0.1471",
            "symmetry3": "e.g., 0.2419",
            "fractal_dimension3": "e.g., 0.07871",
        }

        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = placeholder_map.get(field, '')
            self.fields[field].widget.attrs['class'] = 'form-input' 

class DataInputFileForm(forms.Form):
    file = forms.FileField(label="Upload Excel File")