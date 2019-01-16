from django.urls import path
from manager import views

app_name = 'manager'

urlpatterns = [
    path('1/', views.add_to_stack, name='add_to_stack'),
    path('load_template/', views.load_template, name='load_template'),
    path('get_templates/', views.get_templates, name='get_templates'),
]

