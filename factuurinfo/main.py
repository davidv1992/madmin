from verenigingList import verenigingList
from verenigingNaamCoupler import getVerenigingNaamList
from manager import factuurManager
from gui_lib.core import mainloop
from client_lib.login import prompt_login
from client_lib.servercall import remote_call
import argparse
import getpass
import sys

#Command line parsing
cmd_parser = argparse.ArgumentParser(description='Bekijke facturen')

cmd_parser.add_argument(
	'--user', '-u',
	type=str,
	help='Gebruikersnaam om mee in te loggen (standaard de gebruikersnaam waarme is ingelogd op de lokale machine).',
	default=getpass.getuser()
)

arguments = cmd_parser.parse_args()

#login
prompt_login(arguments.user)

#Start main application
try:
	screenManager = factuurManager(1,1)
	screenManager.push(verenigingList(1,1,getVerenigingNaamList(),screenManager))
	mainloop(screenManager)
except ServerCallException:
	print >> sys.stderr, "Probleem in de verbinding met server."
	sys.exit(1)

