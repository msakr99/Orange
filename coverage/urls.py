from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
app_name = 'coverage'  # تأكد من وجود هذا السطر

urlpatterns = [
    path('delivery-areas/', login_required(views.DeliveryAreaListView.as_view()), name='delivery-areas'),
    path('delivery-area/create/', login_required(views.DeliveryAreaCreateView.as_view()), name='deliveryarea-create'),
    path('delivery-area/<int:pk>/update/', login_required(views.DeliveryAreaUpdateView.as_view()), name='deliveryarea-update'),
    path('delivery-area/<int:pk>/delete/', login_required(views.DeliveryAreaDeleteView.as_view()), name='deliveryarea-delete'),
    path('delivery-area/<int:pk>/', login_required(views.DeliveryAreaDetailView.as_view()), name='deliveryarea-detail'),
    
    path('insurances/', login_required(views.InsuranceListView.as_view()), name='insurance-list'),
    path('insurance/create/', login_required(views.InsuranceCreateView.as_view()), name='insurance-create'),
    path('insurance/<int:pk>/update/', login_required(views.InsuranceUpdateView.as_view()), name='insurance-update'),
    path('insurance/<int:pk>/delete/', login_required(views.InsuranceDeleteView.as_view()), name='insurance-delete'),
    path('insurance/<int:pk>/', login_required(views.InsuranceDetailView.as_view()), name='insurance-detail'),
]