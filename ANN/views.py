from django.shortcuts import render
from .forms import DataInputForm, DataInputFileForm, DataInputTrainingForm
from .model import classify_data, train_model
from BC.blockchain import record_classification, record_model_parameters
from .models import BlockchainRecord
import json
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
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
            try:
                data = form.cleaned_data
                
                model_params = train_model(data)
                
                blockchain_result = record_model_parameters(
                    model_params['params_base64'],
                    model_params['timestamp']
                )
                
                context = {
                    'success': True,
                    'contract_address': blockchain_result['contract_address'],
                    'transaction_hash': blockchain_result['transaction_hash'],
                    'timestamp': model_params['timestamp']
                }
                
                messages.success(request, 'Model trained and parameters stored on blockchain successfully!')
                return render(request, 'training_result.html', context)
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                context = {'success': False, 'error': str(e)}
                return render(request, 'training_result.html', context)
    else:
        form = DataInputTrainingForm()
    
    return render(request, 'form.html', {'form': form})


def data_file_form_view_training(request):
    if request.method == 'POST':
        form = DataInputFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['file']
                df = pd.read_excel(excel_file)
                
                blockchain_results = []
                
                for i in range(df.shape[0]):
                    row = df.iloc[i].to_dict()
                    model_params = train_model(row)
                    
                    blockchain_result = record_model_parameters(
                        model_params['params_base64'],
                        model_params['timestamp']
                    )
                    
                    blockchain_results.append({
                        'row': i + 1,
                        'contract_address': blockchain_result['contract_address'],
                        'transaction_hash': blockchain_result['transaction_hash']
                    })
                
                context = {
                    'success': True,
                    'total_rows': df.shape[0],
                    'blockchain_results': blockchain_results,
                    'last_timestamp': model_params['timestamp']
                }
                
                messages.success(request, f'Model trained on {df.shape[0]} rows and parameters stored on blockchain!')
                return render(request, 'training_result.html', context)
                
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                context = {'success': False, 'error': str(e)}
                return render(request, 'training_result.html', context)
    else:
        form = DataInputFileForm()
    
    return render(request, 'file-form.html', {'form': form})