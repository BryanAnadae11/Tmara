from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import *

class ContactForm(forms.Form):
	name= forms.CharField(label='Full Name', widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
	email= forms.EmailField(label='Email Address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
	message= forms.CharField(label='Message', widget=forms.Textarea(attrs={'placeholder': 'Hi, I would love to work with you on my project...'}))

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ClientForm(ModelForm):
	class Meta:
		model= Client
		fields= '__all__'
		exclude=['user']

class ClientUserForm(ModelForm):
	class Meta:
		model= Client
		fields= '__all__'
		exclude= ['user', 'account_number', 'account_type', 'account_status', 'deposit', 'uncleared_balance', 'total_loan', 'date_created', 'account_currency', 'active_transfer']

class OTPForm(forms.Form):
    otp = forms.CharField(label='Enter OTP', max_length=6)


class SecurityQuestionSetupForm(forms.Form):
	mothers_maiden_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
	home_address_answer = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
	next_of_kin = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))


class SecurityQuestionVerifyForm(forms.Form):
	mothers_maiden_name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
	home_address_answer = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
	next_of_kin = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
