from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Pharmacy , Governorate ,District,Village,User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['phone_number', 'full_name', 'user_type', 'is_active']
    list_filter = ['user_type', 'is_active']
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('المعلومات الشخصية', {'fields': ('full_name', 'user_type')}),
        ('الصلاحيات', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تواريخ مهمة', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'user_type', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'governorate', 'district', 'village')
    search_fields = ('name', 'user__phone_number')
    list_filter = ('governorate', 'district')


class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Governorate, GovernorateAdmin)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate') 
admin.site.register(District, DistrictAdmin)

class VillageAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Village, VillageAdmin)

# admin.py
from django.contrib import admin
from .models import User, Pharmacy, ActivationRequest

@admin.register(ActivationRequest)
class ActivationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_at', 'processed', 'processed_at')
    list_filter = ('processed', 'requested_at')
    readonly_fields = ('requested_at',)
    
    def save_model(self, request, obj, form, change):
        # التأكد من أن processed_at يكون null إذا لم تتم المعالجة
        if not obj.processed:
            obj.processed_at = None
        super().save_model(request, obj, form, change)
