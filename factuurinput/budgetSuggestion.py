from client_lib.servercall import remote_call

_isInitialized = False
_budgetList = None
_budgetNameList = []

def _budgetSugInit():
	global _isInitialized
	global _budgetList
	global _budgetNameList
	_verenigingList = remote_call('/verenigingen')
	_budgetList = []
	for vereniging in _verenigingList:
		_budgetList = remote_call('/budget/vereniging', [('vereniging_id', vereniging['id'])])
		for budget in _budgetList:
			_budgetNameList.append((vereniging['naam'].encode('utf-8') + '-' + budget['naam'].encode('utf-8'), budget['id']))
	
	_budgetNameList.sort()
	
	_isInitialized = True

def findBudget(curInput):
	global _isInitialized
	global _budgetNameList
	if not _isInitialized:
		_budgetSugInit()
	
	if len(_budgetNameList) == 0:
		return (None, '')
	
	low = -1
	high = len(_budgetNameList)-1
	while high-low > 1:
		mid = (low + high)/2
		if _budgetNameList[mid][0] >= curInput:
			high = mid
		else:
			low = mid
	
	if _budgetNameList[high][0].startswith(curInput):
		return (_budgetNameList[high][1], _budgetNameList[high][0])
	
	return (None, '')
