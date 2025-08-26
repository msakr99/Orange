from django.urls import path
from . import views

urlpatterns = [
    path('upload-products-excel/', views.upload_products_excel, name='upload_products_excel'),
    path('process-excel-upload/', views.process_excel_upload, name='process_excel_upload'),
]