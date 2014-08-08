import logging

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError
from madmin_user import hasPermission

log = logging.getLogger(__name__)

def query_vereniging(ver_id):
	try:
		q = Query("""SELECT ver_id, ver_naam, ver_email, ver_basis_budget_id
		             FROM tblvereniging
		             WHERE ver_id=%s""")
		q.run((ver_id,))
		result = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	ver_overview = []
	
	for row in result:
		
		ver_overview.append({
			'id': row[0],
			'naam': row[1],
			'email': row[2],
			'basis_budget': row[3]
		})
	
	return ver_overview

def _convert_vereniging_rows(rows):
	ver_overview = []
	
	for row in rows:
		if not hasPermission(params, 'vereniging', row[0]):
			continue
		
		ver_overview.append({
			'id': row[0],
			'naam': row[1],
			'email': row[2],
			'basis_budget': row[3]
		})
	
	return ver_overview

def handle_verenigingen(params, json_data):
	try:
		q = Query("""SELECT ver_id, ver_naam, ver_email, ver_basis_budget_id 
		             FROM tblvereniging""")
		q.run();
		rows = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	ver_overview = []
	
	for row in rows:
		if not hasPermission(params, 'vereniging', row[0]):
			continue
		
		ver_overview.append({
			'id': row[0],
			'naam': row[1],
			'email': row[2],
			'basis_budget': row[3]
		})
	
	return ver_overview

add_handler('/verenigingen', handle_verenigingen)
log.info('Vereniging module initialized')
