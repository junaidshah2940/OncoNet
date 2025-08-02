from django.shortcuts import render

def homepage(request):
    return render(request, "homepage.html")

def inputSubmit(request):
    return render(request, "inputSubmit.html")