import pytest
from secfiling.reporter import EmailReporter, CredentialReader


def test_sendEmail():
    cred = CredentialReader('/tmp/emailCredential.json')
    you = 'zhanglinchi@gmail.com'
    result = ['my', 'test', 'email']
    reporter = EmailReporter(result, cred.getCredentials(), you)
    ok = reporter.report()
    assert ok

if __name__ == '__main__':
   pytest.main()