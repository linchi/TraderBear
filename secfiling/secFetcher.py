from xml.dom import minidom
import urllib2
import re
from type4 import *

page='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&CIK=0001652044&type=&dateb=&owner=include&start=0&count=10&output=atom'
#page='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&CIK=0001018724&type=&dateb=&owner=include&start=0&count=10&output=atom'

def fetchPage(pageLink):
#	print "getting page ", pageLink
	try:
	    response = urllib2.urlopen(pageLink) 
#	    print 'response headers: "%s"' % response.info()
	    return response
	except IOError, e:
	    print 'ERROR getting page', pageLink
	    if hasattr(e, 'code'): # HTTPError
	        print 'http error code: ', e.code
	    elif hasattr(e, 'reason'): # URLError
	        print "can't connect, reason: ", e.reason
	    else:
	        raise

def getFilings(companypage):
    response = fetchPage(companypage) 
    root = minidom.parse(response)
    listItems = root.getElementsByTagName('entry')
#    print 'item count: ', len(listItems)
    for item in listItems:
#    	print item.getElementsByTagName('title')[0].firstChild.data
    	if item.getElementsByTagName('filing-type')[0].firstChild.data == '4':
            readType4(item)

def readType4(item):
    docLink = __getDocLink(item)
    form = fetchPage(docLink)
    try:
        filing4 = Filing4DocReader(form)
        sigTrans = filing4.getNonDerivativeTransactions().significantTrans(Filing4DocReader.SIG_TRANS_THRESHOLD)
        if not sigTrans['SignificantAcquired'] and not sigTrans['SignificantDisposed']:
            print "skipping ", filing4.getReportDate(), filing4.getOwner().name
        else :
            print filing4.getReportDate(), filing4.getIssuer().symbol
            print filing4.getOwner()
            if sigTrans['SignificantAcquired']:
                print 'SignificantAcquired', sigTrans['SignificantAcquired']
            if sigTrans['SignificantDisposed']:
                print 'SignificantDisposed', sigTrans['SignificantDisposed']

    except:
        print "ERROR reading doc from page", docLink
        raise

def __writePageToFile(page):
    with open('type4.xml', 'w') as output:
        output.write(page.read())

#https://www.sec.gov/Archives/edgar/data/1018724/000101872418000048/0001018724-18-000048.txt
#https://www.sec.gov/Archives/edgar/data/1018724/000101872418000048/0001018724-18-000048-index.htm
#https://www.sec.gov/Archives/edgar/data/1018724/000101872418000048/wf-form4_151994208997238.xml
def __getDocLink(item):
#    print item
#    print '=======reading filing type 4'
    formRef = item.getElementsByTagName('filing-href')[0].firstChild.data
    txtRef = re.sub('-index.htm$', '.txt', formRef)
    txtLink = re.sub('^http', 'https', txtRef)
    txtDoc = fetchPage(txtLink)
    formFileNmae = __getFileName(txtDoc)
    formLink = re.sub('[0-9a-z\-]+.htm$', formFileNmae, formRef)
    return formLink


def __getFileName(txtResponse):
    name = None
    for line in txtResponse.readlines():
        if re.search('<FILENAME>', line):
            name = line[10:]
            break
    return name

def main():
    getFilings(page)

if __name__ == "__main__":
    main()
