from email.mime.text import MIMEText
import smtplib
import json


class CredentialReader:
    def __init__(self, credFile):
        self.file = credFile

    def getCredentials(self):
        data = json.load(open(self.file))
        return {
            'user': data["user"],
            'password': data["password"]
        }


class EmailReporter:
    EMAIL_SUBJECT = 'SEC filling past 10 day summary'
    def __init__(self, resultList, credential, recipient):
        self.txt = '\n\n'.join(resultList)
        self.sender = credential['user']
        self.pwd = credential['password']
        self.recipient = recipient

    def report(self):
        print 'sending email'
        return self.__sendEmail()

    def __sendEmail(self):
        FROM = self.sender
        TO = [self.recipient]
        SUBJECT = self.EMAIL_SUBJECT
        TEXT = self.txt

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
        try:
            server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server_ssl.ehlo()  # optional, called by login()
            server_ssl.login(self.sender, self.pwd)
            # ssl server doesn't support or need tls, so don't call server_ssl.starttls()
            server_ssl.sendmail(FROM, TO, message)
            # server_ssl.quit()
            server_ssl.close()
            print 'successfully sent the mail'
            return True
        except:
            print "failed to send mail"
            return False

class StdoutReporter:
    def __init__(self, resultList):
        self.txt = '\n'.join(resultList)

    def report(self):
        print '====output result to console'
        print self.txt
