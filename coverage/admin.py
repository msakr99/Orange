from django.contrib import admin
from .models import DeliveryArea, InsuranceCompany, Insurance

@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'village', 'delivery_fee')
    list_filter = ('pharmacy', 'village')
    search_fields = ('pharmacy__name', 'village__name')

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('pharmacy', 'insurance')
    list_filter = ('pharmacy', 'insurance')
    search_fields = ('pharmacy__name', 'insurance__name')
