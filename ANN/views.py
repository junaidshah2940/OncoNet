from django.shortcuts import render
from .forms import DataInputForm, DataInputFileForm, DataInputTrainingForm
from .model import classify_data, train_model
from BC.blockchain import record_classification
from .models import BlockchainRecord
import json
import pandas as pd

def data_form_view(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = classify_data(data)

            form.save()

            patient_id = data['patient_id']

            res, contract_address, abi, bytecode = record_classification(patient_id, result)


            BlockchainRecord.objects.create(
                patient_id=patient_id,
                contract_address=contract_address,
                abi=json.dumps(abi),
                bytecode=bytecode
            )


            return render(request, 'result.html', {
                'result': result,
                'res': res,
                'contract_address': contract_address,
                'patient_id': patient_id,
                'abi': abi,
                "bytecode": bytecode
            })
    else:
        form = DataInputForm()
    return render(request, 'form.html', {'form': form})

def data_file_form_view(request):
    if request.method == 'POST':
        form = DataInputFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)

            first_row = df.iloc[0].to_dict()
            result = classify_data(first_row)

            patient_id = first_row['patient_id']

            res, contract_address, abi, bytecode = record_classification(patient_id, result)

            BlockchainRecord.objects.create(
                patient_id=patient_id,
                contract_address=contract_address,
                abi=json.dumps(abi),
                bytecode=bytecode
            )

            return render(request, 'result.html', {
                'result': result,
                'res': res,
                'contract_address': contract_address,
                'patient_id': patient_id,
                'abi': abi,
                "bytecode": bytecode
            })
    else:
        form = DataInputFileForm()
    return render(request, 'file-form.html', {'form': form})


def data_form_view_training(request):
    if request.method == 'POST':
        form = DataInputTrainingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            train_model(data)
            return render(request, 'training_result.html')
    else:
        form = DataInputTrainingForm()
    return render(request, 'form.html', {'form': form})

def data_file_form_view_training(request):
    if request.method == 'POST':
        form = DataInputFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)

            for i in range(df.shape[0]):
                row = df.iloc[i].to_dict()
                train_model(row)

            return render(request, 'training_result.html')
    else:
        form = DataInputFileForm()
    return render(request, 'file-form.html', {'form': form})