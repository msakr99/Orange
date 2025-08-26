from django.db import models
from accounts.models import Governorate ,District , Village , Pharmacy
# Create your models here.
class DeliveryArea(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='delivery_areas')
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('pharmacy', 'village')  # لا يمكن تكرار نفس القرية لنفس الصيدلية

    def __str__(self):
        return f"{self.pharmacy.name} - {self.village.name} ({self.delivery_fee} EGP)"

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='insurance/')
    def __str__(self):
        return self.name

class Insurance(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='insurance')
    insurance = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('pharmacy', 'insurance')  # لا يمكن تكرار نفس القرية لنفس الصيدلية

    def __str__(self):
        return f"{self.pharmacy.name} - {self.insurance.name} "

