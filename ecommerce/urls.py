"""
Developed By : Keerthi
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from ecom import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('adminsignup/', views.admin_signup_view, name='adminsignup'),
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path('admin_dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin_dashboard/', views.admin_dashboard_views, name='admin_dashboard'),
    path('adminlogout/', views.admin_logout_view, name='adminlogout'),

    path('admin_products/', views.admin_products_view, name='admin-products'),
    path('admin_add_product/', views.admin_add_product_view, name='admin-add-product'),
    path('delete-product/<int:pk>/', views.delete_product_view, name='delete-product'),
    path('update_order/<int:pk>/', views.update_order_view, name='update_order'),
    path('admin-view-booking/', views.admin_view_booking_view, name='admin-view-booking'),
    path('delete-order/<int:pk>/', views.delete_order_view, name='delete-order'),
    path('update-order/<int:pk>/', views.update_order_view, name='update-order'),

    # Customer Management
    path('view-customer/', views.view_customer_view, name='view-customer'),
    path('delete-customer/<int:pk>/', views.delete_customer_view, name='delete-customer'),
    path('update-customer/<int:pk>/', views.update_customer_view, name='update-customer'),

    # Authentication
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('logout/', views.logout_view, name='logout'),
    path('customersignup/', views.customer_signup_view, name='customersignup'),
    path('customerlogin/', views.customer_login_view, name='customerlogin'),
    path('customer_home/', views.customer_home_view, name='customer_home'),


    # Customer Dashboard
    path('customer_home/', views.customer_dashboard_view, name='customer_home'),
    path('customer_home/', views.home, name='customer_home'),
    path('my_order/', views.my_order_view, name='my_order'),
    path('my_profile/', views.my_profile_view, name='my_profile'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('download_invoice/<int:orderID>/<int:productID>/', views.download_invoice_view, name='download-invoice'),

    # E-commerce functionalities
    path('add_to_cart/<int:pk>/', views.add_to_cart_view, name='add-to-cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/', views.customer_cart_view, name='customer_cart'),
    path('remove_from_cart/<int:pk>/', views.remove_from_cart_view, name='remove-from-cart'),
    path('customer_address/', views.customer_address_view, name='customer_address'),
    path('payment_success/', views.payment_success_view, name='payment_success'),

    # Chatbot
    path('chatbot/', views.chatbot, name="chatbot"),
    path('chatbot/response/', views.chatbot_response, name='chatbot_response'),

    # General Pages
    path('', views.home_view, name='home'),
    path('aboutus/', views.aboutus_view, name='aboutus'),
    path('contactus/', views.contact_view, name='contactus'),
    path('search/', views.search_view, name='search'),
    path('send_feedback/', views.send_feedback_view, name='send-feedback'),
    path('view_feedback/', views.view_feedback_view, name='view-feedback'),

    path('logout/', views.user_logout, name='logout')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)