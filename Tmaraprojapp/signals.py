
'''
from .models import Client

from django.contrib.auth.models import User

from django.db.models.signals import post_save

from django.dispatch import receiver

@receiver(post_save, sender=User)
def post_save_create_client(sender, instance, created, *args, **kwargs):
	if created:
		Client.objects.create(user=instance, first_name=instance.first_name, last_name= instance.last_name, email= instance.email,)
'''


from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Client, SecurityQuestion


@receiver(post_save, sender=User)
def create_or_update_client(sender, instance, created, **kwargs):
	if created:
		client = Client.objects.create(user=instance, email=instance.email)
		SecurityQuestion.objects.create(client=client)
	else:
		if hasattr(instance, 'client'):
			instance.client.save()