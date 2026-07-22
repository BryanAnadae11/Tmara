from django.shortcuts import render, redirect

from django.core.mail import BadHeaderError, send_mail

from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from django.core.mail import EmailMessage

from django.conf import settings

from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login, logout

from django.utils.html import strip_tags

from django.core.mail import EmailMultiAlternatives

import random

from django.contrib.auth.decorators import login_required

from django.contrib.admin.views.decorators import staff_member_required

from .forms import *

from django.utils import timezone

from .decorators import check_account_status

# Create your views here.

def home(request):
	return render(request, 'Tmaraprojapp/index.html')

def current(request):
	return render(request, 'Tmaraprojapp/current.html')

def kid(request):
	return render(request, 'Tmaraprojapp/kid.html')

def premium(request):
	return render(request, 'Tmaraprojapp/premium.html')

def saving(request):
	return render(request, 'Tmaraprojapp/saving.html')

def corporate(request):
	return render(request, 'Tmaraprojapp/corporate.html')

def career(request):
	return render(request, 'Tmaraprojapp/career.html')

def insurance(request):
	return render(request, 'Tmaraprojapp/insurance.html')

def faq(request):
	return render(request, 'Tmaraprojapp/faq.html')

def card(request):
	return render(request, 'Tmaraprojapp/card.html')


def contact(request):
	if request.method == 'GET':
		form= ContactForm()
	else:
		form = ContactForm(request.POST or None)
		if form.is_valid():
			name= form.cleaned_data['name']
			email= form.cleaned_data['email']
			message= form.cleaned_data['message']
			print(name)
		try:
			send_mail(name, "User with name {} and email {} has sent a message saying: {}".format(name, email, message),email, [''])
			print('Message Sent')
		except:
			print('Message not sent')
			messages.error(request, 'Message Not sent, Try again later.')
		messages.success(request, 'Your message has been sent successfully')
	context={'form':form}
	return render(request, 'Tmaraprojapp/contact.html', context)


def about(request):
	return render(request, 'Tmaraprojapp/about.html')


def news(request):
	return render(request, 'Tmaraprojapp/news.html')

@login_required(login_url='clientsignin')
@check_account_status
def dashboard(request):
	if request.user.is_staff:
		return redirect('admindashboard')
	else:
		client= request.user.client
		clientAccountNumber= client.account_number
		clientAccountType= client.account_type
		clientAccountCurrency= client.account_currency
		clientBalance= float(client.deposit) + float(client.uncleared_balance)
	context={'clientAccountNumber':clientAccountNumber, 'clientAccountType':clientAccountType, 'clientBalance':clientBalance, 'clientAccountCurrency':clientAccountCurrency}
	return render(request, 'Tmaraprojapp/clientdashboard.html', context)

@login_required(login_url='clientsignin')
def account_settings(request):
	client= request.user.client
	form= ClientUserForm(instance=client)
	if request.method=='POST':
		form= ClientUserForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()
	context= {'form':form}
	return render(request, 'Tmaraprojapp/clientaccountsettings.html', context)

@login_required(login_url='clientsignin')
def fundtransfer(request):
	client= request.user.client
	clientAccountNumber= client.account_number
	clientAccountType= client.account_type
	clientAccountCurrency= client.account_currency
	canClientTransfer = client.active_transfer
	clientBalance= float(client.deposit) + float(client.uncleared_balance)
	if request.method == 'POST' and canClientTransfer == True:
		destination_account_name= request.POST.get('account_name')
		destination_bank_name= request.POST.get('bank_name')
		destination_bank_code= request.POST.get('bank_code')
		destination_bank_routing_number= request.POST.get('routing_number')
		destination_country= request.POST.get('country')
		destination_account_number= request.POST.get('account_number')
		amount= request.POST.get('amount')
		transfer_pin= request.POST.get('transfer_pin')
		if float(client.deposit) > float(amount):
			client_transfer_pin= client.transfer_pin
			if str(client_transfer_pin) == str(transfer_pin):
				Foreign_transaction.objects.create(
					client= client,
					bank_name= destination_bank_name,
					country= destination_country,
					account_name=destination_account_name,
					bank_code=destination_bank_code,
					routing_number=destination_bank_routing_number,
					account_number= destination_account_number,
					amount= amount,
					)
				return redirect('foreign_transaction')
			else:
				return HttpResponse('Incorrect transfer pin. Try setting a transfer pin in your account settings')
		else:
			return HttpResponse('Your balance is too low to complete this transaction')
	else:
		return HttpResponse('Invalid Transfer Request. Please Contact Support')

	context={'clientAccountNumber':clientAccountNumber, 'clientAccountType':clientAccountType, 'clientBalance':clientBalance, 'clientAccountCurrency':clientAccountCurrency}
	return render(request, 'Tmaraprojapp/clienttransferpage.html', context)

@login_required(login_url='clientsignin')
def foreign_transaction(request):
	client= request.user.client
	client_deposit= client.deposit
	client_username= client.first_name
	email= client.email
	client_pk= client.id
	client_email= client.email
	canClientTransfer = client.active_transfer
	otp= list(Otp.objects.all())
	otp_code= random.choice(otp)
	foreign_transaction= Foreign_transaction.objects.filter(client=client)
	foreign_transaction_number= foreign_transaction.count()
	last_foreign_transaction= foreign_transaction.last()
	template= render_to_string('Tmaraprojapp/otp.html', {'name':client_username, 'otp':otp_code})
	plain_message= strip_tags(template)
	email_message= EmailMultiAlternatives(
		'Transaction alert on your account!',
		template,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	email_message.attach_alternative(template, 'text/html')
	email_message.send()

	if request.method == 'POST' and canClientTransfer:
		otp= request.POST.get('otp')
		try:
			otp_check= Otp.objects.get(otp)
			foreign_transaction= Foreign_transaction.objects.filter(client=client)
			foreign_transaction_number= foreign_transaction.count()
			last_foreign_transaction= foreign_transaction.last()
		except:
		    pass
		if foreign_transaction and float(foreign_transaction_number):
			amount_sent= last_foreign_transaction.amount
			bank_name= last_foreign_transaction.bank_name
			account_number= last_foreign_transaction.account_number
			client_new_balance= float(client_deposit) - float(amount_sent)
			client_details= Client.objects.filter(id=client_pk)
			client_details.update(deposit=client_new_balance)
			debit_alert_template= render_to_string('Tmaraprojapp/foreign_debit_alert.html', {'name':client_username, 'amount':amount_sent, 'client_balance':client_new_balance})
			email_message= EmailMessage(
				'Debit alert on your account',
				debit_alert_template,
				settings.EMAIL_HOST_USER,
				[client_email],
				)
			email_message.fail_silently=False
			email_message.send()
			return render(request, 'Tmaraprojapp/transaction_proof.html', {'amount_sent':amount_sent, 'bank_name':bank_name, 'account_number':account_number})
		else:
			return HttpResponse('We locked your account due to suspicious activity. Please contact support')
	else:
		return HttpResponse('Invalid Transfer Request. Please Contact Support')
	context={}
	return render(request, 'Tmaraprojapp/foreign_transaction.html', context)

def transactionhistory(request):
	client= request.user.client
	clientAccountNumber= client.account_number
	clientAccountType= client.account_type
	clientAccountCurrency= client.account_currency
	clientBalance= float(client.deposit) + float(client.uncleared_balance)
	transactions= Foreign_transaction.objects.filter(client=client)
	context={'clientAccountNumber':clientAccountNumber, 'clientAccountType':clientAccountType, 'clientBalance':clientBalance,
	'clientAccountCurrency':clientAccountCurrency, 'transactions':transactions}
	return render(request, 'Tmaraprojapp/clienttransactionhistorypage.html', context)


@login_required
def account_questions_validate(request):
	client = request.user.client
	sq, _ = SecurityQuestion.objects.get_or_create(client=client)
	first_time = sq.is_blank()
	FormClass = SecurityQuestionSetupForm if first_time else SecurityQuestionVerifyForm

	if request.method == 'POST':
		form = FormClass(request.POST)
		if form.is_valid():
			if first_time:
				sq.set_answers(form.cleaned_data)
				sq.save()
				client.suspicious_activity = False
				client.save()
				return redirect('dashboard')

			if sq.check_answers(form.cleaned_data):
				client.suspicious_activity = False
				client.save()
				return redirect('dashboard')
			else:
				client.account_blocked = True
				client.blocked_reason = "Failure to verify account"
				client.save()
				return redirect('blocked_account')
	else:
		form = FormClass()

	template = 'account_questions_setup.html' if first_time else 'account_questions_verify.html'
	return render(request, template, {'form': form, 'first_time': first_time})


@login_required(login_url='clientsignin')
@staff_member_required
def admindashboard(request):
	clients= Client.objects.all()
	context={'clients':clients}
	return render(request, 'Tmaraprojapp/admindashboard.html', context)

@login_required(login_url='clientsignin')
@staff_member_required
def admincreateaccount(request):
	form= CreateUserForm()
	if request.method == 'POST':
		form= CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			firstName= form.cleaned_data.get('first_name')
			email= form.cleaned_data.get('email')
			print(firstName)
			template= render_to_string('Tmaraprojapp/WelcomeEmail2.html', {'name':firstName})
			plain_message= strip_tags(template)
			email_message= EmailMultiAlternatives(
				'Welcome on board to Valon Global',
				plain_message,
				settings.EMAIL_HOST_USER,
				[email]

				)
			email_message.attach_alternative(template, 'text/html')
			email_message.send()
			return redirect('admindashboard')
	context={'form':form}
	return render(request, 'Tmaraprojapp/admincreateaccountpage.html', context)

@login_required(login_url='clientsignin')
@staff_member_required
def admingotouserprofile(request, pk):
	client= Client.objects.get(id=pk)
	form= ClientForm(instance=client)
	if request.method=='POST':
		form= ClientForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()
	context= {'form':form}
	return render(request, 'Tmaraprojapp/admingotouserprofilepage.html', context)

@login_required(login_url='clientsignin')
@staff_member_required
def admincreditaccount(request, pk):
	client= Client.objects.get(id=pk)
	client_deposit= client.deposit
	client_id= client.id
	firstName= client.first_name
	email= client.email
	acc_currency= client.account_currency
	if request.method == 'POST':
		amount= request.POST.get('amount')
		if amount:
			newacc_bal= float(client_deposit) + float(amount)
			client_info= Client.objects.filter(id=client_id)
			client_info.update(deposit=newacc_bal)
			template= render_to_string('Tmaraprojapp/creditalert.html', {'name':firstName, 'newacc_bal':newacc_bal, 'acc_currency':acc_currency})
			plain_message= strip_tags(template)
			email_message= EmailMultiAlternatives(
				'Credit on your account!',
				template,
				settings.EMAIL_HOST_USER,
				[email]
				)
			email_message.attach_alternative(template, 'text/html')
			email_message.send()
			return HttpResponse('Account credited successfully')
		else:
			return HttpResponse('Enter an amount in Euros')
	print(client_deposit)
	context={}
	return render(request, 'Tmaraprojapp/admincreditaccount.html', context)

@login_required(login_url='clientsignin')
@staff_member_required
def admindebitaccount(request, pk):
	client= Client.objects.get(id=pk)
	client_deposit= client.deposit
	client_id= client.id
	firstName= client.first_name
	email= client.email
	acc_currency= client.account_currency
	if request.method == 'POST':
		amount= request.POST.get('amount')
		if float(client_deposit) > float(amount):
			newacc_bal= float(client_deposit) - float(amount)
			client_info= Client.objects.filter(id=client_id)
			client_info.update(deposit=newacc_bal)
			template= render_to_string('Tmaraprojapp/debitalert.html', {'name':firstName, 'newacc_bal':newacc_bal, 'acc_currency':acc_currency})
			plain_message= strip_tags(template)
			email_message= EmailMultiAlternatives(
				'Debit on your account!',
				template,
				settings.EMAIL_HOST_USER,
				[email]
				)
			email_message.attach_alternative(template, 'text/html')
			email_message.send()
			return HttpResponse('Account debited successfully')
		else:
			return HttpResponse('Amount is greater than account balance')
	print(client_deposit)
	context={}
	return render(request, 'Tmaraprojapp/admindebitaccount.html', context)


def clientsignin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	else:
		if request.method == "POST":
			username= request.POST.get('username')
			password= request.POST.get('passw')

			user= authenticate(request, username=username, password=password)

			if user is not None:
				# Generate OTP
				otp = str(random.randint(100000, 999999))

				EmailOTP.objects.update_or_create(user=user, defaults={'otp_code': otp, 'created_at': timezone.now()})

				email= user.client.email

				template= render_to_string('Tmaraprojapp/otpalert.html', {'otp':otp})
				plain_message= strip_tags(template)
				email_message= EmailMultiAlternatives(
					'Use this OTP code to login to your Valon Global Account!',
					template,
					settings.EMAIL_HOST_USER,
					[email]
					)
				email_message.attach_alternative(template, 'text/html')
				email_message.send()

				request.session['pre_2fa_user_id'] = user.id
				return redirect('verify_otp')
			else:
				messages.error(request, "username or password is incorrect")
	return render(request, 'Tmaraprojapp/clientsignin.html')

def verify_otp(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('clientsignin')

    user = User.objects.get(id=user_id)
    otp_obj = EmailOTP.objects.get(user=user)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            if str(otp_obj.otp_code) == str(entered_otp) and not otp_obj.is_expired():
                login(request, user)
                otp_obj.delete()  # Invalidate OTP
                return redirect('dashboard')
            else:
                return render(request, 'Tmaraprojapp/verify_otp.html', {'form': form, 'error': 'Invalid or expired OTP'})
    else:
        form = OTPForm()

    return render(request, 'Tmaraprojapp/verify_otp.html', {'form': form})
'''
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            # Generate OTP
            otp = str(random.randint(100000, 999999))

            EmailOTP.objects.update_or_create(user=user, defaults={'otp_code': otp})

            # Send OTP
            send_mail(
                subject='Your OTP Code',
                message=f'Your OTP is {otp}',
                from_email='no-reply@yourapp.com',
                recipient_list=[user.email],
                fail_silently=False,
            )

            request.session['pre_2fa_user_id'] = user.id
            return redirect('verify_otp')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')
'''

def signup(request):
	user_check = request.user.is_authenticated
	if user_check:
		return redirect('dashboard')
	form = CreateUserForm(request.POST or None)
	if form.is_valid():
		form.save()

		username=form.cleaned_data.get('username')
		password= form.cleaned_data.get('password1')
		password_reminder= password[:1]
		password_reminder_two= password[-1:]
		email= form.cleaned_data.get('email')
		template= render_to_string('Tmaraprojapp/WelcomeEmail2.html', {'name':username,'password':password})
		plain_message= strip_tags(template)
		email_message= EmailMultiAlternatives(
			'Welcome to Valon Global',
			plain_message,
			settings.EMAIL_HOST_USER,
			[email],

			)
		email_message.attach_alternative(template, 'text/html')
		email_message.send()

		second_template= render_to_string('Tmaraprojapp/securityEmail.html', {'name': username, 'password_reminder':password_reminder, 'password_reminder_two':password_reminder_two})
		second_plain_message= strip_tags(second_template)
		second_email_message= EmailMultiAlternatives(
			"Stay updated and discover more with Valon Global!",
			second_plain_message,
			settings.EMAIL_HOST_USER,
			[email]
			)
		second_email_message.attach_alternative(second_template, 'text/html')
		second_email_message.send()

		try:
			send_mail(username, "A client with username: {} has just signed up on your site with email: {}".format(username, email),settings.EMAIL_HOST_USER, ['customercare@unicreditpay.com'])
		except BadHeaderError:
			return HttpResponse("Your account has been created but you can't login at this time. please, try to login later")
		user= authenticate(username=username, password=password)
		login(request, user)
		return redirect('dashboard')
	context={'form':form}
	return render(request, 'Tmaraprojapp/clientregister.html', context)

@login_required
def blocked_account(request):
	client = request.user.client
	return render(request, 'blocked_account.html', {'reason': client.blocked_reason})

def logoutuser(request):
	logout(request)
	return redirect('clientsignin')
