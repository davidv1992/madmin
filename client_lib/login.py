import servercall
import getpass
import sys

def prompt_login(user):
	password = getpass.getpass()
	try:
		servercall.login(user, password)
	except servercall.ServerCallException:
		print >> sys.stderr, 'Kon geen verbinding opbouwen met madmin server.'
		sys.exit(1)
	except servercall.ServerLoginError:
		print >> sys.stderr, 'Kon niet inloggen met gegeven gebruikersnaam/wachtwoord.'
		sys.exit(1)

