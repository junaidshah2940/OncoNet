from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile, name='profile'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),

    path('start-prediction/', views.start_prediction_redirect, name='start-prediction'),
    path('file/', views.file_redirect, name='file'),

    path('start-training/', views.start_training_redirect, name='start-training'),
    path('file-training/', views.file_training_redirect, name='file-training'),

    path("retrieve/", views.retrieve_data_view, name="retrieve"),
]
