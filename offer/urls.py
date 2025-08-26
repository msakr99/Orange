from django.urls import path
from .views import (
    OfferListView, OfferCreateView, OfferUpdateView,
    OfferDeleteView, OfferDetailView
)
app_name = 'offer'  # تأكد من وجود هذا السطر

urlpatterns = [
    path('', OfferListView.as_view(), name='offer-list'),
    path('add/', OfferCreateView.as_view(), name='offer-add'),
    path('<int:pk>/edit/', OfferUpdateView.as_view(), name='offer-edit'),
    path('<int:pk>/delete/', OfferDeleteView.as_view(), name='offer-delete'),
    path('<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
