from client_lib.servercall import remote_call

_isInitialized = False
_verenigingList = None
_verenigingNameList = []

def _verSugInit():
	global _isInitialized
	global _verenigingList
	global _verenigingNameList
	_verenigingList = remote_call('/verenigingen')
	
	for vereniging in _verenigingList:
		_verenigingNameList.append((vereniging['naam'].encode('utf-8'), vereniging['id']))
	
	_verenigingNameList.sort()
	
	_isInitialized = True
	

def findVerenigingSuggestion(curInput):
	global _isInitialized
	global _verenigingNameList
	if not _isInitialized:
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
	
