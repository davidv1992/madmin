from factuurData import FactuurData
from factuurInputRegel import FactuurInputHeader
from factuurRegelList import FactuurRegelList
from gui_lib.container import Container
from gui_lib.label import Label
from gui_lib.button import Button
from client_lib.servercall import remote_call, ServerCallException

class FactuurInput(Container):
	def __init__(self, width, height):
		super(FactuurInput, self).__init__(width, height)
		
		self.factuurData = FactuurData(1,1)
		self.factuurListHeader = FactuurInputHeader(1,1)
		self.factuurRegelList = FactuurRegelList(1,1)
		self.statusLine = Label(1,1,"")
		self.submitButton = Button(1,1,self.sendFactuur,"Submit")
		
		self.factuurListHeaderIdx = self.addChild(0,0, self.factuurListHeader)
		self.statusLineIdx = self.addChild(0,0,self.statusLine)
		self.submitButtonIdx = self.addChild(0,0,self.submitButton)
		self.factuurDataIdx = self.addChild(0,0, self.factuurData)
		self.factuurRegelListIdx = self.addChild(0,0,self.factuurRegelList)
		
		self.resize(width, height)
	
	def resize(self, width, height):
		self.width = width
		self.height = height
		
		vOffset = 0
		
		self.factuurData.resize(width, 1)
		self.setChildPos(self.factuurDataIdx, 0, 0)
		vOffset += self.factuurData.size()[1]
		
		self.factuurListHeader.resize(width, 1)
		self.setChildPos(self.factuurListHeaderIdx, 0, vOffset)
		vOffset += 1
		
		self.factuurRegelList.resize(width, height - vOffset-1)
		self.setChildPos(self.factuurRegelListIdx, 0, vOffset)
		vOffset = height-1
		
		self.submitButton.resize(min(width, 6), 1)
		self.setChildPos(self.submitButtonIdx, 1, vOffset)
		self.statusLine.resize(width-min(width, 8), 1)
		self.setChildPos(self.statusLineIdx, min(width, 8), vOffset)
		
	
	def sendFactuur(self):
		result = self.generateFactuur()
		
		if not result[0]:
			self.statusLine.setText(result[2])
			return
		
		if not result[1]:
			self.statusLine.setText("Insufficient input given")
			return
		
		try:
			submitResult = remote_call('/factuur/create', jsondata = result[2])
		except ServerCallException:
			self.statusLine.setText("Kon geen verbinding maken met server.")
			return
		
		if 'error' in submitResult:
			self.statusLine.setText(submitResult['error'].encode('utf-8'))
			return
		
		self.statusLine.setText("")
		self.remChild(self.factuurRegelListIdx)	#warning: fragile
		self.remChild(self.factuurDataIdx)
		self.factuurData = FactuurData(1,1)
		self.factuurDataIdx = self.addChild(0,0,self.factuurData)
		self.factuurRegelList = FactuurRegelList(1,1)
		self.factuurRegelListIdx = self.addChild(0,0,self.factuurRegelList)
		self.resize(self.width, self.height)
		
	def generateFactuur(self):
		result = self.factuurData.generateFactuur()
		
		if not result[0] or not result[1]:
			return result
		
		factuur = result[2]
		
		result = self.factuurRegelList.generateFactuurRegels()
		
		if not result[0] or not result[1]:
			return result
		
		factuur['regels'] = result[2]
		
		return (True, True, factuur)
