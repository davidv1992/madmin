from client_lib.servercall import login, remote_call, ServerLoginError, ServerCallException
import getpass
import sys

username = raw_input("Username: ")
old_pass = getpass.getpass("Old password: ")

try:
	login(username, old_pass)
except ServerLoginError:
	print >> sys.stderr, "Kon niet inloggen met gegeven gebruikersnaam/wachtwoord."
	sys.exit(1)

new_pass = getpass.getpass("New password: ")

try:
	status = remote_call("/setpassword", [('password', new_pass)])
except ServerCallException:
	print >> sys.stderr, "Fout bij veranderen wachtwoord."
	sys.exit(1)
if not status:
	print >> sys.stderr, "Wachtwoord kon niet worden veranderd."
	sys.exit(1)
