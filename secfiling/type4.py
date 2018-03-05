import xml.etree.ElementTree as ET
from xml.dom import minidom

class Issuer:
	def __init__(self, issuerNode):
		self.cik = issuerNode.getElementsByTagName('issuerCik')[0].firstChild.data
		self.name = issuerNode.getElementsByTagName('issuerName')[0].firstChild.data
		self.symbol = issuerNode.getElementsByTagName('issuerTradingSymbol')[0].firstChild.data
	def __str__(self):
		return "Issuer cik: {}\nIssuer name: {}\nIssuer symbol: {}\n".format(self.cik, self.name, self.symbol)

class Owner:
	def __init__(self, ownerNode):
		self.name = ownerNode.getElementsByTagName('rptOwnerName')[0].firstChild.data
		self.title = ownerNode.getElementsByTagName('officerTitle')[0].firstChild.data
		self.relationShips = []
		relationshipNode = ownerNode.getElementsByTagName('reportingOwnerRelationship')[0]
		addRelationship(self.relationShips, relationshipNode, 'isDirector')
		addRelationship(self.relationShips, relationshipNode, 'isOfficer')
		addRelationship(self.relationShips, relationshipNode, 'isTenPercentOwner')
		addRelationship(self.relationShips, relationshipNode, 'isOther')
	def __str__(self):
		return "Owner name: {}\nOwner title: {} \nOwner relationShips: {}\n".format(self.name, self.title, self.relationShips)

class NonDerivative:
	def __init__(self, nonDerivative):
		transActions = nonDerivative.getElementsByTagName('nonDerivativeTransaction')
		for trans in transActions:
			#TO DO

class Filing4Reader:
	def __init__(self, xmlDoc):
		self.doc = xmlDoc

	def parse(self):
		root = minidom.parse(self.doc)
		issuer = Issuer(root.getElementsByTagName('issuer')[0])
		print issuer
		owner = Owner(root.getElementsByTagName('reportingOwner')[0])
		print owner


def addRelationship(relationshipList, relationshipNode, relationshipType):
	isType = relationshipNode.getElementsByTagName(relationshipType)[0].firstChild.data
	if isType == '1':
		relationshipList.append(relationshipType)


