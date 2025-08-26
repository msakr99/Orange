# managers.py
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone_number, user_type, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('يجب أن يملك المستخدم رقم هاتف')
        
        user = self.model(
            phone_number=phone_number,
            user_type=user_type,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, user_type, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_approved', True)
        
        return self.create_user(phone_number, user_type, password, **extra_fields)