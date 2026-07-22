from django.apps import AppConfig


class TmaraprojappConfig(AppConfig):
    name = 'Tmaraprojapp'

    def ready(self):
    	import Tmaraprojapp.signals
