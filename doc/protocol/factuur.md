Factuur JSON protocol
=====================

The factuur module is responsible for processing facturen, and presenting them back to any applications that interact with them.

Output format
-------------
A factuur consists of one or more lines, together with some auxilary information. Note: fields with ? are optional, and | denotes alternatives.
FACTUURREGEL_OUT := {
	'aantal': aantal,
	'stukprijs': stukprijs,
	'totaalprijs': totaalprijs,
	'btw': btw_bedrag,
	'naam': naam,
	('prd_id': product_id,)?
}
FACTUUR_OUT := {
	'id': id_number,
	'type': type_description,
	('vereniging': vereniging_id )|('leverancier': leverancier_naam),
	('verantwoordelijke': verantwoordelijke,)?
	'volgnummer': numbering_in_category_year,
	'factuurdatum': factuurdatum,
	'leverdatum': leverdatum,
	'regels': [FACTUURREGEL_OUT*],
	(
		'saldo_basis': saldo_basis_id,
		'saldo_basis_na': saldo_basis_value_after_transaction
		(
			'saldo_speciaal': saldo_speciaal_id,
			'saldo_speciaal_na': saldo_speciaal_value_after_transaction
		)?
	)?
}

Input format
------------
Output facturen contain a few cases of duplicate or extra information which, in order to preserve system-wide consistency, MUST NOT be present in input facturen.
Notes:
 - price information should not be present on verkoop (aantal > 0) when a product id is given.
FACTUURREGEL_IN := {
	'aantal': aantal,
	(('stukprijs': stukprijs) | ('totaalprijs': totaalprijs))?,
	(
		'naam': product name,
		'btw': btw_percentage,
	) | (
		'product_id': product_id,
	)
}
FACTUUR_IN := {
	'type': type,
	(
		'vereniging': vereniging_id,
		('saldo_speciaal': saldo_speciaal_id,)?
	)|(
		'leverancier': leverancier_naam,
	)
	('verantwoordelijke': verantwoordelijke,)?
	'factuurdatum': factuurdatum,
	'leverdatum': leverdatum,
	'regels': [FACTUURREGEL_IN*]
}

/factuur
--------
Facilitate querying facturen with factuur id's:
Input Arguments:
	factuur_id*
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[FACTUUR_OUT*]

/factuur/vereniging
-------------------
Facilitate querying facturen belong to verenigingen
Input Arguments:
	vereniging_id*
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[FACTUUR_OUT*]

/factuur/leverancier
--------------------
Facilitate querying of all facturen belonging to leveranciers
Input Arguments:
	None
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[FACTUUR_OUT*]

/factuur/create
---------------
Handle the creation of new facturen.
Input Arguments:
	None
Input JSON:
	FACTUUR_IN
Authentication:
	Required
Output JSON:
	{'error': message} | {'Succes': 1}
