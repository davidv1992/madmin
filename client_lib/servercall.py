import httplib
import urllib
import json
import config.servercall_config as config

# TODO: Figure out how to do server certificate verification

class ServerCallException(Exception):
	pass
class ServerLoginError(Exception):
	pass
# Module state
session_key = None

def _build_url(location, urldata):
	#Prepare url
	url = urllib.quote(location)
	url_has_params = False
	
	if urldata is not None:
		if not url_has_params:
			url_has_params = True
			url += '?'
		else:
			url += '&'
		url += urllib.urlencode(urldata)
	
	if session_key is not None:
		if not url_has_params:
			url_has_params = True
			url += '?'
		else:
			url += '&'
		url += 'session_key=' + urllib.quote_plus(session_key)
	
	return url

def remote_call(location, urldata=None, jsondata=None):
	url = _build_url(location, urldata)
	
	try:
		conn = httplib.HTTPConnection(config.server_host, config.server_port)
	
		if jsondata is None:
			conn.request('GET', url)
		else:
			conn.request('POST', url, json.dumps(jsondata))
	
		response = conn.getresponse()
		
		statuscode = response.status
		
		if statuscode == 201:
			return None
		if statuscode <> 200:
			raise ServerCallException
		returned_data = json.load(response)
		
		conn.close()
		
		return returned_data
	except httplib.HTTPException:
		raise ServerCallException

def login(username, password):
	session_key = None
	(succes, key) = remote_call('/login', [('username', username), ('password', password)], None)
	if not succes:
		raise ServerLoginError
	session_key = key
