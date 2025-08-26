from django import forms
from .models import DeliveryArea, Insurance, Village, InsuranceCompany
from django.utils.translation import gettext_lazy as _
from accounts.models import Pharmacy
class DeliveryAreaForm(forms.ModelForm):
    class Meta:
        model = DeliveryArea
        # استخدم الحقول الفعلية الموجودة في النموذج
        fields = ['village', 'delivery_fee']  # إزالة is_active إذا لم يكن موجوداً
        
        # أو إذا كان لديك حقول مختلفة
        # fields = '__all__'  # استخدام جميع الحقول
        
        labels = {
            'village': _('القرية'),
            'delivery_fee': _('رسوم التوصيل'),
            # 'is_active': _('مفعل'),  // إزالة إذا لم يكن الحقل موجوداً
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # إذا كنت تريد إضافة حقل is_active بشكل يدوي (إذا لم يكن في النموذج)
        if 'is_active' not in self.fields:
            # يمكنك إضافة حقل مخصص إذا needed
            # self.fields['is_active'] = forms.BooleanField(
            #     label=_('مفعل'),
            #     required=False,
            #     initial=True
            # )
            pass
    
    def clean(self):
        cleaned_data = super().clean()
        village = cleaned_data.get('village')
        
        if self.request and self.request.user.is_authenticated and village:
            try:
                pharmacy = Pharmacy.objects.get(user=self.request.user)
                
                # التحقق من عدم وجود تكرار
                if DeliveryArea.objects.filter(
                    pharmacy=pharmacy, 
                    village=village
                ).exists():
                    # إذا كان التحرير لنفس السجل، اسمح به
                    if self.instance and self.instance.pk:
                        existing = DeliveryArea.objects.filter(
                            pharmacy=pharmacy, 
                            village=village
                        ).first()
                        if existing and existing.pk == self.instance.pk:
                            return cleaned_data
                    
                    raise forms.ValidationError(
                        _("هذه القرية مسجلة مسبقاً في مناطق التوصيل لهذه الصيدلية")
                    )
                    
            except Pharmacy.DoesNotExist:
                raise forms.ValidationError(_("الصيدلية غير موجودة"))
            except DeliveryArea.DoesNotExist:
                pass  # لا يوجد سجل مسبق، هذا جيد
        
        return cleaned_data
class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['insurance']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # إذا كان النموذج مربوطاً بمثال محدد (مثل التعديل)
        if hasattr(self.instance, 'pharmacy'):
            # يمكنك هنا تصفية شركات التأمين إذا لزم الأمر
            pass