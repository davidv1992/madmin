import logging
import BaseHTTPServer
import ssl
import urlparse
import string
import json
import cgi
from mod_python import apache

log = logging.getLogger(__name__)

import config.madmin_server as config

class AlreadyHandledError(Exception):
	pass
class InvalidRequestException(Exception):
	pass
class InternalServerError(Exception):
	pass

_action_table = {}

def add_handler(target, handler):
	target = config.prefix+target
	if target in _action_table:
		raise AlreadyHandledError
	_action_table[target] = handler

def is_valid_contentlength(content_length):
	if content_length > 0 and content_length < 1024*1024:
		return True
	return False

def process_request_body(req):
	ct = cgi.parse_header(req.headers_in['Content-Type'])[0]
	cl = int(req.headers_in['Content-Length'])
	log.debug("Parsed headers")
	if not is_valid_contentlength(cl):
		log.info("Request errored on invalid content-length")
		raise apache.SERVER_RETURN, apache.HTTP_BAD_REQUEST
	if ct == 'application/x-www-form-urlencoded':
		return (urlparse.parse_qs(req.read(cl)), None)
	if ct == 'application/json':
		return ({}, json.loads(req.read(cl)))
	log.info("Request errored on invalid content-length")
	raise apache.SERVER_RETURN, apache.HTTP_BAD_REQUEST

def handler(req):
	log.debug("Request, target %s.", req.uri)
	if req.uri not in _action_table:
		log.info("Request ignored, unknown target %s.", req.uri)
		return apache.HTTP_NOT_FOUND
	
	if req.args is not None:
		params = urlparse.parse_qs(req.args)
	else:
		params = {}
	
	log.debug("Parsed params")
	
	if 'Content-Type' in req.headers_in and 'Content-Length' in req.headers_in:
		extra_params, json_data = process_request_body(req)
	else:
		extra_params, json_data = {},None
	
	log.debug("Parsed body data")
	
	params.update(extra_params)
	params['ip'] = [req.connection.remote_ip,]
	
	try:
		response = _action_table[req.uri](params,json_data)
	except InternalServerError:
		return apache.HTTP_INTERNAL_SERVER_ERROR
	
	if response is None:
		return apache.OK
	
	try:
		response_json = json.dumps(response)
	except (TypeError, ValueError) as e:
		log.error("Unable to convert response from %s to json, object %s.",
		           req.uri, response, exc_info = e)
		return apache.HTTP_INTERNAL_SERVER_ERROR
	
	req.headers_out.add('Content-Type', 'application/json')
	req.headers_out.add('Content-Length', str(len(response_json)+1))
	req.write(response_json)
	req.write('\n')
	
	return apache.OK

