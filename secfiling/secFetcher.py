from xml.dom import minidom
from datetime import datetime, timedelta
import urllib2
import re
from type4 import *
from reporter import *

#page='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=4&dateb=&owner=include&count=40&output=atom'
page='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=4&dateb=&owner=include&count=40&output=atom'

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

def getFilings(companypage, pastNdays):
    startday = (datetime.datetime.now() - timedelta(days=pastNdays)).date()
    response = fetchPage(companypage) 
    root = minidom.parse(response)
    listItems = root.getElementsByTagName('entry')
#    print 'item count: ', len(listItems)
    result = []
    for item in listItems:
    	filingdateStr = item.getElementsByTagName('filing-date')[0].firstChild.data
        filingdate = datetime.datetime.strptime(filingdateStr, '%Y-%m-%d').date()
    	if filingdate > startday:
            txt = readType4(item)
            if txt is not None:
                print txt
                result.append(txt)
        else:
            break
    if result:
        report(result)

def report(result):
    cred = CredentialReader('/tmp/emailCredential.json')
    subscriber = 'zhanglinchi@gmail.com'
    reporter = EmailReporter(result, cred.getCredentials(), subscriber)
#    reporter = StdoutReporter(result)
    reporter.report()

def readType4(item):
    docLink = __getDocLink(item)
    form = fetchPage(docLink)
    try:
        filing4 = Filing4DocReader(form)
        return filing4.reportSigfinicantTrans()

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
    getFilings(page, 10)

if __name__ == "__main__":
    main()
