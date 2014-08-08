from client_lib.servercall import remote_call

_isInitialized = False
_productList = None
_productNameList = []
_productNumberList = []

def _prodSugInit():
	global _isInitialized
	global _productList
	global _productNameList
	global _productNumberList
	_productList = remote_call('/product/all')
	
	# Build product name and number lists
	for product in _productList:
		_productNameList.append((product['naam'].encode('utf-8'), product['id']))
		_productNumberList.append((product['leverancier_id'].encode('utf-8'), product['id']))
	_productNameList.sort()
	_productNumberList.sort()
	
	_isInitialized = True

def findSuggestion(curInput):
	global _isInitialized
	global _productNameList
	global _productNumberList
	if not _isInitialized:
		_prodSugInit()
	
	low = -1
	high = len(_productNameList)-1
	while high - low > 1:
		mid = (high+low)/2
		if _productNameList[mid][0] >= curInput:
			high = mid
		else:
			low = mid
	
	if _productNameList[high][0].startswith(curInput):
		return (_productNameList[high][1], _productNameList[high][0])
	
	low = -1
	high = len(_productNumberList)-1
	while high - low > 1:
		mid = (high + low)/2
		if _productNumberList[mid][0] >= curInput:
			high = mid
		else:
			low = mid
	
	if _productNumberList[high][0].startswith(curInput):
		return (_productNumberList[high][1], _productNumberList[high][0])
	
	return (None, '')
