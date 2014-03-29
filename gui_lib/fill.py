from widget import Widget
import curses

class Fill(Widget):
	def __init__(self, width, height, character, attribute=curses.A_NORMAL):
		super(Fill, self).__init__(width, height)
		self.attribute = attribute
		self.character = character
	
	def setAttribute(self, attribute):
		self.attribute = attribute
	
	def setCharacter(self, character):
		self.character = character
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		for x in range(minx, maxx):
			for y in range(miny, maxy):
				canvas.addch(y+offsety, x+offsetx, self.character, self.attribute)
