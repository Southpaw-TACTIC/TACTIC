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
# Description: Actions executed when an element of an EditWdg is called to
# update an sobject.  

__all__ = ["DatabaseAction", "DefaultValueDatabaseAction", "MultiDatabaseAction", 'NonEmptyAction', 'RegexAction', "NullAction", "PasswordAction", "IsCurrentAction", "NamespaceAction", 'UniqueValueAction', 'LoginAction', 'GroupNameAction', "UploadAction", "AddToBinAction", "PerforceUploadAction", "FileUploadException", "MultiUploadAction", "MultiZipUploadAction",  "CommandNameAction", "RepoPathAction", "RepoPathPerAssetAction", 'ProjectCreateAction', 'DateAction', 'TimeAction', 'TaskDateAction','XmlAction' ]


import os, shutil, string, types, hashlib, re, zipfile


from pyasm.common import *
from pyasm.biz import *
from pyasm.search import Search, DatabaseImpl, Sql, SearchKey, SearchType
from command import *
from trigger import *
from file_upload import *
from pyasm.prod.biz import *


def get_web_container():
    '''we have a circular reference here, so put in a function to handle it'''
    from pyasm.web import WebContainer
    return WebContainer.get_web()


class DatabaseAction(Command):
    """takes the value and adds it to the current sobject.  It does
    not commit to the database"""

    def __init__(my, **kwargs):
        my.sobject = None
        my.name = None
        my.input_prefix = None
        my.value = None
        my.errors = []
        my.description = ""
        my.response = ''
        my.commit_flag = False
        my.options = {}
        my.sobjects = []
        my.info = {}
        my.kwargs = kwargs
        my.data = None


    def set_data(my, data):
        my.data = data

    def get_data(my):
        return my.data


    def check(my):
        my.web = get_web_container() 
        #value = my.web.get_form_value(my.get_input_name())
        
        value = my.get_value(my.name) 
        # check for save option == false, equivalent to the old NulllAction
        no_action = my.get_option('save') == 'false'
        if no_action:
            return False
        # default for empty is True.
        no_empty = my.get_option('empty') == 'false'
        if no_empty:
            if value == '':
                name = my._get_name()
                raise UserException("The input for [%s] cannot be empty" %name.capitalize())


        # a match or search can be used. Match if for pattern, Search is for invalid chars.
        regexm = my.get_option('regexm')
        regexs = my.get_option('regexs')
        if regexm and value:
            m = re.match(r'%s' % regexm, value) 
            if not m:
                name = my._get_name()
                raise UserException("The input for [%s] is invalid for expression [%s]" \
                        % (name.capitalize(), regexm)) 

        if regexs and value:
            m = re.search(r'%s' % regexs, value) 
            if m:
                name = my._get_name()
                raise UserException("The input for [%s] contains invalid characters [%s]" \
                        % (name.capitalize(), regexs)) 
        return True


    def _get_name(my):
        name = my.get_input_name()
        if '|' in name:
            name = name.split('|', 1)[1]

        return name

    def set_name(my, name):
        my.name = name


    def has_option(my, key):
        return my.options.has_key(key)

    def set_option(my, key, value):
        my.options[key] = value
        
    def get_option(my, key):
        '''gets the value of the specified option'''
        if my.options.has_key(key):
            return my.options[key]
        else:
            return ""





    def set_commit_flag(my, flag):
        '''determines whether a commit is made by the action or it
        is done externally to the action'''
        if flag == True or flag == "True":
            my.commit_flag = True
        else:
            my.commit_flag = False

    def commit(my):
        '''does nothing'''
        pass

    def rollback(my):
        '''does nothing'''
        pass

    def set_input_prefix(my, input_prefix):
        my.input_prefix = input_prefix

    def get_name(my):
        return my.name

    def get_input_name(my):
        if my.input_prefix:
            return "%s|%s" % (my.input_prefix, my.name)
        else:
            return my.name

    def set_sobject(my, sobject):
        my.sobject = sobject

    def get_values(my, name=None):
        # get the value from the form
        if my.value:
            return [my.value]

        if not name:
            name = my.name
            
        if my.input_prefix:
            input_name = "%s|%s" % (my.input_prefix, name)
        else:
            input_name = name

        if my.data != None:
            my.values = [my.data]
        else:
            web = get_web_container()
            my.values = web.get_form_values(input_name)
        return my.values

    def get_value(my, name=None):
        # if set externally, just use it
        if my.value:
            return my.value
        values = my.get_values(name)
        if type(values) == types.InstanceType:
            return values
        elif values:
            return values[0]
        else:
            return ""

    def set_value(my, value):
        my.value = value

    def execute(my):

        column = my.get_option("column")
        if not column:
            column = my.name

        # get the value
        # NOTE: not sure why this was "column".  The value will come
        # through with the name of the element.  The "column" options
        # tells the action which column to set the value to
        #value = my.get_value(column)
        value = my.get_value(my.name)


        # check if there is an expression on the update
        expr = my.get_option("expression")

        # check for parent action to save search_type and search_id or parent_code etc separately
        # this is usually already taken care of in EditCmd
        parent_key_action = my.get_option('parent_key') == 'true'

        if expr:
            vars = {
                'VALUE': value
            }
            Search.eval(expr, my.sobject, vars=vars)
       
        
        else:     

            search_type = my.sobject.get_search_type()
            col_type = SearchType.get_tactic_type(search_type, column)


            value = my.convert_value(col_type, value)
            
            if parent_key_action:
                my.sobject.add_relationship(value)
            else:
                my.sobject.set_value(column, value )

            if my.commit_flag == True:
                my.sobject.commit()



    def convert_value(my, col_type, value):
        if col_type == 'timecode':
            timecode = TimeCode(timecode=value)
            value = timecode.get_frames()
        elif col_type in ["time", "timestamp"]:
            from pyasm.common import SPTDate
            if not SPTDate.has_timezone(value):
                value = SPTDate.add_local_timezone(value)

        return value


class DefaultValueDatabaseAction(DatabaseAction):
    '''This element is executed on every element execution'''

    def execute(my):
        default_values = {
            #'login_id': Environment.get_user_name()
            'login_id': Environment.get_login().get_id(),
            'login': Environment.get_login().get_value("login")
        }

        for column, value in default_values.items():
            cur_value = my.sobject.get_value(column, value)
            if not cur_value:
                my.sobject.set_value(column, value)
            



class MultiDatabaseAction(DatabaseAction):
    '''Stores the value in the database as a || separated list.  There
    is also a || at the beginning and end so that the full string can
    be searched up.'''
    def execute(my):
        values = my.get_values()
        new_values = [i for i in values if i]
        new_values.sort()

        value_string = "||".join(new_values)
        # only do it if there is more than 1 value
        if value_string and '||' in value_string:
            # prepend and append
            value_string = "||%s||" % value_string

        my.sobject.set_value(my.name, value_string)

        if my.commit_flag == True:
            my.sobject.commit()


# DEPRECATED: this should be done at the Javascript Level or at least an
# option to DatabaseAction
class NonEmptyAction(DatabaseAction):
    ''' Make sure the value is not empty '''
    def check(my):
        my.web = get_web_container() 
        #value = my.web.get_form_value(my.get_input_name())
        value = my.get_value()
        
        if not value:
            name = my.get_input_name()
            if '|' in name:
                name = name.split('|')[1]
            raise UserException("[%s] cannot be empty." % name.capitalize()) 

        return True

class RegexAction(DatabaseAction):
    ''' Make sure the value matches the given expression defined in the option <regex> '''
    
    def check(my):
        my.web = get_web_container() 
        value = my.web.get_form_value(my.get_input_name())
       
        regex = my.get_option('regex')
        if value and regex:
            name = my.get_input_name()
            if '|' in name:
                name = name.split('|', 1)[1]
            m = re.match(r'%s' % regex, value) 
            if not m:
                raise UserException("The input for [%s] is invalid for expression [%s]" \
                        % (name.capitalize(), regex)) 

        return True

class NullAction(DatabaseAction):

    def execute(my):
        # do nothing
        pass



class PasswordAction(DatabaseAction):
    '''encrypts the entered password with md5 encryption'''

    def get_title(my):
        return "Password Change"

    def set_password(my, password):
        my.password = password
        my.re_enter = ""

    def set_search_key(my, search_key):
        my.sobject = Search.get_by_search_key(search_key)


    def check(my):
        my.password = my.get_value("password")

        if my.sobject == None:
            return False

        my.re_enter = my.get_value("password re-enter")
        if my.re_enter != "" and my.re_enter != my.password:
            raise UserException( "Passwords must match.  Go back and re-enter")

        return True

    def execute(my):
        assert my.sobject != None

        if my.password == "":
            if my.sobject.is_insert():
                raise UserException("Empty password.  Go back and re-enter")
            else:
                return
        
        # encrypt the password
        #encrypted = md5.new(my.password).hexdigest()
        encrypted = hashlib.md5(my.password).hexdigest()
        my.sobject.set_value("password", encrypted)

        if my.commit_flag == True:
            my.sobject.commit()

        my.description = "Changed Password"


class IsCurrentAction(DatabaseAction):

    def execute(my):
        snapshot = my.sobject

        value = my.get_value()
        if value not in ["on","true"]:
            snapshot.set_value("is_current", False)
            return


        search_type = snapshot.get_value("search_type")
        search_id = snapshot.get_value("search_id")
        context = snapshot.get_value("context")

        # find the last current
        last_current = Snapshot.get_current(search_type, search_id, context)
        if last_current:
            last_current.set_value("is_current", False)
            last_current.commit()

        snapshot.set_value("is_current", True)






# FIXME: this does nothing????
class NamespaceAction(DatabaseAction):

    def execute(my):
        web = get_web_container()
        namespace = web.get_context_name()


class UniqueValueAction(DatabaseAction):
    ''' Ensure the value entered does not violate the Unique Constraint for a column '''
    def check(my):
        my.web = get_web_container() 
        name = my.web.get_form_value(my.get_input_name())
        search_type = my.sobject.get_search_type()

        column = my.get_name()

        search = Search(search_type)
        search.add_filter(column, name)
        sobject = search.get_sobject()
        if sobject:
            raise UserException("%s [%s] has been taken!" \
                %(column.capitalize(), name)) 

        super(UniqueValueAction, my).check()
        return True
            

class LoginAction(DatabaseAction):
    
    def check(my):
        my.web = get_web_container() 
        
        license = Environment.get_security().get_license()
        max_users = license.get_max_users()
        active_users = license.get_current_users()

        # this action is used for both edit and insert
        if my.sobject.is_insert():
            active_users += 1
        
        # allow disabled and float type login user addition
        if active_users > max_users and my.web.get_form_value('license_type') not in ['disabled','float']:
            raise UserException("Max active users [%s] reached for your license"%max_users) 

        return True
            
   

class GroupNameAction(DatabaseAction):
    
    def check(my):
        my.web = get_web_container() 
        my.group = my.web.get_form_value(my.get_input_name())
        if not my.group:
            raise CommandException("Login Group cannot be empty!") 

        return True
            
    def execute(my):
        
        if my.sobject.is_insert():
            #namespace = my.web.get_context_name()
            #if namespace == "admin":
            #    namespace = my.sobject.get_value("namespace")
            namespace = my.get_value("namespace")
            if namespace:
                my.sobject.set_value(my.name, "%s/%s" %(namespace, my.group))
            else:
                my.sobject.set_value(my.name, my.group)
        else:
            my.sobject.set_value(my.name, my.group)





class UploadAction(DatabaseAction):
    """action which saves a file to the tmp directory and processes
    it according to its file type"""
    def __init__(my):
        my.checkin = None
        super(UploadAction, my).__init__()
        
    def get_title(my):
        return "Upload"

    def set_value(my, value):
        my.value = value

    def execute(my):
        '''Do nothing'''
        pass


    def postprocess(my):
        web = get_web_container()

        keys = web.get_form_keys()

        from pyasm.search import Transaction
        transaction = Transaction.get()
        assert transaction

        # first get some data based in
        column = my.get_value("%s|column" % my.name)
        if column == "":
            column = my.name
       
        # NOTE: why did this change?
        #prefix = my.get_input_name()
        prefix = my.get_name()
        
        
        context = my.get_value("%s|context" % prefix)
        description = my.get_value("%s|description" % prefix)
        
        field_storage = my.get_value(prefix)
        handoff_path = my.get_value("%s|path" % prefix )

        from pyasm.widget import CheckboxWdg
        cb = CheckboxWdg("%s|is_revision" % prefix)
        is_rev = cb.is_checked()

        if handoff_path:
            handoff_path = handoff_path.replace("\\", "/")

            # This check causes issues.. Just assume it's in the upload location
            #if not os.path.exists(handoff_path):
            security = Environment.get_security()
            ticket = security.get_ticket_key()

            handoff_path = os.path.basename(handoff_path)
            handoff_path = Common.get_filesystem_name(handoff_path)

            handoff_path = "%s/upload/%s/%s" % (Environment.get_tmp_dir(), ticket, handoff_path)


            print "Uploaded path: ", handoff_path
            if not os.path.exists(handoff_path):
                raise Exception("Uploaded Path [%s] does not exist" % handoff_path)

            my.files = [handoff_path]
            file_types = ['main']

            # create an icon
            icon_creator = IconCreator(handoff_path)
            icon_creator.execute()
            icon_path = icon_creator.get_web_path()
            if icon_path:
                my.files.append(icon_path)
                file_types.append("icon")
            web_path = icon_creator.get_icon_path()
            if web_path:
                my.files.append(web_path)
                file_types.append("web")


        elif field_storage != "":
        #else:
            # process and get the uploaded files
            upload = FileUpload()
            upload.set_field_storage(field_storage)
            upload.execute()

            # get files and file types
            my.files = upload.get_files()
            if not my.files:
                return
            file_types = upload.get_file_types()
        else:
            if my.get_option("file_required") == "true":
                err_msg = _("upload is required")
                raise TacticException("%s %s" % (my.name, err_msg))
            else:
                return


        checkin_class = my.get_option("checkin")
        if checkin_class:
            snapshot_type = my.get_option("snapshot_type")
            my.checkin = Common.create_from_class_path(checkin_class, [my.sobject, my.files, file_types, context, snapshot_type])

        else:
            from pyasm.checkin import FileCheckin
            my.checkin = FileCheckin.get( my.sobject, my.files, file_types,  \
                context=context, column=column, snapshot_type="file" )

        my.sobjects.append(my.sobject)

        my.checkin.set_description(description)
        my.checkin.set_revision(is_rev)
        my.checkin.execute()

        # remove the files in upload area
        for file in my.files:
            if os.path.exists(file):
                os.unlink(file)

        

        

class AddToBinAction(NonEmptyAction):

    def check(my):
        if not my.get_value():
            raise UserException('Please choose a valid bin')
        return True

    def get_title(my):
        return "Add submit to a bin"

    def execute(my):
        Container.put('bin', my.get_value())

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        parent_search_type = web.get_form_value("parent_search_type")
        parent_search_id = web.get_form_value("parent_search_id")

        submit = my.sobject

        # if submitting using a snapshot, then get the snapshot's parent
        parent = Search.get_by_id(parent_search_type, parent_search_id)
        if isinstance(parent, Snapshot):
            my.parent_snapshot = parent
            parent_search_type = my.parent_snapshot.get_value("search_type")
            parent_search_id = my.parent_snapshot.get_value("search_id")

            submit.set_value("version", my.parent_snapshot.get_value("version") )
            submit.set_value("context", my.parent_snapshot.get_value("context") )
            submit.set_value("snapshot_code",  my.parent_snapshot.get_value("code"))
        else:
            my.parent_snapshot = None


        submit.set_value("search_type", parent_search_type)
        submit.set_value("search_id", parent_search_id)

        # have to commit here to get Id of submit
        submit.commit()

        bin_id = my.get_value()

        # have to load this dynamically
        from pyasm.prod.biz import Submission, SubmissionInBin

        # put the submission in a bin
        group = SubmissionInBin.create_new()
        group.set_value('submission_id', submit.get_id())
        group.set_value('bin_id', bin_id)
        group.commit()


    def postprocess(my):
        # if the submitted parent is a snapshot, then connect to that snapshot
        submit = my.sobject

        my.sobjects.append(submit)
        Trigger.call(my, 'email')
        



"""
class SubmitAction(UploadAction):
    '''action which submits a movie file to a daily session(bin)'''
    TO_DAILY = "go_to_daily"
    
    def get_title(my):
        return "Submit a file"
  
    def check(my):
        field_storage = my.get_value(my.name)
        # if no files have been uploaded, don't do anything
        if field_storage == "":
            raise UserException('A file needs to be chosen for submission!')
            return False

        return True
        
    def execute(my):
        # have to load this dynamically
        from pyasm.prod.biz import Submission, SubmissionInBin

         
        context = version = snap_code = ''
        if isinstance(my.sobject, Snapshot):
            context = my.sobject.get_value('context')
            version = my.sobject.get_value('version')
            snap_code = my.sobject.get_code()
            search_type = my.sobject.get_value('search_type')
            search_id = my.sobject.get_value('search_id')

        else:
            search_type = my.sobject.get_search_type()
            search_id = my.sobject.get_id()
            
        # The user is allowed to make multiple submissions for the 
        # same snapshot
        submit = Submission.create_new()

        submit.set_value('search_type', search_type)
        submit.set_value('search_id', search_id)

        submit.set_value('context', context)
        submit.set_value('snapshot_code', snap_code)
        submit.set_value('version', version)
        submit.set_value('login', Environment.get_user_name())

        # assuming the element name = "description"
        # TODO: maybe to create an action for the description, artist field
        description = my.get_value("description")
        submit.set_value('description', description)

        artist = my.get_value("artist")
        if artist:
            submit.set_value('artist', artist)
        submit.commit()

        my.submit = submit
        
        bin_id = Container.get('bin')

        # put the submission in a bin
        group = SubmissionInBin.create_new()
        group.set_value('submission_id', submit.get_id())
        group.set_value('bin_id', bin_id)
        group.commit()

        # TODO: add description to EditCmd
        #from pyasm.prod.biz import Bin
        #my.add_description('Submission to Bin [%s]' % Bin.get_by_id(bin_id).get_code())
        
    def postprocess(my):
        ''' publish the submission into Snapshot '''
        my.check_in(my.submit)

       
        
    def check_in(my, sobject):
        field_storage = my.get_value(my.name)

        # if no files have been uploaded, don't do anything
        if field_storage == "":
            return

        context = 'publish'
        description = "Submission for [%s]" % sobject.get_value('snapshot_code')

        # process and get the uploaded files
        upload = FileUpload()
        upload.set_field_storage(field_storage)
        upload.execute()
        my.files = upload.get_files()
        if not my.files:
            return

        # set a trigger to give a chance to rename files
        Trigger.call(my, "rename_files")

        file_types = upload.get_file_types()

        # let checkin take care of moving files to the lib
        from pyasm.checkin import FileCheckin
        my.checkin = FileCheckin.get( sobject, my.files, file_types,  \
            context=context )
        my.checkin.set_description(description)
        my.checkin.execute()
        
        # remove the files in upload area
        for file in my.files:
            os.unlink(file)

"""


class PerforceUploadAction(UploadAction):

    def postprocess(my):

        web = get_web_container()

        field_storage = web.get_form_value(my.name)

        # if no files have been uploaded, don't do anything
        if field_storage == "":
            return

        context = web.get_form_value("%s|context" % my.name)
        if context == '':
            context = Snapshot.get_default_context()
        description = web.get_form_value("%s|description" % my.name)

        # process and get the uploaded files
        upload = FileUpload()
        upload.set_field_storage(field_storage)
        upload.execute()
        my.files = upload.get_files()

        # set a trigger to give a chance to rename files
        Trigger.call(my, "rename_files")

        snapshot_type = 'file'

        file_types = upload.get_file_types()

        from pyasm.checkin import PerforceCheckin
        checkin = PerforceCheckin( my.sobject, my.files, file_types,  \
            context=context, column=my.name, snapshot_type="file" )
        checkin.set_description(description)
        checkin.execute()




class MultiUploadAction(DatabaseAction):

    def set_value(my, value):
        my.value = value


    def execute(my):
        '''do nothing'''
        pass

    def postprocess(my):
        web = get_web_container()
        my.files = []
        my.file_types = []
        if my.get_option('upload_type') == 'arbitrary':
            my._upload_arbitrary_files()
        else:
            my._upload_specified_files()

        context = my.get_value("%s|context" % my.name)
        subcontext = my.get_value("%s|subcontext" % my.name)
        if subcontext:
            context = '%s/%s' %(context, subcontext)
        description = my.get_value("%s|description" % my.name)
        from pyasm.widget import CheckboxWdg
        cb = CheckboxWdg("%s|is_revision" % my.get_input_name())
        is_rev = cb.is_checked(False)
        
        # let checkin take care of moving files to the lib
        from pyasm.checkin import FileCheckin
        my.checkin = FileCheckin.get( my.sobject, my.files, my.file_types,  \
            context=context, snapshot_type="file" )
        my.checkin.set_description(description)
        my.checkin.set_revision(is_rev)
        my.checkin.execute()


        my.sobjects.append(my.sobject)
        my.info['context'] = context
        my.add_description('File Publish for [%s]' %my.sobject.get_code())
        # remove the files in upload area
        for file in my.files:
            if os.path.exists(file):
                os.unlink(file)

        Trigger.call(my, "email")

    def _upload_arbitrary_files(my):
        ''' upload an arbitrary list of files'''
        field_storage_list = []
        upload_names = []
        web = get_web_container()
        keys = web.get_form_keys()
        name = my.get_input_name().replace('|', '\|')
        pat = re.compile(r'%s\d*$' % name)
        for key in keys:
            if pat.match(key):
                upload_names.append(key)
        for upload_name in upload_names:
            field_storage = web.get_form_value(upload_name)
            if field_storage != '':
                field_storage_list.append(field_storage)

        # if no files have been uploaded, don't do anything
        if not field_storage_list:
            return
        
        for field_storage in field_storage_list:
            create_icon = False
            upload = FileUpload()
            # icon field is optional
            if field_storage == None:
                continue
            upload.set_field_storage(field_storage)

            file_path = upload.get_file_path()
            root, ext = os.path.splitext(file_path)
            if ext in ['.tif','.TIF','.jpg','.JPG', '.png', '.PNG']:
                create_icon = True
            if not ext:
                raise TacticException('file path with extension expected [%s]'\
                        %file_path)

            upload.set_default_type(ext)
            upload.set_create_icon_flag(create_icon)

            upload.execute()
            files = upload.get_files()

            if not files:
                continue

            
            my.files.extend(files)
            file_types = upload.get_file_types()
            my.file_types.extend(file_types)


    def _upload_specified_files(my):
        ''' upload predefined file types specified in the conf.xml file'''
        upload_names = my._get_option('names')
        
        # check for uniqueness in upload_names
        if len(set(upload_names)) != len(upload_names):
            raise TacticException('[names] in the config file must be unique')
        
        upload_types = my._get_option('types')

        assert len(upload_names) == len(upload_types)

        field_storage_dict = {}
        valid_upload_names = []
        valid_upload_types = []

        for idx, name in enumerate(upload_names):
            field_storage = my.get_value(name)
            # if no files have been uploaded, don't do anything
            
            if field_storage == None or field_storage.filename == '':
                continue
            field_storage_dict[name] = field_storage
            valid_upload_names.append(upload_names[idx])
            valid_upload_types.append(upload_types[idx])

        # process and get the uploaded files
        icon_created = False
        has_icon = "icon_main" in valid_upload_names
        
        # if no files or only icon_main is supplied, raise Exception
        if not valid_upload_types or valid_upload_types==['icon_main']:
            raise UserException('You need to browse for a valid main file.')
        
        for idx, name  in enumerate(valid_upload_names):
            upload_type = valid_upload_types[idx]
            create_icon = upload_type == 'icon_main'
            field_storage = field_storage_dict.get(name)
             
            # icon field is optional
            if field_storage == None and create_icon:
                continue

            upload = FileUpload()
            upload.set_default_type(upload_type)
           
            # this ensures icon_main takes precedence for icon creation
            if icon_created or (has_icon and not create_icon):
                upload.set_create_icon_flag(False)
                
            
            upload.set_field_storage(field_storage)
            upload.execute()
            files = upload.get_files()
            if not files:
                continue

            if create_icon and len(files) == 1:
                raise UserException('The uploaded icon file must be an image file. e.g. tif, png, jpg.')
            my.files.extend(files)
            file_types = upload.get_file_types()
            if len(file_types) > 1:
                icon_created = True
            my.file_types.extend(file_types)

        

    def _get_option(my, attr):
        ''' get option delimited by | '''
        upload_names = my.get_option(attr)
        if not upload_names:
            upload_names = [my.name]
        else:
            upload_names = upload_names.split('|')

        return upload_names

class MultiZipUploadAction(MultiUploadAction):

    def check(my):
        my.naming = None
        my.sobject_dict = {}
        naming = my.get_option('naming')
        if naming:
            my.naming = eval('%s()' %naming)
        else:
            raise TacticException('A naming has to be specified in the action option')
        return True

    def postprocess(my):
        web = get_web_container()
        my.files = []
        my.file_types = []
        
        my._upload_zipped_files()

        context = my.get_value("%s|context" % my.name)
        description = my.get_value("%s|description" % my.name)

        # let checkin take care of moving files to the lib
        from pyasm.checkin import FileCheckin
        for sobject in my.sobject_dict.keys():
            files, file_types = my.sobject_dict.get(sobject)
            my.checkin = FileCheckin.get( sobject, files, file_types,  \
                context=context, snapshot_type="file" )
            my.checkin.set_description(description)
            my.checkin.execute()

           
       
        # remove the files in upload area
        for key in my.sobject_dict.keys():
            files, file_types = my.sobject_dict.get(key)
            for file in files:
                os.unlink(file)

    def _upload_zipped_files(my):
        ''' upload an arbitrary list of files'''
        field_storage_list = []
        upload_names = []
        web = get_web_container()
        keys = web.get_form_keys()
        name = my.get_input_name().replace('|', '\|')
        pat = re.compile(r'%s\d*$' % name)
        for key in keys:
            if pat.match(key):
                upload_names.append(key)
        for upload_name in upload_names:
            field_storage = web.get_form_value(upload_name)
            if field_storage != '':
                field_storage_list.append(field_storage)

        # if no files have been uploaded, don't do anything
        if not field_storage_list:
            return
        
        for field_storage in field_storage_list:
            upload = FileUpload()
            
            if field_storage == None:
                continue
            upload.set_field_storage(field_storage)

            
            file_path = upload.get_file_path()
            root, ext = os.path.splitext(file_path) 
            upload.set_default_type(ext)
            
            if my._create_icon(file_path):
                upload.set_create_icon_flag(True)

            upload.execute()
            if zipfile.is_zipfile(file_path):
                unzipped_files = Common.unzip_file(file_path)
                # remove the zip file
                os.unlink(file_path)
                for unzipped_file in unzipped_files:
                    my._process_file(None, unzipped_file)
            else:
                my._process_file(upload, file_path)
            

        


    def _create_icon(my, file_path):
        '''return True if an icon can be created out of it'''
        name, ext = os.path.splitext(file_path)

        create_icon = False
        if ext in ['.tif','.TIF','.jpg','.JPG', '.png', '.PNG']:
            create_icon = True
        if not ext:
            raise TacticException('file path with extension expected [%s]'\
                %file_path)

        return create_icon

   

    def _process_file(my, upload, file_path):
        ''' sort the files, file_types to the corresponding sobject'''
        files = []
        file_types = []
        if not file_path:
            raise TacticException('Empty file path encountered')

        if upload:
            files = upload.get_files()
            file_types = upload.get_file_types()
            if not files or not file_types:
                return

        else:
            name, ext = os.path.splitext(file_path)
            files.append(file_path)
            file_types.append(ext)

            if my._create_icon(file_path):
                icon_creator = IconCreator(file_path)
                icon_creator.create_icons()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()

                if web_path:
                    file_types.append("web")
                    files.append(web_path)

                if icon_path:
                    file_types.append("icon")
                    files.append(icon_path)
       
        head, file_name = os.path.split(file_path)
        

        sobject = my.naming.get_sobject_by_filename(file_name)
        if sobject:
            if my.sobject_dict.get(sobject):
                orig_files, orig_file_types = my.sobject_dict.get(sobject)
                files.extend(orig_files)
                file_types.extend(orig_file_types)
            my.sobject_dict[sobject] = (files, file_types)
            my.add_description("Published [%s] for [%s] " %(file_name, sobject.get_code()))
        else:
            raise UserException('Unrecognized uploaded file name [%s]' %file_name)
           

class CommandNameAction(DatabaseAction):
    
    def check(my):
        my.web = get_web_container() 
        class_name = my.web.get_form_value(my.get_input_name())
        
        if not class_name:
            raise UserException("class name cannot be empty!")
        if "." in class_name:
            raise UserException("class name should be a unique command class name without the module portion!")
        return True

class RepoPathAction(DatabaseAction):
    
     def check(my):
        my.web = get_web_container() 
        repo_path = my.web.get_form_value(my.get_input_name())
        
        if not repo_path:
            raise UserException("Repo path cannot be empty! <br/> \
                A valid example: 'characters/nonplayer'")
        if repo_path.startswith('/') or repo_path.endswith('/'):
            raise UserException("Repo path should not start or end with '/'.<br/> \
                A valid example: 'characters/nonplayer'")
        return True
    
class RepoPathPerAssetAction(DatabaseAction):
    
     def check(my):
        my.web = get_web_container() 
        repo_path = my.web.get_form_value(my.get_input_name())
        
        if repo_path.startswith('/') or repo_path.endswith('/'):
            raise UserException("Perforce path should not start or end with '/'.<br/> \
                A valid example: 'characters/nonplayer/dragon'")
  
        return True


class ProjectCreateAction(DatabaseAction):
    def execute(my):

        if not my.sobject.is_insert():
            # do nothing
            return

        project = my.sobject
        project_code = project.get_code()
        project_type = project.get_base_type()

        database = DatabaseImpl.get()

        # check if database exists
        print "Creating database '%s' ..." % project_code

        if database.database_exists(project_code):
            print "... already exists"
        else:
            # create the datbase
            database.create_database(project_code)

        # import the appropriate schema
        database.import_schema(project_code, project_type)

        # import the appropriate data
        database.import_default_data(project_code, project_type)

        # copy files from the default template
        site_dir = Environment.get_site_dir()
        install_dir = Environment.get_install_dir()
        template_dir = "%s/src/tactic_sites/template" % install_dir
        template_dir = template_dir.replace("\\","/")
        project_dir = "%s/sites/%s" % (site_dir, project_code)
        project_dir = project_dir.replace("\\","/")


        # set the update of the database to current
        project.set_value("last_db_update", Sql.get_timestamp_now(), quoted=False)
        project.commit()



        # copy all of the files from the template to the template directory
        print "Creating project directories [%s]..." % project_dir
        if not os.path.exists(template_dir):
            print "... skipping: template dir [%s] does not exist" % template_dir
            return 

        if not os.path.exists(project_dir):
            for root, dirs, files in os.walk(template_dir):
                root = root.replace("\\","/")

                # ignore ".svn"
                if root.find("/.svn") != -1:
                    continue

                for file in files:
                    # ignore compiled python files
                    if file.endswith(".pyc"):
                        continue

                    old = "%s/%s" % (root, file)
                    new = old.replace(template_dir, project_dir)

                    dirname = os.path.dirname(new)
                    System().makedirs(dirname)

                    shutil.copyfile(old,new)
        else:
            print "... skipping.  Already exists."

        print "Done."




class DateAction(DatabaseAction):
    '''special action class to handle dates'''

    def execute(my):
        value = my.get_value()
        if value == "now":
            from datetime import datetime
            date = datetime.now()
            value = str(date)
            my.set_value(value)



        super(DateAction, my).execute() 



class TimeAction(DatabaseAction):
    '''special action class to handle dates'''

    def execute(my):
        web = get_web_container()
        column = my.get_option("column")

        name = my.get_name()
        hour_name = "%s|hour" % name
        min_name = "%s|minute" % name

        hour_value = int(my.get_value(hour_name))
        min_value = int(my.get_value(min_name))


        from dateutil import parser
        from datetime import datetime, timedelta

        time_change = timedelta(hours=hour_value, minutes=min_value)

        sobject = my.sobject
        date_value = sobject.get_value(column)
        if not date_value:
            date = datetime.now()
        else:
            date = parser.parse(date_value)

        date = datetime(date.year, date.month, date.day, hour_value, min_value)
        my.set_value(date)

        super(TimeAction, my).execute() 





class TaskDateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def execute(my):
        bid_end_date = my.get_value()
        my.sobject.update_dependent_tasks()

        super(TaskDateAction, my).execute() 

        
__all__.append("InitialTaskCreateAction")
class InitialTaskCreateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def execute(my):
        # do nothing
        pass

    def postprocess(my):
        value = my.get_value()
        if not value:
            return

        from pyasm.biz import Task
        Task.add_initial_tasks(my.sobject)


class XmlAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def check(my):
        value = my.get_value()
        try:
            from pyasm.common import Xml, XmlException
            Xml(string=value)
        except XmlException, e:
            error =  e.__str__()
            raise TacticException("Invalid XML: %s" %error)
        
        return True
