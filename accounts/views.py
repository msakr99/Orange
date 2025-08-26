# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import PharmacyRegistrationForm
from .models import User, ActivationRequest ,Pharmacy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.http import JsonResponse  # هذا السطر الناقص!
from django.http import HttpResponseForbidden
from .models import District ,Village 
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.shortcuts import redirect
from .decorators import pharmacy_required
from .forms import PhoneLoginForm
from django.shortcuts import get_object_or_404

 # تأكد من استيراد النموذج
def pharmacy_register(request):
 
    if request.method == 'POST':
        form = PharmacyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'تم إنشاء حساب الصيدلية بنجاح! يرجى الانتظار حتى يتم تفعيله بواسطة المسؤول.')
            return redirect('accounts:waiting_approval')
        else:
            messages.error(request, 'حدث خطأ في التسجيل. يرجى التحقق من البيانات المدخلة.')
    else:
        form = PharmacyRegistrationForm()
    
    return render(request, 'registration/pharmacy_register.html', {'form': form})

def waiting_approval(request):
    return render(request, 'registration/waiting_approval.html')

def is_admin(user):
    return user.is_authenticated and user.is_staff and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def activation_requests(request):
    pending_requests = ActivationRequest.objects.filter(
        processed=False, 
        user__user_type='pharmacy'
    ).select_related('user')
    return render(request, 'admin/activation_requests.html', {'requests': pending_requests})

@login_required
@user_passes_test(is_admin)
def approve_pharmacy(request, user_id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id, user_type='pharmacy')
            user.is_approved = True
            user.save()
            
            # تحديث طلب التفعيل
            activation_request = ActivationRequest.objects.get(user=user)
            activation_request.processed = True
            activation_request.processed_at = timezone.now()
            activation_request.processed_by = request.user
            activation_request.save()
            
            messages.success(request, f'تم تفعيل حساب الصيدلية {user.pharmacy.name} بنجاح.')
        except User.DoesNotExist:
            messages.error(request, 'الصيدلية غير موجودة.')
        except ActivationRequest.DoesNotExist:
            messages.error(request, 'طلب التفعيل غير موجود.')
    
    return redirect('accounts:activation_requests')

def home_view(request):
    return render(request, 'home.html')


def get_districts(request):
    governorate_id = request.GET.get('governorate_id')
    districts = District.objects.filter(governorate_id=governorate_id).values('id', 'name')
    return JsonResponse({'districts': list(districts)})

def get_villages(request):
    district_id = request.GET.get('district_id')
    villages = Village.objects.filter(district_id=district_id).values('id', 'name')
    return JsonResponse({'villages': list(villages)})




class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = PhoneLoginForm

    def form_valid(self, form):
        """تسجيل الدخول والتحقق من صلاحية المستخدم"""
        user = form.get_user()
        
        if not user.is_active:
            messages.error(self.request, "هذا الحساب غير مفعل.")
            return redirect('login')

        if user.user_type == 'pharmacy' and not user.is_approved:
            messages.error(self.request, "لم يتم الموافقة على حساب الصيدلية بعد.")
            return redirect('login')
        
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user

        if user.user_type == 'pharmacy':
            return reverse('accounts:pharmacy_dashboard')
        elif user.user_type == 'customer':
            return reverse('customer_home')
        elif user.user_type == 'delivery':
            return reverse('delivery_dashboard')
        elif user.user_type == 'callcenter':
            return reverse('callcenter_dashboard')
        elif user.user_type == 'admin':
            return reverse('admin_dashboard')

        return reverse('default_home')  # مسار افتراضي في حال لم يتم تحديد نوع






@login_required
@pharmacy_required
def pharmacy_dashboard(request):
    user = request.user
    
    if user.user_type != 'pharmacy':
        return render(request, 'not_authorized.html')  # أو يمكنك إعادة توجيه المستخدم
    
    pharmacy = get_object_or_404(Pharmacy, user=user)

    context = {
        'pharmacy_name': pharmacy.name,
        'phone_number': user.phone_number,
        'pharmacy_address': pharmacy.address,
        'pharmacy_license_number': pharmacy.license_number,


    }

    return render(request, 'pharmacy/dashboard.html', context)
