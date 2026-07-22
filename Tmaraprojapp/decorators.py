# decorators.py
from functools import wraps
from django.shortcuts import redirect

def check_account_status(view_func):
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		if request.user.is_authenticated and hasattr(request.user, 'client'):
			client = request.user.client

			if client.account_blocked:
				return redirect('blocked_account')

			if client.suspicious_activity:
				return redirect('account_questions_validate')

		return view_func(request, *args, **kwargs)
	return _wrapped_view