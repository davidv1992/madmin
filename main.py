import logging

logging.basicConfig(level=logging.DEBUG)

import madmin_server

#Functionality modules
import madmin_user

#Data modules
import madmin_barcodes
import madmin_budget
import madmin_products
import madmin_voorraad

madmin_server.run()
