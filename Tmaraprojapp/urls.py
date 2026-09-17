from django.urls import path

from django.contrib.auth import views as auth_views

from django.conf import settings

from . import views

urlpatterns=[
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
	path('current/', views.current, name='current'),
	path('kid/', views.kid, name='kid'),
	path('premium/', views.premium, name='premium'),
	path('saving/', views.saving, name='saving'),
	path('corporate/', views.corporate, name='corporate'),
	path('career/', views.career, name='career'),
	path('insurance/', views.insurance, name='insurance'),
	path('faq/', views.faq, name='faq'),
	path('card/', views.card, name='card'),
	path('contact/', views.contact, name='contact'),
	path('news/', views.news, name='news'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('blocked/', views.blocked_account, name='blocked_account'),
	path('account-questions/', views.account_questions_validate, name='account_questions_validate'),
	path('account_settings/', views.account_settings, name='account_settings'),
	path('profile_view/', views.profile_view, name="profile_view"),
	path('fundtransfer/', views.fundtransfer, name='fundtransfer'),
	path('foreign_transaction/', views.foreign_transaction, name='foreign_transaction'),
	path('transactionhistory/', views.transactionhistory, name='transactionhistory'),
	path('admindashboard/', views.admindashboard, name='admindashboard'),
	path('admincreateaccount/', views.admincreateaccount, name='admincreateaccount'),
	path('admingotouserprofile/<str:pk>/', views.admingotouserprofile, name='admingotouserprofile'),
	path('admincreditaccount/<str:pk>/', views.admincreditaccount, name='admincreditaccount'),
	path('admindebitaccount/<str:pk>/', views.admindebitaccount, name='admindebitaccount'),
	path('clientsignin/', views.clientsignin, name='clientsignin'),
	path('verify-otp/', views.verify_otp, name='verify_otp'),
	path('signup/', views.signup, name='signup'),
	path('logout/', views.logoutuser, name='logout'),
	path('reset_password/', auth_views.PasswordResetView.as_view(template_name="Tmaraprojapp/password_reset.html"), name='reset_password'),
	path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="Tmaraprojapp/password_reset_done.html"), name='password_reset_done'),
	path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="Tmaraprojapp/password_reset_form.html"), name='password_reset_confirm'),
	path('reset_password_complete/', auth_views.PasswordResetView.as_view(template_name="Tmaraprojapp/password_reset_complete.html"), name='password_reset_complete'),
]


urlpatterns += [
	# ... your existing patterns (home, dashboard, signin, etc.) stay as-is ...

	# ---------- PAYEES ----------
	path('payments/payees/', views.payee_list, name='payee_list'),
	path('payments/payees/add/', views.payee_add, name='payee_add'),
	path('payments/payees/<int:pk>/edit/', views.payee_edit, name='payee_edit'),
	path('payments/payees/<int:pk>/delete/', views.payee_delete, name='payee_delete'),

	# ---------- MAKE A PAYMENT ----------
	path('payments/make/', views.make_payment, name='make_payment'),
	path('payments/make/review/', views.make_payment_review, name='make_payment_review'),

	# ---------- TRANSFER ----------
	path('payments/transfer/', views.transfer_money, name='transfer_money'),
	path('payments/transfer/review/', views.transfer_review, name='transfer_review'),

	# ---------- INTERNATIONAL PAYMENT ----------
	path('payments/international/', views.international_payment, name='international_payment'),
	path('payments/international/review/', views.international_review, name='international_review'),

	# ---------- SCHEDULED PAYMENTS / STANDING ORDERS ----------
	path('payments/scheduled/', views.scheduled_payments, name='scheduled_payments'),
	path('payments/scheduled/add/', views.add_standing_order, name='add_standing_order'),
	path('payments/scheduled/<int:pk>/cancel/', views.cancel_standing_order, name='cancel_standing_order'),

	# ---------- SHARED: PIN CONFIRMATION + EXECUTION ----------
	path('payments/verify-pin/', views.verify_pin, name='verify_pin'),
	path('payments/success/', views.payment_success, name='payment_success'),

	# ---------- ADMIN: TRANSFER REVIEW (domestic + international) ----------
	path('staff/transfers/', views.admin_transfer_review_list, name='admin_transfer_review_list'),
	path('staff/transfers/<str:kind>/<int:pk>/approve/', views.admin_transfer_approve, name='admin_transfer_approve'),
	path('staff/transfers/<str:kind>/<int:pk>/decline/', views.admin_transfer_decline, name='admin_transfer_decline'),
]