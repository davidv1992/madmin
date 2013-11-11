import logging

logging.basicConfig(filename='/var/www/madmin-log.txt', level=logging.DEBUG)

import madmin_server

#Functionality modules
import madmin_user

#Data modules
import madmin_barcodes
import madmin_budget
import madmin_products
import madmin_voorraad
import madmin_vereniging
import madmin_factuur

def handler(req):
	return madmin_server.handler(req)	#Pass requests through to madmin_server
