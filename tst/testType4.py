import pytest
from secfiling.type4 import Filing4DocReader
import datetime

def test_parse3():
    expectation = {
        'date': datetime.datetime(2018, 2, 26).date(),
        'symbol': 'GOOG',
        'name': 'Alphabet Inc.',
        'owner': 'SCHMIDT ERIC E',
        'ownerRelation': 'isDirector',
        'acquired': {u'Class C Capital Stock': 2901, u'Class A Common Stock': 2768},
        'disposed': {u'Class C Google Stock Units': 5491, u'Class A Google Stock Units': 5491},
        'postTrans': {u'Class C Capital Stock': 1282228, u'Class C Google Stock Units': 21966, u'Class A Common Stock': 32629, u'Class A Google Stock Units': 21966},
        'sigAquire': [{u'Class A Common Stock': {'transShares': 2768, 'percentage': '9.27%', 'postTransShares': 32629}}],
        'sigDispose': [{u'Class C Google Stock Units': {'transShares': 5491, 'percentage': '20.00%', 'postTransShares': 21966}}, {u'Class A Google Stock Units': {'transShares': 5491, 'percentage': '20.00%', 'postTransShares': 21966}}]
    }
    __verifyFields('data/googtype4.xml', expectation)

def test_parse2():
    expectation = {
        'date': datetime.datetime(2018, 2, 28).date(),
        'symbol': 'AMZN',
        'name': 'AMAZON COM INC',
        'owner': 'WILKE JEFFREY A',
        'ownerRelation': 'isOfficer',
        'acquired': {},
        'disposed': {u'Common Stock, par value $.01 per share': 250},
        'postTrans': {u'Common Stock, par value $.01 per share': 55174},
        'sigAquire': [],
        'sigDispose': []

    }
    __verifyFields('data/amzntype4.xml', expectation)

def __verifyFields(doc, expectation):
    reader = Filing4DocReader(doc)
    print 'Date: ', reader.getReportDate()
    nonDerivativeTable = reader.getNonDerivativeTransactions()
    print "number of transactions: ",len(nonDerivativeTable.transactions)
    print "Acquired: ", nonDerivativeTable.getAquiredShares()
    print "Disposed: ", nonDerivativeTable.getDisposedShares()
    print "PostTrans: ", nonDerivativeTable.getPostTransactionShare()
    sigTrans = nonDerivativeTable.significantTrans(0.01)
    print "sig trans A: ", sigTrans['SignificantAcquired']
    print "sig trans D: ", sigTrans['SignificantDisposed']

    assert reader.getReportDate() == expectation['date']
    assert reader.getIssuer().symbol == expectation['symbol']
    assert reader.getIssuer().name == expectation['name']
    assert reader.getOwner().name == expectation['owner']
    assert reader.getOwner().relationShips.__contains__(expectation['ownerRelation'])
    assert nonDerivativeTable.getAquiredShares() == expectation['acquired']
    assert nonDerivativeTable.getDisposedShares() == expectation['disposed']
    assert nonDerivativeTable.getPostTransactionShare() == expectation['postTrans']
    assert sigTrans['SignificantAcquired'] == expectation['sigAquire']
    assert sigTrans['SignificantDisposed'] == expectation['sigDispose']


if __name__ == '__main__':
   pytest.main()