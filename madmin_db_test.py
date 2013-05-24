import time
import logging

logging.basicConfig()

import madmin_db

i = 0
while True:
	try:
		q = madmin_db.Query("SELECT value FROM test")
		q.run()
		print "Succes", i
	except madmin_db.DatabaseError, e:
		print "Fail", i
	i = i + 1
	time.sleep(1)
