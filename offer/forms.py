from django import forms
from .models import Offer

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # التحقق من حجم الصورة
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("حجم الصورة يجب أن لا يتجاوز 2MB.")
            # التحقق من نوع الملف
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise forms.ValidationError("نوع الملف غير مدعوم. الرجاء استخدام صيغة jpg, jpeg, png, أو webp.")
        return image