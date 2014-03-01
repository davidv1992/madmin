Budget Module
=============

The budget module is responsible for providing access to budget information.

Budget JSON object
---------------------
All budget information is reported through json objects of the form
BUDGET := {
	'id': id
	'naam': naam
	'current': current value
	'minimum': minimum value
}

/budget
-------
Produce budget information belonging to one or more budget ids
Input parameters:
	budget_id (1 or more)
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[BUDGET*]

/budget/ver
-----------
Produce budget information for all budgets that belong to a vereniging
Input Parameters:
	vereniging_id (1 or more)
Input JSON:
	None
Authentication:
	Required
Output JSON:
	[BUDGET*]
