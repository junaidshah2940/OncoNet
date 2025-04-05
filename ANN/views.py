from django.shortcuts import render
from .forms import DataInputForm
from .model import classify_data
from BC.blockchain import record_classification
from BC.deploy import deploy_contract

def data_form_view(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = classify_data(data)

            # Blockchain hash + store
            patient_id = data['patient_id']

            # Use deploy_contract to load the ABI and address if not already loaded
            contract_address, abi = deploy_contract()

            # Store the result in the blockchain
            tx_hash = record_classification(patient_id, result)

            return render(request, 'result.html', {
                'result': result,
                'tx_hash': tx_hash,
                'contract_address': contract_address,
                'patient_id': patient_id,
            })
    else:
        form = DataInputForm()
    return render(request, 'form.html', {'form': form})
