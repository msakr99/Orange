from django.contrib import admin
from .models import Brand, Category, SubCategory, Product, AlternativeProduct, SimilarProduct

# إدارة العلامات التجارية
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']


# إدارة التصنيفات الرئيسية
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    search_fields = ['name']


# إدارة التصنيفات الفرعية
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'image']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


# إدارة المنتجات
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'subcategory', 'brand', 'required_prescription']
    list_filter = ['category', 'subcategory', 'brand', 'required_prescription']
    search_fields = ['name', 'active_ingredient']
    autocomplete_fields = ['category', 'subcategory', 'brand']
    readonly_fields = [ ]  # إذا أضفتها في الموديل
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'description', 'price', 'category', 'subcategory', 'brand')
        }),
        ('معلومات إضافية', {
            'fields': ('required_prescription', 'active_ingredient')
        }),
    )


# إدارة المنتجات البديلة
@admin.register(AlternativeProduct)
class AlternativeProductAdmin(admin.ModelAdmin):
    list_display = ['original_product', 'alternative_product', 'created_at']
    search_fields = ['original_product__name', 'alternative_product__name']
    autocomplete_fields = ['original_product', 'alternative_product']


# إدارة المنتجات المشابهة
@admin.register(SimilarProduct)
class SimilarProductAdmin(admin.ModelAdmin):
    list_display = ['original_product', 'similar_product', 'similarity_score', 'created_at']
    search_fields = ['original_product__name', 'similar_product__name']
    autocomplete_fields = ['original_product', 'similar_product']
    list_filter = ['similarity_score']
