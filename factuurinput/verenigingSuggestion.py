from client_lib.servercall import remote_call

_verenigingList = None
_verenigingNameList = []

def _verSugInit():
	_verenigingList = remote_call('/verenigingen')
	
	for vereniging in _verenigingList:
		_verenigingNameList.append((vereniging['naam'].encode('utf-8'), vereniging['id']))
	

def findVerenigingSuggestion(curInput):
	if _verenigingList is None:
		_verSugInit()
	
	if len(_verenigingNameList) == 0:
		return (None, '')
	
	low = -1
	high = len(_verenigingNameList)-1
	while high - low > 1:
		mid = (high+low)/2
		if _verenigingNameList[mid][0] >= curInput:
			high = mid
		else:
			low = mid
	
	if _verenigingNameList[high][0].startswith(curInput):
		return (_verenigingNameList[high][1], _verenigingNameList[high][0])
	
	return (None, '')
	
