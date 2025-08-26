from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import DeliveryArea, Insurance, Pharmacy
from .forms import DeliveryAreaForm, InsuranceForm
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

# عروض DeliveryArea
class DeliveryAreaListView(LoginRequiredMixin, ListView):
    model = DeliveryArea
    template_name = 'delivery/deliveryarea_list.html'
    context_object_name = 'delivery_areas'
    
    def get_queryset(self):
        # جلب فقط مناطق التوصيل الخاصة بالصيدلية المرتبطة بالمستخدم الحالي
        return DeliveryArea.objects.filter(pharmacy__user=self.request.user)

class DeliveryAreaCreateView(LoginRequiredMixin, CreateView):
    model = DeliveryArea
    form_class = DeliveryAreaForm
    template_name = 'delivery/deliveryarea_form.html'
    
    def get_success_url(self):
        return reverse_lazy('coverage:delivery-areas')  # تأكد من اسم URL الصحيح
    
    def get_form_kwargs(self):
        # الحصول على kwargs الأساسية أولاً
        kwargs = super().get_form_kwargs()
        
        # ثم إضافة request إلى kwargs
        if hasattr(self, 'request'):
            kwargs['request'] = self.request
        
        return kwargs
    
    def form_valid(self, form):
        try:
            # تعيين الصيدلية تلقائياً
            form.instance.pharmacy = Pharmacy.objects.get(user=self.request.user)
            return super().form_valid(form)
            
        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e):
                form.add_error(
                    'village', 
                    _("هذه القرية مسجلة مسبقاً في مناطق التوصيل لهذه الصيدلية")
                )
            else:
                form.add_error(None, _("حدث خطأ أثناء الحفظ"))
            return self.form_invalid(form)
        except Pharmacy.DoesNotExist:
            form.add_error(None, _("الصيدلية غير موجودة"))
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("إضافة منطقة توصيل جديدة")
        return context
class DeliveryAreaUpdateView(LoginRequiredMixin, UpdateView):
    model = DeliveryArea
    form_class = DeliveryAreaForm
    template_name = 'delivery/deliveryarea_form.html'
    success_url = reverse_lazy('coverage:delivery-areas')
    
    def get_queryset(self):
        # التأكد من أن المستخدم يمكنه تعديل منطقة التوصيل الخاصة به فقط
        return DeliveryArea.objects.filter(pharmacy__user=self.request.user)

class DeliveryAreaDeleteView(LoginRequiredMixin, DeleteView):
    model = DeliveryArea
    template_name = 'delivery/deliveryarea_confirm_delete.html'  # تأكد من المسار الصحيح
    success_url = reverse_lazy('coverage:delivery-areas')
    
    def get_queryset(self):
        """التأكد من أن المستخدم يمكنه حذف منطقة التوصيل الخاصة به فقط"""
        return DeliveryArea.objects.filter(pharmacy__user=self.request.user)
    
    def get_object(self, queryset=None):
        """الحصول على الكائن مع التحقق من الصلاحية"""
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get('pk')
        return get_object_or_404(queryset, pk=pk)
    
    def delete(self, request, *args, **kwargs):
        """معالجة عملية الحذف مع إضافة رسالة نجاح"""
        messages.success(request, _("تم حذف منطقة التوصيل بنجاح"))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """إضافة بيانات إضافية للقالب"""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _("حذف منطقة التوصيل")
        return context

class DeliveryAreaDetailView(LoginRequiredMixin, DetailView):
    model = DeliveryArea
    template_name = 'delivery/deliveryarea_detail.html'
    
    def get_queryset(self):
        # التأكد من أن المستخدم يمكنه عرض منطقة التوصيل الخاصة به فقط
        return DeliveryArea.objects.filter(pharmacy__user=self.request.user)

# عروض Insurance
class InsuranceListView(LoginRequiredMixin, ListView):
    model = Insurance
    template_name = 'insurance/insurance_list.html'
    context_object_name = 'insurances'
    
    def get_queryset(self):
        # جلب فقط شركات التأمين المرتبطة بالصيدلية الخاصة بالمستخدم الحالي
        return Insurance.objects.filter(pharmacy__user=self.request.user)

# في ملف forms.py أو في أعلى الملف
class InsuranceFormWithValidation(InsuranceForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        if self.request and self.request.user.is_authenticated:
            pharmacy = Pharmacy.objects.get(user=self.request.user)
            insurance_company = cleaned_data.get('insurance_company')
            
            if pharmacy and insurance_company:
                if Insurance.objects.filter(
                    pharmacy=pharmacy, 
                    insurance_company=insurance_company
                ).exists():
                    raise forms.ValidationError(
                        "هذه التأمينة مسجلة مسبقاً لهذه الصيدلية"
                    )
        return cleaned_data

class InsuranceCreateView(LoginRequiredMixin, CreateView):
    model = Insurance
    form_class = InsuranceFormWithValidation  # استخدام النموذج المخصص
    template_name = 'insurance/insurance_form.html'
    success_url = reverse_lazy('coverage:insurance-list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # تمرير طلب المستخدم إلى النموذج
        if kwargs.get('instance') is None:
            kwargs['instance'] = Insurance(pharmacy=Pharmacy.objects.get(user=self.request.user))
        return kwargs
    
    def form_valid(self, form):
        try:
            form.instance.pharmacy = Pharmacy.objects.get(user=self.request.user)
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "هذه التأمينة مسجلة مسبقاً لهذه الصيدلية")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        for error in form.errors:
            messages.error(self.request, form.errors[error])
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "إضافة تأمين جديد"
        return context
class InsuranceUpdateView(LoginRequiredMixin, UpdateView):
    model = Insurance
    form_class = InsuranceForm
    template_name = 'insurance/insurance_form.html'
    success_url = reverse_lazy('coverage:insurance-list')
    
    def get_queryset(self):
        # التأكد من أن المستخدم يمكنه تعديل التأمين الخاص به فقط
        return Insurance.objects.filter(pharmacy__user=self.request.user)

class InsuranceDeleteView(LoginRequiredMixin, DeleteView):
    model = Insurance
    template_name = 'insurance/insurance_confirm_delete.html'
    success_url = reverse_lazy('coverage:insurance-list')
    
    def get_queryset(self):
        # التأكد من أن المستخدم يمكنه حذف التأمين الخاص به فقط
        return Insurance.objects.filter(pharmacy__user=self.request.user)

class InsuranceDetailView(LoginRequiredMixin, DetailView):
    model = Insurance
    template_name = 'insurance/insurance_detail.html'
    
    def get_queryset(self):
        # التأكد من أن المستخدم يمكنه عرض التأمين الخاص به فقط
        return Insurance.objects.filter(pharmacy__user=self.request.user)