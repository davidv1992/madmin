from budgetSuggestion import findBudget
from gui_lib.textline import Textline
import gui_lib.core as core
import curses

class BudgetLine(Textline):
	def __init__(self, width, attribute=curses.A_NORMAL, attribute_suggestion=curses.A_REVERSE):
		super(BudgetLine,self).__init__(width, "", attribute)
		self.suggestion = ""
		self.suggestionID = None
		self.currentID = None
		self.attribute_suggestion = attribute_suggestion
	
	def draw(self, canvas, offsetx, offsety, minx, miny, maxx, maxy):
		if miny > 0 or maxy < 0:
			return
		
		super(BudgetLine,self).draw(canvas, offsetx, offsety, minx, miny, maxx, maxy)
		
		if self.hasFocus:
			for x in range(minx, maxx):
				if (x+self.textOffset >= len(self.text)
				   and x+self.textOffset < len(self.suggestion)):
					canvas.addch(offsety, offsetx+x, 
					  self.suggestion[x+self.textOffset], self.attribute_suggestion)
	
	def keyEvent(self,key):
		retVal = super(BudgetLine,self).keyEvent(key)
		
		if key >= 32 and key < 127:
			self.currentID = None;
			(self.suggestionID, self.suggestion) = findBudget(self.text)
			self.attribute = curses.A_NORMAL
		
		if key == curses.KEY_ENTER or key == ord('\n'):
			self.currentID = self.suggestionID
			self.text = self.suggestion
			if self.currentID is not None:
				self.attribute = curses.color_pair(core.COLORPAIR_GREEN)
		
		return retVal
