import xml.etree.ElementTree as ET
from xml.dom import minidom
import datetime

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
        self.relationShips = []
        relationshipNode = ownerNode.getElementsByTagName('reportingOwnerRelationship')[0]
        addRelationship(self.relationShips, relationshipNode, 'isDirector')
        addRelationship(self.relationShips, relationshipNode, 'isOfficer')
        addRelationship(self.relationShips, relationshipNode, 'isTenPercentOwner')
        addRelationship(self.relationShips, relationshipNode, 'isOther')
    def __str__(self):
        return "Owner: {}, {}".format(self.name, self.relationShips)

class TransactionAmounts:
    def __init__(self, amountNode):
        self.transactionShares = int(getValue(amountNode.getElementsByTagName('transactionShares')[0]))
        self.transactionPricePerShare = float(getValue(amountNode.getElementsByTagName('transactionPricePerShare')[0]))
        self.transactionAcquiredDisposedCode = 'Acquired' if getValue(amountNode.getElementsByTagName('transactionAcquiredDisposedCode')[0]) == 'A' else 'Disposed'

    def __str__(self):
        return "Transaction shares: {}\n\npricePerShare: {}\n\ncode: {}\n".format(self.transactionShares, self.transactionPricePerShare, self.transactionAcquiredDisposedCode)

class PostTransactionAmounts:
    def __init__(self, amountNode):
        self.sharesOwnedFollowingTransaction = int(getValue(amountNode.getElementsByTagName('sharesOwnedFollowingTransaction')[0]))
    def __str__(self):
        return "PostTransactionAmounts: {}\n".format(self.sharesOwnedFollowingTransaction)

class TransactionCode:
    CODE = {
        'P': 'OpenPurchase',
        'S': 'OpenSale',
        'V': 'ColuntarilyReport',
        'A': 'Grant',
        'D': 'Disposition',
        'F': 'TaxWithhold',
        'I': 'DiscretionaryTransaction',
        'M': 'ExerciseOfConversion',
        'C': 'Conversion',
        'E': 'ExpirationShort',
        'H': 'ExpirationLong',
        'O': 'ExerciseOTM',
        'X': 'ExerciseITM'
    }
    def __init__(self, code):
        self.coding = code

    def __str__(self):
        return self.CODE[self.coding] if self.coding in self.CODE else self.coding

class TransactionCoding:
    def __init__(self, codingNode):
        self.transactionFormType = codingNode.getElementsByTagName('transactionFormType')[0].firstChild.data
        self.transactionCode = TransactionCode(codingNode.getElementsByTagName('transactionCode')[0].firstChild.data)
        self.equitySwapInvolved = codingNode.getElementsByTagName('equitySwapInvolved')[0].firstChild.data
        # TODO: read footnote

    def __str__(self):
        return "Transaction FormType: {}\n\nTransactionCode: {}\n\nequitySwapInvolved: {}\n".\
            format(self.transactionFormType, self.transactionCode, self.equitySwapInvolved)

class OwnershipNature:
    def __init__(self, natureNode):
        value = natureNode.getElementsByTagName('directOrIndirectOwnership')[0].firstChild.data
        self.nature = 'Direct' if value == 'D' else 'InDirect'

    # TODO: read footnote

    def __str__(self):
        return "Transaction FormType: {}\n\nTransactionCode: {}\n\nequitySwapInvolved: {}\n". \
            format(self.transactionFormType, self.transactionCode, self.equitySwapInvolved)


class NonDerivativeTransaction:
    def __init__(self, transactionNode):
        self.date = getValue(transactionNode.getElementsByTagName('transactionDate')[0])
        self.securityTitle = getValue(transactionNode.getElementsByTagName('securityTitle')[0])
        self.transActionAmount = TransactionAmounts(transactionNode.getElementsByTagName('transactionAmounts')[0])
        self.transActionCoding = TransactionCoding(transactionNode.getElementsByTagName('transactionCoding')[0])
        self.postTransactionAmount = PostTransactionAmounts(transactionNode.getElementsByTagName('postTransactionAmounts')[0])
        self.ownershipNature = OwnershipNature(transactionNode.getElementsByTagName('ownershipNature')[0])
    def __str__(self):
        return "Transaction: title {}\n\nAmount: {}\n\nPostAmount: {}\n\nDate: {}\n\nCode: {}\n". \
            format(self.securityTitle, self.transActionAmount, self.postTransactionAmount, self.date, self.transActionCoding)


class NonDerivativeTransactionTable:
    def __init__(self, nonDerivative):
        transActions = nonDerivative.getElementsByTagName('nonDerivativeTransaction')
        self.transactions = []
        for trans in transActions:
            self.transactions.append(NonDerivativeTransaction(trans))

    def getAquiredShares(self):
        return self.__getSharesOfOperationType('Acquired')

    def getDisposedShares(self):
        return self.__getSharesOfOperationType('Disposed')

    def getPostTransactionShare(self):
        shares = {}
        for t in self.transactions:
#            print t.securityTitle, t.postTransactionAmount.sharesOwnedFollowingTransaction
            shares[t.securityTitle] = t.postTransactionAmount.sharesOwnedFollowingTransaction
        return shares

    def significantTrans(self, threshold):
        aquired = self.__getSharesOfOperationType('Acquired')
        disposed = self.__getSharesOfOperationType('Disposed')
        postTrans = self.getPostTransactionShare()
        result = {'SignificantAcquired': [], 'SignificantDisposed': []}
        for key, value in postTrans.iteritems():
            if key in aquired:
                ap = 1 if postTrans[key] == aquired[key] else aquired[key]/float(postTrans[key] - aquired[key])
#                print aquired[key], postTrans[key], ap
                if ap > threshold:
                    result['SignificantAcquired'].append({
                        key: {
                            'percentage': '{:.2%}'.format(ap),
                            'transShares': aquired[key],
                            'postTransShares': postTrans[key]
                        }})
            if key in disposed:
                dp = disposed[key]/float(postTrans[key] + disposed[key])
#                print disposed[key], postTrans[key], dp
                if dp > threshold:
                    result['SignificantDisposed'].append({
                        key: {
                            'percentage': '{:.2%}'.format(dp),
                            'transShares': disposed[key],
                            'postTransShares': postTrans[key]
                        }})
        return result


    def __getSharesOfOperationType(self, type):
        shares = {}
        for t in filter(lambda e : e.transActionAmount.transactionAcquiredDisposedCode == type, self.transactions):
#            print t.transActionCoding.transactionCode
            if t.securityTitle in shares:
                shares[t.securityTitle] += t.transActionAmount.transactionShares
            else:
                shares[t.securityTitle] = t.transActionAmount.transactionShares
        return shares


class Filing4DocReader:
    SIG_TRANS_THRESHOLD = 0.1
    def __init__(self, xmlDoc):
        self.doc = xmlDoc
        self.root = minidom.parse(self.doc)

    def getIssuer(self):
        issuer = Issuer(self.root.getElementsByTagName('issuer')[0])
        return issuer

    def getReportDate(self):
        dateStr = self.root.getElementsByTagName('periodOfReport')[0].firstChild.data
        return datetime.datetime.strptime(dateStr, '%Y-%m-%d').date()

    def getOwner(self):
        owner = Owner(self.root.getElementsByTagName('reportingOwner')[0])
        return owner

    def getNonDerivativeTransactions(self):
        table = NonDerivativeTransactionTable(self.root.getElementsByTagName('nonDerivativeTable')[0])
        return table

    def reportSigfinicantTrans(self):
        sigTrans = self.getNonDerivativeTransactions().significantTrans(Filing4DocReader.SIG_TRANS_THRESHOLD)
        if not sigTrans['SignificantAcquired'] and not sigTrans['SignificantDisposed']:
            print "skipping ", self.getReportDate(), self.getOwner().name
            return None
        else:
            result = str(self.getReportDate()) + ' ' + str(self.getIssuer().symbol) + ' ' + str(self.getOwner()) + '\n'
            if sigTrans['SignificantAcquired']:
                result += 'SignificantAcquired' + str(sigTrans['SignificantAcquired'])
            if sigTrans['SignificantDisposed']:
                result += 'SignificantDisposed' +  str(sigTrans['SignificantDisposed'])
            return result


def addRelationship(relationshipList, relationshipNode, relationshipType):
    isType = relationshipNode.getElementsByTagName(relationshipType)[0].firstChild.data
    if isType == '1':
        relationshipList.append(relationshipType)

def getValue(parentNode):
    return filter(lambda e : e.nodeType == 1, parentNode.childNodes)[0].firstChild.data