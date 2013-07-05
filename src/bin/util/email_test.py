import smtplib
import sys
from email.MIMEText import MIMEText

class EmailTest(object):

    def __init__(my):
        my.mailserver = 'smtp.gmail.com'
        my.user =''
        my.password = ''
        my.port = '587'
        my.sender_email = 'name@emailserver.com'
        my.mail_tls_enabled = True 
        my.mail_sender_disabled = False
        my.recipient_emails = ['name@emailserver.com']
        my.msg = 'Subject: test \n testing'
    
    def email(my):    
        s = smtplib.SMTP()
        s.connect(my.mailserver, my.port)

        if my.mail_tls_enabled:
            s.ehlo()
            s.starttls()
            s.ehlo()

        if my.user:
            s.login(my.user,my.password)
        s.set_debuglevel(1)
        if my.mail_sender_disabled:
            # to get around some email server security check if the addr 
            # is owned by the sender email address's owner
            my.sender_email = ''
        s.sendmail(my.sender_email, my.recipient_emails, my.msg)
        s.quit()

if __name__ == '__main__':
    
    executable = sys.argv[0]
    args = sys.argv[1:]
    main = EmailTest()
    main.email()

