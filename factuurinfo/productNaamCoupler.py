from client_lib.servercall import remote_call

_got_info = False
_name_dict = {}
_id_dict = {}

class UnknownProductException(Exception):
	pass

def _init_product_list():
	global _got_info
	global _name_dict
	global _id_dict
	product_list = remote_call('/product/all')
	for vereniging in vereniging_list:
		_name_dict[product['id']] = product['naam']
		_id_dict[product['naam']] = product['id']
	_got_info = True

def getProductNaam(product_id)
	global _got_info
	global _name_dict
	if not _got_info:
		_init_product_list()
	if product_id not in _name_dict:
		raise UnknownProductException
	return _name_dict[product_id]

def getVerenigingId(product_naam):
	global _got_info
	global _id_dict
	if not _got_info:
		_init_product_list()
	if product_naam not in _id_dict:
		raise UnknownProductException
	return _id_dict[product_naam]
	
