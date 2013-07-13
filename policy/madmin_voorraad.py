import operator

def voorraad_order(voorraad):
	return sorted(voorraad, key=attrgetter('datum'))
