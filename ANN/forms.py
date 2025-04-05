from django import forms

class DataInputForm(forms.Form):
    # Set 1
    radius1 = forms.FloatField()
    texture1 = forms.FloatField()
    perimeter1 = forms.FloatField()
    area1 = forms.FloatField()
    smoothness1 = forms.FloatField()
    compactness1 = forms.FloatField()
    concavity1 = forms.FloatField()
    concave_points1 = forms.FloatField()
    symmetry1 = forms.FloatField()
    fractal_dimension1 = forms.FloatField()

    # Set 2
    radius2 = forms.FloatField()
    texture2 = forms.FloatField()
    perimeter2 = forms.FloatField()
    area2 = forms.FloatField()
    smoothness2 = forms.FloatField()
    compactness2 = forms.FloatField()
    concavity2 = forms.FloatField()
    concave_points2 = forms.FloatField()
    symmetry2 = forms.FloatField()
    fractal_dimension2 = forms.FloatField()

    # Set 3
    radius3 = forms.FloatField()
    texture3 = forms.FloatField()
    perimeter3 = forms.FloatField()
    area3 = forms.FloatField()
    smoothness3 = forms.FloatField()
    compactness3 = forms.FloatField()
    concavity3 = forms.FloatField()
    concave_points3 = forms.FloatField()
    symmetry3 = forms.FloatField()
    fractal_dimension3 = forms.FloatField()
