# forms.py
from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="ارفع ملف Excel")

class StockUploadForm(forms.Form):
    excel_file = forms.FileField()


# forms.py
# forms.py
from django import forms
from .models import Stock, Product, PharmacyProductCode

class StockForm(forms.ModelForm):
    search_product = forms.CharField(
        required=False,
        label='بحث عن المنتج',
        widget=forms.TextInput(attrs={'placeholder': 'ابحث باسم المنتج'})
    )
    
    class Meta:
        model = Stock
        fields = ['product', 'quantity']
        labels = {
            'product': 'المنتج',
            'quantity': 'الكمية',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # الحصول على الصيدلية الخاصة بالمستخدم
            pharmacy = user.pharmacy
            
            # الحصول على جميع أكواد المنتجات في هذه الصيدلية
            product_codes = PharmacyProductCode.objects.filter(pharmacy=pharmacy)
            
            # استخراج المنتجات التي لها أكواد في هذه الصيدلية
            products_with_codes = Product.objects.filter(
                id__in=product_codes.values_list('product_id', flat=True)
            )
            
            # تصفية المنتجات المتاحة فقط لتلك التي لها أكواد
            self.fields['product'].queryset = products_with_codes
            
            # جعل حقل البحث غير مطلوب
            self.fields['search_product'].required = False