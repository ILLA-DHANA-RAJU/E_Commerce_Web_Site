from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User




def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/homebase.html',{'products':products,'product_count_in_cart':product_count_in_cart})
    

#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
from django.shortcuts import render
from django.db.models import Sum
from .models import Customer, Product, Orders

def admin_dashboard_view(request):
    total_customers = Customer.objects.count()
    total_orders = Orders.objects.count()
    total_products = Product.objects.count()

    total_revenue = Orders.objects.filter(
        status='Delivered',
        total_price__isnull=False
    ).aggregate(total=Sum('total_price'))['total'] or 0

    pending_orders = Orders.objects.filter(status='Pending').count()

    # Active customers based on having orders
    active_customers = Customer.objects.filter(orders__isnull=False).distinct().count()

    context = {
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'active_customers': active_customers,  # ⭐ Added here
    }

    return render(request, 'ecom/admin_dashboard.html', context)



# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')




@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = Customer.objects.get(id=pk)
    user = customer.user  # Access related AdminUser

    if request.method == 'POST':
        userForm = forms.AdminUserForm(request.POST, request.FILES, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)

        if userForm.is_valid() and customerForm.is_valid():
            userForm.save()
            customerForm.save()
            return redirect('view-customer')
    else:
        userForm = forms.AdminUserForm(instance=user)
        customerForm = forms.CustomerForm(instance=customer)

    context = {
        'userForm': userForm,
        'customerForm': customerForm
    }

    return render(request, 'ecom/admin_update_customer.html', context=context)



# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})


# admin add product by clicking on floating button

from django.shortcuts import render, redirect
from .forms import ProductForm

@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    form = ProductForm()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin-products')  # or any page after successful submission

    return render(request, 'ecom/admin_add_products.html', {'productForm': form})



@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from . import models, forms

@login_required(login_url='adminlogin')
def update_product_view(request, pk):
    product = get_object_or_404(models.Product, id=pk)
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            messages.success(request, "Product updated successfully!")
            return redirect('admin-products')
    else:
        productForm = forms.ProductForm(instance=product)
    
    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Orders

@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders = Orders.objects.select_related('customer__user', 'product').all().order_by('-id')
    
    # Filter out invalid orders (e.g., without product or customer)
    valid_orders = [order for order in orders if order.customer and order.product and order.id]

    return render(request, 'ecom/admin_view_booking.html', {'data': valid_orders})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderStatusForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderStatusForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products= models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response



# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ecom.models import Product


@login_required(login_url='customerlogin')
def customer_home_view(request):
    # Fetch all products from the database
    products = models.Product.objects.all()
    
    # Initialize cart count

    # Check if product_ids cookie exists
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_list = list(set(product_ids.split('|')))
        product_count_in_cart = len(product_id_list)
    else:
        product_count_in_cart = 0

    # Render the customer home template with products and cart count
    return render(request, 'ecom/customer_home.html', {
        'products': products,
        'product_count_in_cart': product_count_in_cart
    })



# shipment address before placing order
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import forms, models

@login_required(login_url='customerlogin')
def customer_address_view(request):
    product_in_cart = False
    product_ids = request.COOKIES.get('product_ids')

    if product_ids:
        product_in_cart = True
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    addressForm = forms.AddressForm()

    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['email']
            mobile = addressForm.cleaned_data['mobile']
            address = addressForm.cleaned_data['address']
            city = addressForm.cleaned_data['city']
            state = addressForm.cleaned_data['state']
            zipcode = addressForm.cleaned_data['zipcode']

            # Save to DB
            models.Address.objects.create(
                user=request.user,
                email=email,
                mobile=mobile,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode
            )

            # Total Price Calculation
            total = 0
            if product_ids:
                product_id_in_cart = product_ids.split('|')
                products = models.Product.objects.filter(id__in=product_id_in_cart)
                for p in products:
                    total += p.price

            # Set cookies and go to payment
            response = render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            response.set_cookie('city', city)
            response.set_cookie('state', state)
            response.set_cookie('zipcode', zipcode)
            return response

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart
    })




# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import models

@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)

    # Get product IDs from cookies
    product_ids = request.COOKIES.get('product_ids')
    if not product_ids:
        messages.warning(request, "Your cart is empty. Payment not processed.")
        return redirect('customer_cart')

    # Extract product objects
    product_id_list = product_ids.split('|')
    products = models.Product.objects.filter(id__in=product_id_list)

    if not products.exists():
        messages.warning(request, "No products found in cart. Payment not processed.")
        return redirect('customer_cart')

    # Get address info
    email = request.COOKIES.get('email')
    mobile = request.COOKIES.get('mobile')
    address = request.COOKIES.get('address')

    for product in products:
        models.Orders.objects.create(
            customer=customer,
            product=product,
            email=email,
            mobile=mobile,
            address=address,
            status='Order Placed'
        )

    response = render(request, 'ecom/payment_success.html')
    
    # Clear cart cookies after success
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import models

@login_required(login_url='customerlogin')
def customer_cart_view(request):
    product_ids = request.COOKIES.get('product_ids')
    
    if product_ids:
        product_id_list = product_ids.split('|')
        products = models.Product.objects.filter(id__in=product_id_list)

        total = sum([product.price for product in products])
        
        return render(request, 'ecom/customer_cart.html', {
            'products': products,
            'total': total
        })
    else:
        return render(request, 'ecom/customer_cart.html', {
            'products': [],
            'total': 0
        })





@login_required(login_url='customerlogin')
def my_order_view(request):
    
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})
 



# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})    



#--------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()

    # Use utf-8 encoding to support Unicode properly
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result, encoding='utf-8')

    if not pdf.err:
        # Wrap the result in a HttpResponse with proper headers
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


from django.contrib.auth.decorators import login_required
from . import models

@login_required(login_url='customerlogin')
def download_invoice_view(request, orderID, productID):
    order = models.Orders.objects.get(id=orderID)
    product = models.Product.objects.get(id=productID)

    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,
        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,
    }

    return render_to_pdf('ecom/download_invoice.html', mydict)





@login_required(login_url='customerlogin')
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


from django.contrib.auth import get_user_model
User = get_user_model()



@login_required(login_url='customerlogin')
def edit_profile_view(request):
    customer = models.Customer.objects.get(user=request.user)
    user = request.user
    # now this is correct, as request.user IS your AdminUser
    userForm = forms.CustomerForm(instance=request.user)
    customerForm = forms.CustomerForm(instance=customer)

    if request.method == 'POST':
        userForm = forms.CustomerForm(request.POST, instance=request.user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            userForm.save()
            customerForm.save()
            return redirect('edit_profile')

    return render(request, 'ecom/edit_profile.html', {
        'userForm': userForm,
        'customerForm': customerForm,
    })


#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'ecom/aboutus.html')


from .forms import ContactusForm
from .models import ContactUs

def contact_view(request):
    if request.method == 'POST':
        form = ContactusForm(request.POST)
        if form.is_valid():
            ContactUs.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message']
            )
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return redirect('contact')
    else:
        form = ContactusForm()
    return render(request, 'ecom/contactus.html', {'form': form})



# Create your views here.
@login_required(login_url='customerlogin')
def chatbot(request):
    return render(request, "ecom/chatbot.html")


def chatbot_response(request):
    user_message = request.GET.get("message", "").strip().lower()

    responses = {
        "hello": "Hi there! How can I help you?",
        "how are you": "I'm just a bot, but I'm doing great! How about you?",
        "what is your name": "I'm your friendly chatbot!",
        "bye": "Goodbye! Have a nice day!",
    }

    bot_response = responses.get(user_message, "I'm not sure how to respond to that.")

    return JsonResponse({"response": bot_response})

#my_profile code in views

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Customer


@login_required
def edit_profile(request):
    if request.method == "POST":
        customer = Customer.objects.get(user=request.user)
        customer.address = request.POST.get("address")
        customer.mobile = request.POST.get("mobile")
        
        if "profile_pic" in request.FILES:
            customer.profile_pic = request.FILES["profile_pic"]
        
        customer.save()
        return redirect("customer-profile")

    return render(request, "ecom/edit_profile.html")


# logout section connection

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('ecom/logout.html')  # Redirect to login page


#customers page connection

from django.shortcuts import render

def customer_home(request):
    return render(request, 'ecom/customer_home.html')

# add product by admin

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProductForm

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("admin-add-product")  # Redirect to the same page after submission
    else:
        form = ProductForm()
    
    return render(request, "ecom/admin_add_product.html", {"productForm": form})

# ecom/views.py



# Home Views

def home_view(request):
    return render(request, "ecom/homebase.html")

def home(request):
    return render(request, "ecom/customer_home.html")




# Admin Views

# ecom/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db import IntegrityError

from .forms import (
    UserForm, AdminUserForm, AdminLoginForm,
    CustomerForm
)
from .models import AdminUser, Customer


# -------------------- Admin Signup -------------------- #

from django.contrib.auth import login
from .forms import AdminUserForm  # Ensure this is for AdminUser creation

def admin_signup_view(request):
    if request.method == 'POST':
        form = AdminUserForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the admin user
            admin_user = form.save(commit=False)
            admin_user.set_password(form.cleaned_data['password'])
            admin_user.save()
            login(request, admin_user)  # Optional: Log the admin in
            messages.success(request, 'Admin account created successfully!')
            return redirect('adminlogin')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminUserForm()
    return render(request, 'ecom/adminsignup.html', {'adminForm': form})


# -------------------- Admin Login -------------------- #

def admin_login_view(request):
    form = AdminLoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and AdminUser.objects.filter(username=username).exists():
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, "Invalid credentials or not an admin user.")
    return render(request, 'ecom/adminlogin.html', {'form': form})



# -------------------- Admin Dashboard -------------------- #
@login_required(login_url='adminlogin')
def admin_dashboard_views(request):
    if not AdminUser.objects.filter(username=request.user.username).exists():
        return redirect('adminlogin')
    return render(request, 'ecom/admin_dashboard.html')


# -------------------- Admin Logout -------------------- #
from django.contrib.auth import logout
from django.shortcuts import redirect

def admin_logout_view(request):
    logout(request)  # Ends session, logs out
    return redirect('adminlogin')  # No DB access here




# -------------------- Customer Signup -------------------- #
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserForm, CustomerForm, CustomerLoginForm
from .models import Customer, Product

def customer_signup_view(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        customer_form = CustomerForm(request.POST, request.FILES)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)  # Hash the password
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            messages.success(request, "Account created successfully! Please log in.")
            return redirect('ecom/customerlogin.html')  # Update this with your actual login URL name

        else:
            messages.error(request, "Something went wrong. Please check the form.")

    else:
        user_form = UserForm()
        customer_form = CustomerForm()

    return render(request, 'ecom/customersignup.html', {
        'user_form': user_form,
        'customer_form': customer_form,
    })


# -------------------- Customer Login -------------------- #
def customer_login_view(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                try:
                    customer = Customer.objects.get(user=user)
                    login(request, user)
                    return redirect('customer_home')  # Make sure this URL name exists
                except Customer.DoesNotExist:
                    messages.error(request, 'You are not registered as a customer.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = CustomerLoginForm()

    return render(request, 'ecom/customerlogin.html', {'form': form})


# -------------------- Customer Dashboard -------------------- #
@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    try:
        customer = Customer.objects.get(user=request.user)
        return render(request, 'ecom/customer_home.html', {'customer': customer})
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found')
        return redirect('ecom/customerlogin.html')


# -------------------- Logout -------------------- #
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('customerlogin')  # or 'adminlogin' depending on the user type


