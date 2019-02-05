from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('all/', views.all_records, name='all'),
    path('new/', views.new_record, name='new'),
    path('check/', views.check_connect, name='check'),
    path('start_daemons/', views.start_daemons, name='start_daemons'),
]

