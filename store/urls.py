# urls.py
from django.urls import path
from . import views
app_name = 'store'
urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('upload/success/', views.upload_excel, name='upload_success'),  # ممكن تعرض رسالة نجاح هنا
    path('upload/template/', views.download_excel_template, name='download_excel_template'),
    path('upload-stock/', views.upload_stock_excel, name='upload-stock'),
    path('download-stock-template/', views.download_empty_stock_excel, name='download_stock_template'),
    path('', views.StockListView.as_view(), name='stock_list'),
    path('create/', views.StockCreateView.as_view(), name='stock_create'),
    path('update/<int:pk>/', views.StockUpdateView.as_view(), name='stock_update'),
    path('delete/<int:pk>/', views.StockDeleteView.as_view(), name='stock_delete'),
    path('search-products/', views.search_products, name='search_products'),

]
