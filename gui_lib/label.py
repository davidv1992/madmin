from widget import Widget
from gui_util import text_arrange
import curses

class Label(Widget):
	def __init__(self, width, height, text, attr=curses.A_NORMAL):
		super(Label, self).__init__(width, height)
		self.text = text
		self.attribute = attr
	
	def setText(self, text):
		self.text = text
		self.dirty = True
	
	def setAttribute(self, attribute):
		self.attribute = attribute
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		lines = text_arrange(self.text, self.width, self.height)
		for line in lines:
			line.replace('\n', ' ')
		for x in range(minx, maxx):
			for y in range(miny, maxy):
				if y >= len(lines) or x >= len(lines[y]):
					canvas.addch(y+offsety,x+offsetx,' ',self.attribute)
				else:
					canvas.addch(y+offsety,x+offsetx,lines[y][x],self.attribute)
