from django.urls import path
from . import views

urlpatterns = [
    path('',         views.home,           name='home'),
    path('generate/', views.generate_poster, name='generate_poster'),
    path('history/', views.history,         name='history'),
]