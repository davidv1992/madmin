from client_lib.servercall import remote_call

_got_info = False
_name_dict = {}
_id_dict = {}

class UnknownVerenigingException(Exception):
	pass

def _init_vereniging_list():
	global _got_info
	global _name_dict
	global _id_dict
	vereniging_list = remote_call('/verenigingen')
	for vereniging in vereniging_list:
		_name_dict[vereniging['id']] = vereniging['naam']
		_id_dict[vereniging['naam']] = vereniging['id']
	_got_info = True

def getVerenigingNaamList():
	global _got_info
	global _name_dict
	if not _got_info:
		_init_vereniging_list()
	result = []
	for vereniging_naam, vereniging_id in _name_dict.iteritems():
		result.append((vereniging_naam, vereniging_id))
	return result

def getVerenigingNaam(vereniging_id):
	global _got_info
	global _name_dict
	if not _got_info:
		_init_vereniging_list()
	if vereniging_id not in _name_dict:
		raise UnknownVerenigingException
	return _name_dict[vereniging_id]

def getVerenigingId(vereniging_naam):
	global _got_info
	global _id_dict
	if not _got_info:
		_init_vereniging_list()
	if vereniging_naam not in _id_dict:
		raise UnknownVerenigingException
	return _id_dict[vereniging_naam]
	
