Verenigingen
============

The verenigingen module is responsible for managing vereniging information.

Vereniging JSON object
----------------------
Vereniging data is suplied using the following JSON object structure
VERENIGING := {
	'id': id,
	'naam': verenigingsnaam,
	'email': Email-address associated with vereniging,
	'basis_budget': Budget associated with vereniging
}

/verenigingen
-------------
Provides a list of all verenigingen with associated information
Input Parameters:
	None
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[VERENIGING*]
