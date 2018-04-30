from datetime import datetime, timedelta
import urllib2
from xml.dom import minidom
import re

class Edgar(object):
    SEARCH_URL = ('https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany' \
                 '&CIK={company}&type={filing}&dateb={endday}&owner=include&count=40&output=atom')

    def __init__(self, companyCik, filingType):
        self.company = companyCik
        self.filing = filingType

    def getFilingDocuments(self, startDayStr, endDayStr):
        startday = datetime.strptime(startDayStr, '%Y-%m-%d').date()
        searchPageUrl = self.SEARCH_URL.format(company=self.company, filing=self.filing, endday=endDayStr)

        return self.__getDocuments(searchPageUrl, startday)

    def __getDocuments(self, searchPageUrl, startday):
        docs = []
        documentListPage = self.__readPage(searchPageUrl)
        root = minidom.parse(documentListPage)
        listItems = root.getElementsByTagName('entry')
        #    print 'item count: ', len(listItems)
        result = []
        for item in listItems:
            filingdateStr = item.getElementsByTagName('filing-date')[0].firstChild.data
            filingdate = datetime.strptime(filingdateStr, '%Y-%m-%d').date()
            if filingdate > startday:
                docLink = self.__getDocLink(item)
                docs.append(self.__readPage(docLink))
        return docs


    def __readPage(self, url):
        print "getting page ", url
        maxTry = 10
        while maxTry > 0:
            try:
                response = urllib2.urlopen(url)
                #	    print 'response headers: "%s"' % response.info()
                return response
            except IOError, e:
                print 'ERROR getting page', url
                if hasattr(e, 'code'):  # HTTPError
                    print 'http error code: ', e.code
                else:
                    print "error", e.code
            maxTry -= 1

        raise Exception("cannot connect to {}", url)

    def __getDocLink(self, item):
        #    print '=======reading filing type 4'
        formRef = item.getElementsByTagName('filing-href')[0].firstChild.data
        txtRef = re.sub('-index.htm$', '.txt', formRef)
        txtLink = re.sub('^http', 'https', txtRef)
        txtDoc = self.__readPage(txtLink)
        formFileName = None
        for line in txtDoc.readlines():
            if re.search('<FILENAME>.*\.xml$', line):
                formFileName = line[10:]
                break
        if formFileName is None:
            raise Exception("cannot extract xml document name")

        formLink = re.sub('[0-9a-z\-]+.htm$', formFileName, formRef)
        return formLink