from edgar import Edgar

def fetch10K(company, start, end):
    edgar = Edgar(company, '10')
    docs = edgar.getFilingDocuments(start, end)
    print "get back doc count: ", len(docs)
    for d in docs:
        print d


def main():
    fetch10K('AMZN', '2013-01-01', '2015-01-01')

if __name__ == "__main__":
    main()
