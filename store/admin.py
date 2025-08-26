from django.contrib import admin
from .models import  PharmacyProductCode, Stock



@admin.register(PharmacyProductCode)
class PharmacyProductCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'product', 'pharmacy')
    search_fields = ('code', 'product__name', 'pharmacy__name')
    list_filter = ('product', 'pharmacy')
    ordering = ('product', 'pharmacy', 'code')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'pharmacy', 'quantity', 'last_updated', 'product_code')
    search_fields = ('product__name', 'pharmacy__name', 'product_code__code')
    list_filter = ('pharmacy',)
    ordering = ('pharmacy', 'product')
    readonly_fields = ('last_updated',)
