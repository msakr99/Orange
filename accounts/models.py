from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone

class Governorate(models.Model):
    name = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name
class District(models.Model):
    governorate = models.ForeignKey(Governorate,on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name

class Village(models.Model):
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.name
class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, user_type=None, **extra_fields):
        if not phone_number:
            raise ValueError("رقم الهاتف مطلوب")
        if not user_type:
            raise ValueError("نوع المستخدم مطلوب")
        if user_type not in dict(User.USER_TYPE_CHOICES):
            raise ValueError("نوع المستخدم غير صالح")
        user = self.model(phone_number=phone_number, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')  # ✅ هنا فقط نضيفها

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('pharmacy', 'Pharmacy'),
        ('customer', 'Customer'),
        ('delivery', 'Delivery'),
        ('callcenter', 'Call Center'),
        ('admin', 'Admin'),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # حقل جديد للتفعيل بواسطة المسؤول
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_type']

    def __str__(self):
        return f"{self.phone_number} - {self.get_user_type_display()}"
    
    def can_login(self):
        """يتحقق مما إذا كان يمكن للصيدلية تسجيل الدخول"""
        return self.is_active and self.is_approved and self.user_type == 'pharmacy'


class Pharmacy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'pharmacy'})
    name = models.CharField(max_length=100,blank=True)
    governorate = models.ForeignKey(Governorate,on_delete=models.CASCADE)
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    village = models.ForeignKey(Village,on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    license_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    def clean(self):
        if self.user.user_type != 'pharmacy':
            raise ValidationError('المستخدم يجب أن يكون نوعه صيدلية')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class ActivationRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activation_request')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='processed_activations')
    
    def __str__(self):
        return f"تفعيل الصيدلية: {self.user.phone_number}"
    
    def save(self, *args, **kwargs):
        # التأكد من أن processed_at يكون null إذا لم تتم المعالجة
        if not self.processed:
            self.processed_at = None
        super().save(*args, **kwargs)