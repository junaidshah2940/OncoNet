from django.shortcuts import render
from .forms import DataInputForm

# Create your views here.

def data_form_view(request):
    if request.method == 'POST':
        form = DataInputForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = DataInputForm()
    return render(request, 'form.html', {'form': form})