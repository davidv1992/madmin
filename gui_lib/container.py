from widget import Widget
from gui_util import intersect

# Simple container, list of children is not meant to be mutable
class Container(Widget):
	def __init__(self, width, height):
		super(Container, self).__init__(width, height)
		self.children = []
		self.curFocus = 0
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		for (child_x, child_y, child_widget) in self.children:
			(child_width, child_height) = child_widget.size()
			regions = intersect((minx, miny, maxx, maxy),
			      (child_x, child_y, child_x+child_width, child_y+child_height))
			for (cminx, cminy, cmaxx, cmaxy) in regions:
				child_widget.draw(canvas, offsetx+child_x, offsety+child_y,
					cminx-child_x, cminy-child_y, cmaxx-child_x, cmaxy-child_y)
	
	def addChild(self, child_x, child_y, child_widget):
		self.children.append((child_x, child_y, child_widget))
		return len(self.children)-1
	
	def getChild(self, index):
		return self.children[index]
	
	def remChild(self, index):
		self.children.pop(index)
	
	def setChildPos(self, index, child_x, child_y):
		self.children[index] = (child_x, child_y, self.children[index][2])
	
	def numChildren(self):
		return len(self.children)
	
	def onFocus(self):
		while self.curFocus < len(self.children):
			if self.children[self.curFocus][2].onFocus():
				return True
			self.curFocus += 1
		self.curFocus = 0
		return False
	
	def changeFocus(self):
		# child that has focus gets chance to handle it self first
		if self.children[self.curFocus][2].changeFocus():
			return True
		
		# Then we handle it
		self.curFocus += 1
		while self.curFocus < len(self.children):
			if self.children[self.curFocus][2].onFocus():
				return True
			self.curFocus += 1
		self.curFocus = 0
		return False
	
	def offFocus(self):
		self.children[self.curFocus][2].offFocus()
		
	def keyEvent(self, key):
		if self.curFocus < len(self.children):
			return self.children[self.curFocus][2].keyEvent(key)
