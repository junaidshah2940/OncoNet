from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('start-prediction/', views.start_prediction_redirect, name='start-prediction'),
    path('profile/', views.profile, name='profile'),
    path("retrieve/", views.retrieve_data_view, name="retrieve"),
]

