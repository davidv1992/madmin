import logging

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError

import policy.madmin_product as policy

log = logging.getLogger(__name__)

def handle_kantine(params, json_data):
	try:
		q = Query("""SELECT prd_id, prd_naam, prd_kantineprijs_leden, 
		                            prd_kantineprijs_extern
		             FROM tblproduct 
		             WHERE prd_verwijderd = 0 AND prd_type = %s""")
		q.run((policy.product_type_kantine,))
		rows = q.rows()
	except DatabaseError:
		raise InternalServerError
	
	result = []
	
	for product in rows:
		result.append({'id':product[0], 'naam':product[1], 'prijs_leden':product[2], 'prijs_extern':product[3]})
	
	return result

def _convert_product_rows(rows_prod, rows_rel):
	result = []
	
	rel_iter = 0
	
	for product in rows_prod:
		while rel_iter < len(rows_rel) and rows_rel[rel_iter][0] < product[0]:
			rel_iter+=1
		
		cur_relations = []
		while rel_iter < len(rows_rel) and rows_rel[rel_iter][0] == product[0]:
			cur_relations.append({
				'id':rows_rel[rel_iter][1],
				'aantal':rows_rel[rel_iter][2]
			})
		
		result.append({
			'id':product[0],
			'naam':product[1],
			'type':policy.product_name_mapping[product[2]],
			'btw':product[3],
			'leverancier_id':product[7],
			'related':cur_relations
		})
		
		if product[4] is not None:
			result[-1]['kantineprijs_leden'] = product[4]
		if product[5] is not None:
			result[-1]['kantineprijs_extern'] = product[5]
		if product[6] is not None:
			result[-1]['borrelmarge'] = product[6]
		if product[8] is not None:
			result[-1]['emballageprijs'] = product[8]
	
	return result

def query_product(prd_id):
	log.debug("Query for product %s", prd_id)
	try:
		q_prod = Query("""SELECT prd_id, prd_naam, prd_type, prd_btw,
		                         prd_kantineprijs_leden, prd_kantineprijs_extern, 
		                         prd_borrelmarge, prd_leverancier_id, 
		                         prd_emballageprijs 
		                  FROM tblproduct WHERE prd_verwijderd = 0 AND prd_id = %s""")
		q_prod.run((prd_id,))
		rows_prod = q_prod.rows()
		
		q_rel = Query("""SELECT prdrel_orig_prd_id, prdrel_rel_prd_id
		                        prdrel_aantal
		                 FROM tblproductrelation
		                 WHERE prdrel_orig_prd_id = %s""")
		q_rel.run((prd_id,))
		rows_rel = q_rel.rows()
	except DatabaseError:
		raise InternalServerError
	
	return _convert_product_rows(rows_prod, rows_rel)

def handle_product_all(params, json_data):
	try:
		q_prod = Query("""SELECT prd_id, prd_naam, prd_type, prd_btw,
		                         prd_kantineprijs_leden, prd_kantineprijs_extern, 
		                         prd_borrelmarge, prd_leverancier_id, 
		                         prd_emballageprijs 
		                  FROM tblproduct WHERE prd_verwijderd = 0 
		                  ORDER BY prd_id""")
		q_prod.run()
		rows_prod = q_prod.rows()
		
		q_rel = Query("""SELECT prdrel_orig_prd_id, prdrel_rel_prd_id,
		                        prdrel_aantal
		                 FROM tblproductrelation
		                 ORDER BY prdrel_orig_prd_id""")
		q_rel.run()
		rows_rel = q_rel.rows()
	except DatabaseError:
		raise InternalServerError
	
	return _convert_product_rows(rows_prod, rows_rel)

def handle_product(params, json_data):
	if 'product_id' not in params:
		return []
	
	result = []
	
	try:	
		q_prod = Query("""SELECT prd_id, prd_naam, prd_type, prd_btw,
				                 prd_kantineprijs_leden, prd_kantineprijs_extern, 
				                 prd_borrelmarge, prd_leverancier_id, 
				                 prd_emballageprijs 
				          FROM tblproduct WHERE prd_verwijderd = 0
				          AND prd_id = %s
				          ORDER BY prd_id""")
		q_rel = Query("""SELECT prdrel_orig_prd_id, prdrel_rel_prd_id,
			                    prdrel_aantal
			             FROM tblproductrelation
			             WHERE prdrel_orig_prd_id = %s
			             ORDER BY prdrel_orig_prd_id""")
	except DatabaseError:
		raise InternalServerError
	
	for prd_id in params['product_id']:
		try:
			q_prod.run((prd_id,))
			rows_prod = q_prod.rows()
		
			q_rel.run((prd_id,))
			rows_rel = q_rel.rows()
		except DatabaseError:
			raise InternalServerError
		
		result += _convert_product_rows(rows_prod, rows_rel)
	
	return result

add_handler('/product/kantine', handle_kantine)
add_handler('/product/all', handle_product_all)
add_handler('/product', handle_product)
log.info("Product module initialized.")
