from django.urls import path
from users import views

app_name = 'users'

urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('deauth/', views.deauth, name='deauth'),
    path('reg/', views.reg, name='reg'),
]

