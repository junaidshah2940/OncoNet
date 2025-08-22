from django.db import models

TARGET_CHOICES = (
    ("M", "Malignant"),
    ("B", "Benign"),
)

class BC(models.Model):
    patient_id = models.IntegerField(unique=True)

    # feature set 1
    radius1 = models.FloatField()
    texture1 = models.FloatField()
    perimeter1 = models.FloatField()
    area1 = models.FloatField()
    smoothness1 = models.FloatField()
    compactness1 = models.FloatField()
    concavity1 = models.FloatField()
    concave_points1 = models.FloatField()
    symmetry1 = models.FloatField()
    fractal_dimension1 = models.FloatField()

    # feature set 2
    radius2 = models.FloatField()
    texture2 = models.FloatField()
    perimeter2 = models.FloatField()
    area2 = models.FloatField()
    smoothness2 = models.FloatField()
    compactness2 = models.FloatField()
    concavity2 = models.FloatField()
    concave_points2 = models.FloatField()
    symmetry2 = models.FloatField()
    fractal_dimension2 = models.FloatField()

    # feature set 3
    radius3 = models.FloatField()
    texture3 = models.FloatField()
    perimeter3 = models.FloatField()
    area3 = models.FloatField()
    smoothness3 = models.FloatField()
    compactness3 = models.FloatField()
    concavity3 = models.FloatField()
    concave_points3 = models.FloatField()
    symmetry3 = models.FloatField()
    fractal_dimension3 = models.FloatField()

    target = models.CharField(max_length=1, choices=TARGET_CHOICES, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id}"

class BlockchainRecord(models.Model):
    patient_id = models.CharField(max_length=100)
    contract_address = models.CharField(max_length=42)
    abi = models.TextField()
    bytecode = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.contract_address}"
