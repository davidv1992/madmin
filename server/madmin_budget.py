import logging

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError
from madmin_user import hasPermission

log = logging.getLogger(__name__)

def handle_budget(params, json_data):
	if 'budget_id' not in params:
		return None

	budget_data = []	
	try:
		q = Query('SELECT bdgt_id, bdgt_naam, bdgt_minimum, bdgt_current, bdgt_ver_id FROM tblbudget WHERE bdgt_id = %s')
	except DatabaseError:
		raise InternalServerError
			
	for budget_id in params['budget_id']:	
		try:
			q.run((budget_id,))
			cur_result = q.rows()
		except DatabaseError:
			raise InternalServerError

		for row in cur_result:
			if not hasPermission(params, 'budget', row[4]):
				continue
			
			budget_data.append({
				'id': row[0], 
				'vereniging_id': row[4], 
				'naam': row[1], 
				'current': row[3], 
				'minimum': row[2]})
	
	return budget_data

def handle_budget_ver(params, json_data):
	if 'vereniging_id' not in params:
		return None
	
	try:
		q = Query('SELECT bdgt_id, bdgt_naam, bdgt_minimum, bdgt_current FROM tblbudget WHERE bdgt_ver_id = %s')
	except DatabaseError:
		raise InternalServerError
	
	budget_data = []
	
	for vereniging_id in params['vereniging_id']:
		if not hasPermission(params, 'budget', vereniging_id):
			continue
		
		try:
			q.run((vereniging_id,))
			cur_result = q.rows()
		except DatabaseError:
			raise InternalServerError
		
		for row in cur_result:
			budget_data.append({
				'id': row[0], 
				'vereniging_id': vereniging_id, 
				'naam': row[1], 
				'current': row[3], 
				'minimum': row[2]})
	
	return budget_data

def budget_query(budget_id):
	try:
		q = Query("""SELECT bdgt_id, bdgt_current, bdgt_minimum, bdgt_ver_id
		             FROM tblbudget
		             WHERE bdgt_id = %s""")
		q.run((budget_id,))
		rows = q.rows()
	except DatabaseError:
		raise InternalServerError
		
	result = []
	for row in rows:
		result.append({
			'budget_id': row[0],
			'vereniging_id': row[3],
			'minimum': row[2],
			'current': row[1]
		})
	
	return result

def budget_vereniging_query(vereniging_id):
	try:
		q = Query('SELECT bdgt_id FROM tblbudget WHERE bdgt_ver_id = %s')
		q.run((vereniging_id,))
		result = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	budget_ids = []
	
	for row in result:
		budget_ids.append(result[0][0])
	
	return budget_ids

def budget_update(budget_id, value_change):
	try:
		q = Query('UPDATE tblbudget SET bdgt_current = bdgt_current + %s WHERE bdgt_id = %s')
		q.run((value_change, budget_id))
	except DatabaseError:
		raise InternalServerError

add_handler('/budget', handle_budget)
add_handler('/budget/ver', handle_budget_ver)
log.info("Budget module initialized")
