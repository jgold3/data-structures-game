from django.urls import path
from . import views

urlpatterns = [

    # Views
    path('', views.register, name='register')

]