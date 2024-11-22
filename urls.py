# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_user_profile, name='submit_user_profile'),
    # Other URL patterns here
]
