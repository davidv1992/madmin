def voorraad_order(voorraad):
	return sorted(voorraad, key=lambda voorraad_el: voorraad_el['datum'])
