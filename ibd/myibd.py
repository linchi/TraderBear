import requests
import re
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IBDSession(object):
    ENTRY_UTL='https://research.investors.com'
    LOGIN_URL = 'https://myibd.investors.com/secure/signin.aspx'
    IBD50_URL = 'https://research.investors.com/stock-lists/ibd-50/'
    CANSLIM_URL = 'https://research.investors.com/stock-lists/can-slim-select/'
    SECTORLEADER_URL = 'https://research.investors.com/stock-lists/sector-leaders'
    UPEST_URL = 'https://research.investors.com/stock-lists/rising-profit-estimates/'
    BYFUNDS_URL = 'https://research.investors.com/stock-lists/stocks-that-funds-are-buying/'

    def __init__(self, credential, driverPath):
        self.user = credential['user']
        self.pwd = credential['password']
        self.browser = webdriver.Chrome(driverPath)

    def loginrequest(self):
        payload = {
            'action': 'login',
            'username': self.user,
            'password': self.pwd
        }

        # with requests.session() as c:
        #     c.post(self.LOGIN_URL, data=payload)
        #     response = c.get('https://research.investors.com/stock-lists/ibd-50/')
        #     print(response.headers)
        #     print(response.text)
        session_requests = requests.session()
        result = session_requests.post(
            self.LOGIN_URL,
            data=payload,
            headers=dict(referer=self.LOGIN_URL)
        )
        print result.text
        page = session_requests.get(
            self.IBD50_URL,
            headers=dict(referer=self.IBD50_URL)
        )
        print page.text
        return True

    def loginPage(self):
        self.browser.get(self.LOGIN_URL)
        # innerHTML = self.browser.execute_script("return document.body.innerHTML")

        frame = WebDriverWait(self.browser, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, 'signin-iframe'))
        )
        # self.browser.switch_to_frame('signin-iframe')
        # html = self.browser.page_source
        # print htm        # html = self.browser.page_source
        # print html
        user = WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//form[@id='gigya-login-form']/div/div/div/input[@name='username']"))
        )
        # user = self.browser.find_element_by_name('username')
        user.send_keys(self.user)
        pw = WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//form[@id='gigya-login-form']/div/div/div/input[@name='password']"))
        )
        # pw = self.browser.find_element_by_name('password')
        pw.send_keys(self.pwd)
        sub = WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//form[@id='gigya-login-form']/div/div/div/input[@type='submit']"))
        )
        sub.click()
        login = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.account-initials'))
        )

        print "Login success for", login.text

    def getIBD50(self):
        return self._getStockLisk(self.IBD50_URL)

    def getCANSLIM(self):
        return self._getStockLisk(self.CANSLIM_URL)

    def getSectorLeader(self):
        return self._getStockLisk(self.SECTORLEADER_URL)

    def getUpEstimation(self):
        return self._getStockLisk(self.UPEST_URL)

    def getByFunds(self):
        return self._getStockLisk(self.BYFUNDS_URL)

    def _getStockLisk(self, listURL):
        list = {}
        self.browser.get(listURL)
        table = WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='stockListMobileTable']/table/tbody"))
        )
        # print self.browser.page_source
        for t in table.find_elements_by_tag_name('tr'):
            entry = t.find_elements_by_tag_name('td')[0].find_element_by_css_selector('a.slSymbol')
            symbol = entry.text
            # link is in attribute:
            # onclick='OpenQuotes("https://research.investors.com/stock-quotes/nasdaq-abiomed-inc-abmd.htm");'
            link = entry.get_attribute('onclick')[12:-3]
            list[symbol] = link
        print 'get back list length ', len(list)
        return list

    def filterLeaderBorad(self, ibd50):
        leader = {}
        for key, value in ibd50.iteritems():
            link = re.sub('/stock-quotes/', '/stock-charts/', value) + '?cht=pvc&type=daily'
            if self._isOnLeaderBoard(link):
                print key, 'YES', link
                leader[key] = link
            else:
                print key, 'NO'
        return leader

    def _isOnLeaderBoard(self, link):
        self.browser.get(link)
        chart = WebDriverWait(self.browser, 100).until(
            EC.visibility_of_element_located((By.ID, "chart-content"))
        )
        board = chart.find_element_by_id('dvLeaderboard')
        return 'display: block;' in board.get_attribute('style')

    def getStockUtlFromSymbol(self, symbol):
        self.browser.get(self.ENTRY_UTL)
        form = WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'section.nav-container'))
        )
        search = form.find_element_by_tag_name("input")
        search.send_keys(symbol)
        search.send_keys(Keys.ENTER)
        company = WebDriverWait(self.browser, 30).until(
            EC.url_matches('https://research.investors.com/stock-quotes/*')
        )
        stockUrl = self.browser.current_url
        # 'https://research.investors.com/stock-quotes/nasdaq-amazoncom-inc-amzn.htm?fromsearch=1'
        # remove the end "?fromsearch=1"
        return stockUrl[0:-13]


    def checkSymbol(self, symbol):
        stockUrl = self.getStockUtlFromSymbol(symbol)
        # print stockUrl
        self.browser.get(stockUrl)
        cr = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.CheckupBox'))
        )
        rating = cr.find_element_by_tag_name('span').text
        print symbol, "composite rating ", rating

        chart = re.sub('/stock-quotes/', '/stock-charts/', stockUrl) + '?cht=pvc&type=daily'
        onboard = self._isOnLeaderBoard(chart)
        print symbol, "is ", onboard, " on leaderboard"

        failedChecks = self.checkup(stockUrl)
        print symbol, "has ", len(failedChecks), ' failed checks: ', str(failedChecks)


    def checkup(self, stockLink):
        # 'https://research.investors.com/stock-quotes/nasdaq-amazoncom-inc-amzn.htm'
        # 'https://research.investors.com/stock-checkup/nasdaq-amazoncom-inc-amzn.aspx'
        failed = []
        checkupLink = re.sub('/stock-quotes/', '/stock-checkup/', stockLink)
        checkupLink = re.sub('.htm', '.aspx', checkupLink)
        print checkupLink
        self.browser.get(checkupLink)
        print "Checking technical"
        tech = WebDriverWait(self.browser, 30).until(
            EC.presence_of_element_located((By.ID, 'stock-checkup-technical'))
        )
        rows = tech.find_elements_by_tag_name('tr')
        for r in rows:
            cols = r.find_elements_by_tag_name('td')
            p = cols[2].find_element_by_tag_name('a')
            passFail = self.__checkPass(p.get_attribute('rel'))
            if passFail == 'FAIL':
                failed.append(cols[0].text)

            print cols[0].text, cols[1].text, passFail
        return failed

    def __checkPass(self, attr):
        if '#cluetipPass' == attr:
            return 'PASS'
        elif '#cluetipNeutral' == attr:
            return 'WARN'
        elif '#cluetipFail' == attr:
            return 'FAIL'
        else:
            print 'Does not categorize', attr
            return attr


    def close(self):
        self.browser.quit()

class CredentialReader:
    def __init__(self, credFile):
        self.file = credFile

    def getCredentials(self):
        data = json.load(open(self.file))
        return {
            'user': data["user"],
            'password': data["password"]
        }

def getLeader(cred, driver):
    session = IBDSession(cred, driver)
    try:
        session.loginPage()
        # ibd50 = session.getIBD50()
        sec = session.getIBD50()
        print 'BY FUNDS', str(sec)
        leaders = session.filterLeaderBorad(sec)
        print 'LEADER', str(leaders.keys())
    finally:
        session.close()


def checkStock(cred, driver):
    symbol = 'AMZN'
    session = IBDSession(cred, driver)
    try:
        session.loginPage()
        session.checkSymbol(symbol)
    finally:
        session.close()

def main():
    driverPath = '/Users/linchi/workspace/git/TraderBear/chromedriver'
    cred = CredentialReader('/tmp/ibdCredential.json')
    checkStock(cred.getCredentials(), driverPath)

if __name__ == "__main__":
    main()

