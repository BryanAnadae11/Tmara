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