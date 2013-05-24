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
		global _has_error
		"""Run query with given parameters"""
		if _has_error:
			_db_connect()
		try:
			if (parameters is None):
				self.cursor.execute(self.querystring)
			else:
				self.cursor.execute(self.querystring, parameters)
		except dbapi.Error, e:
			log.error("Error during query execution.", exc_info=e)
			_has_error = True
			raise DatabaseError
	
	def rows(self):
		global _has_error
		"""
		Get result rows from last executed query.
		Can throw DatabaseError if query does not produce rows as a result
		"""
		if _has_error:
			_db_connect()
		try:
			result = self.cursor.fetchall()
		except dbapi.Error, e:
			log.error("Error during fetching of rows.", exc_info=e)
			_has_error = True
			raise DatabaseError
