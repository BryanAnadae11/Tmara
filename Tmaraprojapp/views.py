from django.shortcuts import render, redirect, get_object_or_404

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

from .models import *

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

@login_required(login_url='clientsignin')
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

		domestic = Transaction.objects.filter(client=client).order_by('-date_created')[:5]
		foreign = Foreign_transaction.objects.filter(client=client).order_by('-date_created')[:5]

		recentTransactions = []
		for t in domestic:
			recentTransactions.append({
				'description': t.destination_account_name or 'Domestic transfer',
				'category': 'Reversal' if t.is_reversal else 'Domestic transfer',
				'amount': t.amount if t.is_reversal else -t.amount,
				'date_created': t.date_created,
				'status': t.get_status_display(),
				'status_code': t.status,
			})
		for f in foreign:
			recentTransactions.append({
				'description': f.account_name or 'International transfer',
				'category': 'Reversal' if f.is_reversal else f"International — {f.country}" if f.country else 'International transfer',
				'amount': f.amount if f.is_reversal else -f.amount,
				'date_created': f.date_created,
				'status': f.get_status_display(),
				'status_code': f.status,
			})

		recentTransactions.sort(key=lambda row: row['date_created'] or timezone.now(), reverse=True)
		recentTransactions = recentTransactions[:5]

	context={'clientAccountNumber':clientAccountNumber, 'clientAccountType':clientAccountType, 'clientBalance':clientBalance,
	'clientAccountCurrency':clientAccountCurrency, 'recentTransactions':recentTransactions}
	return render(request, 'Tmaraprojapp/dashboard.html', context)

@login_required(login_url='clientsignin')
def account_settings(request):
	client= request.user.client
	form= ClientUserForm(instance=client)
	if request.method=='POST':
		form= ClientUserForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()
	context= {'form':form}
	return render(request, 'Tmaraprojapp/profile_settings.html', context)



from decimal import Decimal, InvalidOperation

@login_required(login_url='clientsignin')
def fundtransfer(request):
	return redirect('payee_list')


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

@login_required(login_url='clientsignin')
def transactionhistory(request):
	client= request.user.client
	clientAccountNumber= client.account_number
	clientAccountType= client.account_type
	clientAccountCurrency= client.account_currency
	clientBalance= float(client.deposit) + float(client.uncleared_balance)

	domestic = Transaction.objects.filter(client=client)
	foreign = Foreign_transaction.objects.filter(client=client)

	normalized = []
	for t in domestic:
		normalized.append({
			'bank_name': '',
			'account_number': t.destination_account_number,
			'account_name': t.destination_account_name,
			'amount': t.amount,
			'date_created': t.date_created,
			'status': t.get_status_display(),
			'status_code': t.status,
			'is_reversal': t.is_reversal,
		})
	for f in foreign:
		normalized.append({
			'bank_name': f.bank_name,
			'account_number': f.account_number,
			'account_name': f.account_name,
			'amount': f.amount,
			'date_created': f.date_created,
			'status': f.get_status_display(),
			'status_code': f.status,
			'is_reversal': f.is_reversal,
		})

	transactions = sorted(
		normalized,
		key=lambda row: row['date_created'] or timezone.now(),
		reverse=True,
	)

	context={'clientAccountNumber':clientAccountNumber, 'clientAccountType':clientAccountType, 'clientBalance':clientBalance,
	'clientAccountCurrency':clientAccountCurrency, 'transactions':transactions}
	return render(request, 'Tmaraprojapp/Transactionhistory.html', context)


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

	template = 'Tmaraprojapp/account_questions_setup.html' if first_time else 'Tmaraprojapp/account_questions_verify.html'
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
    # 1. Safely fetch client instance or return a clean 404 page if missing
    client = get_object_or_404(Client, id=pk)

    if request.method == 'POST':
        raw_amount = request.POST.get('amount')
        
        if raw_amount:
            try:
                # Convert both values to Decimal for reliable mathematical calculations
                amount = Decimal(str(raw_amount))
                current_deposit = Decimal(str(client.deposit or 0))
                
                if amount <= 0:
                    return HttpResponse('Credit amount must be greater than zero.', status=400)
                
                # Perform arithmetic operation
                newacc_bal = current_deposit + amount
                
                # 2. Update model directly on the instance to guarantee .save() trigger execution
                client.deposit = newacc_bal
                client.save()  # Triggers tracking mechanisms and custom save logic
                
                # 3. Build email configurations cleanly
                template = render_to_string('Tmaraprojapp/creditalert.html', {
                    'name': client.first_name, 
                    'newacc_bal': newacc_bal, 
                    'acc_currency': client.account_currency
                })
                plain_message = strip_tags(template)
                
                email_message = EmailMultiAlternatives(
                    subject='Credit on your account!',
                    body=plain_message,  # FIX: Sent clean text version for strict mail parsers
                    from_email=settings.EMAIL_HOST_USER,
                    to=[client.email]
                )
                email_message.attach_alternative(template, 'text/html')
                email_message.send()
                
                return HttpResponse('Account credited successfully')
                
            except (ValueError, InvalidOperation):
                return HttpResponse('Invalid numeric amount entered.', status=400)
        else:
            return HttpResponse('Enter an amount to credit.', status=400)
    return render(request, 'Tmaraprojapp/admincreditaccount.html')



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
			password= request.POST.get('password')

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
			send_mail(username, "A client with username: {} has just signed up on your site with email: {}".format(username, email),settings.EMAIL_HOST_USER, ['support@valonglobal.com'])
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
	return render(request, 'Tmaraprojapp/blocked_account.html', {'reason': client.blocked_reason})

@login_required(login_url='clientsignin')
def profile_view(request):
	client = request.user.client
	return render(request, 'Tmaraprojapp/profile_view.html', {'client': client})

def logoutuser(request):
	logout(request)
	return redirect('clientsignin')




# --------------- Everything that has to do with the new payment features ----------


def _get_client(request):
	return request.user.client


# ---------- PAYEES ----------

@login_required
def payee_list(request):
	client = _get_client(request)
	payees = client.payees.all()
	return render(request, 'Tmaraprojapp/payee_list.html', {'payees': payees})


@login_required
def payee_add(request):
	client = _get_client(request)
	if request.method == 'POST':
		Payee.objects.create(
			client=client,
			name=request.POST.get('name'),
			sort_code=f"{request.POST.get('sc1','')}-{request.POST.get('sc2','')}-{request.POST.get('sc3','')}",
			account_number=request.POST.get('account_number'),
			reference=request.POST.get('reference'),
		)
		return redirect('payee_list')
	return render(request, 'Tmaraprojapp/payee_add.html')

def payee_edit(request, pk):
	return HttpResponse('Payee Edit')

def payee_delete(request, pk):
	return HttpResponse(f'Payee Edit {pk}')


# ---------- MAKE A PAYMENT ----------

@login_required
def make_payment(request):
	client = _get_client(request)
	payees = client.payees.all()

	if request.method == 'POST':
		payee_option = request.POST.get('payee_option')  # 'existing' | 'new'
		when = request.POST.get('when', 'today')

		if payee_option == 'existing':
			payee = get_object_or_404(Payee, pk=request.POST.get('payee_id'), client=client)
			payee_name, sort_code, account_number = payee.name, payee.sort_code, payee.account_number
			payee_id = payee.id
		else:
			payee_id = None
			payee_name = request.POST.get('new_payee_name')
			sort_code = f"{request.POST.get('sc1','')}-{request.POST.get('sc2','')}-{request.POST.get('sc3','')}"
			account_number = request.POST.get('new_account_number')

		request.session['pending_action'] = {
			'type': 'payment',
			'from_account': client.account_type,
			'payee_id': payee_id,
			'payee_name': payee_name,
			'sort_code': sort_code,
			'account_number': account_number,
			'amount': request.POST.get('amount'),
			'reference': request.POST.get('reference'),
			'payment_date': request.POST.get('payment_date') if when == 'later' else timezone.now().date().isoformat(),
			'save_new_payee': bool(request.POST.get('save_payee')) if payee_option == 'new' else False,
		}
		return redirect('make_payment_review')

	return render(request, 'Tmaraprojapp/make_payment.html', {
		'client': client,
		'payees': payees,
		'today': timezone.now().date().isoformat(),
	})


@login_required
def make_payment_review(request):
	pending = request.session.get('pending_action')
	if not pending or pending.get('type') != 'payment':
		return redirect('make_payment')
	if request.method == 'POST':
		return redirect('verify_pin')
	return render(request, 'Tmaraprojapp/review.html', {'pending': pending, 'back_url': 'make_payment'})


# ---------- TRANSFER (to a payee — see the account-model note above) ----------

@login_required
def transfer_money(request):
	client = _get_client(request)
	payees = client.payees.all()

	if request.method == 'POST':
		payee = get_object_or_404(Payee, pk=request.POST.get('payee_id'), client=client)
		when = request.POST.get('when', 'today')
		request.session['pending_action'] = {
			'type': 'transfer',
			'from_account': client.account_type,
			'payee_id': payee.id,
			'payee_name': payee.name,
			'sort_code': payee.sort_code,
			'account_number': payee.account_number,
			'amount': request.POST.get('amount'),
			'reference': request.POST.get('reference', ''),
			'payment_date': request.POST.get('payment_date') if when == 'later' else timezone.now().date().isoformat(),
		}
		return redirect('transfer_review')

	return render(request, 'Tmaraprojapp/transfer.html', {
		'client': client, 'payees': payees, 'today': timezone.now().date().isoformat(),
	})


@login_required
def transfer_review(request):
	pending = request.session.get('pending_action')
	if not pending or pending.get('type') != 'transfer':
		return redirect('transfer_money')
	if request.method == 'POST':
		return redirect('verify_pin')
	return render(request, 'Tmaraprojapp/review.html', {'pending': pending, 'back_url': 'transfer_money'})


# ---------- INTERNATIONAL PAYMENT ----------

@login_required
def international_payment(request):
	client = _get_client(request)
	if request.method == 'POST':
		when = request.POST.get('when', 'today')
		request.session['pending_action'] = {
			'type': 'international',
			'from_account': client.account_type,
			'country': request.POST.get('country'),
			'recipient_name': request.POST.get('recipient_name'),
			'address': request.POST.get('address'),
			'iban': request.POST.get('iban'),
			'bic': request.POST.get('bic'),
			'amount': request.POST.get('amount'),
			'currency': request.POST.get('currency'),
			'reference': request.POST.get('reference'),
			'payment_date': request.POST.get('payment_date') if when == 'later' else timezone.now().date().isoformat(),
		}
		return redirect('international_review')

	return render(request, 'Tmaraprojapp/international.html', {
		'client': client, 'today': timezone.now().date().isoformat(),
	})


@login_required
def international_review(request):
	pending = request.session.get('pending_action')
	if not pending or pending.get('type') != 'international':
		return redirect('international_payment')
	if request.method == 'POST':
		return redirect('verify_pin')
	return render(request, 'Tmaraprojapp/review.html', {'pending': pending, 'back_url': 'international_payment'})


# ---------- SCHEDULED PAYMENTS / STANDING ORDERS ----------

@login_required
def scheduled_payments(request):
	client = _get_client(request)
	orders = client.standing_orders.filter(is_active=True).order_by('next_payment_date')
	return render(request, 'Tmaraprojapp/scheduled_list.html', {'orders': orders})


@login_required
def add_standing_order(request):
	client = _get_client(request)
	payees = client.payees.all()

	if request.method == 'POST':
		payee = get_object_or_404(Payee, pk=request.POST.get('payee_id'), client=client)
		end_type = request.POST.get('end_type', 'never')
		request.session['pending_action'] = {
			'type': 'standing_order',
			'payee_id': payee.id,
			'payee_name': payee.name,
			'amount': request.POST.get('amount'),
			'reference': request.POST.get('reference'),
			'first_payment_date': request.POST.get('first_payment_date'),
			'frequency': request.POST.get('frequency', 'monthly'),
			'end_date': request.POST.get('end_date') if end_type == 'specific' else None,
		}
		return redirect('verify_pin')

	return render(request, 'Tmaraprojapp/add_standing_order.html', {
		'payees': payees, 'today': timezone.now().date().isoformat(),
	})


@login_required
def cancel_standing_order(request, pk):
	client = _get_client(request)
	order = get_object_or_404(StandingOrder, pk=pk, client=client)
	if request.method == 'POST':
		order.is_active = False
		order.save()
		return redirect('scheduled_payments')
	return render(request, 'Tmaraprojapp/cancel_standing_order.html', {'order': order})


# ---------- SHARED: PIN CONFIRMATION + EXECUTION ----------

from django.db import transaction
from django.db.models import F


@login_required
def verify_pin(request):
	client = _get_client(request)
	pending = request.session.get('pending_action')
	if not pending:
		return redirect('make_payment')

	error = None
	if request.method == 'POST':
		pin = request.POST.get('pin', '')
		if not client.transfer_pin or pin != client.transfer_pin:
			error = "Incorrect PIN. Please try again."
		else:
			try:
				amount = float(pending.get('amount') or 0)
			except (TypeError, ValueError):
				amount = 0

			if amount <= 0:
				error = "Enter a valid amount."
			elif pending['type'] in ('payment', 'transfer', 'international'):
				with transaction.atomic():
					locked_client = Client.objects.select_for_update().get(pk=client.pk)
					if (locked_client.deposit or 0) < amount:
						error = "Insufficient funds for this payment."
					else:
						_execute_pending_action(locked_client, pending)
				if not error:
					del request.session['pending_action']
					return redirect('payment_success')
			else:
				# standing orders don't debit anything yet
				_execute_pending_action(client, pending)
				del request.session['pending_action']
				return redirect('payment_success')

	return render(request, 'Tmaraprojapp/verify_pin.html', {'pending': pending, 'error': error})

@login_required
def payment_success(request):
	return render(request, 'Tmaraprojapp/success.html')


def _execute_pending_action(client, pending):
	amount = float(pending.get('amount') or 0)

	if pending['type'] in ('payment', 'transfer'):
		Transaction.objects.create(
			client=client,
			destination_account_number=pending.get('account_number'),
			destination_account_name=pending.get('payee_name'),
			amount=amount,
			date_created=timezone.now(),
		)
		client.deposit = F('deposit') - amount
		client.save(update_fields=['deposit'])

		if pending['type'] == 'payment' and pending.get('save_new_payee') and not pending.get('payee_id'):
			Payee.objects.create(
				client=client,
				name=pending.get('payee_name'),
				sort_code=pending.get('sort_code'),
				account_number=pending.get('account_number'),
				reference=pending.get('reference'),
			)

	elif pending['type'] == 'international':
		Foreign_transaction.objects.create(
			client=client,
			bank_name='',
			country=pending.get('country'),
			account_number=pending.get('iban'),
			account_name=pending.get('recipient_name'),
			bank_code=pending.get('bic'),
			routing_number='',
			amount=amount,
			date_created=timezone.now(),
		)
		client.deposit = F('deposit') - amount
		client.save(update_fields=['deposit'])

	elif pending['type'] == 'standing_order':
		payee = Payee.objects.get(pk=pending['payee_id'], client=client)
		StandingOrder.objects.create(
			client=client,
			payee=payee,
			amount=amount,
			reference=pending.get('reference'),
			first_payment_date=pending['first_payment_date'],
			next_payment_date=pending['first_payment_date'],
			frequency=pending.get('frequency', 'monthly'),
			end_date=pending.get('end_date') or None,
		)

@login_required(login_url='clientsignin')
@staff_member_required
def admin_transfer_review_list(request):
	domestic = Transaction.objects.filter(status='pending_review', is_reversal=False)
	foreign = Foreign_transaction.objects.filter(status='pending_review', is_reversal=False)

	rows = (
		[{'kind': 'domestic', 'obj': t} for t in domestic] +
		[{'kind': 'foreign', 'obj': t} for t in foreign]
	)
	rows.sort(key=lambda r: r['obj'].date_created or timezone.now(), reverse=True)

	return render(request, 'Tmaraprojapp/admin_transfer_review_list.html', {'rows': rows})


@login_required(login_url='clientsignin')
@staff_member_required
def admin_transfer_approve(request, kind, pk):
	model = Transaction if kind == 'domestic' else Foreign_transaction
	txn = get_object_or_404(model, pk=pk)

	if request.method == 'POST':
		if txn.status != 'pending_review':
			messages.error(request, 'This transfer has already been reviewed.')
			return redirect('admin_transfer_review_list')

		txn.status = 'approved'
		txn.reviewed_by = request.user
		txn.reviewed_at = timezone.now()
		txn.save()

		client = txn.client
		destination_name = txn.destination_account_name if kind == 'domestic' else txn.account_name
		if client and client.email:
			template = render_to_string('Tmaraprojapp/transfer_approved_alert.html', {
				'name': client.first_name,
				'amount': txn.amount,
				'destination_account_name': destination_name,
			})
			plain_message = strip_tags(template)
			email_message = EmailMultiAlternatives(
				'Your transfer has been confirmed',
				plain_message,
				settings.EMAIL_HOST_USER,
				[client.email],
			)
			email_message.attach_alternative(template, 'text/html')
			email_message.send()

		messages.success(request, 'Transfer approved and confirmation email sent.')
	return redirect('admin_transfer_review_list')


@login_required(login_url='clientsignin')
@staff_member_required
def admin_transfer_decline(request, kind, pk):
	model = Transaction if kind == 'domestic' else Foreign_transaction
	txn = get_object_or_404(model, pk=pk)

	if request.method == 'POST':
		if txn.status != 'pending_review':
			messages.error(request, 'This transfer has already been reviewed.')
			return redirect('admin_transfer_review_list')

		with transaction.atomic():
			locked_txn = model.objects.select_for_update().get(pk=txn.pk)
			if locked_txn.status != 'pending_review':
				messages.error(request, 'This transfer has already been reviewed.')
				return redirect('admin_transfer_review_list')

			client = Client.objects.select_for_update().get(pk=locked_txn.client_id)
			client.deposit = F('deposit') + locked_txn.amount
			client.save(update_fields=['deposit'])

			if kind == 'domestic':
				Transaction.objects.create(
					client=client,
					destination_account_number=locked_txn.destination_account_number,
					destination_account_name=locked_txn.destination_account_name,
					amount=locked_txn.amount,
					date_created=timezone.now(),
					status='approved',
					is_reversal=True,
					reversal_of=locked_txn,
				)
			else:
				Foreign_transaction.objects.create(
					client=client,
					bank_name=locked_txn.bank_name,
					country=locked_txn.country,
					account_number=locked_txn.account_number,
					account_name=locked_txn.account_name,
					bank_code=locked_txn.bank_code,
					routing_number=locked_txn.routing_number,
					amount=locked_txn.amount,
					date_created=timezone.now(),
					status='approved',
					is_reversal=True,
					reversal_of=locked_txn,
				)

			locked_txn.status = 'declined'
			locked_txn.reviewed_by = request.user
			locked_txn.reviewed_at = timezone.now()
			locked_txn.save()

		client.refresh_from_db()
		if client.email:
			template = render_to_string('Tmaraprojapp/transfer_declined_alert.html', {
				'name': client.first_name,
				'amount': locked_txn.amount,
				'new_balance': client.deposit,
			})
			plain_message = strip_tags(template)
			email_message = EmailMultiAlternatives(
				'Your transfer was declined and reversed',
				plain_message,
				settings.EMAIL_HOST_USER,
				[client.email],
			)
			email_message.attach_alternative(template, 'text/html')
			email_message.send()

		messages.success(request, 'Transfer declined, funds returned to the client.')
	return redirect('admin_transfer_review_list')