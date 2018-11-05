###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ["EmailTrigger","EmailTrigger2", "EmailTriggerThread", "SendEmail", "EmailTriggerTest", "EmailTriggerTestCmd"]


import re
import threading
import smtplib
import types
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.mime.application import MIMEApplication
from email.MIMEImage import MIMEImage
from email.Utils import formatdate
from command import CommandException

from pyasm.common import *
from pyasm.biz import Project, GroupNotification, Notification, CommandSObj, ProdSetting
from pyasm.biz import ExpressionParser
from pyasm.security import *
from pyasm.search import SObject, Search, SearchType, SObjectValueException
from pyasm.command import Command
from trigger import *

class EmailTrigger(Trigger):

    def __init__(self):
        super(EmailTrigger, self).__init__()
        self.cmd_attrs = {}


    def get_title(self):
        return "EmailTrigger"

    def check(self):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def execute(self):

        print("WARNING: EmailTrigger deprecated, use EmailTrigger2")

        # get command sobject and the notification code associated with it
        class_name = self.get_command().__class__.__name__
        cmd_sobj = CommandSObj.get_by_class_name(class_name)
        # if this command is not registered, it cannot have a notification
        # code, so skip
        if not cmd_sobj:
            return
        self.notification_code = cmd_sobj.get_value('notification_code')


        # get the search objects operated on by the command and iterate
        # through them
        command = self.get_command()
        sobjects = command.get_sobjects()
        if not sobjects:
            msg = "Command [%s] has no sobjects.  Triggers cannot be called" % class_name
            Environment.add_warning("Command has no sobjects", msg)

        input = self.get_input()

        # TODO: figure out what to do when there are multiple sobjects
        # Right now, there is a single mail per sobject which may be
        # way too heavy.
        for sobject in sobjects:
            self.handle_sobject(sobject, command, input)



    def handle_sobject(self, main_sobject, command, input):

        search_type = main_sobject.get_search_type_obj().get_base_key()
        parent = None
        if main_sobject.has_value('search_type') and main_sobject.has_value('search_id'):
            parent = main_sobject.get_parent() 
            if not parent:
                Environment.add_warning('Parent not found', 'Parent not found for task [%s]' % main_sobject.get_search_key())
                return

            # the command needs to set this info if it wants to search 
            # for the search type of its parent
            if command.get_info('parent_centric') == True:
                search_type = parent.get_search_type_obj().get_base_key()

        # get all of the notifications for this search_type
        search = Search("sthpw/notification")
        #search.add_where("(\"search_type\" = '%s' or \"search_type\" is NULL)"% search_type)
        search.add_filter("search_type", search_type)
        search.add_where("(\"project_code\" = '%s' or \"project_code\" is NULL)" % Project.get().get_code() )
        
        # Basically, this selects which command this notification will be
        # run from.  Other commands will be ignored.
        search.add_filter("code", self.notification_code)
        notifications = search.get_sobjects()
        
        # send an email for each notification that matches the rules
        for notification in notifications:
            # check if there are any recievers for this notification
            notification_id = notification.get_id()

            #logins = GroupNotification.get_logins_by_id(notification_id)
            #if not logins:
            #    continue
            # get the rules from the database
            rules_xml = notification.get_xml_value("rules")
            rule_nodes = rules_xml.get_nodes("rules/rule")
            is_skipped = True
            for rule_node in rule_nodes:
                rule = []
                group_type = Xml.get_attribute( rule_node, "group" )
                rule_key = Xml.get_attribute(rule_node, 'key')
                rule_value = Xml.get_attribute(rule_node, 'value')
                compare = Xml.get_attribute(rule_node, 'compare')
                # parse the rule
                if group_type == "sobject":
                    if not self._process_sobject(main_sobject, rule_key, compare):
                        break
                    value = main_sobject.get_value(rule_key, no_exception=True )
                elif group_type == "parent":
                    if not parent or not self._process_sobject(parent, rule_key, compare):
                        break
                    value = parent.get_value(rule_key, no_exception=True )
                else: # group_type == 'command'
                    value = command.get_info(rule_key)
                if not value:
                    break
                
                # match the rule to the value
                p = re.compile(rule_value)
                if not p.match(value):
                    print "... skipping: '%s' != %s" % (value, rule_value)
                    break
            else:
                is_skipped = False
           
            # allow the handler to check for whether an email should be sent
            handler = self.get_email_handler(notification, main_sobject, parent, command, input)
            if is_skipped or not handler.check_rule():
                continue
            # if all rules are met then get the groups for this notification

            try:
                to_users = handler.get_to()
                cc_users = handler.get_cc()
                bcc_users = handler.get_bcc()


                subject = handler.get_subject()
                if len(subject) > 60:
                    subject = subject[0:60] + " ..."
                message = handler.get_message()
            except SObjectValueException, e:
                raise Exception("Error in running Email handler [%s]. %s" \
                        %(handler.__class__.__name__, e.__str__()))

            # set the email
            self.send(to_users, cc_users, bcc_users, subject, message)
            
            
            from_user = Environment.get_user_name()

            project_code = Project.get_project_code()
            # log the notification
            sobject = SearchType.create("sthpw/notification_log")
            sobject.set_value("command_cls", command.get_title())
            sobject.set_user()
            sobject.set_value("subject", subject)
            sobject.set_value("message", message)
            sobject.set_value("project_code", project_code)
            sobject.commit(triggers=False)

            log_id = sobject.get_id()

            # add the recipients
            # log the notification
            for to_user in to_users:
                login = to_user.get_value("login")
                sobject = SearchType.create("sthpw/notification_login")
                sobject.set_value("notification_log_id", log_id)
                sobject.set_value("login", login)
                sobject.set_value("type", "to")
                sobject.set_value("project_code", project_code)
                sobject.commit(triggers=False)

            sobject = SearchType.create("sthpw/notification_login")
            sobject.set_value("notification_log_id", log_id)
            sobject.set_value("login", from_user)
            sobject.set_value("type", "from")
            sobject.set_value("project_code", project_code)
            sobject.commit(triggers=False)




    def _process_sobject(self, sobject, rule_key, compare):
        # if the sobject does not have this value, then return
        if not sobject.has_value(rule_key):
            print "... skipping: sobject has no attr: '%s'" % rule_key
            return False

        # if the value hasn't changed ... don't bother
        value = sobject.get_value(rule_key)
        if compare not in ["False", "false"]:
            prev_value = sobject.get_prev_value(rule_key)
            if value == prev_value:
                return False

        return True


    def get_email_handler(self, notification, sobject, parent, command, input={}):

        email_handler_cls = notification.get_value("email_handler_cls")
        if not email_handler_cls:
            email_handler_cls = "EmailHandler"

        handler = Common.create_from_class_path(email_handler_cls, [notification, sobject, parent, command, input])
        return handler


    def add_email(cls, email_set, email):
        if email.find('@') > 0:
            email_set.add(email)
    add_email = classmethod(add_email)

    def send(cls, to_users, cc_users, bcc_users, subject, message, cc_emails=[], bcc_emails=[], from_user=None):

        cc = set()
        sender = set()
        to_emails = set()
        total_cc_emails = set()
        total_bcc_emails = set()
        recipients = set()

        if cc_emails:
            total_cc_emails.update(cc_emails)
        if bcc_emails:
            total_bcc_emails.update(bcc_emails)

        if from_user:
            sender.add(from_user)
            user_email = from_user
        else:
            user_email = Environment.get_login().get_full_email()
            if not user_email:
                print("Sender's email is empty. Please check the email attribute of [%s]." %Environment.get_user_name())
                return
            sender.add(user_email)

        for x in to_users:
            print "ssssss: ", x
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x

            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(to_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                
                cls.add_email(to_emails, email)


        for x in cc_users:
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x
            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(total_cc_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                cls.add_email(total_cc_emails, email)

        for x in bcc_users:
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x
            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(total_bcc_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                cls.add_email(total_bcc_emails, email)
        total_cc_emails = total_cc_emails - to_emails
        total_bcc_emails = total_bcc_emails - to_emails - total_cc_emails

        charset = 'us-ascii'
        is_uni = False
        if type(message) == types.UnicodeType:
            message = message.encode('utf-8')
            subject = subject.encode('utf-8')
            charset = 'utf-8'
            is_uni = True
        
        if "<html>" in message:
            st = 'html'
        else:
            st = 'plain'
        
        msg = MIMEText(message, _subtype=st, _charset=charset)
        ''' 
        msg['Subject'] = subject
        msg['From'] = user_email
        msg['Reply-To'] = user_email
        msg['To'] = ", ".join(to_emails)
        msg['Cc'] = ','.join(total_cc_emails)
        msg['Bcc'] = ','.join(total_bcc_emails)
        msg['Date'] = formatdate(localtime=True)
        '''
        
        msg.add_header('Subject', subject)
        msg.add_header('From', user_email)
        msg.add_header('Reply-To', user_email)
        msg.add_header('To', ", ".join(to_emails))
        msg.add_header('Cc', ", ".join(total_cc_emails))
        msg.add_header('Bcc', ", ".join(total_bcc_emails))
        msg.add_header('Date', formatdate(localtime=True))
        if is_uni:
            msg.add_header('html_encoding', 'base64')
       
        email_to_sender = ProdSetting.get_value_by_key('email_to_sender')
        if not email_to_sender:
            email_to_sender = 'false'

        if email_to_sender in ['False','false']:
            recipients = total_bcc_emails|total_cc_emails|to_emails
        else:
            recipients = total_bcc_emails|total_cc_emails|to_emails|sender

        email = EmailTriggerThread(user_email, recipients, "%s" %msg.as_string())
        email.start()
              
        
    send = classmethod(send)






class SendEmail(Command):

    '''Class to send an email in a separate thread. The kwargs are as follows:
        sender_email - string
        recipient_emails - list of strings
        msg - string, email message
        subject - string, email header
        cc - list of cc in email header
        bcc - list of strings, email header
        paths - paths of files to attach
    '''
    def execute(self):
        
        sender_email = self.kwargs.get('sender_email')
        sender_name = self.kwargs.get('sender_name')
        paths = self.kwargs.get("paths") or []

        if not sender_email:
            sender_email = Environment.get_login().get_full_email()
            if not sender_email:
                print("Sender's email is empty. Please check the email attribute of [%s]." %Environment.get_user_name())
                return

        recipient_emails = self.kwargs.get('recipient_emails')
        message = self.kwargs.get('msg')

        is_unicode = False
        if "<html>" in message or paths:
            st = 'html'
        else:
            st = 'plain'
        charset = 'us-ascii'
        subject = "Email Test"
        new_subject = self.kwargs.get('subject')
        if new_subject:
            subject = new_subject


        cc = self.kwargs.get('cc') or []
        bcc = self.kwargs.get('bcc') or []

        if type(message) == types.UnicodeType:
            message = message.encode('utf-8')
            subject = subject.encode('utf-8')
            charset = 'utf-8'
            is_unicode = True


        msg = MIMEMultipart()
        msg.add_header('Reply-To', sender_email)
        msg.add_header('To',  ','.join(recipient_emails))
        msg.add_header('Date', formatdate(localtime=True))
        msg.add_header('Cc', ','.join(cc))
        msg.add_header('Bcc', ','.join(bcc))


        msg_text = MIMEText(message, _subtype=st, _charset=charset)
        msg.attach(msg_text)

        for path in paths:
            #message = '''<div style="text-align: center"><img src="cid:%s"/></div>''' % path
            #msg_text = MIMEText(message, _subtype=st, _charset=charset)
            #msg.attach(msg_text)

            with open(path, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=os.path.basename(path)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(path)
            msg.attach(part)

       

        msg.add_header('Subject', subject)
        if sender_name:
            msg.add_header('From', "%s <%s>" % (sender_name, sender_email))
        else:
            msg.add_header('From', "%s" % sender_email)

        if is_unicode:
            msg.add_header('html_encoding', 'base64')

        recipient_emails = set(recipient_emails)
        cc = set(cc)
        bcc = set(bcc)

        recipients =  cc|bcc|recipient_emails

        email = EmailTriggerThread(sender_email, recipients, "%s" %msg.as_string())
        email.start()

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)






class EmailTrigger2(EmailTrigger):

    def __init__(self):
        super(EmailTrigger, self).__init__()
        self.cmd_attrs = {}

    def get_title(self):
        return "EmailTrigger"

    def check(self):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def execute(self):
        # get the caller
        caller = self.get_caller()

        # check to see if the caller is a serach object
        import pyasm
        if isinstance(caller, pyasm.search.SObject):
            sobjects = [caller]
        else:
            sobjects = caller.get_sobjects()
            if not sobjects:
                msg = "Caller has no sobjects.  Triggers cannot be called" 
                Environment.add_warning("Caller has no sobjects", msg)


        # get the notification
        notification = self.get_trigger_sobj()
        input = self.get_input()

        # TODO: figure out what to do when there are multiple sobjects
        # Right now, there is a single mail per sobject which may be
        # too heavy.
        for sobject in sobjects:
            self.handle_sobject(sobject, caller, notification, input)



    def handle_sobject(self, main_sobject, caller, notification, input):

        # TODO: deal with parents later
        parent = main_sobject.get_parent()

        snapshot = input.get('snapshot')
        env_sobjects = {}
        if snapshot:
            env_sobjects['snapshot'] = snapshot
        note = input.get('note')
        if note:
            env_sobjects['note'] = note

        
        # get the rules from the database
        rules_xml = notification.get_xml_value("rules")
        rule_nodes = rules_xml.get_nodes("rules/rule")
        is_skipped = True

        parser = ExpressionParser()
        
        # process the rules
        for rule_node in rule_nodes:
            rule = []
            group_type = Xml.get_attribute( rule_node, "group" )
            rule_key = Xml.get_attribute(rule_node, 'key')
            rule_value = Xml.get_attribute(rule_node, 'value')
            compare = Xml.get_attribute(rule_node, 'compare')

            # evaluate the expression if it exists
            expression = Xml.get_node_value(rule_node)
            if expression:
                result = parser.eval(expression, main_sobject, env_sobjects=env_sobjects)
                if not result:
                    break
                else:
                    continue

            # DEPRECATED: likely the expression complete replaces this
            # parse the rule
            if group_type == "sobject":
                if not self._process_sobject(main_sobject, rule_key, compare):
                    break
                value = main_sobject.get_value(rule_key, no_exception=True )
            elif group_type == "parent":
                if not parent or not self._process_sobject(parent, rule_key, compare):
                    break
                value = parent.get_value(rule_key, no_exception=True )
            else: # group_type == 'command'
                try:
                    value = caller.get_info(rule_key)
                except:
                    value = ''
            if not value:
                break
            
            # match the rule to the value
            p = re.compile(rule_value)
            if not p.match(value):
                print "... skipping: '%s' != %s" % (value, rule_value)
                break

        else:
            is_skipped = False


        # allow the handler to check for whether an email should be sent
        handler = self.get_email_handler(notification, main_sobject, parent, caller, input)
        if is_skipped or not handler.check_rule():
            self.add_description('Notification not sent due to failure to pass the set rules. Comment out the rules for now if you are just running email test.')
            return


        # if all rules are met then get the groups for this notification
        try:
            to_users = handler.get_to()
            cc_users = handler.get_cc()
            bcc_users = handler.get_bcc()

            subject = handler.get_subject()
            if len(subject) > 60:
                subject = subject[0:60] + " ..."
            message = handler.get_message()
        except SObjectValueException, e:
            raise Exception("Error in running Email handler [%s]. %s" \
                    %(handler.__class__.__name__, e.__str__()))

        if not to_users:
            return

        #sobj_data = main_sobject.get_aux_data()
        #email_info = sobj_data.get('__tactic_email_info__')
        #extra_ccs = email_info.get('mail_cc')
        #extra_bccs = email_info.get('mail_bcc')
        # send the email
        if handler.send_email():
            self.send(to_users, cc_users, bcc_users, subject, message)
            self.add_description('\nEmail sent to [%s]' %all_emails) 
    
        if isinstance(to_users, set) and isinstance(cc_users, set) and \
                isinstance(bcc_users, set):
            all_users = to_users.union(cc_users).union(bcc_users)
        elif isinstance(to_users, list) and isinstance(cc_users, list) and \
                isinstance(bcc_users, list):
            all_users = set(to_users + cc_users + bcc_users)
        else:
            raise TacticException('to, cc and bcc_users should be of the same type')

        # filter out email addr as set does not work on SObjects
        email_list = []
        email_users = set()
        if handler.send_email():
            for user in all_users:
                if type(user) in types.StringTypes:
                    email = user
                else:
                    email =  user.get_value('email')
                if email not in email_list:
                    email_users.add(user)
                    email_list.append(email)
        else:
            email_users = all_users
        project_code = Project.get_project_code()

        all_emails = ", ".join(email_list)
        self.add_notification(email_users, subject, message, project_code, from_user='')

    def add_notification(all_users, subject, message, project_code, from_user=''):

        if not from_user:
            from_user = Environment.get_user_name()
        # log the notification
        sobject = SearchType.create("sthpw/notification_log")
        #sobject.set_value("command_cls", command.get_title())
        sobject.set_user()
        sobject.set_value("subject", subject)
        sobject.set_value("message", message)
        sobject.set_value("project_code", project_code)
        sobject.commit(triggers=False)

        log_id = sobject.get_id()

        # add the recipients
        # log the notification
        for to_user in all_users:
            if isinstance(to_user, Login):
                login = to_user.get_value("login")
            else:
                login = to_user

            sobject = SearchType.create("sthpw/notification_login")
            sobject.set_value("notification_log_id", log_id)
            sobject.set_value("login", login)
            sobject.set_value("type", "to")
            sobject.set_value("project_code", project_code)
            sobject.commit(triggers=False)

        sobject = SearchType.create("sthpw/notification_login")
        sobject.set_value("notification_log_id", log_id)
        sobject.set_value("login", from_user)
        sobject.set_value("type", "from")
        sobject.set_value("project_code", project_code)
        sobject.commit(triggers=False)

    add_notification = staticmethod(add_notification)







class EmailTriggerThread(threading.Thread):
    '''Sending email as a separate thread'''
    def __init__(self, sender_email, recipient_emails, msg):
        super(EmailTriggerThread,self).__init__()
        self.sender_email = sender_email
        self.recipient_emails = recipient_emails
        self.msg = msg
        self.mailserver = Config.get_value('services','mailserver')
        # get optional arguments
        self.user = Config.get_value('services','mail_user', True)
        self.password = Config.get_value('services','mail_password', True)
        self.port = Config.get_value('services','mail_port', True)
        self.mail_sender_disabled = Config.get_value('services','mail_sender_disabled', True) == 'true'
        self.mail_tls_enabled = Config.get_value('services','mail_tls_enabled', True) == 'true'

        if not self.port:
            self.port = 25
        else:
            self.port = int(self.port)
            

    def set_mailserver(self, mailserver):
        self.mailserver = mailserver

   
    def run(self):
        try:
            s = smtplib.SMTP()
            s.connect(self.mailserver, self.port)

            if self.mail_tls_enabled:
                s.ehlo()
                s.starttls()
                s.ehlo()

            if self.user:
                s.login(self.user,self.password)
            #s.set_debuglevel(1)
            if self.mail_sender_disabled:
                # to get around some email server security check if the addr 
                # is owned by the sender email address's owner
                self.sender_email = ''
            s.sendmail(self.sender_email, self.recipient_emails, self.msg)
            s.quit()

        except Exception, e:
            print "-"*20
            print "WARNING: Error sending email:"
            print str(e)
            print
            print "mailserver: ", self.mailserver
            print "port: ", self.port
            print "sender: ", self.sender_email
            print "recipients: ", self.recipient_emails
            print
            #raise

class EmailTriggerTestCmd(Command):
    '''This is run in the same thread for the email testing button'''
    def __init__(self, **kwargs):
        
        self.kwargs = kwargs
        self.sender_email = self.kwargs.get('sender_email')

        if not self.sender_email:
            raise TacticException("Sender's email is empty.")
        self.recipient_emails = self.kwargs.get('recipient_emails')
        message = self.kwargs.get('msg')

        is_unicode = False
        st = 'plain'
        charset = 'us-ascii'
        subject = "Email Test"
        new_subject = self.kwargs.get('subject')
        if new_subject:
            subject = new_subject

        if type(message) == types.UnicodeType:
            message = message.encode('utf-8')
            subject = subject.encode('utf-8')
            charset = 'utf-8'
            is_unicode = True

        msg = MIMEText(message, _subtype=st, _charset=charset)
        msg.add_header('Subject', subject)
        msg.add_header('From', self.sender_email)
        msg.add_header('Reply-To', self.sender_email)
        msg.add_header('To',  ','.join(self.recipient_emails))
        msg.add_header('Date', formatdate(localtime=True))
       

        if is_unicode:
            msg.add_header('html_encoding', 'base64')
        self.msg = msg
        
        self.mailserver = Config.get_value('services','mailserver')
        # get optional arguments
        self.user = Config.get_value('services','mail_user', True)
        self.password = Config.get_value('services','mail_password', True)
        self.port = Config.get_value('services','mail_port', True)
        self.mail_sender_disabled = Config.get_value('services','mail_sender_disabled', True) == 'true'
        self.mail_tls_enabled = Config.get_value('services','mail_tls_enabled', True) == 'true'


        if not self.port:
            self.port = 25
        else:
            self.port = int(self.port)
         
        super(EmailTriggerTestCmd, self).__init__()

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def set_mailserver(self, mailserver):
        self.mailserver = mailserver

   
    def execute(self):
        try:
            s = smtplib.SMTP()
            s.connect(self.mailserver, self.port)

            if self.mail_tls_enabled:
                s.ehlo()
                s.starttls()
                s.ehlo()

            if self.user:
                s.login(self.user,self.password)
            #s.set_debuglevel(1)
            if self.mail_sender_disabled:
                # to get around some email server security check if the addr 
                # is owned by the sender email address's owner
                self.sender_email = ''
            s.sendmail(self.sender_email, self.recipient_emails, self.msg.as_string())
            s.quit()

        except Exception, e:
            msg = []
            msg.append( "-"*60)
            msg.append( "WARNING: Error sending email:")
            msg.append( str(e))
            msg.append( "mailserver: %s"%self.mailserver)
            msg.append("port: %s" %self.port)
            msg.append( "sender: %s"% self.sender_email)
            msg.append( "recipients: %s"% ','.join(self.recipient_emails))
            
            raise TacticException('\n'.join(msg))


class EmailTriggerTest(EmailTrigger2):
    ''' this is needed by Email Test button'''

    def send(cls, to_users, cc_users, bcc_users, subject, message, cc_emails=[], bcc_emails=[]):

        cc = set()
        sender = set()
        to_emails = set()
        total_cc_emails = set()
        total_bcc_emails = set()
    
        if cc_emails:
            total_cc_emails.update(cc_emails)
        if bcc_emails:
            total_bcc_emails.update(bcc_emails)

        user_email = Environment.get_login().get_full_email()
        sender.add(user_email)

        for x in to_users:
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x

            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(to_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                
                cls.add_email(to_emails, email)


        for x in cc_users:
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x
            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(total_cc_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                cls.add_email(total_cc_emails, email)

        for x in bcc_users:
            if isinstance(x, Login):
                email = x.get_full_email()
            elif isinstance(x, SObject):
                email = x.get_value("email", no_exception=True)
            else:
                email = x
            email_list = []
            if email.find(',') != -1:
                email_list = [y.strip() for y in email.split(',') if y.strip()]
                for email in email_list:
                    cls.add_email(total_bcc_emails, email)
            else:
                if not email:
                    print "WARNING: email for [%s] cannot be determined" % x
                    continue
                cls.add_email(total_bcc_emails, email)
        total_cc_emails = total_cc_emails - to_emails
        total_bcc_emails = total_bcc_emails - to_emails - total_cc_emails
        """
        charset = 'us-ascii'
        if type(message) == types.UnicodeType:
            message = Common.process_unicode_string(message) 
            charset = 'utf-8'

        if "<html>" in message:
            st = 'html'
        else:
            st = 'plain'
        msg = MIMEText(message, _subtype=st, _charset=charset)
        
        msg['Subject'] = subject
        msg['From'] = user_email
        msg['Reply-To'] = user_email
        msg['To'] = ", ".join(to_emails)
        msg['Cc'] = ','.join(total_cc_emails)
        msg['Bcc'] = ','.join(total_bcc_emails)
        
        '''
        msg.add_header('Subject', subject)
        msg.add_header('From', user_email)
        msg.add_header('Reply-To', user_email)
        msg.add_header('To', ", ".join(to_emails))
        msg.add_header('Cc', ", ".join(cc_emails))
        '''
        """
        recipient_emails =  total_bcc_emails|total_cc_emails|to_emails|sender
        email = EmailTriggerTestCmd(sender_email=user_email, \
                recipient_emails=recipient_emails, msg=message)
        email.execute()

    send = classmethod(send)
  
