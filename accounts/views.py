from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .decorators import doctor_required

from .forms import SignUpForm, LoginForm
from .models import Profile

from BC.blockchain import retrieve_classification

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                Profile.objects.get_or_create(user=user)

                login(request, user)
                if user.profile.is_doctor:
                    return redirect('doctor_dashboard')
                else:
                    return redirect('profile')
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
@doctor_required
def doctor_dashboard(request):
    return render(request, 'accounts/doctor_dashboard.html')

@login_required
def start_prediction_redirect(request):
    return redirect('prediction-form')  

@login_required
def file_redirect(request):
    return redirect('prediction-file-form') 

@login_required
@doctor_required
def start_training_redirect(request):
    return redirect('training-form')  

@login_required
@doctor_required
def file_training_redirect(request):
    return redirect('training-file-form') 

@csrf_exempt
@login_required
def retrieve_data_view(request):
    context = {}
    if request.method == "POST":
        patient_id = request.POST.get("patient_id")
        try:
            data = retrieve_classification(patient_id)
            context["result"] = data
        except Exception as e:
            context["error"] = str(e)
    return render(request, "accounts/retrieve_result.html", context)
