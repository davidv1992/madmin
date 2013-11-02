import logging
import BaseHTTPServer
import ssl
import urlparse
import string
import json
import cgi

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
	if target in _action_table:
		raise AlreadyHandledError
	_action_table[target] = handler

class _MadminRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	server_version = "MadminServer"
	
	test_message = "<html><head><title>OK</title></head><body>OK</body></html>"
	
	def log_error(self, format, *args):
		log.error(format, *args)
	
	def log_message(self, format, *args):
		log.info(format, *args)
	
	def is_valid_contentlength(self, content_lenght):
		if content_lenght > 0 and content_lenght < 1024*1024:
			return True
		return False
	
	def process_request_body(self):
		ct = cgi.parse_header(self.headers.getheader('Content-Type'))[0]
		cl = int(self.headers.getheader('Content-Length'))
		if not self.is_valid_contentlength(cl):
			send_error(400, "Invalid Content-Length")
			log.info("Request errored on invalid content-length")
			raise InvalidRequestException
		if ct == 'application/x-www-form-urlencoded':
			return (urlparse.parse_qs(self.rfile.read(cl)), None)
		if ct == 'application/json':
			return ({}, json.loads(self.rfile.read(cl)))
		send_error(400, "Invalid Content-Type")
		log.info("Request errored on invalid content-length")
		raise InvalidRequestException
	
	def process_request(self):
		_, _, target, _, query, _ = urlparse.urlparse(self.path)
		if target not in _action_table:
			self.send_error(404)
			log.info("Request ignored, unknown target %s.", target)
			raise InvalidRequestException
		params = urlparse.parse_qs(query)
		if 'Content-Type' in self.headers and 'Content-Length' in self.headers:
			extra_params, json_data = self.process_request_body()
		else:
			extra_params, json_data = {}, None
		params.update(extra_params)
		params['ip'] = [self.client_address[0]]
		response = _action_table[target](params, json_data)
		if response is None:
			self.send_response(204)
			self.end_headers()
			return
		try:
			response_json = json.dumps(response)
		except (TypeError, ValueError) as e:
			log.error("Unable to convert response from %s to json, object %s.",
			           target, response, exc_info = e)
			self.send_error(500)
			raise InvalidRequestException
		
		if len(response_json) == 0:
			log.error("Empty non None response from %s.", target)
			self.send_error(500)
			raise InvalidRequestException
		
		self.send_response(200)
		self.send_header("Content-Type", "text/plain")
		self.send_header("Content-Length", len(response_json)+1)
		self.end_headers()
		self.wfile.write(response_json)
		self.wfile.write('\n')
	
	def do_GET(self):
		try:
			self.process_request()
		except InvalidRequestException:
			pass
		except InternalServerError:
			self.send_error(500)
		log.info("Request processed.")
		
	def do_POST(self):
		try:
			self.process_request()
		except InvalidRequestException:
			pass
		except InternalServerError:
			self.send_error(500)
		log.info("Request processed.")
		

class _MadminServer(BaseHTTPServer.HTTPServer):
	def __init__(self, server_address, certfile=None, ssl_version=None,
	             RequestHandlerClass = _MadminRequestHandler):
		BaseHTTPServer.HTTPServer.__init__(self, server_address, 
		                                   RequestHandlerClass)
		if (certfile is not None) and (ssl_version is not None):
			ssl.wrap_socket(socket, server_side = True,
			                ssl_version = ssl_version, certfile = certfile)


def run():
	server = _MadminServer((config.host, config.port))
	log.info("Starting server.")
	server.serve_forever()
