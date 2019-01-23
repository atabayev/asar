from django.urls import path
from grabber import views

app_name = 'grabber'

urlpatterns = [
    path('get_emails/', views.get_emails, name='get_emails'),
    path('add_email/', views.add_email, name='add_email'),
    path('delete_email/', views.delete_email, name='delete_email'),
    path('get_zips/', views.get_zips, name='get_zips'),
    path('get_arch_info/', views.get_arch_info, name='get_arch_info'),
    path('set_scan_time/', views.set_scan_time, name='set_scan_time'),
    path('get_dirs/', views.get_dirs, name='get_dirs'),
    path('clear_zips_table/', views.clear_zips_table, name='clear_zips_table'),
    path('grab/', views.grab, name='grab'),

]

