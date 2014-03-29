class Widget(object):
	def __init__(self, width, height):
		super(Widget, self).__init__()
		self.width = width
		self.height = height
		
	# Draw the widget
	#  canvas: curses window object to draw the widget on
	#  offset_{x,y}: offset of widget on window
	#  min{x,y}, max{x,y}: coordinates of region of widget to redraw
	#                      minima are inclusive, maxima exclusive
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		pass
		
	def resize(self, width, height):
		self.width = width
		self.height = height
		
	def size(self):
		return (self.width, self.height)
	
	# Return whether we accepted the focus
	def onFocus(self):
		return False
	
	def offFocus(self):
		pass
	
	# Return whether change was succesfull internally
	#  if not, widget loses focus WITHOUT call to offFocus
	# default implementation just call offFocus, and then returns false
	def changeFocus(self):
		self.offFocus()
		return False
	
	def keyEvent(self, key):
		pass
