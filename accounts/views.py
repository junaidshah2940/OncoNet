# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from BC.blockchain import retrieve_classification
from .forms import SignUpForm, LoginForm


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def start_prediction_redirect(request):
    if request.user.is_authenticated:
        return redirect('prediction-form') 
    else:
        return redirect('login')


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'accounts/profile.html') 
    else:
        return redirect('login')

@csrf_exempt
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