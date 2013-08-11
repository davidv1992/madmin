import logging
from madmin_server import InternalServerError, add_handler
from madmin_db import Query, DatabaseError

log = logging.getLogger(__name__)

def handle_barcodes(params, json_data):
	try:
		log.debug("Fetching barcode table.")
		q = Query("SELECT bar_ean, bar_prd_id FROM tblbarcode")
		q.run()
		log.debug("Fetching rows.")
		rows = q.rows()
		log.debug("Rows: %s", rows)
		return rows
	except DatabaseError:
		raise InternalServerError

add_handler("/barcodes", handle_barcodes)
log.info("Barcode module initialized.")
