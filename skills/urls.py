from django.urls import path
from . import views # import views.py from the current directory

urlpatterns = [ 
    path('', views.home, name='home'), 
    path("signup/", views.signup, name="signup"),
]