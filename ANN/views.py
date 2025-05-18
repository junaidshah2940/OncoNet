from django.shortcuts import render
from .forms import DataInputForm
from .model import classify_data
from BC.blockchain import record_classification
# from BC.deploy import deploy_contract

def data_form_view(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = classify_data(data)

            # Blockchain hash + store
            patient_id = data['patient_id']

            # Store the result in the blockchain
            res, contract_address, abi, bytecode = record_classification(patient_id, result)

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
