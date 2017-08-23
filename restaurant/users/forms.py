from django.contrib.auth.models import User
from .models import Customer, Staff
from django import forms
from django.forms import ModelForm


class UserForm(ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	confirm_password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields= ('first_name','last_name','email','username','password')

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = ('balance',)

class StaffForm(ModelForm):
	class Meta:
		model = Staff
		fields = ('salary','user_type')

class AddressForm(forms.Form):
	street = forms.CharField(max_length=50, required=True)
	city = forms.CharField(max_length=15, required=True)
	state = forms.CharField(max_length=2, required=True)
	zipcode = forms.IntegerField(required=True)
