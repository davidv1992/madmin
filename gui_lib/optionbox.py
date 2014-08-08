from label import Label
import curses

class Optionbox(Label):
	def __init__(self, width, height):
		super(Optionbox, self).__init__(width, height, "")
		self.options = []
		self.curOption = 0
	
	def addOption(self, opt):
		self.options.append(opt)
		if len(self.options) == 1:
			self.setText(self.options[0])
		
	def onFocus(self):
		self.setAttribute(curses.A_REVERSE)
		return True;
	
	def offFocus(self):
		self.setAttribute(curses.A_NORMAL)
		
	def keyEvent(self, key):
		if key == curses.KEY_UP or key == curses.KEY_LEFT:
			self.curOption -= 1
			if self.curOption < 0:
				self.curOption += len(self.options)
			self.setText(self.options[self.curOption])
		if key == curses.KEY_DOWN or key == curses.KEY_RIGHT:
			self.curOption += 1
			if self.curOption >= 0:
				self.curOption -= len(self.options)
			self.setText(self.options[self.curOption])
