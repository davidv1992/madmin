Barcode JSON protocol
=====================

The barcode interface allows access to the list of barcodes registered with the server.

/barcodes
---------
The /barcodes interface provides a list of all registered EAN codes and their corresponding product id's in madmin
Input arguments:
	None
Input JSON:
	None
Authentication:
	None required
Output:
	JSON object of form
	[
		[ean_code, product_id]*
	]
