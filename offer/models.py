from django.db import models
from product.models import Product
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from decimal import Decimal
class Offer(models.Model):
    OFFER_TYPES = [
        ('PERCENTAGE', 'خصم بنسبة مئوية'),
        ('BOGO', 'اشترِ واحدة واحصل على واحدة مجانًا'),
        ('SECOND_HALF', 'اشترِ واحدة واحصل على الثانية بنصف السعر'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default='PERCENTAGE')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    # إضافة حقل الصورة مع تحقق من نوع الملف وحجمه
    image = models.ImageField(
        upload_to='offers/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        help_text="الصور المسموح بها: jpg, jpeg, png, webp. الحجم الأقصى: 2MB"
    )

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("تاريخ الانتهاء لا يمكن أن يكون قبل تاريخ البداية.")
        if self.offer_type == 'PERCENTAGE' and self.discount_percentage is None:
            raise ValidationError("يجب تحديد نسبة الخصم لعروض الخصم.")
        if self.offer_type != 'PERCENTAGE':
            self.discount_percentage = None  # لا نحتاج النسبة في عروض غير الخصم المباشر
        
        # التحقق من حجم الصورة إذا كانت موجودة
        if self.image and hasattr(self.image, 'size') and self.image.size > 2 * 1024 * 1024:
            raise ValidationError("حجم الصورة يجب أن لا يتجاوز 2MB.")

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def __str__(self):
        return f"{self.title} - {self.get_offer_type_display()}"
    
    def apply_offer(self, quantity=1):
        """
        حساب السعر النهائي بناءً على الكمية ونوع العرض.
        """
        unit_price = self.product.price
        if not self.is_active():
            return unit_price * quantity

        if self.offer_type == 'PERCENTAGE':
            discount_factor = Decimal('1') - (self.discount_percentage / Decimal('100'))
            return unit_price * quantity * discount_factor
        elif self.offer_type == 'BOGO':  # اشترِ واحدة واحصل على واحدة مجانًا
            paid_items = (quantity // 2) + (quantity % 2)
            return unit_price * paid_items

        elif self.offer_type == 'SECOND_HALF':  # اشترِ واحدة والثانية بنصف السعر
            pairs = quantity // 2
            remaining = quantity % 2
            total = (pairs * unit_price * 1.5) + (remaining * unit_price)
            return total

        return unit_price * quantity