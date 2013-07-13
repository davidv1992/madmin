import logging

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError
from madmin_user import hasPermission
import policy.madmin_voorraad as policy

log = logging.getLogger(__name__)

class VoorraadTekortError(Exception):
	pass

def add_voorraad(prd_id, stukprijs, btw, aantal):
	try:
		q = Query("""INSERT INTO tblvoorraad (vrd_prd_id, vrd_datum, vrd_aantal, vrd_resterend, vrd_stukprijs, vrd_btw)
		             VALUES (%s, NOW(), %s, %s, %s, %s)""")
		q.run((prd_id, aantal, aantal, stukprijs, btw))
		return q.lastrowid()
	except DatabaseError:
		raise InternalServerError

def query_voorraad(prd_id):
	try:
		q = Query("""SELECT vrd_id, vrd_datum, vrd_resterend, vrd_stukprijs, vrd_btw 
		             FROM tblvoorraad
		             WHERE vrd_resterend <> 0""")
		q.run((prd_id,))
		rows = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	result = []
	
	for row in rows:
		result.append({
		    'id': row[0],
		    'datum': row[1],
		    'resterend': row[2],
		    'stukprijs': row[3],
		    'btw': row[4]
		})
	
	return policy.voorraad_order(result)

def use_voorraad(prd_id, aantal):
	cur_voorraad = query_voorraad(prd_id)
	
	i=0
	result = []
	try:
		q = Query("""UPDATE tblvoorraad SET vrd_resterend = %s WHERE vrd_id = %s""")
	except DatabaseError:
		raise InternalServerError
		
	while aantal != 0:
		if (i > len(cur_voorraad)):
			raise VoorraadTekortError
		if (cur_voorraad[i]['resterend'] > aantal):
			deel_aantal = aantal
		else
			deel_aantal = cur_voorraad[i]['resterend']
		
		try:
			q.run((cur_voorraad[i]['resterend'] - deel_aantal, cur_voorraad[i]['id']))
		except DatabaseError:
			raise InternalServerError	
			# Try to think up a way of making this more robust against partial execution of query
		aantal -= deel_aantal
		result.append({
			'aantal': deel_aantal,
			'stukprijs': cur_voorraad[i]['stukprijs'],
			'btw': cur_voorraad[i]['btw']
		})
	
	return result

def _convert_datum(voorraad_el)
	voorraad_el['datum'] = str(voorraad_el['datum'])
	return voorraad_el

def handle_voorraad(params, json_data)
	if not hasPermission(params, 'voorraad', None):
		return []
	
	result = []
	for prd_id in params=['product_id']:
		voorraad = query_voorraad(prd_id)
		voorraad = map(_convert_datum, voorraad)
		result.append({
			'id': prd_id,
			'voorraad': voorraad
		})
	
	return result
