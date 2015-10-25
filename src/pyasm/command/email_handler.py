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

__all__ = ["EmailHandler", 'TaskAssignEmailHandler', 'NoteEmailHandler', 'GeneralNoteEmailHandler', 'GeneralPublishEmailHandler','TaskStatusEmailHandler', 'SubmissionStatusEmailHandler', 'SubmissionEmailHandler', 'SubmissionNoteEmailHandler', 'TestEmailHandler']

from pyasm.common import Environment, Xml, Date
from pyasm.security import Login, LoginGroup, Sudo
from pyasm.search import Search, SObject, SearchType
from pyasm.biz import GroupNotification, Pipeline, Task, Snapshot, File, Note
from pyasm.biz import ExpressionParser


class EmailHandler(object):
    '''Base class for email notifications'''

    def __init__(my, notification, sobject, parent, command, input):
        my.notification = notification
        my.sobject = sobject
        my.command = command
        my.parent = parent
        my.input = input

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True
        


    def get_mail_users(my, column):
        # mail groups
        recipients = set()

        expr = my.notification.get_value(column, no_exception=True)
        if expr:
            sudo = Sudo()
            # Introduce an environment that can be reflected
            env = {
                'sobject': my.sobject
            }

            #if expr.startswith("@"):
            #    logins = Search.eval(expr, list=True, env_sobjects=env)
            #else:
            parts = expr.split("\n")

            # go through each login and evaluate each
            logins = []
            for part in parts:
                if part.startswith("@") or part.startswith("{"):
                    results = Search.eval(part, list=True, env_sobjects=env)
                    # clear the container after each expression eval
                    ExpressionParser.clear_cache()
                    # these can just be login names, get the actual Logins
                    if results:
                        if isinstance(results[0], basestring):
                            login_sobjs = Search.eval("@SOBJECT(sthpw/login['login','in','%s'])" %'|'.join(results),  list=True)
                        
                            login_list = SObject.get_values(login_sobjs, 'login')
                            
                            for result in results:
                                # the original result could be an email address already
                                if result not in login_list:
                                    logins.append(result)
                                
                            if login_sobjs:
                                logins.extend( login_sobjs )
                        else:
                            logins.extend(results)

                elif part.find("@") != -1:
                    # this is just an email address
                    logins.append( part )
                elif part:
                    # this is a group
                    group = LoginGroup.get_by_code(part)
                    if group:
                        logins.extend( group.get_logins() )

            del sudo
        else:
            notification_id = my.notification.get_id()
            logins = GroupNotification.get_logins_by_id(notification_id)

        for login in logins:
            recipients.add(login) 

        return recipients


    def get_to(my):
        return my.get_mail_users("mail_to")

    def get_cc(my):
        return my.get_mail_users("mail_cc")

    def get_bcc(my):
        return my.get_mail_users("mail_bcc")


    def get_subject(my):
        subject = my.notification.get_value("subject",no_exception=True)
        if subject:
            # parse it through the expression
            sudo = Sudo()
            parser = ExpressionParser()
            subject  = parser.eval(subject, my.sobject, mode='string')
            del sudo
        else:
            subject = '%s - %s' %(my.sobject.get_update_description(), my.command.get_description())
        return subject


    def get_message(my):
        search_type_obj = my.sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        subject = my.get_subject()
        notification_message = my.notification.get_value("message")
        if notification_message:
            # parse it through the expression
            sudo = Sudo()
            parser = ExpressionParser()
            snapshot = my.input.get('snapshot')
            env_sobjects = {}

            # turn prev_data and update_data from input into sobjects
            prev_data = SearchType.create("sthpw/virtual")
            id_col = prev_data.get_id_col()

            if id_col:
                del prev_data.data[id_col]

            prev_dict = my.input.get("prev_data")
            if prev_dict:
                for name, value in prev_dict.items():
                    if value != None:
                        prev_data.set_value(name, value)


            update_data = SearchType.create("sthpw/virtual")
            id_col = update_data.get_id_col()

            if id_col:
                del update_data.data[id_col]

            update_dict = my.input.get("update_data")
            if update_dict:
                for name, value in update_dict.items():
                    if value != None:
                        update_data.set_value(name, value)



            if snapshot:

                env_sobjects = {
                'snapshot': snapshot
            }


            env_sobjects['prev_data'] = prev_data
            env_sobjects['update_data'] = update_data

            notification_message  = parser.eval(notification_message, my.sobject, env_sobjects=env_sobjects, mode='string')
            del sudo
            return notification_message

        message = "%s %s" % (title, my.sobject.get_name())
        message = '%s\n\nReport from transaction:\n%s\n' % (message, subject)
        return message






class TaskAssignEmailHandler(EmailHandler):
    '''Email sent when a task is assigned'''

    def get_subject(my):
        
        task = my.sobject

        sobject = task.get_parent()
        name = sobject.get_name()

        assigned = task.get_value("assigned")
        task_process = task.get_value("process")
        task_description = task.get_value("description")

        #title = my.notification.get_description()
        title = "Assignment"

        return "%s: %s to %s (%s) %s"  % (title, name, assigned, task_process, task_description)


    def get_to(my):
        # add the assigned user to the list of users sent.
        recipients = super(TaskAssignEmailHandler, my).get_to()

        task = my.sobject
        assigned = task.get_value("assigned")

        login = Login.get_by_login(assigned)
        if not login:
            Environment.add_warning("Non existent user", "User %s does not exist" % assigned)
            return recipients

        recipients.add(login)

        return recipients


    def get_message(my):

        task = my.sobject
       
        assigned = task.get_value("assigned")
        task_process = task.get_value("process")
        task_description = task.get_value("description")
        status = task.get_value("status")

        search_type = task.get_value("search_type")
        search_id = task.get_value("search_id")

        sobject = Search.get_by_search_key("%s|%s" %(search_type, search_id) )

        search_type_obj = sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        code = sobject.get_code()
        name = sobject.get_name()

        msg = []
        msg.append("The following task has been assigned to '%s':" % assigned)

        msg.append("")
        msg.append("Description: %s" % task_description)
        msg.append("Process: %s" % task_process)
        msg.append("Status: %s" % status)

        msg.append("")
        if name == code:
            msg.append("To %s: %s" % (title, name))
        else:
            msg.append("To %s: %s - (%s)" % (title, name, code))

        if sobject.has_value("description"):
            description = sobject.get_value("description")
            msg.append("\"%s\"" % description)

        return "\n".join(msg)



class NoteEmailHandler(EmailHandler):

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    

    def get_to(my):
        #recipients = super(NoteEmailHandler, my).get_to()
        recipients = set()
        note = my.sobject

        search = Search(Task)
        search.add_filter('search_type', note.get_value('search_type'))
        search.add_filter('search_id', note.get_value('search_id'))
        # it will get the context if process not found
        search.add_filter('process', note.get_process())
        search.add_filter('project_code',note.get_value('project_code'))
        tasks = search.get_sobjects()
        for task in tasks:
            assigned = my._get_login(task.get_assigned())
            if assigned:
                recipients.add(assigned)
            supe = my._get_login(task.get_supervisor())
            if supe:
                recipients.add(supe)
        return recipients


class GeneralNoteEmailHandler(EmailHandler):

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    def get_to(my):
        #recipients = super(NoteEmailHandler, my).get_to()
        recipients = set()
        note = my.sobject

        search = Search(Task)
        grand_parent = None
        parent_search_type = note.get_value('search_type')
        if 'prod/submission' in parent_search_type:
            grand_parent = my.parent.get_parent()
        
        search_type = note.get_value('search_type')
        search_id = note.get_value('search_id')
        if grand_parent:
            search_type = grand_parent.get_search_type()
            search_id = grand_parent.get_id()

        search.add_filter('search_type', search_type)
        search.add_filter('search_id', search_id )
        # it will get the context if process not found
        #search.add_filter('process', note.get_process())
        search.add_filter('project_code',note.get_value('project_code'))
        tasks = search.get_sobjects()
        for task in tasks:
            assigned = my._get_login(task.get_assigned())
            if assigned:
                recipients.add(assigned)
            supe = my._get_login(task.get_supervisor())
            if supe:
                recipients.add(supe)
        return recipients

    def get_message(my):
        
        search_type_obj = my.sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        
        notification_message = my.notification.get_value("message")

        message = "%s %s" % (title, my.sobject.get_name())
        if notification_message:
            message = "%s (%s)" %(message, notification_message)

        update_desc = my.sobject.get_update_description()
        parent_search_type = my.sobject.get_value('search_type')
        grand_parent = None
        if 'prod/submission' in parent_search_type:
            parent = Search.get_by_id(parent_search_type, my.sobject.get_value('search_id') )
            snapshot = Snapshot.get_latest_by_sobject(parent, 'publish')
            if snapshot:
                file_name = snapshot.get_file_name_by_type('main')
                update_desc = '%s \n %s \n' %(update_desc, file_name)
            grand_parent = parent.get_parent()
            if grand_parent:
                update_desc = '%s %s'%(update_desc, grand_parent.get_code())
        command_desc = my.command.get_description()

        message = '%s\n\nReport from transaction:\n%s\n\n%s' \
            % (message, update_desc, command_desc)
        return message

class GeneralPublishEmailHandler(EmailHandler):
    ''' On publish of a shot/asset, it will find all the assignees of this 
        shot/asset and send the notification to them'''

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    def get_to(my):
        recipients = super(GeneralPublishEmailHandler, my).get_to()
        sobj = my.sobject

        search = Search(Task)
        
        search_type = sobj.get_search_type()
        
        search_id = sobj.get_id()
       
        search.add_filter('search_type', search_type)
        search.add_filter('search_id', search_id )
        # it will get the context if process not found
        #search.add_filter('process', note.get_process())
        from pyasm.biz import Project
        search.add_filter('project_code', Project.get_project_code())
        tasks = search.get_sobjects()
        for task in tasks:
            assigned = my._get_login(task.get_assigned())
            if assigned:
                recipients.add(assigned)
            supe = my._get_login(task.get_supervisor())
            if supe:
                recipients.add(supe)
        return recipients

    def get_message(my):
        
        search_type_obj = my.sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        
        notification_message = my.notification.get_value("message")

        message = "%s %s" % (title, my.sobject.get_name())
        if notification_message:
            message = "%s (%s)" %(message, notification_message)

        update_desc = my.sobject.get_update_description()
        
        command_desc = my.command.get_description()

        message = '%s\n\nReport from transaction:\n%s\n\n%s' \
            % (message, update_desc, command_desc)
        return message

class TaskStatusEmailHandler(EmailHandler):

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    def get_to(my):
        recipients = super(TaskStatusEmailHandler, my).get_to()
        sobj = my.sobject
       
        # it could be the parent of task:
        if not isinstance(sobj, Task):
            tasks = Task.get_by_sobject(sobj)
        else:
            tasks = [sobj]

        for task in tasks:
            assigned = my._get_login(task.get_assigned())
            if assigned:
                recipients.add(assigned)
            supe = my._get_login(task.get_supervisor())
            if supe:
                recipients.add(supe)
        return recipients

class SubmissionEmailHandler(EmailHandler):
    '''Email sent when a submission is entered'''

    def get_message(my):
        search_type_obj = my.sobject.get_search_type_obj()
        title = search_type_obj.get_title()
        subject = my.get_subject()
        notification_message = my.notification.get_value("message")

        message = "%s %s" % (title, my.sobject.get_name())
        if notification_message:
            message = "%s (%s)" %(message, notification_message)

        submit_desc = ''

        from pyasm.prod.biz import Submission
        if isinstance(my.sobject, Submission):
            update_info = ['']
            # add more info about the file and bin
            snapshot = Snapshot.get_latest_by_sobject(my.sobject)
            xpath = "snapshot/file[@type='main']"
            if not snapshot:
                return "no snapshot found"
            xml = snapshot.get_xml_value('snapshot')
            file = None
            if xml.get_node(xpath) is not None:
                file = my._get_file_obj(snapshot)
            else:
                snapshots = snapshot.get_all_ref_snapshots()
                snapshot_file_objects = []
                if snapshots:
                    snapshot = snapshots[0]
                    file = my._get_file_obj(snapshot, type=None)
            if file:
                file_name = file.get_file_name()
                web_path = file.get_web_path()
                from pyasm.web import WebContainer 
                host = WebContainer.get_web().get_base_url()
                update_info.append('Browse: %s %s%s' %( file_name, host.to_string(), web_path))

            bins = my.sobject.get_bins()
            bin_labels = [ bin.get_label() for bin in bins]
            update_info.append('Bin: %s' %', '.join(bin_labels))

            update_info.append('Artist: %s' %my.sobject.get_value('artist'))
            update_info.append('Description: %s' %my.sobject.get_value('description'))
             
            # get notes
            search = Note.get_search_by_sobjects([my.sobject])
            if search:
                search.add_order_by("context")
                search.add_order_by("timestamp desc")
            notes = search.get_sobjects()

            last_context = None
            note_list = []
            for i, note in enumerate(notes):
                context = note.get_value('context')
                # explicit compare to None
                if last_context == None or context != last_context:
                    note_list.append( "[ %s ] " % context )
                last_context = context
                
                #child_notes = my.notes_dict.get(note.get_id())
                # draw note item
                date = Date(db=note.get_value('timestamp'))
                note_list.append('(%s) %s'%(date.get_display_time(), note.get_value("note")))
            update_info.append('Notes: \n %s' % '\n'.join(note_list))

            submit_desc =  '\n'.join(update_info)

            
        update_desc = my.sobject.get_update_description()
        command_desc = my.command.get_description()

        message = '%s\n\nReport from transaction:\n%s\n\n%s\n%s' \
            % (message, update_desc, command_desc, submit_desc)
        return message

    def _get_file_obj(my, snapshot, type='main'):
        if type:
            xpath = "snapshot/file[@type='%s']" %type
        else:
            xpath = "snapshot/file[@type]"
        xml = snapshot.get_xml_value('snapshot')
        node = xml.get_node(xpath)
        file = None
        if node is not None:
            file_code = Xml.get_attribute(node, "file_code")
            file = File.get_by_code(file_code)
        return file

class SubmissionStatusEmailHandler(SubmissionEmailHandler):

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    def get_to(my):
        recipients = super(SubmissionStatusEmailHandler, my).get_to()
        submission = my.sobject
        artist = submission.get_value('artist')
        assigned = my._get_login(artist)
        if assigned:
            recipients.add(assigned)
        
        return recipients

class SubmissionNoteEmailHandler(SubmissionEmailHandler):

    def check_rule(my):
        '''determine whether an email should be sent'''
        return True

    def get_message(my):
        search_type_obj = my.parent.get_search_type_obj()
        title = search_type_obj.get_title()
        subject = my.get_subject()
        notification_message = my.notification.get_value("message")

        message = "%s %s Note Entry" % (title, my.parent.get_name())
        if notification_message:
            message = "%s (%s)" %(message, notification_message)

        submit_desc = ''

        from pyasm.prod.biz import Submission
        if isinstance(my.parent, Submission):
            update_info = ['']
            # add more info about the file and bin
            snapshot = Snapshot.get_latest_by_sobject(my.parent, "publish")
            xpath = "snapshot/file[@type='main']"
            xml = snapshot.get_xml_value('snapshot')
            file = None
            if xml.get_node(xpath) is not None:
                file = my._get_file_obj(snapshot)
            else:
                snapshots = snapshot.get_all_ref_snapshots()
                snapshot_file_objects = []
                if snapshots:
                    snapshot = snapshots[0]
                    file = my._get_file_obj(snapshot, type=None)
            if file:
                file_name = file.get_file_name()
                web_path = file.get_web_path()
                from pyasm.web import WebContainer 
                host = WebContainer.get_web().get_base_url()
                update_info.append('Browse: %s %s%s' %( file_name, host.to_string(), web_path))

            bins = my.parent.get_bins()
            bin_labels = [ bin.get_label() for bin in bins]
            update_info.append('Bin: %s' %', '.join(bin_labels))

            update_info.append('Artist: %s' %my.parent.get_value('artist'))
            update_info.append('Description: %s' %my.parent.get_value('description'))
             
            # get notes
            search = Note.get_search_by_sobjects([my.parent])
            if search:
                search.add_order_by("context")
                search.add_order_by("timestamp desc")
            notes = search.get_sobjects()

            last_context = None
            note_list = []
            for i, note in enumerate(notes):
                context = note.get_value('context')
                # explicit compare to None
                if last_context == None or context != last_context:
                    note_list.append( "[ %s ] " % context )
                last_context = context
                
                #child_notes = my.notes_dict.get(note.get_id())
                # draw note item
                date = Date(db=note.get_value('timestamp'))
                note_list.append('(%s) %s'%(date.get_display_time(), note.get_value("note")))
            update_info.append('Notes: \n %s' % '\n'.join(note_list))

            submit_desc =  '\n'.join(update_info)

            
        update_desc = my.sobject.get_update_description()
        command_desc = my.command.get_description()

        message = '%s\n\nReport from transaction:\n%s\n\n%s\n%s' \
            % (message, update_desc, command_desc, submit_desc)
        return message

        

    def _get_login(my, assigned):
        return Login.get_by_login(assigned)
        
    def get_to(my):
        recipients = super(SubmissionNoteEmailHandler, my).get_to()
        submission = my.parent
        artist = submission.get_value('artist')
        assigned = my._get_login(artist)
        if assigned:
            recipients.add(assigned)
        
        return recipients

class TestEmailHandler(EmailHandler):
    '''Email sent when a task is assigned'''

    def check_rule(my):
        task = my.sobject
       
        assigned = task.get_value("assigned")
        task_process = task.get_value("process")
        task_description = task.get_value("description")

        # get the pipeline
        my.parent = task.get_parent()
        pipeline_code = my.parent.get_value("pipeline_code")
        my.pipeline = Pipeline.get_by_code(pipeline_code)
        if not my.pipeline:
            # No pipeline, so don't email
            print "Warning: No Pipeline"
            return False


        task_status = task.get_value("status")
        if task_status == "Review":
            return True
        else:
            return False



