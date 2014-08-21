Product JSON protocol
=====================

For the communication of information about products two interfaces are used in madmin. One is meant primarily for kantine endpoints and will remain read only. The other interface provides all product information known to the system and (in a future version) will be read/write.

Kantine product JSON object
---------------------------
This communicates all product information relevant to kantine endpoints
PRODUCT_KANTINE := {
	'id': product_id,
	'naam': product_naam,
	'prijs_leden': prijs_ledenvanleden,
	'prijs_extern': prijs_externen,
}

Full product JSON object
------------------------
All properties registered in madmin for a product
PRODUCT_RELATION := {
	'id': product_id_related_product,
	'aantal': aantal,
}
PRODUCT := {
	'id': product_id,
	'naam': product_naam,
	'type': product_type,
	'btw': btw_percentage,
	('kantineprijs_leden': kantineprijs_ledenvanleden,)?
	('kantineprijs_extern': kantineprijs_externen,)?
	('borrelmarge': marge_borrelverkoop,)?
	'leverancier_id': idcode_for_product_leverancier,
	('embalageprijs': embalagevalue,)?
	'related': [PRODUCT_RELATION*],
}

/product
--------
Interface for requesting info for single product.
Input Arguments
	product_id*
Input JSON
	None
Authentication
	None
Output JSON
	[PRODUCT*]

/product/all
------------
Interface for requesting info on all products.
Input Arguments
	None
Input JSON
	None
Authentication
	None
Output JSON
	[PRODUCT*]

/product/kantine
----------------
Interface for requesting kantine product information
Input Arguments:
	None
Input JSON:
	None
Authentication:
	None
Output JSON
	[PRODUCT_KANTINE*]
