from django.urls import path
from django.contrib.auth import views as auth_views

from accounts.forms import PhoneLoginForm
from django.views.generic import TemplateView
from . import views
app_name = 'accounts'  # هذا السطر مهم

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('pharmacy/dashboard/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('', views.home_view, name='home'),
    path('pharmacy/register/', views.pharmacy_register, name='pharmacy_register'),
    path('waiting-approval/', views.waiting_approval, name='waiting_approval'),
    path('admin/activation-requests/', views.activation_requests, name='activation_requests'),
    path('admin/approve-pharmacy/<int:user_id>/', views.approve_pharmacy, name='approve_pharmacy'),
    path('get-districts/', views.get_districts, name='get_districts'),
    path('get-villages/', views.get_villages, name='get_villages'),
]