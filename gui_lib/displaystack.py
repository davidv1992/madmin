from widget import Widget

class DisplayStack(Widget):
	def __init__(self, width, height):
		super(DisplayStack,self).__init__(width, height)
		self.pages = []
	
	def resize(self, width, height):
		super(DisplayStack,self).resize(width,height)
		for page in self.pages:
			page.resize(width, height)
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		if len(self.pages) == 0:
			return
		self.pages[-1].draw(canvas, offsetx, offsety, minx, miny, maxx, maxy)
	
	def push(self, page):
		page.resize(self.width, self.height)
		self.pages.append(page)
		page.onFocus()
	
	def pop(self):
		self.pages.pop()
	
	def onFocus(self):
		if len(self.pages) == 0:
			return False
		else:
			return self.pages[-1].onFocus()
	
	def changeFocus(self):
		if len(self.pages) == 0:
			return False
		else:
			return self.pages[-1].changeFocus()
	
	def offFocus(self):
		if len(self.pages) == 0:
			return
		else:
			self.pages[-1].offFocus()
	
	def keyEvent(self, key):
		if len(self.pages):
			self.pages[-1].keyEvent(key)
