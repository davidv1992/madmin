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

_flood_protect = {}

def _check_flood_protect(ip):
	if (ip not in _flood_protect):
		return True;
	
	if (_flood_protect[ip]['timelim'] < time.time()):
		del _flood_protect[ip]
		return True
	
	if (_flood_protect[ip]['ammount'] < config.flood_maxAmmount):
		return True
	
	_flood_protect[ip]['timelim'] = time.time() + config.flood_timeout
	return False
	
def _add_flood_protect(ip):
	if (ip not in _flood_protect):
		_flood_protect[ip] = {'timelim': time.time()+config.flood_timeout, 'ammount':1}
		return
	
	_flood_protect[ip]['timelim'] = time.time()+config.flood_timeout
	_flood_protect[ip]['ammount'] = _flood_protect[ip]['ammount'] + 1

def _reset_flood_protect(ip):
	if (ip in _flood_protect):
		del _flood_protect[ip]

def _verify_session(ip, session_key):
	if (not _check_flood_protect(ip)):
		return False
	if (session_key not in _sessions):
		_add_flood_protect(ip)
		return False
	
	cur_session = _sessions[session_key]
	if (cur_session['timelim'] < time.time()):
		del _sessions[session_key]
		return False
	
	if (cur_session['ip'] != ip):
		_add_flood_protect(ip)
		return False
		
	cur_session['timelim'] = time.time()+config.timeout
	
	return (cur_session['user'],)

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
		return (False,'')
	if not sha512_crypt.verify(params['password'][0], results[0][1]):
		_add_flood_protect(params['ip'][0])
		return (False,'')
	
	#Generate session key
	session_key = b64encode(urandom(8))
	
	_sessions[session_key] = {
		'user':results[0][0],
		'timelim': time.time()+config.timeout,
		'ip': params['ip'][0]
	}
	
	_reset_flood_protect(params['ip'][0])
	
	return (True, session_key)


add_handler("/login", handle_login)
log.info("User module initialized.")
