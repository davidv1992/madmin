from gui_lib.listbox import Listbox
from factuurInputRegel import FactuurInputRegel

class FactuurRegelList(Listbox):
	def __init__(self, width, height):
		super(FactuurRegelList, self).__init__(width, height)
		
		self.append(FactuurInputRegel(self.width,1))
		
	def keyEvent(self, key):
		if key > 31 and key < 128 and self.curFocus == len(self.items)-1:
			self.append(FactuurInputRegel(self.width,1))
		
		return super(FactuurRegelList, self).keyEvent(key)
	
	def generateFactuurRegels(self):
		result = []
		
		for item in self.items:
			regel = item.generateFactuurRegel()
			if not regel[0]:
				return regel
			if regel[1]:
				result.append(regel[2])
		
		return (True, True, result)
