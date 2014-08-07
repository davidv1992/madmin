from label import Label
import curses

class Button(Label):
	def __init__(self, width, height, action, text):
		super(Button, self).__init__(width, height, text)
		self.action = action
	
	def onFocus(self):
		self.setAttribute(curses.A_REVERSE)
		return True
	
	def offFocus(self):
		self.setAttribute(curses.A_NORMAL)
	
	def keyEvent(self, key):
		if key == curses.KEY_ENTER or key == ord('\n'):
			self.action()
