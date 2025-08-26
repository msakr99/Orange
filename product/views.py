import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Product, Category, SubCategory, Brand, Shape
import tempfile
import os

def upload_products_excel(request):
    """
    عرض صفحة رفع ملف Excel للمنتجات
    """
    return render(request, 'product_upload.html')

@require_POST
@csrf_exempt
def process_excel_upload(request):
    """
    معالجة ملف Excel المرفوع وإنشاء المنتجات
    """
    if 'excel_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'لم يتم اختيار ملف'})
    
    excel_file = request.FILES['excel_file']
    
    # التحقق من نوع الملف
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return JsonResponse({'success': False, 'error': 'نوع الملف غير مدعوم. يرجى رفع ملف Excel'})
    
    try:
        # حفظ الملف مؤقتاً ومعالجته
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in excel_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # قراءة ملف Excel
        df = pd.read_excel(tmp_file_path)
        
        # التحقق من الأعمدة المطلوبة
        required_columns = ['name', 'price', 'category', 'subcategory', 'brand', 'active_ingredient', 'required_prescription']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            os.unlink(tmp_file_path)
            return JsonResponse({
                'success': False, 
                'error': f'الأعمدة التالية مفقودة في الملف: {", ".join(missing_columns)}'
            })
        
        # معالجة البيانات وإنشاء المنتجات
        results = {
            'success_count': 0,
            'error_count': 0,
            'errors': []
        }
        
        for index, row in df.iterrows():
            try:
                # البحث عن الفئة
                try:
                    category = Category.objects.get(name=row['category'])
                except Category.DoesNotExist:
                    results['error_count'] += 1
                    results['errors'].append({
                        'row': index + 2,  # +2 لأن الصف الأول هو العناوين وindex يبدأ من 0
                        'product_name': row.get('name', 'غير معروف'),
                        'error': f"الفئة '{row['category']}' غير موجودة في النظام"
                    })
                    continue
                
                # البحث عن الفئة الفرعية
                try:
                    subcategory = SubCategory.objects.get(
                        name=row['subcategory'], 
                        category=category
                    )
                except SubCategory.DoesNotExist:
                    results['error_count'] += 1
                    results['errors'].append({
                        'row': index + 2,
                        'product_name': row.get('name', 'غير معروف'),
                        'error': f"الفئة الفرعية '{row['subcategory']}' غير موجودة أو لا تنتمي إلى الفئة '{category.name}'"
                    })
                    continue
                
                # البحث عن الماركة
                try:
                    brand = Brand.objects.get(name=row['brand'])
                except Brand.DoesNotExist:
                    results['error_count'] += 1
                    results['errors'].append({
                        'row': index + 2,
                        'product_name': row.get('name', 'غير معروف'),
                        'error': f"الماركة '{row['brand']}' غير موجودة في النظام"
                    })
                    continue
                
                # البحث عن الشكل (إذا كان موجوداً)
                shape = None
                if 'shape' in row and pd.notna(row['shape']):
                    try:
                        shape = Shape.objects.get(name=row['shape'])
                    except Shape.DoesNotExist:
                        # يمكنك هنا إنشاء الشكل تلقائياً إذا أردت
                        pass
                
                # معالجة حقل requires_prescription
                requires_prescription = False
                prescription_value = row['required_prescription']
                
                if isinstance(prescription_value, bool):
                    requires_prescription = prescription_value
                elif isinstance(prescription_value, str):
                    requires_prescription = prescription_value.lower() in ['نعم', 'yes', 'true', '1', 'صحيح']
                elif isinstance(prescription_value, (int, float)):
                    requires_prescription = bool(prescription_value)
                
                # إنشاء المنتج
                product, created = Product.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'description': row.get('description', ''),
                        'price': row['price'],
                        'category': category,
                        'subcategory': subcategory,
                        'brand': brand,
                        'shape': shape,
                        'required_prescription': requires_prescription,
                        'active_ingredient': row['active_ingredient']
                    }
                )
                
                if created:
                    results['success_count'] += 1
                else:
                    # إذا كان المنتج موجوداً مسبقاً، نقوم بتحديثه
                    product.description = row.get('description', '')
                    product.price = row['price']
                    product.category = category
                    product.subcategory = subcategory
                    product.brand = brand
                    product.shape = shape
                    product.required_prescription = requires_prescription
                    product.active_ingredient = row['active_ingredient']
                    product.save()
                    results['success_count'] += 1
                    
            except Exception as e:
                results['error_count'] += 1
                results['errors'].append({
                    'row': index + 2,
                    'product_name': row.get('name', 'غير معروف'),
                    'error': f"خطأ غير متوقع: {str(e)}"
                })
                continue
        
        # حذف الملف المؤقت
        os.unlink(tmp_file_path)
        
        # إعداد رسالة النجاح
        message = f"تم معالجة {results['success_count']} منتج بنجاح"
        if results['error_count'] > 0:
            message += f"، مع {results['error_count']} أخطاء"
        
        return JsonResponse({
            'success': True,
            'message': message,
            'results': results
        })
        
    except Exception as e:
        # تنظيف الملف المؤقت في حالة الخطأ
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
            
        return JsonResponse({
            'success': False,
            'error': f'حدث خطأ أثناء معالجة الملف: {str(e)}'
        })
