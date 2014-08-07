from factuurInput import FactuurInput
from gui_lib.core import mainloop
from client_lib.login import prompt_login
import argparse
import getpass
import sys

#Command line parsing
cmd_parser = argparse.ArgumentParser(description='Voer facturen in')

cmd_parser.add_argument(
	'--user', '-u',
	type=str,
	help='Gebruikersnaam om mee in te loggen (standaard de gebruikersnaam waarme is ingelogd op de lokale machine).',
	default=getpass.getuser()
)

arguments = cmd_parser.parse_args()

#login
prompt_login(arguments.user)

#mainloop
mainloop(FactuurInput(1,1))
