from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(Client)
admin.site.register(History)
admin.site.register(EmailOTP)
admin.site.register(Transaction)
admin.site.register(Otp)
admin.site.register(Foreign_transaction)
