# Product type constants
product_type_kantine = 1 # Required
product_type_borrel = 2
product_type_emballage = 3

# Product type description mapping
product_name_mapping = {
	product_type_kantine: 'kantine',
	product_type_borrel: 'borrel',
	product_type_emballage: 'emballage',
}

product_id_mapping = {
	'kantine': product_type_kantine,
	'borrel': product_type_borrel,
	'emballage': product_type_emballage,
}
