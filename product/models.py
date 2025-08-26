from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='brands/')
    def __str__(self):
        return self.name

class Shape(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='shape/')
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category/')
    def __str__(self):
        return self.name
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='subcategories')
    image = models.ImageField(upload_to='subcategory/')
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,related_name='products')
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE,related_name='products',blank=True , null= True)
    required_prescription = models.BooleanField(default=False)
    active_ingredient = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name} (${self.price})" 
    def clean(self):
        # Ensure subcategory belongs to the selected category
        if self.subcategory and self.category and self.subcategory.category != self.category:
            raise ValidationError("Subcategory must belong to the selected category.")

class AlternativeProduct(models.Model):
    original_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alternatives_as_original')
    alternative_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alternatives_as_alternative')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('original_product', 'alternative_product')

    def __str__(self):
        return f"{self.alternative_product.name} is alternative to {self.original_product.name}"

    def clean(self):
        if self.original_product == self.alternative_product:
            raise ValidationError("A product cannot be an alternative to itself.")

class SimilarProduct(models.Model):
    original_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similars_as_original')
    similar_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similars_as_similar')
    similarity_score = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('original_product', 'similar_product')

    def __str__(self):
        return f"{self.similar_product.name} is similar to {self.original_product.name} ({self.similarity_score})"

    def clean(self):
        if self.original_product == self.similar_product:
            raise ValidationError("A product cannot be similar to itself.")