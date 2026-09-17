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
	active_transfer= models.BooleanField(default=False)
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
	STATUS = (
		('pending_review', 'Pending Review'),
		('approved', 'Approved'),
		('declined', 'Declined'),
	)
	client= models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
	destination_account_number= models.CharField(max_length=12, null=True, blank=True)
	destination_account_name= models.CharField(max_length=65, null=True, blank=True)
	destination_account_email= models.CharField(max_length=65, null=True, blank=True)
	amount= models.FloatField(null=True, blank=True)
	date_created= models.DateTimeField(auto_now_add=False, null=True)

	status = models.CharField(max_length=20, choices=STATUS, default='pending_review')
	reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_transactions')
	reviewed_at = models.DateTimeField(null=True, blank=True)
	is_reversal = models.BooleanField(default=False)
	reversal_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reversal')

	def __str__(self):
		return self.client.first_name

class Otp(models.Model):
	otp_code= models.CharField(max_length=6, null=True, blank=True)

	def __str__(self):
		return self.otp_code

class Foreign_transaction(models.Model):
	STATUS = (
		('pending_review', 'Pending Review'),
		('approved', 'Approved'),
		('declined', 'Declined'),
	)
	client= models.ForeignKey(Client, null=True, on_delete= models.SET_NULL)
	bank_name= models.CharField(max_length=80, null=True, blank=True)
	country= models.CharField(max_length=80, null=True, blank=True)
	account_number= models.CharField(max_length=80, null=True, blank=True)
	account_name= models.CharField(max_length=80, null=True, blank=True)
	bank_code= models.CharField(max_length=80, null=True, blank=True)
	routing_number= models.CharField(max_length=80, null=True, blank=True)
	amount= models.FloatField(null=True, blank=True)
	date_created= models.DateTimeField(auto_now_add=False, null=True)

	status = models.CharField(max_length=20, choices=STATUS, default='pending_review')
	reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_foreign_transactions')
	reviewed_at = models.DateTimeField(null=True, blank=True)
	is_reversal = models.BooleanField(default=False)
	reversal_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reversal')

	def __str__(self):
		return self.client.first_name


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


class Payee(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payees')
	name = models.CharField(max_length=200)
	sort_code = models.CharField(max_length=8, blank=True, null=True)  # "20-00-00"
	account_number = models.CharField(max_length=20)
	reference = models.CharField(max_length=200, blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

	@property
	def masked_account(self):
		if self.account_number and len(self.account_number) >= 4:
			return f"****{self.account_number[-4:]}"
		return self.account_number


class StandingOrder(models.Model):
	FREQUENCY = (
		('weekly', 'Weekly'),
		('monthly', 'Monthly'),
		('yearly', 'Yearly'),
	)
	client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='standing_orders')
	payee = models.ForeignKey(Payee, on_delete=models.CASCADE, related_name='standing_orders')
	amount = models.FloatField()
	reference = models.CharField(max_length=200, blank=True, null=True)
	first_payment_date = models.DateField()
	next_payment_date = models.DateField()
	frequency = models.CharField(max_length=20, choices=FREQUENCY, default='monthly')
	end_date = models.DateField(null=True, blank=True)  # null = "Never" ends
	is_active = models.BooleanField(default=True)
	date_created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.payee.name} - £{self.amount} ({self.frequency})"