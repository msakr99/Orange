# views.py
import pandas as pd
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm ,StockUploadForm
from .models import *
from product.models import *
from .models import *

# views.py
from django.http import HttpResponse
import io
from django.contrib import messages
from openpyxl import Workbook
# views.py
def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES["file"]
            try:
                df = pd.read_excel(excel_file)

                expected_columns = ["product_id", "pharmacy_id", "code"]
                if not all(col in df.columns for col in expected_columns):
                    return render(request, "upload.html", {
                        "form": form,
                        "error": "ملف الإكسل يجب أن يحتوي على الأعمدة: product_id, pharmacy_id, code"
                    })

                updated = []
                created = []

                for _, row in df.iterrows():
                    product_id = row["product_id"]
                    pharmacy_id = row["pharmacy_id"]
                    code = row["code"]

                    try:
                        product = Product.objects.get(id=product_id)
                        pharmacy = Pharmacy.objects.get(id=pharmacy_id)

                        obj, created_flag = PharmacyProductCode.objects.update_or_create(
                            product=product,
                            pharmacy=pharmacy,
                            defaults={"code": code}
                        )

                        if created_flag:
                            created.append(obj)
                        else:
                            updated.append(obj)

                    except (Product.DoesNotExist, Pharmacy.DoesNotExist):
                        continue

                return render(request, "upload_success.html", {
                    "created": created,
                    "updated": updated
                })

            except Exception as e:
                return render(request, "upload.html", {
                    "form": form,
                    "error": f"خطأ أثناء قراءة الملف: {e}"
                })

    else:
        form = ExcelUploadForm()

    return render(request, "upload.html", {"form": form})




def download_excel_template(request):
    # إنشاء DataFrame فارغ بالأعمدة المطلوبة
    df = pd.DataFrame(columns=["product_id", "pharmacy_id", "code"])

    # حفظ الملف في الذاكرة
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Template")

    output.seek(0)
    
    # تجهيز الاستجابة
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=template.xlsx'
    return response



def upload_stock_excel(request):
    if request.method == "POST":
        form = StockUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                df = pd.read_excel(excel_file)
                
                # الحصول على كود الصيدلية من المستخدم الحالي
                try:
                    # افترض أن لديك نموذج User مرتبط بالصيدلية
                    pharmacy = request.user.pharmacy
                    pharmacy_code = pharmacy.id
                except AttributeError:
                    messages.error(request, "المستخدم الحالي غير مرتبط بأي صيدلية")
                    return render(request, 'upload_stock.html', {'form': form})

                # التأكد إن كل كود منتج في الصيدلية موجود في الداتا
                missing_codes = []
                for code in df['pharmacy_product_code'].unique():
                    if not PharmacyProductCode.objects.filter(code=code).exists():
                        missing_codes.append(code)

                if missing_codes:
                    messages.error(
                        request,
                        f"خطأ: الأكواد التالية غير موجودة في قاعدة البيانات: {', '.join(missing_codes)}"
                    )
                    return render(request, 'upload_stock.html', {'form': form})

                # حذف بيانات الاستوك القديمة للصيدلية الحالية فقط
                Stock.objects.filter(pharmacy=pharmacy).delete()

                for index, row in df.iterrows():
                    pharmacy_product_code = PharmacyProductCode.objects.get(code=row['pharmacy_product_code'])
                    product = pharmacy_product_code.product
                    quantity = int(row['quantity'])

                    Stock.objects.create(
                        pharmacy=pharmacy,
                        product=product,
                        quantity=quantity,
                        product_code=pharmacy_product_code,
                    )

                messages.success(request, "تم تحديث بيانات المخزون بنجاح!")
                return redirect('upload_stock_excel')

            except Exception as e:
                messages.error(request, f"خطأ أثناء معالجة الملف: {str(e)}")

    else:
        form = StockUploadForm()

    return render(request, 'upload_stock.html', {'form': form})


def download_empty_stock_excel(request):
    # إنشاء ملف Excel جديد
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock Data"

    # أسماء الأعمدة المطلوبة في الملف (تم إزالة pharmacy_code)
    columns = ['pharmacy_product_code', 'quantity']

    # إضافة أسماء الأعمدة في الصف الأول
    ws.append(columns)

    # تحضير استجابة تحميل الملف
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=empty_stock_template.xlsx'

    # حفظ ملف Excel في الاستجابة
    wb.save(response)
    return response

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Stock, Pharmacy, Product, PharmacyProductCode
from .forms import StockForm

# عرض قائمة المخزون
class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'stock_list.html'
    context_object_name = 'stocks'
    
    def get_queryset(self):
        return Stock.objects.filter(pharmacy__user=self.request.user)

# views.py
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import Stock, Pharmacy, Product, PharmacyProductCode
from .forms import StockForm

class StockCreateView(LoginRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'stock_form.html'
    success_url = reverse_lazy('store:stock_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def form_valid(self, form):
        form.instance.pharmacy = Pharmacy.objects.get(user=self.request.user)
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, 'هذا المنتج موجود بالفعل في مخزون الصيدلية')
            return self.form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إضافة قائمة المنتجات للبحث
        pharmacy = self.request.user.pharmacy
        product_codes = PharmacyProductCode.objects.filter(pharmacy=pharmacy)
        products_with_codes = Product.objects.filter(
            id__in=product_codes.values_list('product_id', flat=True)
        )
        
        context['products'] = products_with_codes
        return context

# دالة للبحث عن المنتجات (AJAX)
def search_products(request):
    if request.method == 'GET' and request.is_ajax():
        search_term = request.GET.get('term', '')
        pharmacy = request.user.pharmacy
        
        # البحث في المنتجات التي لها أكواد في الصيدلية
        product_codes = PharmacyProductCode.objects.filter(pharmacy=pharmacy)
        products = Product.objects.filter(
            id__in=product_codes.values_list('product_id', flat=True),
            name__icontains=search_term
        )[:10]  # الحد الأقصى 10 نتائج
        
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'text': product.name,
                'code': product.code if hasattr(product, 'code') else ''
            })
        
        return JsonResponse(results, safe=False)
    
    return JsonResponse({'error': 'Invalid request'})

# views.py - إضافة كلاس التعديل
class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'stock_form.html'
    success_url = reverse_lazy('store:stock_list')
    
    def get_queryset(self):
        return Stock.objects.filter(pharmacy__user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إضافة قائمة المنتجات للبحث
        pharmacy = self.request.user.pharmacy
        product_codes = PharmacyProductCode.objects.filter(pharmacy=pharmacy)
        products_with_codes = Product.objects.filter(
            id__in=product_codes.values_list('product_id', flat=True)
        )
        
        context['products'] = products_with_codes
        return context
# حذف عنصر من المخزون
class StockDeleteView(LoginRequiredMixin, DeleteView):
    model = Stock
    template_name = 'stock_confirm_delete.html'
    success_url = reverse_lazy('stock_list')
    
    def get_queryset(self):
        return Stock.objects.filter(pharmacy__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'تم حذف العنصر من المخزون بنجاح')
        return super().delete(request, *args, **kwargs)