from xml.dom import minidom
import urllib2
import re
from type4 import *

googlepage='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&CIK=0001652044&type=&dateb=&owner=include&start=0&count=40&output=atom'

def fetchPage(pageLink):
	print "getting page ", pageLink
	try:
	    response = urllib2.urlopen(pageLink) 
	    print 'response headers: "%s"' % response.info()
	    return response
	except IOError, e:
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
    print 'item count: ', len(listItems)
    for item in listItems:
    	print item.getElementsByTagName('title')[0].firstChild.data
    	if item.getElementsByTagName('filing-type')[0].firstChild.data == '4':
            readType4(item)
            break


def readType4(item):
    print '=======reading filing type 4'
    link = item.getElementsByTagName('filing-href')[0].firstChild.data
    docPage = re.sub('[0-9a-z\-]+.htm$', 'doc4.xml', link)
    docPage = re.sub('^http', 'https', docPage)
    doc = fetchPage(docPage)
    print '=======printing filing 4 from page ', docPage
    filing4 = Filing4Reader(doc)
    filing4.parse()

def main():
    getFilings(googlepage)

if __name__ == "__main__":
    main()
