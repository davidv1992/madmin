from widget import Widget
import curses

class Listbox(Widget):
	def __init__(self, width, height):
		super(Listbox, self).__init__(width, height)
		
		self.items = []
		self.curFocus = 0
		self.curOffset = 0
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		for i in range(self.curOffset+miny, min(self.curOffset+maxy, len(self.items))):
			if miny < self.items[i].size()[0]:
				self.items[i].draw(canvas, offsetx, offsety+i-self.curOffset, 
					minx, 0, min(maxx, self.items[i].size()[0]), 1)
	
	def resize(self, width, height):
		self.width = width
		self.height = height
		for item in self.items:
			item.resize(width, 1)
		while (self.curFocus-self.curOffset >= self.height - min(1, self.height-1)
		and len(self.items)-self.curOffset > self.height):
			self.curOffset += 1
		while (self.curFocus - self.curOffset <= min(0, self.height-2)
		and self.curOffset > 0):
			self.curOffset -= 1
	
	def append(self, widget):
		if widget.size()[1] != 1:
			widget.resize(widget.size()[0], 1)
		self.items.append(widget)
		while (self.curFocus-self.curOffset >= self.height - min(1, self.height-1)
		and len(self.items)-self.curOffset > self.height):
			self.curOffset += 1
	
	def insert(self, pos, widget):
		if widget.size()[1] != 1:
			widget.resize(widget.size()[0],1)
		self.items.insert(pos,widget)
		while (self.curFocus-self.curOffset >= self.height - min(1, self.height-1)
		and len(self.items)-self.curOffset > self.height):
			self.curOffset += 1
	
	def remove(self, pos):
		self.items = self.items[:pos] + self.items[pos+1:]
		if self.curFocus >= len(self.items):
			self.curFocus -= 1
		while (self.curFocus-self.curOffset >= self.height - min(1, self.height-1)
		and len(self.items)-self.curOffset > self.height):
			self.curOffset += 1
		while (self.curFocus - self.curOffset <= min(0, self.height-2)
		and self.curOffset > 0):
			self.curOffset -= 1
	
	def keyEvent(self, key):
		#Handle the up and down arrow keys, rest is passed on
		if key == curses.KEY_UP:
			if self.curFocus > 0:
				self.items[self.curFocus].offFocus()
				self.curFocus -= 1
				self.items[self.curFocus].onFocus()
			while (self.curFocus - self.curOffset <= min(0, self.height-2)
			and self.curOffset > 0):
				self.curOffset -= 1
			return True
		elif key == curses.KEY_DOWN:
			if self.curFocus + 1 < len(self.items):
				self.items[self.curFocus].offFocus()
				self.curFocus += 1
				self.items[self.curFocus].onFocus()
			while (self.curFocus-self.curOffset >= self.height - min(1, self.height-1)
			and len(self.items)-self.curOffset > self.height):
				self.curOffset += 1
			return True
		else:
			return self.items[self.curFocus].keyEvent(key)
	
	def onFocus(self):
		if len(self.items) == 0:
			return False
		self.items[self.curFocus].onFocus()
		return True
	
	def changeFocus(self):
		return self.items[self.curFocus].changeFocus()
	
	def offFocus(self):
		self.items[self.curFocus].offFocus()
