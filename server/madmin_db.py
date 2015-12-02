"""
Database module for madmin

On init creates connection to the database.
Errors in this initial connect are considered critical.
"""

# Module properties & assumptions:
#  NOT thread safe
#  dbapi handles escaping of arguments
#  Errors are rare, so reconecting on error wont be a performance problem

import logging
import sys
import MySQLdb as dbapi

import config.madmin_db as db_config

#module variables
_connection = None
_has_error = False



# Error classes
class DatabaseError(Exception):
	pass



# Utility functions
def _db_connect():
	global _connection
	global _has_error
	try:
		log.debug("Connecting to %s, user %s, db %s", db_config.host, db_config.username, db_config.database)
		_connection = dbapi.connect(db_config.host, db_config.username, 
		                            db_config.password, db_config.database)
	except dbapi.Error, e:
		log.error("Unable to (re)connect to database.", exc_info = e)
		raise DatabaseError
	_has_error = False



#logging
log = logging.getLogger(__name__)

#Initialize db connection
try:
	_db_connect()
except DatabaseError:
	log.critical("Unable to do initial connect do database.")
	sys.exit(0)

log.info("module initialized")

_in_transaction = False
_at_first_query = False
_num_retries = 0

def commit():
	global _in_transaction, _at_first_query, _has_error
	_in_transaction = False
	_at_first_query = False
	log.debug("Starting commit")
	try:
		_connection.commit()
	except dbapi.Error, e:
		log.error("Unable to commit current database transaction.", exc_info=e)
		_has_error = True
		raise DatabaseError
	log.debug("Commit finished")

def rollback():
	global _in_transaction, _at_first_query
	_in_transaction = False
	_at_first_query = False
	try:
		_connection.rollback()
	except dbapi.Error, e:
		pass

def start_transaction():
	global _in_transaction, _at_first_query
	q = Query("START TRANSACTION WITH CONSISTENT SNAPSHOT");
	q.run();
	_in_transaction = True;
	_at_first_query = True;

class Query(object):
	"""
	Wrapper for database query
	
	Is intended to wrap one or more calls with the same SQL, given
	during creation
	"""
	def __init__(self, querystring):
		"""Create query with given querystring"""
		global _has_error
		if _has_error:
			_db_connect()
		self.querystring = querystring
		try:
			self.cursor = _connection.cursor()
		except dbapi.Error, e:
			log.error("Unable to create query.", exc_info=e)
			_has_error = True
			raise DatabaseError
	
	def run(self, parameters=None):
		global _has_error, _num_retries, _in_transaction, _at_first_query
		"""Run query with given parameters"""
		if _has_error:
			_db_connect()
			try:
				self.cursor = _connection.cursor()
			except dbapi.Error, e:
				log.error("Unable tot recover from database problem.", exc_info=e)
				_has_error = True
				raise DatabaseError
		try:
			if (parameters is None):
				self.cursor.execute(self.querystring)
			else:
				self.cursor.execute(self.querystring, parameters)
			log.debug("Query %s, data %s, rows affected: %d", self.querystring, parameters, self.cursor.rowcount)
			if not _in_transaction:
				commit()
		except dbapi.Error, e:
			log.error("Error during query execution.", exc_info=e)
			log.error("Query %s", self.querystring)
			_has_error = True
			
			#can we retry?
			if not _in_transaction or _at_first_query:
				log.error("Retrying after error")
				if _num_retries > 5:
					log.error("Too many retries, aborting.");
					raise DatabaseError
				if _in_transaction:
					start_transaction()
					self.cursor = _connection.cursor()
				self.run(parameters)
			else:
				#ah well
				raise DatabaseError
			
		#reset retry count, we were succesfull somehow
		_num_retries = 0
	
	def rows(self):
		global _has_error
		"""
		Get result rows from last executed query.
		Can throw DatabaseError if query does not produce rows as a result
		"""
		if _has_error:
			raise DatabaseError # cannot return sensible result after an error, so error
		try:
			return self.cursor.fetchall()
		except dbapi.Error, e:
			log.error("Error during fetching of rows.", exc_info=e)
			_has_error = True
			raise DatabaseError
	
	def lastrowid(self):
		global _has_error
		"""
		Get id of last inserted row
		Can throw DatabaseError
		"""
		if _has_error:
			raise DatabaseError	# Cannot return sensible result after an error, so error
		
		try:
			return self.cursor.lastrowid
		except dbapi.Error, e:
			log.error("Error during fetching of lastrowid.", exc_info=e)
			_has_error = True
			raise DatabaseError
