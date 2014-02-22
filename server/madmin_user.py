import logging
import time
from passlib.hash import sha512_crypt
from os import urandom
from base64 import b64encode

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError

import config.madmin_user as config

log = logging.getLogger(__name__)

_sessions = {}

def _check_flood_protect(ip):
	try:
		q = Query('SELECT fc_ammount FROM tblfloodcontrol WHERE fc_ip = %s AND fc_timelim > NOW()')
		q.run((ip,))
		rows = q.rows()
		if len(rows) == 0:
			return True
		elif rows[0][0] < config.flood_maxAmmount:
			return True
		qu = Query('UPDATE tblfloodcontrol set fc_timelim = NOW() + INTERVAL %s MINUTE')
		qu.run((ip,config.flood_timeout))
		return False
	except DatabaseError:
		raise InternalServerError
	# Failing is best here, as someone could try to selectively block access
	#  to database so as to be able to run a brute-force attack on passwords

def _add_flood_protect(ip):
	try:
		qr = Query('DELETE FROM tblfloodcontrol WHERE fc_timelim < NOW()')
		qr.run()
		q = Query('SELECT fc_ip FROM tblfloodcontrol WHERE fc_ip = %s')
		q.run((ip,))
		rows = q.rows()
		if (len(rows) != 0):
			qu = Query('UPDATE tblfloodcontrol SET fc_ammount = fc_ammount+1, fc_timelim = NOW() + INTERVAL %s MINUTE WHERE fc_ip = %s')
			qu.run((config.flood_timeout, ip))
		else:
			qu = Query('INSERT into tblfloodcontrol (fc_ip, fc_ammount, fc_timelim) VALUES (%s, 1, NOW() + INTERVAL %s MINUTE)')
			qu.run((ip, config.flood_timeout))
	except DatabaseError:
		raise InternalServerError
	# Failing is best here, as someone could try to selectively block access
	#  to database so as to be able to run a brute-force attack on passwords

def _create_session(ip, user):
	session_key = b64encode(urandom(8))
	try:
		q = Query('DELETE FROM tblsession WHERE ses_id = %s OR ses_timelim < NOW()')
		q.run((session_key,))
		qu = Query('INSERT INTO tblsession (ses_id, ses_timelim, ses_gebr_id, ses_ip) VALUES (%s, NOW() + INTERVAL %s MINUTE, %s, %s)')
		qu.run((session_key, config.timeout, user, ip))
	except DatabaseError:
		raise InternalServerError
	
	return session_key

def _verify_session(ip, session_key):
	if (not _check_flood_protect(ip)):
		return False
	
	try:
		q = Query('SELECT ses_gebr_id FROM tblsession WHERE ses_id = %s AND ses_ip = %s AND ses_timelim > NOW()')
		q.run((session_key, ip))
		rows = q.rows()
		qu = Query('UPDATE tblsession SET ses_timelim = NOW() + INTERVAL %s MINUTE WHERE ses_timelim > NOW() AND ses_id = %s AND ses_ip = %s')
		qu.run((config.timeout, session_key, ip))
	except DatabaseError:
		raise InternalServerError
	
	if len(rows) == 0:
		_add_flood_protect(ip)
		return False
	
	return rows[0][0]

def hasPermission(query_params, data_type, data_owner):
	#partial STUB!
	if ('session_key' not in query_params):
		log.debug('Request without session key')
		return False
	
	log.debug('Request with session key {0}'.format(query_params['session_key'][0]))
	
	session_data = _verify_session(query_params['ip'][0], query_params['session_key'][0])
	
	if not session_data:
		return False
	
	return True

# This function IS susceptible to timing attacks, in that it returns faster
#  when a user does not exists, than when a password mismatch is detected
def handle_login(params, json_data):
	if (not _check_flood_protect(params['ip'][0])):
		return (False, '')
	if 'username' not in params or 'password' not in params:
		return (False,'')
	
	try:
		q = Query('SELECT gebr_id, gebr_wachtwoord FROM tblgebruiker WHERE gebr_naam = %s')
		q.run((params['username'][0],))
		results = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	if (len(results) != 1):
		_add_flood_protect(params['ip'][0])
		return (False,'')
	if not sha512_crypt.verify(params['password'][0], results[0][1]):
		_add_flood_protect(params['ip'][0])
		return (False,'')
	
	#Generate session key
	session_key = _create_session(params['ip'][0], results[0][0])
	
	return (True, session_key)


add_handler("/login", handle_login)
log.info("User module initialized.")
