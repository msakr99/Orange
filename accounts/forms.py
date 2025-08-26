from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, Pharmacy , Governorate , District , Village
from django.contrib.auth.forms import AuthenticationForm

class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(label="رقم الهاتف")

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("هذا الحساب غير مفعل.", code='inactive')

class PharmacyRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=200, label="اسم الصيدلية")
    address = forms.CharField(widget=forms.Textarea, label="العنوان")
    license_number = forms.CharField(max_length=100, label="رقم الترخيص")
    governorate = forms.ModelChoiceField(
        queryset=Governorate.objects.all(),
        label="المحافظة"
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        label="المنطقة"
    )
    village = forms.ModelChoiceField(
        queryset=Village.objects.all(),
        label="القرية"
    )
    
    class Meta:
        model = User
        fields = ('phone_number', 'full_name', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إخفاء حقل نوع المستخدم وتعيينه تلقائياً كصيدلية
        self.fields['user_type'].initial = 'pharmacy'
        self.fields['user_type'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        # حفظ المستخدم كنوع صيدلية
        user = super().save(commit=False)
        user.user_type = 'pharmacy'  # تأكيد تعيين النوع
        user.is_approved = False  # الحساب غير مفعل تلقائياً
        
        if commit:
            user.save()
            # حفظ معلومات الصيدلية الإضافية
            pharmacy = Pharmacy(
                user=user,
                name=self.cleaned_data['name'],
                governorate=self.cleaned_data['governorate'],
                district=self.cleaned_data['district'],
                village=self.cleaned_data['village'],
                address=self.cleaned_data['address'],
                license_number=self.cleaned_data['license_number']
            )
            pharmacy.save()
            
            # إنشاء طلب تفعيل
            from .models import ActivationRequest
            ActivationRequest.objects.create(user=user)
        
        return user

class PhoneLoginForm(AuthenticationForm):
    username = forms.CharField(label="رقم الهاتف", max_length=15)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'رقم الهاتف'})
        self.fields['password'].widget.attrs.update({'placeholder': 'كلمة المرور'})