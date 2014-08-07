from gui_lib.textline import Textline
from gui_lib.container import Container
from gui_lib.label import Label
from productLine import ProductLine
import curses

_regelLayout = [
	('Productnaam/omschrijving', 2, ProductLine),
	('Aantal', 1, Textline),
	('Bedrag per stuk', 1, Textline),
	('Bedrag totaal', 1, Textline)
]

def parseMoney(text):
	hadComma = False
	value = 0
	for i in range(0, len(text)):
		if text[i] != ',' and (text[i] < '0' or text[i] > '9'):
			return (False, 0)
		if text[i] == ',' and hadComma:
			return (False, 0)
		if text[i] == ',':
			value *= 100
		else:
			value += ord(text[i]) - ord('0')
	
	if not hadComma:
		value *= 100
	
	return (True, value)

class FactuurInputRegel(Container):
	def __init__(self, width, height):
		super(FactuurInputRegel, self).__init__(width, height)
		
		self.totalWeight = 0
		self.fieldControl = []
		self.fieldControlIdx = []
		for i in range(0, len(_regelLayout)):
			self.totalWeight += _regelLayout[i][1]
			self.fieldControl.append(_regelLayout[i][2](0))
			self.fieldControlIdx.append(self.addChild(0,0,self.fieldControl[-1]))
		
		self.resize(width, height)
	
	def resize(self, width, height):
		self.width = width
		self.height = height
		self.boxPerWeight = width/self.totalWeight
		
		offset = 0
		for i in range(0, len(_regelLayout)):
			self.fieldControl[i].resize(self.boxPerWeight * _regelLayout[i][1],1)
			self.setChildPos(self.fieldControlIdx[i], offset, 0)
			offset += _regelLayout[i][1] * self.boxPerWeight
	
	def generateFactuurRegel(self):
		result = {}
		
		if self.fieldControl[0].text == "":
			return (True, False, '')
		
		if self.fieldControl[0].currentID is not None:
			result['product_id'] = self.fieldControl[0].currentID
		else:
			result['naam'] = self.fieldControl[0].text
		result['aantal'] = int(self.fieldControl[1].text)
		if self.fieldControl[2].text != "":
			(isOk, stukprijs) = parseMoney(self.fieldControl[2].text)
			if not isOk:
				return (False, False, "Invalid stukprijs")
			result['stukprijs'] = stukprijs
		if self.fieldControl[3].text != "":
			(isOk, totaalprijs) = parseMoney(self.fieldControl[3].text)
			if not isOk:
				return (False, False, "Invalid totaalprijs")
			result['totaalprijs'] = totaalprijs
		
		return (True, True, result)
		

class FactuurInputHeader(Container):
	def __init__(self, width, height):
		super(FactuurInputHeader, self).__init__(width, height)
		
		self.totalWeight = 0
		self.fieldLabel = []
		self.fieldLabelIdx = []
		for i in range(0, len(_regelLayout)):
			self.totalWeight += _regelLayout[i][1]
			self.fieldLabel.append(Label(0,0,_regelLayout[i][0], curses.A_BOLD))
			self.fieldLabelIdx.append(self.addChild(0,0,self.fieldLabel[-1]))
		
		self.resize(width, height)
	
	def resize(self, width, height):
		self.width = width
		self.height = height
		self.boxPerWeight = width/self.totalWeight
		
		offset = 0
		for i in range(0, len(_regelLayout)):
			self.fieldLabel[i].resize(self.boxPerWeight * _regelLayout[i][1],1)
			self.setChildPos(self.fieldLabelIdx[i], offset, 0)
			offset += self.boxPerWeight * _regelLayout[i][1]
