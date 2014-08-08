from gui_lib.container import Container
from gui_lib.label import Label
from gui_lib.textline import Textline
from gui_lib.fill import Fill
from gui_lib.optionbox import Optionbox
from verenigingLine import VerenigingLine
from budgetLine import BudgetLine
import datetime

class FactuurData(Container):
	def __init__(self, width, height):
		super(FactuurData,self).__init__(width, height)

		# Layout settings
		self.labelWidth = 23
		self.minValueWidth = 20

		self.otherPartyLabel = Label(0,1,"Vereniging/Leverancier")
		self.otherPartyValue = VerenigingLine(1)

		self.leverDatumLabel = Label(0,1,"Leverdatum")
		self.leverDatumValue = Textline(0)
		
		self.separatorFill = Fill(0,0,'|')
		
		self.verantwoordelijkeLabel = Label(0,1,"Verantwoordelijke")
		self.verantwoordelijkeValue = Textline(0)

		self.specialBudgetLabel = Label(0,1,"Speciaal budget")
		self.specialBudgetValue = BudgetLine(1)
		
		self.typeValue = Optionbox(1,1)
		self.typeValue.addOption('inkoop')
		self.typeValue.addOption('verkoop')
		
		self.typeValueIdx = self.addChild(0,0,self.typeValue)
		self.otherPartyLabelIdx = self.addChild(0,0,self.otherPartyLabel)
		self.otherPartyValueIdx = self.addChild(0,0,self.otherPartyValue)
		self.leverDatumLabelIdx = self.addChild(0,0,self.leverDatumLabel)
		self.leverDatumValueIdx = self.addChild(0,0,self.leverDatumValue)
		self.separatorFillIdx = self.addChild(0,0,self.separatorFill)
		self.verantwoordelijkeLabelIdx = self.addChild(0,0,self.verantwoordelijkeLabel)
		self.verantwoordelijkeValueIdx = self.addChild(0,0,self.verantwoordelijkeValue)
		self.specialBudgetLabelIdx = self.addChild(0,0,self.specialBudgetLabel)
		self.specialBudgetValueIdx = self.addChild(0,0,self.specialBudgetValue)
		
		self.resize(width, 0)
	
	def resize(self, width, height):
		#  ignore height, selfdetermined
		self.width = width
		
		self.typeValue.resize(width,1)
		self.setChildPos(self.typeValueIdx, 0,0)
		
		if (self.width-1)/2 - self.labelWidth >= self.minValueWidth:
			#two column layout
			colWidth = (self.width-1)/2
			colOffset = colWidth+1
			valueWidth = max(0, colWidth - self.labelWidth)
			
			self.separatorFill.resize(1,2)
			self.setChildPos(self.separatorFillIdx, colWidth, 1)
			
			self.otherPartyLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.otherPartyLabelIdx, 0, 1)
			self.otherPartyValue.resize(valueWidth, 1)
			self.setChildPos(self.otherPartyValueIdx, self.labelWidth, 1)
			
			self.leverDatumLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.leverDatumLabelIdx, 0, 2)
			self.leverDatumValue.resize(valueWidth, 1)
			self.setChildPos(self.leverDatumValueIdx, self.labelWidth, 2)
			
			self.verantwoordelijkeLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.verantwoordelijkeLabelIdx, colOffset, 1)
			self.verantwoordelijkeValue.resize(valueWidth, 1)
			self.setChildPos(self.verantwoordelijkeValueIdx, colOffset + self.labelWidth, 1)
			
			self.specialBudgetLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.specialBudgetLabelIdx, colOffset, 2)
			self.specialBudgetValue.resize(valueWidth, 1)
			self.setChildPos(self.specialBudgetValueIdx, colOffset + self.labelWidth, 2)
			
			self.height = 3
		else:
			valueWidth = max(0, self.width - self.labelWidth)
			
			self.separatorFill.resize(0,0)
			self.setChildPos(self.separatorFillIdx, 0,0)
			
			self.otherPartyLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.otherPartyLabelIdx, 0, 1)
			self.otherPartyValue.resize(valueWidth, 1)
			self.setChildPos(self.otherPartyValueIdx, self.labelWidth, 1)
			
			self.leverDatumLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.leverDatumLabelIdx, 0, 2)
			self.leverDatumValue.resize(valueWidth, 1)
			self.setChildPos(self.leverDatumValueIdx, self.labelWidth, 2)
			
			self.verantwoordelijkeLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.verantwoordelijkeLabelIdx, 0, 3)
			self.verantwoordelijkeValue.resize(valueWidth, 1)
			self.setChildPos(self.verantwoordelijkeValueIdx, self.labelWidth, 3)
			
			self.specialBudgetLabel.resize(self.labelWidth, 1)
			self.setChildPos(self.specialBudgetLabelIdx, 0, 4)
			self.specialBudgetValue.resize(valueWidth, 1)
			self.setChildPos(self.specialBudgetValueIdx, self.labelWidth, 4)
			
			self.height = 5
	
	def generateFactuur(self):
		if self.otherPartyValue.text == "":
			return (False, False, "Mis vereniging/leverancier")
		if self.leverDatumValue.text == "":
			return (False, False, "Mis leverdatum")
			
		try:
			datetime.datetime.strptime(self.leverDatumValue.text, "%Y-%m-%d")
		except ValueError:
			return (False, False, "Ongeldige leverdatum")
		
		result = {}
		
		result['type'] = self.typeValue.text
		
		if self.otherPartyValue.currentID is not None:
			result['vereniging'] = self.otherPartyValue.currentID
			if self.specialBudgetValue.currentID is not None:
				result['saldo_speciaal'] = self.specialBudgetValue.currentID
		else:
			result['leverancier'] = self.otherPartyValue.text
		
		result['leverdatum'] = self.leverDatumValue.text
		result['factuurdatum'] = datetime.datetime.today().strftime("%Y-%m-%d")
		
		if self.verantwoordelijkeValue.text != "":
			result['verantwoordelijke'] = self.verantwoordelijkeValue.text
		
		return (True, True, result)
