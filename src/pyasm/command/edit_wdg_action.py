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


import os, shutil, string, types, hashlib, re, zipfile, six


from pyasm.common import *
from pyasm.biz import *
from pyasm.search import Search, DatabaseImpl, Sql, SearchKey, SearchType
from pyasm.security import Login
from pyasm.prod.biz import *

from .command import *
from .trigger import *
from .file_upload import *



def get_web_container():
    '''we have a circular reference here, so put in a function to handle it'''
    from pyasm.web import WebContainer
    return WebContainer.get_web()


class DatabaseAction(Command):
    """takes the value and adds it to the current sobject.  It does
    not commit to the database"""

    def __init__(self, **kwargs):
        self.sobject = None
        self.name = None
        self.input_prefix = None
        self.value = None
        self.errors = []
        self.description = ""
        self.response = ''
        self.commit_flag = False
        self.options = {}
        self.sobjects = []
        self.info = {}
        self.kwargs = kwargs
        self.data = None


    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data


    def check(self):
        self.web = get_web_container()
        #value = self.web.get_form_value(self.get_input_name())

        value = self.get_value(self.name)
        # check for save option == false, equivalent to the old NulllAction
        no_action = self.get_option('save') == 'false'
        if no_action:
            return False
        # default for empty is True.
        no_empty = self.get_option('empty') == 'false'
        if no_empty:
            if value == '':
                name = self._get_name()
                raise UserException("The input for [%s] cannot be empty" %name.capitalize())


        # a match or search can be used. Match if for pattern, Search is for invalid chars.
        regexm = self.get_option('regexm')
        regexs = self.get_option('regexs')
        if regexm and value:
            m = re.match(r'%s' % regexm, value)
            if not m:
                name = self._get_name()
                raise UserException("The input for [%s] is invalid for expression [%s]" \
                        % (name.capitalize(), regexm))

        if regexs and value:
            m = re.search(r'%s' % regexs, value)
            if m:
                name = self._get_name()
                raise UserException("The input for [%s] contains invalid characters [%s]" \
                        % (name.capitalize(), regexs))


        if not value:
            default = self.get_option('default_col')
            if default:
                column_value = self.get_value(default)
                if column_value:
                    self.value = column_value

        return True


    def _get_name(self):
        name = self.get_input_name()
        if '|' in name:
            name = name.split('|', 1)[1]

        return name

    def set_name(self, name):
        self.name = name


    def has_option(self, key):
        return key in self.options

    def set_option(self, key, value):
        self.options[key] = value

    def get_option(self, key):
        '''gets the value of the specified option'''
        if key in self.options:
            return self.options[key]
        else:
            return ""


    def get_options(self):
        return self.options


    def set_commit_flag(self, flag):
        '''determines whether a commit is made by the action or it
        is done externally to the action'''
        if flag == True or flag == "True":
            self.commit_flag = True
        else:
            self.commit_flag = False

    def commit(self):
        '''does nothing'''
        pass

    def rollback(self):
        '''does nothing'''
        pass

    def set_input_prefix(self, input_prefix):
        self.input_prefix = input_prefix

    def get_name(self):
        return self.name

    def get_input_name(self):
        if self.input_prefix:
            return "%s|%s" % (self.input_prefix, self.name)
        else:
            return self.name

    def set_sobject(self, sobject):
        self.sobject = sobject

    def get_values(self, name=None):
        # get the value from the form
        if self.value:
            return [self.value]

        if not name:
            name = self.name

        if self.input_prefix:
            input_name = "%s|%s" % (self.input_prefix, name)
        else:
            input_name = name

        if self.data != None:
            self.values = [self.data]
        else:
            web = get_web_container()
            self.values = web.get_form_values(input_name)
        return self.values

    def get_value(self, name=None):
        # if set externally, just use it
        if self.value:
            return self.value
        values = self.get_values(name)
        if isinstance(values, list):
            if values:
                return values[0]
            else:
                return ''
        elif values:
            return values
        else:
            return ""

    def set_value(self, value):
        self.value = value

    def execute(self):

        column = self.get_option("column")
        if not column:
            column = self.name

        # get the value
        # NOTE: not sure why this was "column".  The value will come
        # through with the name of the element.  The "column" options
        # tells the action which column to set the value to
        #value = self.get_value(column)
        value = self.get_value(self.name)


        # check if there is an expression on the update
        expr = self.get_option("expression")

        # check for parent action to save search_type and search_id or parent_code etc separately
        # this is usually already taken care of in EditCmd
        parent_key_action = self.get_option('parent_key') == 'true'

        if expr:
            vars = {
                'VALUE': value
            }
            Search.eval(expr, self.sobject, vars=vars)


        else:

            search_type = self.sobject.get_search_type()
            col_type = SearchType.get_tactic_type(search_type, column)


            value = self.convert_value(col_type, value)

            if value == None:
                pass
            elif parent_key_action:
                self.sobject.add_relationship(value)
            else:
                self.sobject.set_value(column, value )

            if self.commit_flag == True:
                self.sobject.commit()


        # the default way to handle data is:
        # { search_key: { name: value, name2: value2 } }
        """
        if self.data:

            for s_key, item_data in self.data.items():
                s = Search.get_by_search_key(s_key)
                if not s:
                    continue

                for name, value in item_data.items():
                    s.set_value(name, value)
                s.commit()
        """

    def post_execute(self):
        return



    def convert_value(self, col_type, value):
        if col_type == 'timecode':
            timecode = TimeCode(timecode=value)
            value = timecode.get_frames()
        elif col_type in ["time", "timestamp"]:

            from pyasm.common import SPTDate
            if not value:
                value = ""
            elif not SPTDate.has_timezone(value):
                timezone = PrefSetting.get_value_by_key('timezone')
                if timezone:
                    value = SPTDate.add_timezone(value, timezone)
                else:
                    value = SPTDate.add_local_timezone(value)
        elif col_type in ["float", "integer"]:
            if isinstance(value, six.string_types):
                value = value.replace(",", "")
                if value.startswith("$"):
                    value = value.lstrip("$")

            try:
                if not value:
                    value = None
                elif col_type == "float":
                    value = float(value)
                else:
                    value = int(value)
            except:
                raise UserException("[%s] must a number." % value)
        return value



__all__.append("ForeignKeyDatabaseAction")
class ForeignKeyDatabaseAction(DatabaseAction):

    def execute(self):
        # do nothing
        pass

    def postprocess(self):

        search_type = self.get_option("search_type")
        column = self.get_option("column")

        search_type = "construction/login_in_trade"
        column = "trade_code"

        value = self.get_value(self.name)


        sobject = self.sobject

        search = Search(search_type)
        search.add_relationship_filter(sobject)
        related = search.get_sobject()

        if not related:
            related = SearchType.create(search_type)
            related.set_parent(sobject)

        if not value:
            related.delete()
        else:
            related.set_value(column, value)
            related.commit()


class DefaultValueDatabaseAction(DatabaseAction):
    '''This element is executed on every element execution'''

    def execute(self):
        default_values = {
            #'login_id': Environment.get_user_name()
            'login_id': Environment.get_login().get_id(),
            'login': Environment.get_login().get_value("login")
        }

        for column, value in default_values.items():
            cur_value = self.sobject.get_value(column, value)
            if not cur_value:
                self.sobject.set_value(column, value)




class MultiDatabaseAction(DatabaseAction):
    '''Stores the value in the database as a || separated list.  There
    is also a || at the beginning and end so that the full string can
    be searched up.'''
    def execute(self):
        values = self.get_values()
        new_values = [i for i in values if i]
        new_values.sort()

        value_string = "||".join(new_values)
        # only do it if there is more than 1 value
        if value_string and '||' in value_string:
            # prepend and append
            value_string = "||%s||" % value_string

        self.sobject.set_value(self.name, value_string)

        if self.commit_flag == True:
            self.sobject.commit()


# DEPRECATED: this should be done at the Javascript Level or at least an
# option to DatabaseAction
class NonEmptyAction(DatabaseAction):
    ''' Make sure the value is not empty '''
    def check(self):
        self.web = get_web_container()
        #value = self.web.get_form_value(self.get_input_name())
        value = self.get_value()

        if not value:
            name = self.get_input_name()
            if '|' in name:
                name = name.split('|')[1]
            raise UserException("[%s] cannot be empty." % name.capitalize())

        return True

class RegexAction(DatabaseAction):
    ''' Make sure the value matches the given expression defined in the option <regex> '''

    def check(self):
        self.web = get_web_container()
        value = self.web.get_form_value(self.get_input_name())

        regex = self.get_option('regex')
        if value and regex:
            name = self.get_input_name()
            if '|' in name:
                name = name.split('|', 1)[1]
            m = re.match(r'%s' % regex, value)
            if not m:
                raise UserException("The input for [%s] is invalid for expression [%s]" \
                        % (name.capitalize(), regex))

        return True

class NullAction(DatabaseAction):

    def execute(self):
        # do nothing
        pass



class PasswordAction(DatabaseAction):
    '''encrypts the entered password'''

    def get_title(self):
        return "Password Change"

    def set_password(self, password):
        self.password = password
        self.re_enter = ""

    def set_search_key(self, search_key):
        self.sobject = Search.get_by_search_key(search_key)


    def check(self):
        self.password = self.get_value("password")

        if self.sobject == None:
            return False

        self.re_enter = self.get_value("password re-enter")
        if self.re_enter != "" and self.re_enter != self.password:
            raise UserException( "Passwords must match.  Go back and re-enter")

        return True

    def execute(self):
        assert self.sobject != None

        if self.password == "":
            if self.sobject.is_insert():
                raise UserException("Empty password.  Go back and re-enter")
            else:
                return

        # encrypt the password
        password = self.password.encode('utf8')
        encrypted = Login.encrypt_password(password)
        self.sobject.set_value("password", encrypted)

        if self.commit_flag == True:
            self.sobject.commit()

        self.description = "Changed Password"


class IsCurrentAction(DatabaseAction):

    def execute(self):
        snapshot = self.sobject

        value = self.get_value()
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

    def execute(self):
        web = get_web_container()
        namespace = web.get_context_name()


class UniqueValueAction(DatabaseAction):
    ''' Ensure the value entered does not violate the Unique Constraint for a column '''
    def check(self):
        self.web = get_web_container()
        name = self.web.get_form_value(self.get_input_name())
        search_type = self.sobject.get_search_type()

        column = self.get_name()

        search = Search(search_type)
        search.add_filter(column, name)
        sobject = search.get_sobject()
        if sobject:
            raise UserException("%s [%s] has been taken!" \
                %(column.capitalize(), name))

        super(UniqueValueAction, self).check()
        return True


class LoginAction(DatabaseAction):

    def check(self):
        self.web = get_web_container()

        license = Environment.get_security().get_license()
        max_users = license.get_max_users()
        active_users = license.get_current_users()

        # this action is used for both edit and insert
        if self.sobject.is_insert():
            active_users += 1

        # allow disabled and float type login user addition
        if active_users > max_users and self.web.get_form_value('license_type') not in ['disabled','float']:
            raise UserException("Max active users [%s] reached for your license"%max_users)

        super(LoginAction, self).check()
        return True



class GroupNameAction(DatabaseAction):

    def check(self):
        self.web = get_web_container()
        self.group = self.web.get_form_value(self.get_input_name())
        if not self.group:
            raise CommandException("Login Group cannot be empty!")

        return True

    def execute(self):

        if self.sobject.is_insert():
            #namespace = self.web.get_context_name()
            #if namespace == "admin":
            #    namespace = self.sobject.get_value("namespace")
            namespace = self.get_value("namespace")
            if namespace:
                self.sobject.set_value(self.name, "%s/%s" %(namespace, self.group))
            else:
                self.sobject.set_value(self.name, self.group)
        else:
            self.sobject.set_value(self.name, self.group)





class UploadAction(DatabaseAction):
    """action which saves a file to the tmp directory and processes
    it according to its file type"""
    def __init__(self):
        self.checkin = None
        super(UploadAction, self).__init__()

    def get_title(self):
        return "Upload"

    def set_value(self, value):
        self.value = value

    def execute(self):
        '''Do nothing'''
        pass


    def postprocess(self):
        web = get_web_container()

        keys = web.get_form_keys()

        from pyasm.search import Transaction
        transaction = Transaction.get()
        assert transaction

        # first get some data based in
        column = self.get_value("%s|column" % self.name)
        if column == "":
            column = self.name

        # NOTE: why did this change?
        #prefix = self.get_input_name()
        prefix = self.get_name()


        context = self.get_value("%s|context" % prefix)
        description = self.get_value("%s|description" % prefix)

        field_storage = self.get_value(prefix)
        handoff_path = self.get_value("%s|path" % prefix )
        custom_ticket = self.get_value("%s|ticket" % prefix )

        from pyasm.widget import CheckboxWdg
        cb = CheckboxWdg("%s|is_revision" % prefix)
        is_rev = cb.is_checked()

        if handoff_path:
            handoff_path = handoff_path.replace("\\", "/")

            security = Environment.get_security()
            ticket = security.get_ticket_key()

            # in case it's supplied by widget like SimpleUploadWdg
            if custom_ticket:
                ticket = custom_ticket

            handoff_path = os.path.basename(handoff_path)
            handoff_path = Common.get_filesystem_name(handoff_path)

            handoff_path = "%s/upload/%s/%s" % (Environment.get_tmp_dir(), ticket, handoff_path)


            print("Uploaded path: ", handoff_path)
            if not os.path.exists(handoff_path):
                raise Exception("Uploaded Path [%s] does not exist" % handoff_path)

            self.files = [handoff_path]
            file_types = ['main']

            # create an icon
            icon_creator = IconCreator(handoff_path)
            icon_creator.execute()
            icon_path = icon_creator.get_web_path()
            if icon_path:
                self.files.append(icon_path)
                file_types.append("web")

            web_path = icon_creator.get_icon_path()
            if web_path:
                self.files.append(web_path)
                file_types.append("icon")


        elif field_storage != "":

            # process and get the uploaded files
            upload = FileUpload()
            upload.set_field_storage(field_storage)
            upload.execute()

            # get files and file types
            self.files = upload.get_files()
            if not self.files:
                return
            file_types = upload.get_file_types()
        else:
            if self.get_option("file_required") == "true":
                err_msg = _("upload is required")
                raise TacticException("%s %s" % (self.name, err_msg))
            else:
                return


        checkin_class = self.get_option("checkin")
        if checkin_class:
            snapshot_type = self.get_option("snapshot_type")
            self.checkin = Common.create_from_class_path(checkin_class, [self.sobject, self.files, file_types, context, snapshot_type])

        else:

            from pyasm.checkin import FileCheckin
            self.checkin = FileCheckin.get( self.sobject, self.files, file_types,
                context=context, column=column, snapshot_type="file", mode="uploaded" )

        self.sobjects.append(self.sobject)

        self.checkin.set_description(description)
        self.checkin.set_revision(is_rev)
        self.checkin.execute()

        # remove the files in upload area
        for file in self.files:
            if os.path.exists(file):
                os.unlink(file)





class AddToBinAction(NonEmptyAction):

    def check(self):
        if not self.get_value():
            raise UserException('Please choose a valid bin')
        return True

    def get_title(self):
        return "Add submit to a bin"

    def execute(self):
        Container.put('bin', self.get_value())

        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        parent_search_type = web.get_form_value("parent_search_type")
        parent_search_id = web.get_form_value("parent_search_id")

        submit = self.sobject

        # if submitting using a snapshot, then get the snapshot's parent
        parent = Search.get_by_id(parent_search_type, parent_search_id)
        if isinstance(parent, Snapshot):
            self.parent_snapshot = parent
            parent_search_type = self.parent_snapshot.get_value("search_type")
            parent_search_id = self.parent_snapshot.get_value("search_id")

            submit.set_value("version", self.parent_snapshot.get_value("version") )
            submit.set_value("context", self.parent_snapshot.get_value("context") )
            submit.set_value("snapshot_code",  self.parent_snapshot.get_value("code"))
        else:
            self.parent_snapshot = None


        submit.set_value("search_type", parent_search_type)
        submit.set_value("search_id", parent_search_id)

        # have to commit here to get Id of submit
        submit.commit()

        bin_id = self.get_value()

        # have to load this dynamically
        from pyasm.prod.biz import Submission, SubmissionInBin

        # put the submission in a bin
        group = SubmissionInBin.create_new()
        group.set_value('submission_id', submit.get_id())
        group.set_value('bin_id', bin_id)
        group.commit()


    def postprocess(self):
        # if the submitted parent is a snapshot, then connect to that snapshot
        submit = self.sobject

        self.sobjects.append(submit)
        Trigger.call(self, 'email')





class PerforceUploadAction(UploadAction):

    def postprocess(self):

        web = get_web_container()

        field_storage = web.get_form_value(self.name)

        # if no files have been uploaded, don't do anything
        if field_storage == "":
            return

        context = web.get_form_value("%s|context" % self.name)
        if context == '':
            context = Snapshot.get_default_context()
        description = web.get_form_value("%s|description" % self.name)

        # process and get the uploaded files
        upload = FileUpload()
        upload.set_field_storage(field_storage)
        upload.execute()
        self.files = upload.get_files()

        # set a trigger to give a chance to rename files
        Trigger.call(self, "rename_files")

        snapshot_type = 'file'

        file_types = upload.get_file_types()

        from pyasm.checkin import PerforceCheckin
        checkin = PerforceCheckin( self.sobject, self.files, file_types,  \
            context=context, column=self.name, snapshot_type="file" )
        checkin.set_description(description)
        checkin.execute()




class MultiUploadAction(DatabaseAction):

    def set_value(self, value):
        self.value = value


    def execute(self):
        '''do nothing'''
        pass

    def postprocess(self):
        web = get_web_container()
        self.files = []
        self.file_types = []
        if self.get_option('upload_type') == 'arbitrary':
            self._upload_arbitrary_files()
        else:
            self._upload_specified_files()

        context = self.get_value("%s|context" % self.name)
        subcontext = self.get_value("%s|subcontext" % self.name)
        if subcontext:
            context = '%s/%s' %(context, subcontext)
        description = self.get_value("%s|description" % self.name)
        from pyasm.widget import CheckboxWdg
        cb = CheckboxWdg("%s|is_revision" % self.get_input_name())
        is_rev = cb.is_checked(False)

        # let checkin take care of moving files to the lib
        from pyasm.checkin import FileCheckin
        self.checkin = FileCheckin.get( self.sobject, self.files, self.file_types,  \
            context=context, snapshot_type="file" )
        self.checkin.set_description(description)
        self.checkin.set_revision(is_rev)
        self.checkin.execute()


        self.sobjects.append(self.sobject)
        self.info['context'] = context
        self.add_description('File Publish for [%s]' %self.sobject.get_code())
        # remove the files in upload area
        for file in self.files:
            if os.path.exists(file):
                os.unlink(file)

        Trigger.call(self, "email")

    def _upload_arbitrary_files(self):
        ''' upload an arbitrary list of files'''
        field_storage_list = []
        upload_names = []
        web = get_web_container()
        keys = web.get_form_keys()
        name = self.get_input_name().replace('|', '\|')
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


            self.files.extend(files)
            file_types = upload.get_file_types()
            self.file_types.extend(file_types)


    def _upload_specified_files(self):
        ''' upload predefined file types specified in the conf.xml file'''
        upload_names = self._get_option('names')

        # check for uniqueness in upload_names
        if len(set(upload_names)) != len(upload_names):
            raise TacticException('[names] in the config file must be unique')

        upload_types = self._get_option('types')

        assert len(upload_names) == len(upload_types)

        field_storage_dict = {}
        valid_upload_names = []
        valid_upload_types = []

        for idx, name in enumerate(upload_names):
            field_storage = self.get_value(name)
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
            self.files.extend(files)
            file_types = upload.get_file_types()
            if len(file_types) > 1:
                icon_created = True
            self.file_types.extend(file_types)



    def _get_option(self, attr):
        ''' get option delimited by | '''
        upload_names = self.get_option(attr)
        if not upload_names:
            upload_names = [self.name]
        else:
            upload_names = upload_names.split('|')

        return upload_names

class MultiZipUploadAction(MultiUploadAction):

    def check(self):
        self.naming = None
        self.sobject_dict = {}
        naming = self.get_option('naming')
        if naming:
            self.naming = eval('%s()' %naming)
        else:
            raise TacticException('A naming has to be specified in the action option')
        return True

    def postprocess(self):
        web = get_web_container()
        self.files = []
        self.file_types = []

        self._upload_zipped_files()

        context = self.get_value("%s|context" % self.name)
        description = self.get_value("%s|description" % self.name)

        # let checkin take care of moving files to the lib
        from pyasm.checkin import FileCheckin
        for sobject in self.sobject_dict.keys():
            files, file_types = self.sobject_dict.get(sobject)
            self.checkin = FileCheckin.get( sobject, files, file_types,  \
                context=context, snapshot_type="file" )
            self.checkin.set_description(description)
            self.checkin.execute()



        # remove the files in upload area
        for key in self.sobject_dict.keys():
            files, file_types = self.sobject_dict.get(key)
            for file in files:
                os.unlink(file)

    def _upload_zipped_files(self):
        ''' upload an arbitrary list of files'''
        field_storage_list = []
        upload_names = []
        web = get_web_container()
        keys = web.get_form_keys()
        name = self.get_input_name().replace('|', '\|')
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

            if self._create_icon(file_path):
                upload.set_create_icon_flag(True)

            upload.execute()
            if zipfile.is_zipfile(file_path):
                unzipped_files = Common.unzip_file(file_path)
                # remove the zip file
                os.unlink(file_path)
                for unzipped_file in unzipped_files:
                    self._process_file(None, unzipped_file)
            else:
                self._process_file(upload, file_path)





    def _create_icon(self, file_path):
        '''return True if an icon can be created out of it'''
        name, ext = os.path.splitext(file_path)

        create_icon = False
        if ext in ['.tif','.TIF','.jpg','.JPG', '.png', '.PNG']:
            create_icon = True
        if not ext:
            raise TacticException('file path with extension expected [%s]'\
                %file_path)

        return create_icon



    def _process_file(self, upload, file_path):
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

            if self._create_icon(file_path):
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


        sobject = self.naming.get_sobject_by_filename(file_name)
        if sobject:
            if self.sobject_dict.get(sobject):
                orig_files, orig_file_types = self.sobject_dict.get(sobject)
                files.extend(orig_files)
                file_types.extend(orig_file_types)
            self.sobject_dict[sobject] = (files, file_types)
            self.add_description("Published [%s] for [%s] " %(file_name, sobject.get_code()))
        else:
            raise UserException('Unrecognized uploaded file name [%s]' %file_name)


class CommandNameAction(DatabaseAction):

    def check(self):
        self.web = get_web_container()
        class_name = self.web.get_form_value(self.get_input_name())

        if not class_name:
            raise UserException("class name cannot be empty!")
        if "." in class_name:
            raise UserException("class name should be a unique command class name without the module portion!")
        return True

class RepoPathAction(DatabaseAction):

     def check(self):
        self.web = get_web_container()
        repo_path = self.web.get_form_value(self.get_input_name())

        if not repo_path:
            raise UserException("Repo path cannot be empty! <br/> \
                A valid example: 'characters/nonplayer'")
        if repo_path.startswith('/') or repo_path.endswith('/'):
            raise UserException("Repo path should not start or end with '/'.<br/> \
                A valid example: 'characters/nonplayer'")
        return True

class RepoPathPerAssetAction(DatabaseAction):

     def check(self):
        self.web = get_web_container()
        repo_path = self.web.get_form_value(self.get_input_name())

        if repo_path.startswith('/') or repo_path.endswith('/'):
            raise UserException("Perforce path should not start or end with '/'.<br/> \
                A valid example: 'characters/nonplayer/dragon'")

        return True


class ProjectCreateAction(DatabaseAction):
    def execute(self):

        if not self.sobject.is_insert():
            # do nothing
            return

        project = self.sobject
        project_code = project.get_code()
        project_type = project.get_base_type()

        database = DatabaseImpl.get()

        # check if database exists
        print("Creating database '%s' ..." % project_code)

        if database.database_exists(project_code):
            print("... already exists")
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
        print("Creating project directories [%s]..." % project_dir)
        if not os.path.exists(template_dir):
            print("... skipping: template dir [%s] does not exist" % template_dir)
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
            print("... skipping.  Already exists.")

        print("Done.")




class DateAction(DatabaseAction):
    '''special action class to handle dates'''

    def execute(self):
        value = self.get_value()
        if value == "now":
            from datetime import datetime
            date = datetime.now()
            value = str(date)
            self.set_value(value)



        super(DateAction, self).execute()



class TimeAction(DatabaseAction):
    '''special action class to handle dates'''

    def execute(self):
        web = get_web_container()
        column = self.get_option("column")

        name = self.get_name()
        hour_name = "%s|hour" % name
        min_name = "%s|minute" % name

        hour_value = int(self.get_value(hour_name))
        min_value = int(self.get_value(min_name))


        from dateutil import parser
        from datetime import datetime, timedelta

        time_change = timedelta(hours=hour_value, minutes=min_value)

        sobject = self.sobject
        date_value = sobject.get_value(column)
        if not date_value:
            date = datetime.now()
        else:
            date = parser.parse(date_value)

        date = datetime(date.year, date.month, date.day, hour_value, min_value)
        self.set_value(date)

        super(TimeAction, self).execute()





class TaskDateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def postprocess(self):

        # TODO: This should only happen *IF* the pipeline process defines it
        return

        bid_end_date = self.get_value()
        self.sobject.update_dependent_tasks()

        super(TaskDateAction, self).execute()


__all__.append("InitialTaskCreateAction")
class InitialTaskCreateAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def execute(self):
        # do nothing
        pass

    def postprocess(self):
        value = self.get_value()
        if not value:
            return

        from pyasm.biz import Task
        Task.add_initial_tasks(self.sobject)


class XmlAction(DatabaseAction):
    '''simple class to update the task dependencies'''

    def check(self):
        value = self.get_value()
        try:
            from pyasm.common import Xml, XmlException
            Xml(string=value)
        except XmlException as e:
            error =  e.__str__()
            raise TacticException("Invalid XML: %s" %error)

        return True
