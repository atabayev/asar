from django.urls import path
from grabber import views

app_name = 'grabber'

urlpatterns = [
    path('', views.grab, name='grab'),
]

