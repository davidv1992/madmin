import logging
import datetime

from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError
from madmin_user import hasPermission
from madmin_voorraad import add_voorraad, use_voorraad, ammount_voorraad
from madmin_products import query_product
from madmin_vereniging import query_vereniging
import policy.madmin_factuur as policy

class MalformedDataException(Exception):
	pass

class NonExistingProductException(Exception):
	def __init__(self, product_id):
		Exception.__init__(self, "Product does not exist")
		self.product_id = product_id

class NonExistingVerenigingException(Exception):
	def __init__(self, vereniging):
		Exception.__init__(self, "Vereniging does not exist")
		self.vereniging = vereniging

class NonExistingBudgetException(Exception):
	def __init__(self, budget):
		Exception.__init__(self, "Budget does not exist")
		self.budget = budget

class IncompatibleBudgetException(Exception):
	def __init__(self, budget, vereniging):
		Exception.__init__(self, "Budget does not belong to vereniging")
		self.budget = budget;
		self.vereniging = vereniging

class NoVoorraadException(Exception):
	def __init__(self, product_id):
		Exception.__init__(self, "Not enough suplies")
		self.product_id = product_id

log = logging.getLogger(__name__)

def handle_factuur_create(params, json_data):
	log.debug('Start factuur_create')
	log.debug('Input data:%s', json_data)
	if type(json_data) != list:
		return {'error': 'incorrectly structured data'}
	
	if not hasPermission(params,'factuur_create',None):
		return {'error': 'insufficient permissions'}
	
	facturen = []
	
	#Start transaction
	
	try:
		for factuur in json_data:
			facturen.append(parse_factuur(factuur))
				
	except MalformedDataException:
		return {'error': 'incorrectly structured data'}
	
	try:
		for factuur in facturen:
			verify_factuur(factuur)
			process_factuur(factuur)
			policy.process_factuur(factuur)
	except NonExistingProductException, e:
		return {'error': 'No such product {0}'.format(e.product_id), 'product_id': e.product_id}
	except NonExistingVerenigingException, e:
		return {'error': 'No such vereniging {0}'.format(e.vereniging), 'vereniging_id': e.vereniging}
	except NonExistingBudgetException, e:
		return {'error': 'No such budget {0}'.format(e.budget), 'budget_id': e.budget}
	except IncompatibleBudgetException, e:
		return {'error': 'Budget {0} is not compatible with vereniging {1}'.format(e.budget, e.vereniging),
		        'budget_id': e.budget, 'vereniging_id': e.vereniging}
	except NoVoorraadException, e:
		return {'error': 'Not enough supplies of {0}'.format(e.product_id), 'product_id': e.product_id}
	
	return {'succes': len(facturen)}

# ------------------------------------------------------------------------------
# Process factuur
#  Do all processing of the factuur, ie:
#   - changes in voorraad
#   - creation of permanent representation of factuur
#
#  This should not do validation, the only errors this should throw are
#  database errors
# ------------------------------------------------------------------------------

def process_factuur(factuur):
	# Gen. nones for possible non-existent values
	leverancier = None
	if 'leverancier' in factuur:
		leverancier = factuur['leverancier']
	vereniging = None
	saldo_basis = None
	if 'vereniging' in factuur:
		vereniging = factuur['vereniging']
		saldo_basis=query_vereniging(vereniging)[0]['basis_budget']
	saldo_speciaal = None
	if 'saldo_speciaal' in factuur:
		saldo_speciaal = factuur['saldo_speciaal']
	verantwoordelijke = None
	if 'verantwoordelijke' in factuur:
		verantwoordelijke = factuur['verantwoordelijke']
	
	# Generate next number for factuur
	try:
		q = Query("""SELECT MIN(fac_volgnummer)
		             FROM tblfactuur
		             WHERE fac_ver_id = %s AND fac_leverancier = %s""")
		q.run((vereniging, leverancier))
		rows = q.rows()
	except DatabaseError:
		raise InternalServerError
	if rows[0][0] is None:
		number = 1
	else:
		number = rows[0][0] + 1
	
	# Create factuur entry
	try:
		q = Query("""INSERT INTO tblfactuur (fac_ver_id, 
		                                     fac_leverancier,
		                                     fac_type,
		                                     fac_volgnummer,
		                                     fac_factuurdatum,
		                                     fac_leverdatum,
		                                     fac_verantwoordelijke,
		                                     fac_saldo_speciaal,
		                                     fac_saldo_basis,
		                                     fac_bkjr_id) 
		             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
		                    (SELECT bkjr_id FROM tblboekjaar
		                     WHERE bkjr_is_huidig = -1))""")
		q.run((vereniging,
		       leverancier,
		       factuur['type'],
		       number,
		       factuur['factuurdatum'],
		       factuur['leverdatum'],
		       verantwoordelijke,
		       saldo_speciaal,
		       saldo_basis));
		fac_id = q.lastrowid()
	except DatabaseError:
		raise InternalServerError
	
	log.debug('factuur created with id: %d', fac_id)
	
	# Pocess lines
	factuur_bedrag = 0
	for regel in factuur['regels']:
		factuur_bedrag += process_factuur_regel(regel, fac_id)
	
	# Finish up
	if saldo_speciaal is not None:
		budget_speciaal = query_budget(saldo_speciaal)[0]
		mutatie_speciaal = max(factuur_bedrag, 
		               budget_speciaal['minimum'] - budget_speciaal['current'])
		mutatie_basis = factuur_bedrag - mutatie_speciaal
		budget_update(saldo_speciaal, mutatie_speciaal)
		budget_update(saldo_basis, mutatie_basis)
		budget_speciaal = query_budget(saldo_speciaal)[0]
		budget_basis = query_budget(saldo_basis)[0]
		try:
			q = Query("""UPDATE tblfactuur SET saldo_speciaal_na = %s
			                                   saldo_basis_na = %s
			                               WHERE fac_id = %s""")
			q.run((budget_speciaal['current'], budget_basis['current'], fac_id))
		except DatabaseError:
			raise InternalServerError
	elif saldo_basis is not None:
		budget_update(saldo_basis, factuur_bedrag)
		budget_basis = query_budget(saldo_basis)[0]
		try:
			q = Query("""UPDATE tblfactuur SET saldo_basis_na = %s
			                               WHERE fac_id = %s""")
			q.run((budget_basis['current'], fac_id))
		except DatabaseError:
			raise InternalServerError

def process_factuur_regel_inkoop(regel, factuur_id):
	if 'product_id' in regel:
		product = query_product(regel['product_id'])[0]
		
		if 'btw' not in regel:
			regel['btw'] = product['btw']
		
		if 'stukprijs' not in regel:
			regel['stukprijs'] = regel['totaalprijs'] / (-regel['aantal'])
			if regel['totaalprijs'] % (-regel['aantal']):
				regel['stukprijs'] += 1
		
		if 'totaalprijs' not in regel:
			regel['totaalprijs'] = regel['stukprijs'] * (-regel['aantal'])
		
		btw = regel['totaalprijs']*regel['btw']/(1000+regel['btw'])
		if regel['totaalprijs']*regel['btw'] % (1000+regel['btw']) > (999+regel['btw'])/2:
			btw += 1
		
		vrd_id = add_voorraad(regel['product_id'], regel['stukprijs'], regel['btw'], -regel['aantal'])
		
		try:
			q = Query("""INSERT INTO tblfactuurregel (
			                 frgl_fac_id, frgl_type,
			                 frgl_vrd_id, frgl_aantal, frgl_stukprijs,
			                 frgl_totprijs, frgl_btw)
			             VALUES (
			                 %s, 0,
			                 %s, %s, %s,
			                 %s, %s)""")
			q.run((factuur_id, vrd_id, regel['aantal'], regel['stukprijs'],
			       regel['totaalprijs'], btw))
		except DatabaseError:
			raise InternalServerError
			
		return regel['totaalprijs']
	else:
		if 'stukprijs' not in regel:
			regel['stukprijs'] = regel['totaalprijs'] / (-regel['aantal'])
			if regel['totaalprijs'] % (-regel['aantal']):
				regel['stukprijs'] += 1
		
		if 'totaalprijs' not in regel:
			regel['totaalprijs'] = regel['stukprijs'] * (-regel['aantal'])
		
		btw = regel['totaalprijs']*regel['btw']/(1000+regel['btw'])
		if regel['totaalprijs']*regel['btw'] % (1000+regel['btw']) > (999+regel['btw'])/2:
			btw += 1
		
		try:
			q = Query("""INSERT INTO tblfactuurregel (
			                 frgl_fac_id, frgl_type,
			                 frgl_omschrijving, frgl_aantal,
			                 frgl_stukprijs, frgl_totprijs,
			                 frgl_btw)
			             VALUES (
			                 %s, 0,
			                 %s, %s,
			                 %s, %s,
			                 %s)""")
			q.run((factuur_id, regel['naam'], regel['aantal'],
			       regel['stukprijs'], regel['totaalprijs'],
			       btw))
		except DatabaseError:
			raise InternalServerError
		return regel['totaalprijs']

def process_factuur_regel_verkoop(regel, factuur_id):
	if 'product_id' in regel:
		verbruik = use_voorraad(regel['product_id'], regel['aantal'])
		try:
			q = Query("""INSERT INTO tblfactuurregel (
			                 frgl_fac_id, frgl_type,
			                 frgl_vrd_id, frgl_aantal, frgl_stukprijs,
			                 frgl_totprijs, frgl_btw)
			             VALUES (
			                 %s, 0,
			                 %s, %s, %s,
			                 %s, %s)""")
		except DatabaseError:
			raise InternalServerError
		
		c_totaalprijs = 0
		for vc in verbruik:
			totaalprijs = vc['stukprijs'] * vc['aantal']
			btw = totaalprijs*vc['btw']/(1000+vc['btw'])
			if totaalprijs*vc['btw']%(1000+vc['btw']) > (999+vc['btw'])/2:
				btw += 1
			try:
				q.run((factuur_id, vc['id'], vc['aantal'],
				       vc['stukprijs'], totaalprijs, btw))
			except DatabaseError:
				raise InternalServerError
			c_totaalprijs += totaalprijs
			
		return c_totaalprijs
	else:
		if 'totaalprijs' not in regel:
			regel['totaalprijs'] = regel['stukprijs'] * regel['aantal']
		
		if 'stukprijs' not in regel:
			regel['stukprijs'] = regel['totaalprijs'] / regel['aantal']
			if regel['totaalprijs'] % regel['aantal'] > 0:
				regel['stukprijs']+=1
		
		btwperc = regel['btw']
		regel['btw'] = regel['totaalprijs']*btwperc/(1000+btwperc)
		if regel['totaalprijs']*btwperc % (1000+btwperc) > (999+btwperc)/2:
			regel['btw']+=1
		
		try:
			q = Query("""INSERT INTO tblfactuurregel (
			                 frgl_fac_id, frgl_type,
			                 frgl_omschrijving, frgl_aantal,
			                 frgl_stukprijs, frgl_totprijs,
			                 frgl_btw)
			             VALUES (
			                 %s, 0,
			                 %s, %s,
			                 %s, %s,
			                 %s)""")
			q.run((factuur_id, regel['naam'], regel['aantal'],
			       regel['stukprijs'], regel['totaalprijs'],
			       regel['btw']))
		except DatabaseError:
			raise InternalServerError
		
		return regel['totaalprijs']

def process_factuur_regel(regel, factuur_id):
	if regel['aantal'] > 0:
		return -process_factuur_regel_verkoop(regel, factuur_id)
	else:
		return process_factuur_regel_inkoop(regel, factuur_id)

# ------------------------------------------------------------------------------
# End of factuur processing
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Factuur verification
#  Check the validity of all values within the fields
# ------------------------------------------------------------------------------

def verify_factuur(factuur):
	if 'vereniging' in factuur:
		ver = query_vereniging(factuur['vereniging'])
		if len(ver) == 0:
			raise NonExistingVerenigingException(factuur['vereniging'])
		budget = budget_query(ver[0]['basis_budget'])
		if len(budget) == 0:
			raise NonExistingBudgetException(ver[0]['basis_budget'])
	if 'saldo_speciaal' in factuur:
		budget = budget_query(factuur['saldo_speciaal'])
		if len(budget) == 0:
			raise NonExistingBudgetException(factuur['saldo_speciaal'])
		budget = budget[0]
		if budget['vereniging_id'] != factuur['vereniging']:
			raise IncompatibleBudgetException(factuur['saldo_speciaal'],
			                                  factuur['vereniging'])
	
	for regel in factuur['regels']:
		verify_factuur_regel(regel)

def verify_factuur_regel(regel):
	if 'product_id' not in regel:
		return
	#check existence
	if len(query_product(regel['product_id'])) == 0:
		raise NonExistingProductException(product_id = regel['product_id'])
	
	if regel['aantal'] > 0:
		# check voorraad
		if ammount_voorraad(regel['product_id']) < regel['aantal']:
			raise NoVoorraadException(product_id = regel['product_id'], )

# ------------------------------------------------------------------------------
# End of factuur verification
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Factuur parsing
#  Check typing and existence of fields and combinations of fields, and make
#  sure only the actually checked fields exist in the data structure that is
#  sent to the rest of the code
# ------------------------------------------------------------------------------

def parse_factuur_regels(regels):
	result = []
	for regel in regels:
		if 'aantal' not in regel:
			raise MalformedDataException
		
		if type(regel['aantal']) != int:
			raise MalformedDataException
		if regel['aantal'] == 0:
			raise MalformedDataException
		
		if regel['aantal'] < 0 and 'stukprijs' not in regel and 'totaalprijs' not in regel:
			raise MalformedDataException
		
		if 'naam' not in regel and 'product_id' not in regel:
			raise MalformedDataException
		
		if regel['aantal'] > 0 and 'product_id' in regel and ('stukprijs' in regel or 'totaalprijs' in regel):
			raise MalformedDataException
		
		if 'product_id' not in regel and 'btw' not in regel:
			raise MalformedDataException
		
		curRegel = {
			'aantal': regel['aantal']
		}
		
		if 'stukprijs' in regel:
			if type(regel['stukprijs']) != int:
				raise MalformedDataException
			curRegel['stukprijs'] = regel['stukprijs']
		
		if 'totaalprijs' in regel:
			if 'stukprijs' in regel:
				raise MalformedDataException
			if type(regel['totaalprijs']) != int:
				raise MalformedDataException
			curRegel['totaalrpijs'] = regel['totaalprijs']
		
		if 'btw' in regel:
			if type(regel['btw']) != int:
				raise MalformedDataException
			curRegel['btw'] = regel['btw']
		
		if 'product_id' in regel:
			if type(regel['product_id']) != int:
				raise MalformedDataException
			curRegel['product_id'] = regel['product_id']
		
		if 'naam' in regel:
			if not isinstance(regel['naam'], (str,unicode)):
				raise MalformedDataException
			curRegel['naam'] = regel['naam']
		
		result.append(curRegel)
	
	return result

def parse_factuur(factuur):
	if 'type' not in factuur:
		raise MalformedDataException
	if 'factuurdatum' not in factuur:
		raise MalformedDataException
	if 'leverdatum' not in factuur:
		raise MalformedDataException
	if 'regels' not in factuur:
		raise MalformedDataException
	if 'leverancier' not in factuur and 'vereniging' not in factuur:
		raise MalformedDataException
	
	log.debug('all required fields present')
	
	if factuur['type'] not in policy.factuur_type_mapping:
		log.debug('incorrect type')
		raise MalformedDataException
	if not isinstance(factuur['factuurdatum'], (str,unicode)):
		log.debug('factuurdatum incorrectly typed')
		raise MalformedDataException
	if not isinstance(factuur['leverdatum'], (str,unicode)):
		log.debug('leverdatum incorrectly typed')
		raise MalformedDataException
	if type(factuur['regels']) != list:
		raise MalformedDataException
	
	log.debug('all required non-date fields of proper type')
	
	try:
		datetime.datetime.strptime(factuur['factuurdatum'], "%Y-%m-%d")
		datetime.datetime.strptime(factuur['leverdatum'], "%Y-%m-%d")
	except ValueError:
		raise MalformedDataException
	
	log.debug('initial checks complete, generate factur')
	
	result = {
		'type': policy.factuur_type_mapping[factuur['type']],
		'factuurdatum': factuur['factuurdatum'],
		'leverdatum': factuur['leverdatum'],
		'regels': parse_factuur_regels(factuur['regels'])
	}
	
	log.debug('lines checked and valid')
	
	if 'leverancier' in factuur:
		if not isinstance(factuur['leverancier'], (str,unicode)):
			raise MalformedDataException
		result['leverancier'] = factuur['leverancier']
		
	if 'vereniging' in factuur:
		if 'leverancier' in factuur:
			raise MalformedDataException
		if type(factuur['vereniging']) is not int:
			raise MalformedDataException
		result['vereniging'] = factuur['vereniging']
	
	if 'verantwoordelijke' in factuur:
		if not isinstance(factuur['verantwoordelijke'], (str,unicode)):
			raise MalformedDataException
		result['verantwoordelijke'] = factuur['verantwoordelijke']
	
	if 'saldo_speciaal' in factuur:
		if type(factuur['saldo_speciaal']) is not int:
			raise MalformedDataException
		if 'vereniging' not in factuur:
			raise MalformedDataException
		result['saldo_speciaal'] = factuur['saldo_speciaal']
	
	log.debug('factuur valid')
	
	return result

# ------------------------------------------------------------------------------
# End of factuur parsing
# ------------------------------------------------------------------------------

def handle_factuur(params, json_data):
	if 'factuur_id' not in params:
		return None
	
	try:
		q = Query("""SELECT fac_id, fac_cor_op_id, fac_type, fac_ver_id,
		             fac_leverancier, fac_volgnummer, fac_factuurdatum, 
		             fac_leverdatum, fac_verantwoordelijke, fac_saldo_speciaal,
		             fac_saldo_basis, fac_saldo_speciaal_na, fac_saldo_basis_na,
		             frgl_type, prd_naam, frgl_omschrijving, frgl_aantal,
		             frgl_stukprijs, frgl_totprijs, frgl_btw, vrd_prd_id
		             FORM tblfactuur
		             LEFT JOIN tblfactuurregel ON fac_id = frgl_fac_id
		             LEFT JOIN tblvoorraad on frgl_vrd_id = vrd_id
		             LEFT JOIN tblproduct on vrd_prd_id = prd_id
		             WHERE fac_id = %s""")
	except DatabaseError:
		raise InternalServerError
	
	result = []
	
	for fac_id in params['factuur_id']:
		try:
			q.run((fac_id,))
			regels = q.rows()
		except DatabaseError:
			raise InternalServerError
		
		if len(regels) == 0:	#Non-existing factuur
			continue
		
		if not hasPermission(params, 'factuur', regels[0][4]):
			continue
		
		huidige_factuur = {
			'id': regels[0][0],
			'type': policy.factuur_name_mapping[regels[0][2]],
			'volgnummer': regels[0][5],
			'factuurdatum': str(regels[0][6]),
			'leverdatum': str(regels[0][7]),
			'regels': []
		}
		
		if regels[0][10] is not None:
			huidige_factuur['saldo_basis'] = regels[0][10]
			huidige_factuur['saldo_basis_na'] = regels[0][12]
		
		if regels[0][3] is not None:
			huidige_factuur['vereniging'] = regels[0][3]
		
		if regels[0][4] is not None:
			huidige_factuur['leverancier'] = regels[0][4]
		
		if regels[0][8] is not None:
			huidige_factuur['verantwoordelijke'] = regels[0][8]
		
		if regels[0][9] is not None:
			huidige_factuur['saldo_speciaal'] = regels[0][9]
			huidige_factuur['saldo_speciaal_na'] = regels[0][11]
		
		for regel in regels:
			if regel[13] is None:
				continue
				
			huidige_regel = {
				'aantal': regel[16],
				'stukprijs': regel[17],
				'totaalprijs': regel[18],
				'btw': regel[19]
			}
			
			if regel[14] is not None:
				huidige_regel['naam'] = regel[14]
			
			if regel[15] is not None:
				huidige_regel['naam'] = regel[15]
			
			if regel[20] is not None:
				huidige_regel['prd_id'] = regel[20]
			
			huidige_factuur['regels'].append(huidige_regel)
		
		result.append(huidige_factuur)
	
	return result



add_handler('/factuur', handle_factuur)
add_handler('/factuur/create', handle_factuur_create)
log.info("Factuur module initialized.")
