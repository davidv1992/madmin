Authentication
==============

Madmin_user provides authentication and rights management for the rest of the madmin core server. For this, it provides an interface for loging in, as well as providing an interface component for other interfaces of madmin that require authentication.

Authentication interface
------------------------
Logged in user of the madmin core server are verified with the use of session keys. Login requests (see below) produce these, and any request requiring authentication expects to be supplied with an extra argument, session_key
Authentication Input Arguments:
	session_key

/login
------
Process a login request and produce a session key
Input Arguments:
	username, password
Input JSON:
	None
Authentication:
	None needed (obviously)
Return JSON:
	[Succes, session_key]
