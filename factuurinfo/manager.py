from gui_lib.displaystack import DisplayStack
from gui_lib.core import end

class factuurManager(DisplayStack):
	def keyEvent(self, key):
		if key == ord('x'):
			end()
		else:
			super(factuurManager,self).keyEvent(key)
