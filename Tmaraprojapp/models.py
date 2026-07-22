from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from .utils import *

from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Client(models.Model):
	TYPE=(
		('starter', 'starter'),
		('savings', 'savings'),
		('standard', 'standard'),
		('premium', 'premium'),
		('current', 'current'),
		)
	CURRENCY= (
	    ('USD', 'USD'),
	    ('EUR', 'EUR'),
	    ('CAD', 'CAD'),
	    ('GBP', 'GBP'),
	    )
	user= models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	first_name= models.CharField(max_length=200, null=True)
	last_name= models.CharField(max_length=200, null=True)
	home_address= models.CharField(default="Update your account", max_length=200, null=True)
	phone= models.CharField(default="Update your account", max_length=200, null=True)
	email= models.CharField(max_length=200, null=True)
	account_number= models.CharField(max_length=12, blank=True)
	account_type= models.CharField(max_length= 200, null=True, choices=TYPE, default='starter')
	account_currency= models.CharField(max_length=200, null=True, blank=True, choices=CURRENCY, default='EUR')
	account_status= models.BooleanField(default=True, null=True, blank=True)
	transfer_pin= models.CharField(max_length= 4, null=True, blank=True)
	deposit= models.FloatField(default=0, null=True, blank=True)
	uncleared_balance= models.FloatField(default=0, null=True)
	total_loan= models.FloatField(default=0, null=True)
	profile_pic= models.ImageField(null=True, blank=True)
	active_transfer= models.BooleanField(default=True)
	date_created= models.DateTimeField(auto_now_add=True, null=True)
	suspicious_activity = models.BooleanField(default=False)
	account_blocked = models.BooleanField(default=False)
	blocked_reason = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return self.user.username

	@property
	def profile_picUrl(self):
		try:
			url= self.profile_pic.url
		except:
			url=''
		return url

	def save(self, *args, **kwargs):
		if self.account_number == '':
			account_number= generate_account_number()
			self.account_number= account_number
		super().save(*args, **kwargs)

class History(models.Model):
	client= models.ForeignKey(Client, null=True, on_delete= models.CASCADE)
	account_number= models.CharField(max_length=12, null=True, blank=True)
	account_name= models.CharField(max_length=12, null=True, blank=True)
	amount= models.FloatField(null=True, blank=True)

	def __str__(self):
		return self.client.first_name

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        print(f"created_at: {self.created_at} (tzinfo: {self.created_at.tzinfo})")
        print(f"now: {timezone.now()} (tzinfo: {timezone.now().tzinfo})")

        created = self.created_at
        if timezone.is_naive(created):
            print("created_at is naive! Making it aware...")
            created = timezone.make_aware(created, timezone.get_current_timezone())

        return timezone.now() > created + datetime.timedelta(minutes=5)

    def __str__(self):
        return self.user.username

class Transaction(models.Model):
	client= models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
	destination_account_number= models.CharField(max_length=12, null=True, blank=True)
	destination_account_name= models.CharField(max_length=65, null=True, blank=True)
	destination_account_email= models.CharField(max_length=65, null=True, blank=True)
	amount= models.FloatField(null=True, blank=True)

	def __str__(self):
		return self.client.first_name

class Otp(models.Model):
	otp_code= models.CharField(max_length=6, null=True, blank=True)

	def __str__(self):
		return self.otp_code

class Foreign_transaction(models.Model):
	client= models.ForeignKey(Client, null=True, on_delete= models.SET_NULL)
	bank_name= models.CharField(max_length=80, null=True, blank=True)
	country= models.CharField(max_length=80, null=True, blank=True)
	account_number= models.CharField(max_length=80, null=True, blank=True)
	account_name= models.CharField(max_length=80, null=True, blank=True)
	bank_code= models.CharField(max_length=80, null=True, blank=True)
	routing_number= models.CharField(max_length=80, null=True, blank=True)
	amount= models.FloatField(null=True, blank=True)

	def __str__(self):
		return self.client


class SecurityQuestion(models.Model):
	client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='security_questions')
	mothers_maiden_name = models.CharField(max_length=255, blank=True, null=True)
	home_address_answer = models.CharField(max_length=255, blank=True, null=True)
	next_of_kin = models.CharField(max_length=255, blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)

	FIELDS = ['mothers_maiden_name', 'home_address_answer', 'next_of_kin']

	def is_blank(self):
		return not any(getattr(self, f) for f in self.FIELDS)

	def set_answers(self, answers: dict):
		for f in self.FIELDS:
			if answers.get(f):
				setattr(self, f, make_password(answers[f].strip().lower()))

	def check_answers(self, answers: dict) -> bool:
		for f in self.FIELDS:
			stored = getattr(self, f)
			given = (answers.get(f) or '').strip().lower()
			if not stored or not check_password(given, stored):
				return False
		return True

	def __str__(self):
		return f"Security questions for {self.client}"

