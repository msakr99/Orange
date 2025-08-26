from django.db import models
from accounts.models import Pharmacy
from product.models import Product
from django.core.validators import MinValueValidator

# Create your models here.



class PharmacyProductCode(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="pharmacy_product_codes", related_query_name="pharmacy_product_codes"
    )
    pharmacy = models.ForeignKey(
        Pharmacy, on_delete=models.CASCADE, related_name="pharmacy_product_codes", related_query_name="pharmacy_product_codes"
    )
    code = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.code} - {self.product} - {self.pharmacy}"

    class Meta:
        unique_together = ('product', 'pharmacy', 'code')
        indexes = [
            models.Index(fields=["product", "pharmacy"]),
            models.Index(fields=["product"]),
            models.Index(fields=["pharmacy"]),
        ]
  
class Stock(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='stocks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    product_code = models.ForeignKey(
        PharmacyProductCode,
        on_delete=models.CASCADE,
        related_name="offers",
        related_query_name="offers",
        null=True,
        blank=True,
)
    class Meta:
        unique_together = ('pharmacy', 'product')

    def __str__(self):
        return f"{self.product.name} in {self.pharmacy.name} - {self.quantity} pcs"