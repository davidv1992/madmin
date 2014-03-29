from gui_lib.container import Container
from gui_lib.label import Label
from gui_lib.listbox import Listbox
from client_lib.servercall import remote_call
from factuurList import factuurList
import curses

class verenigingListItem(Label):
	def __init__(self, width, vereniging_info, manager):
		self.manager = manager
		super(verenigingListItem,self).__init__(width, 1, vereniging_info[1].encode('utf-8'))
		self.vereniging_info = vereniging_info
	
	def keyEvent(self, key):
		if key == ord('\n'):
			self.manager.push(factuurList(1,1,
				remote_call('/factuur/vereniging',[('vereniging_id', self.vereniging_info[0])]),
				self.manager))
		
	def onFocus(self):
		self.setAttribute(curses.A_REVERSE)
		return True
	
	def offFocus(self):
		self.setAttribute(curses.A_NORMAL)

class leverancierListItem(Label):
	def __init__(self, width, manager):
		self.manager = manager
		super(leverancierListItem,self).__init__(width, 1, 'leveranciers')
	
	def keyEvent(self, key):
		if key == ord('\n'):
			self.manager.push(factuurList(1,1,
				remote_call('/factuur/leverancier'), self.manager))
	
	def onFocus(self):
		self.setAttribute(curses.A_REVERSE)
		return True
	
	def offFocus(self):
		self.setAttribute(curses.A_NORMAL)

class verenigingList(Container):
	def __init__(self, width, height, vereniging_list, manager):
		super(verenigingList, self).__init__(width, height)
		self.manager = manager
		self.listbox = Listbox(width, height)
		for vereniging_info in vereniging_list:
			self.listbox.append(verenigingListItem(width,vereniging_info,manager))
		self.listbox.append(leverancierListItem(width,manager))
		
		self.listboxId = self.addChild(0,0,self.listbox)
	
	def resize(self, width, height):
		self.width = width
		self.height = height
		self.listbox.resize(width, height)
