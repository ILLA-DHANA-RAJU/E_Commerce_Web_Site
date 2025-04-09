from django import forms
from django.contrib.auth import get_user_model
from .models import Customer, AdminUser, Product, Orders, Feedback, ContactUs

User = get_user_model()

# -------------------- Auth Forms -------------------- #

class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Admin Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

class CustomerLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

# -------------------- Signup Forms -------------------- #

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# -------------------- Profile Forms -------------------- #

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['address', 'mobile', 'profile_pic']

from django import forms
from .models import AdminUser

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = AdminUser
        fields = ['username', 'email', 'password', 'profile_pic', 'mobile']


# -------------------- Product & Order Forms -------------------- #

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price','description', 'stock', 'category', 'product_image']

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['status']

# -------------------- Contact & Feedback Forms -------------------- #

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'feedback']

class ContactusForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Phone Number (Optional)'
        })
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message'
        })
    )


#------------------- Address details ----------------#
# forms.py
from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['email', 'address', 'city', 'state', 'zipcode', 'mobile']
