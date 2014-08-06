from widget import Widget
import core
import curses
import string

class Textline(Widget):
	def __init__(self, width, text="", attribute = curses.A_NORMAL, cursorPos=0):
		super(Textline, self).__init__(width, 1)
		self.text = text
		self.attribute = attribute
		self.hasFocus = False
		self.cursorPos = cursorPos
		self.setTextOffset()
	
	def resize(self, width, height):
		super(Textline, self).resize(width, height)
		self.setTextOffset()
	
	def setTextOffset(self):
		if (self.cursorPos < self.width):
			self.textOffset = 0
		else:
			self.textOffset = self.cursorPos + 1 - self.width
	
	def processInputCharacter(self, c):
		self.text = self.text[:self.cursorPos] + c + self.text[self.cursorPos:]
		self.cursorPos += 1
		if self.cursorPos - self.textOffset >= self.width:
			self.textOffset += 1
	
	def processDelete(self):
		if self.cursorPos == 0:
			return
		self.text = self.text[:self.cursorPos-1] + self.text[self.cursorPos:]
		self.cursorPos -= 1
		if self.cursorPos - self.textOffset < 1 and self.textOffset != 0:
			self.textOffset -= 1
	
	def processMove(self, direction):
		self.cursorPos += direction
		if self.cursorPos < 0 or self.cursorPos > len(self.text):
			self.cursorPos -= direction
			return
		if self.cursorPos - self.textOffset >= self.width:
			self.textOffset += 1
		if self.cursorPos - self.textOffset < 1 and self.textOffset != 0:
			self.textOffset -= 1
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		if miny > 0 or maxy < 0:
			return
		
		for x in range(minx, maxx):
			if x + self.textOffset >= len(self.text):
				canvas.addch(offsety, offsetx+x, ' ', self.attribute)
			else:
				canvas.addch(offsety, offsetx+x, self.text[x+self.textOffset],
				             self.attribute)
		if (self.hasFocus):
			core.setCursor(offsetx+self.cursorPos-self.textOffset,
				offsety)
	
	def keyEvent(self, key):
		#distinguish special keys
		if key > 256:
			if key == curses.KEY_ENTER:
				core.stepFocus()
				return True
			elif key == curses.KEY_BACKSPACE:
				self.processDelete()
				return True
			elif key == curses.KEY_DC:
				if len(self.text) > self.cursorPos:
					self.cursorPos += 1
					self.processDelete()
				return True
			elif key == curses.KEY_LEFT:
				self.processMove(-1)
				return True
			elif key == curses.KEY_RIGHT:
				self.processMove(1)
				return True
			else:
				return False
		else:
			if key == ord('\n') or key == ord('\t'):
				core.stepFocus()
				return True
			elif key < 32:
				return False
			elif key >= 127:
				return False
			else:
				ckey = chr(key)
				if (string.printable.find(ckey) != -1 and 
					string.whitespace.find(ckey) == -1) or ckey == ' ':
					self.processInputCharacter(ckey)
					return True
				else:
					return False
	
	def onFocus(self):
		self.hasFocus = True
		return True
	
	def offFocus(self):
		self.hasFocus = False
		core.unsetCursor()
		
	
