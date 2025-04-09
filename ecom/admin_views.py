# ecom/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.db import transaction
from . import forms, models
from datetime import datetime, timedelta
import csv
from ecom.forms import AdminSignupForm, AdminLoginForm, AdminDetailsForm



# ======================
# UTILITY FUNCTIONS
# ======================
def is_admin(user):
    """Check if user has admin privileges"""
    return user.is_authenticated and user.is_staff

def validate_admin_access(view_func):
    """Decorator to validate admin access"""
    @login_required(login_url='admin-login')
    @user_passes_test(is_admin)
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(request, "You don't have admin privileges")
            return redirect('admin-login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ======================
# AUTHENTICATION VIEWS
# ======================
def admin_signup_view(request):
    """Handle admin registration"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin-dashboard')

    if request.method == 'POST':
        form = forms.AdminUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    
                    admin_group, _ = Group.objects.get_or_create(name='ADMIN')
                    admin_group.user_set.add(user)
                    
                    messages.success(request, 'Admin account created successfully!')
                    return redirect('admin-login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = forms.AdminUserForm()

    return render(request, 'ecom/adminsignup.html', {'form': form})

def admin_login_view(request):
    """Handle admin login"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('admin-dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user and is_admin(user):
            login(request, user)
            next_url = request.GET.get('next', 'admin-dashboard')
            return redirect(next_url)
        messages.error(request, 'Invalid credentials or insufficient privileges')

    return render(request, 'ecom/adminlogin.html')

@validate_admin_access
def admin_logout_view(request):
    """Handle admin logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('admin-login')

# ======================
# DASHBOARD VIEWS
# ======================
@validate_admin_access
def admin_dashboard_view(request):
    """Admin dashboard with analytics"""
    try:
        # Basic statistics
        stats = {
            'customers': models.Customer.objects.count(),
            'products': models.Product.objects.count(),
            'orders': models.Orders.objects.count(),
            'revenue': models.Orders.objects.aggregate(
                total_revenue=Sum('product__price')
            )['total_revenue'] or 0
        }

        # Recent orders
        recent_orders = models.Orders.objects.select_related(
            'customer', 'product'
        ).order_by('-order_date')[:5]

        # Sales data for charts
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        sales_data = models.Orders.objects.filter(
            order_date__range=[start_date, end_date]
        ).values('order_date__date').annotate(
            total_orders=Count('id'),
            daily_revenue=Sum('product__price')
        ).order_by('order_date__date')

        context = {
            'stats': stats,
            'recent_orders': recent_orders,
            'sales_data': list(sales_data),
        }
        return render(request, 'ecom/admin_dashboard.html', context)
    
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('admin-dashboard')

# ======================
# CUSTOMER MANAGEMENT
# ======================
@validate_admin_access
def customer_management_view(request):
    """Manage customers with search functionality"""
    try:
        search_query = request.GET.get('q', '')
        customers = models.Customer.objects.select_related('user')
        
        if search_query:
            customers = customers.filter(
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(mobile__icontains=search_query)
            )
        
        return render(request, 'ecom/admin_customers.html', {
            'customers': customers,
            'search_query': search_query
        })
    except Exception as e:
        messages.error(request, f'Error loading customers: {str(e)}')
        return redirect('admin-dashboard')

# ... [Include all other views with similar error handling and structure] ...

# ======================
# ORDER STATUS UPDATE (AJAX)
# ======================
@validate_admin_access
def update_order_status(request):
    """Handle AJAX order status updates"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            
            if not order_id or not new_status:
                return JsonResponse({
                    'success': False, 
                    'error': 'Missing parameters'
                }, status=400)

            order = models.Orders.objects.get(id=order_id)
            order.status = new_status
            order.save()
            
            return JsonResponse({
                'success': True,
                'new_status': order.get_status_display()
            })
            
        except models.Orders.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Order not found'
            }, status=404)
            
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'Invalid request'
    }, status=400)


#New codes
#admin sign up

def admin_signup_view(request):
    if request.method == "POST":
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, "Admin registered successfully! Please log in.")
            return redirect('admin-login')
        else:
            messages.error(request, "Registration failed. Please check your details.")
    else:
        form = AdminUserForm()
    
    return render(request, 'ecom/adminsignup.html', {'form': form})

#admin login

def admin_login_view(request):
    if request.user.is_authenticated and is_admin(request.user):
        return redirect("admin-dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin-dashboard")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "ecom/adminlogin.html")

