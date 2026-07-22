import uuid

def generate_account_number():
	code= str(uuid.uuid4()).replace("-", "")[:12]
	return code