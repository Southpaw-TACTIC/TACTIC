import smtplib
import sys
from email.MIMEText import MIMEText

class EmailTest(object):

    def __init__(self):
        self.mailserver = 'smtp.gmail.com'
        self.user =''
        self.password = ''
        self.port = '587'
        self.sender_email = 'name@emailserver.com'
        self.mail_tls_enabled = True 
        self.mail_sender_disabled = False
        self.recipient_emails = ['name@emailserver.com']
        self.msg = 'Subject: test \n testing'
    
    def email(self):    
        s = smtplib.SMTP()
        s.connect(self.mailserver, self.port)

        if self.mail_tls_enabled:
            s.ehlo()
            s.starttls()
            s.ehlo()

        if self.user:
            s.login(self.user,self.password)
        s.set_debuglevel(1)
        if self.mail_sender_disabled:
            # to get around some email server security check if the addr 
            # is owned by the sender email address's owner
            self.sender_email = ''
        s.sendmail(self.sender_email, self.recipient_emails, self.msg)
        s.quit()

if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main = EmailTest()
    main.email()

