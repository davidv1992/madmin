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


def handle_product(params, json_data):
	try:
		q_prod = Query("""SELECT prd_id, prd_naam, prd_type, prd_btw,
		                         prd_kantineprijs_leden, prd_kantineprijs_extern, 
		                         prd_borrelmarge, prd_leverancier_id, 
		                         prd_embalageprijs 
		                  FROM tblproduct WHERE prd_verwijderd = 0
		                  ORDER BY prd_id""")
		q_prod.run()
		rows_prod = q_prod.rows()
		
		q_rel = Query("""SELECT prdrel_orig_prd_id, prdrel_rel_prd_id
		                        prdrel_aantal
		                 FROM tblproductrelation""")
		q_rel.run()
		rows_rel = q_rel.rows()
	except DatabaseError:
		raise InternalServerError
	
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
			'kantineprijs_leden':product[4],
			'kantineprijs_extern':product[5],
			'borrelmarge':product[6],
			'leverancier_id':product[7],
			'embalageprijs':product[8],
			'related':cur_relations
		})
	
	return result

add_handler('/product/kantine', handle_kantine)
add_handler('/product', handle_product)
log.info("Product module initialized.")
