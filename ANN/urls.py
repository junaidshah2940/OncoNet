from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.data_form_view, name='prediction-form'),
]