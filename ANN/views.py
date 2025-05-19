from django.shortcuts import render
from .forms import DataInputForm
from .model import classify_data
from BC.blockchain import record_classification
from .models import BlockchainRecord
import json

def data_form_view(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = classify_data(data)

            form.save()

            # Blockchain hash + store
            patient_id = data['patient_id']

            # Store the result in the blockchain
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
