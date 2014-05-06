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

# This is a stub for accessing the TACTIC server.  It simplifies the access for
# scripts using the client api.  Thin wrapper to the client API.  
# These are meant to be copied to client directories.

import datetime
import re
import xmlrpclib, os, getpass, shutil, httplib, sys, urllib, types, hashlib

class TacticApiException(Exception):
    pass

''' Class: TacticServerStub
    It allows client to send commands to and receive information from the TACTIC
    server.'''
class TacticServerStub(object):
    '''
        Constructor: TacticServerStub
    '''
    def __init__(my, login=None, setup=True, protocol=None, server=None, project=None, ticket=None, user=None, password=""):
        '''Function: __init__(login=None, setup=True, protocol=None, server=None, project=None, ticket=None, user=None, password="")
        Initialize the TacticServerStub

        @keyparam:
            login - login_code
            setup - if set to True, it runs the protocol set-up
            protocol - xmlrpc or local. it defaults to xmlrpc
            server - tactic server
            project - targeted project
            ticket - login ticket key
            user - tactic login_code that overrides the login
            password - password for login'''
            

        # initialize some variables
        if user:
            login = user
        my.login = login
        my.project_code = None
        my.server = None
        my.has_server = False
        my.server_name = None

        my.ticket = None                # the ticket sent to the server
        my.login_ticket = None
        my.transaction_ticket = None



        # autodetect protocol
        if not protocol:
            protocol = 'xmlrpc'
            try:
                import tactic
                from pyasm.web import WebContainer
                web = WebContainer.get_web()
                if web:
                    server_name = web.get_http_host()
                    if server_name:
                        protocol = 'local'
            except ImportError:
                pass
        my.protocol = protocol

        # if all of the necessary parameters are set, then
        if server and (ticket or login) and project:
            my.set_server(server)

            my.set_project(project)
            if ticket:
                my.set_ticket(ticket)
            elif login:
                # else try with no password (api_require_password)
                ticket = my.get_ticket(login, password)
                my.set_ticket(ticket)


        elif setup:
            my._setup(protocol)

        # cached handoff dir
        my.handoff_dir = None

    

    '''if the function does not exist, call this and make an attempt
    '''
    def _call_missing_method(my, *args):
        # convert from tuple to sequence
        args = [x for x in args]
        args.insert(0, my.ticket)
        return my.server.missing_method(my.missing_method_name, args)

    ''' DISABLING for now
    def __getattr__(my, attr):
        my.missing_method_name = attr
        return my._call_missing_method
    '''

    def test_error(my):
        return my.server.test_error(my.ticket)

    def get_protocol(my):
        '''Function: get_protocol() 
           
        @return: 
           string - local or xmlrpc'''
        return my.protocol


    def set_protocol(my, protocol):
        '''Function: get_protocol() 
       
        @params
           string - local or xmlrpc'''
        my.protocol = protocol


    def set_ticket(my, ticket):
        '''set the login ticket'''
        my.set_login_ticket(ticket)

    def set_login_ticket(my, ticket):
        '''Function: set_login_ticket(ticket)
           Set the login ticket with the ticket key'''
        my.login_ticket = ticket
        my.set_transaction_ticket(ticket)


    def set_transaction_ticket(my, ticket):
        if not my.project_code:
            my.project_code = ''

        my.ticket = {
            'ticket': ticket,
            'project': my.project_code,
            'language': 'python'
        }

        """
        if my.project_code:
            my.ticket = {
                'ticket': ticket,
                'project': my.project_code,
                'language': 'python'
            }
        else:
            raise TacticApiException("No project has been set. Please set a project using method TacticServerStub.set_project()")
        """

        my.transaction_ticket = ticket


    def get_transaction_ticket(my):
        return my.transaction_ticket

    def get_login_ticket(my):
        return my.login_ticket

    def get_login(my):
        return my.login


    def set_server(my, server_name):
        '''Function: set_server(server_name)
           Set the server name for this XML-RPC server'''
        my.server_name = server_name
        if my.protocol == "local":
            from pyasm.prod.service import ApiXMLRPC
            my.server = ApiXMLRPC()
            my.server.set_protocol('local')
            my.has_server = True
            return
            

        if my.server_name.startswith("http://") or my.server_name.startswith("https://"):
            url = "%s/tactic/default/Api/" % my.server_name
        else:
            url = "http://%s/tactic/default/Api/" % my.server_name
        #url = "http://localhost:8081/"

        # TODO: Not implmeneted: This is needed for isolation of transactions
        #if my.transaction_ticket:
        #    url = '%s%s' % (url, my.transaction_ticket)
        my.server = xmlrpclib.Server(url, allow_none=True)

        try:
            pass
            #print my.server.test(my.ticket)
        except httplib.InvalidURL:
            raise TacticApiException("You have supplied an invalid server name [%s]" % \
                my.server_name)
            
        my.has_server = True
        # WARNING: this is changing code in the xmlrpclib library.  This
        # library is not sending a proper user agent.  Hacking it in
        # so that at least the OS is sent
        if os.name == "nt":
            user_agent = 'xmlrpclib.py (Windows)'
        else:
            user_agent = 'xmlrpclib.py (Linux)'
        xmlrpclib.Transport.user_agent = user_agent

        
    def get_server_name(my):
        return my.server_name

    def get_server(my):
        return my.server

    def set_project(my, project_code):
        '''Function: set_project(project_code)
           Set the project code'''
        my.project_code = project_code
        if my.protocol == 'local':
            from pyasm.biz import Project
            Project.set_project(project_code)
        #my.set_project_state(project_code)

        # switch the project code on the ticket
        my.set_transaction_ticket(my.transaction_ticket)

    def get_project(my):
        return my.project_code


    def set_palette(my, palette):
        my.server.set_palette(palette)

    #-----------------------------------
    # API FUNCTIONS
    #
    #


    #
    # Building earch type functions
    #
    def build_search_type(my, search_type, project_code=None):
        '''API Function: build_search_type(search_type, project_code=None)
        Convenience method to build a search type from its components.  It is
        a simple method that build the proper format for project scoped search
        types.  A full search type has the form:
            prod/asset?project=bar.
        It uniquely defines a type of sobject in a project.

        @param:
        search_type - the unique identifier of a search type: ie prod/asset
        project_code (optional) - an optional project code.  If this is not
            included, the project from get_ticket() is added.

        @return:
        search type string

        @example
        [code]
        search_type = "prod/asset"
        full_search_type = server.build_search_type(search_type)
        [/code]
        '''
        # do not append project for sthpw/* search_type
        if search_type.startswith('sthpw/'):
            return search_type
        if not project_code:
            project_code = my.project_code
        assert project_code
        return "%s?project=%s" % (search_type, project_code)


    def build_search_key(my, search_type, code, project_code=None, column='code'):
        '''API Function: build_search_key(search_type, code, project_code=None, column='code')
        Convenience method to build a search key from its components.  A
        search_key uniquely indentifies a specific sobject.  This string
        that is returned is heavily used as an argument in the API to
        identify an sobject to operate one
        
        A search key has the form: "prod/shot?project=bar&code=XG001"
        where search_type = "prod/shot", project_code = "bar" and code = "XG001"

        @param:
        search_type - the unique identifier of a search type: ie prod/asset
        code - the unique code of the sobject

        @keyparam:
        project_code - an optional project code.  If this is not
            included, the project from get_ticket() is added.

        @return:
        string - search key 

        @example:
        [code]
        search_type = "prod/asset"
        code = "chr001"
        search_key = server.build_search_key(search_type, code)
        e.g. search_key = prod/asset?project=code=chr001
        [/code]

        [code]
        search_type = "sthpw/login"
        code = "admin"
        search_key = server.build_search_key(search_type, code, column='code')
        e.g. search_key = sthpw/login?code=admin
        [/code]

        '''
        if not project_code:
            if not search_type.startswith("sthpw/"):
                project_code = my.project_code
                assert project_code
        
        if search_type.find('?') == -1:
            if search_type.startswith('sthpw/'):
                search_key = "%s?%s=%s" %(search_type, column, code)
            else:
                search_key = "%s?project=%s&%s=%s" % (search_type, project_code, column, code)
        else:
            search_key = "%s&%s=%s" %(search_type, column, code)

        return search_key

    def split_search_key(my, search_key):
        '''API Function: split_search_key(search_key)
        Convenience method to split a search_key in into its search_type and search_code/id components. Note: only accepts the new form prod/asset?project=sample3d&code=chr001

        @param:
        search_key - the unique identifier of a sobject

        @return:
        tuple - search type, search code/id

        '''
        if search_key.find('&') != -1: 
            search_type, code = search_key.split('&')
        else:
            # non project-based search_key
            search_type, code = search_key.split('?')
        codes = code.split('=')
        assert len(codes) == 2;
        return search_type, codes[1]

    def get_home_dir(my):
        '''API Function: get_home_dir()
        OS independent method to Get the home directory of the current user.

        @return: 
        string - home directory


        '''
        if os.name == "nt":
            dir = "%s%s" % (os.environ.get('HOMEDRIVE'), os.environ.get('HOMEPATH'))
            if os.path.exists(dir):
                return dir
        
        return os.path.expanduser('~')


    def create_resource_path(my, login=None):
        '''DEPRECATED: use create_resource_paths() or get_resource_path()
           Create the resource path'''
        # get the current user
        if not login:
            login = getpass.getuser()
        filename = "%s.tacticrc" % login

        # first check home directory
        dir = my.get_home_dir()
        is_dir_writeable = os.access(dir, os.W_OK) and os.path.isdir(dir)
        
        # if the home directory is not existent or writable,
        # use the temp directory
        if not os.path.exists(dir) or not is_dir_writeable:
            if os.name == "nt":
                dir = "C:/sthpw/etc"
            else:
                dir = "/tmp/sthpw/etc"
            if not os.path.exists(dir):
                os.makedirs(dir)
        else:
            dir = "%s/.tactic/etc" % dir
            if not os.path.exists(dir):
                os.makedirs(dir)

            # if an old resource path does exist, then remove it
            if os.name == "nt":
                old_dir = "C:/sthpw/etc"
            else:
                old_dir = "/tmp/sthpw/etc"

            old_path = "%s/%s" % (old_dir, filename)
            if os.path.exists(old_path):
                os.unlink(old_path)
                print "Removing deprectated resource file [%s]" % old_path


        path = "%s/%s" % (dir,filename)
        return path

    def create_resource_paths(my, login=None):
        '''Get the 1 or possiblly 2 the resource paths for creation'''

        # get the current user
        os_login = getpass.getuser()
        if not login:
            login = os_login
        filename = "%s.tacticrc" % login
        filename2 = "%s.tacticrc" % os_login

        # first check home directory
        dir = my.get_home_dir()
        is_dir_writeable = os.access(dir, os.W_OK) and os.path.isdir(dir)
        
        # if the home directory is not existent or writable,
        # use the temp directory
        if not os.path.exists(dir) or not is_dir_writeable:
            if os.name == "nt":
                dir = "C:/sthpw/etc"
            else:
                dir = "/tmp/sthpw/etc"
            if not os.path.exists(dir):
                os.makedirs(dir)
        else:
            dir = "%s/.tactic/etc" % dir
            if not os.path.exists(dir):
                os.makedirs(dir)

            # if an old resource path does exist, then remove it
            if os.name == "nt":
                old_dir = "C:/sthpw/etc"
            else:
                old_dir = "/tmp/sthpw/etc"

            old_path = "%s/%s" % (old_dir, filename)
            if os.path.exists(old_path):
                os.unlink(old_path)
                print "Removing deprectated resource file [%s]" % old_path

        
        path = "%s/%s" % (dir,filename)
        path2 = "%s/%s" % (dir,filename2)
        paths = [path]
        if path2 != path:
            paths.append(path2)
        return paths



    def get_resource_path(my, login=None):
        '''API Function: get_resource_path(login=None)
        Get the resource path of the current user. It differs from 
        create_resource_paths() which actually create dir. The resource path
        identifies the location of the file which is used to cache connection information.
        An exmple of the contents is shown below:

        [code]
        login=admin
        server=localhost
        ticket=30818057bf561429f97af59243e6ef21
        project=unittest
        [/code]

        The contents in the resource file represent the defaults to use
        when connection to the TACTIC server, but may be overriden by the
        API methods: set_ticket(), set_server(), set_project() or the
        environment variables: TACTIC_TICKET, TACTIC_SERVER, and TACTIC_PROJECT

        Typically this method is not explicitly called by API developers and
        is used automatically by the API server stub. It attempts to get from 
        home dir first and then from temp_dir is it fails. 
        
        @param:
        login (optional) - login code. If not provided, it gets the current system user

        @return:
        string - resource file path
        '''

        # get the current user
        if not login:
            login = getpass.getuser()
        filename = "%s.tacticrc" % login

        # first check home directory
        dir = my.get_home_dir()

        is_dir_writeable = os.access(dir, os.W_OK) and os.path.isdir(dir)
        path = "%s/.tactic/etc/%s" % (dir,filename)
        # if the home directory path does not exist, check the temp directory
        if not is_dir_writeable or not os.path.exists(path):
            if os.name == "nt":
                dir = "C:/sthpw/etc"
            else:
                dir = "/tmp/sthpw/etc"

        else:
            dir = "%s/.tactic/etc" % dir
        path = "%s/%s" % (dir,filename)
    
        return path



    def get_ticket(my, login, password):
        '''API Function: get_ticket(login, password)
        Get an authentication ticket based on a login and password.
        This function first authenticates the user and the issues a ticket.
        The returned ticket is used on subsequent calls to the client api

        @param:
        login - the user that is used for authentications
        password - the password of that user

        @return:
        string - ticket key  
        '''
        return my.server.get_ticket(login, password)



    def get_info_from_user(my, force=False):
        '''API Function: get_info_from_user(force=False)
        Get input from the user about the users environment.  Questions
        asked pertain to the location of the tactic server, the project worked
        on and the user's login and password.  This information is stored in
        an .<login>.tacticrc file.

        @keyparam:
        force - if set to True, it will always ask for new infomation from the 
        command prompt again
        '''
        if my.protocol == "local":
            return

        old_server_name = my.server_name
        old_project_code = my.project_code
        old_ticket = my.login_ticket
        old_login = my.login

        default_login = getpass.getuser()
        if not force and old_server_name and old_project_code:
            return

        print
        print "TACTIC requires the following connection information:"

        print
        server_name = raw_input("Enter name of TACTIC server (%s): " % old_server_name)
        if not server_name:
            server_name = old_server_name

        print
        login = raw_input("Enter user name (%s): " % default_login)
        if not login:
            login = default_login

        print
        if login == old_login and old_ticket:
            password = getpass.getpass("Enter password (or use previous ticket): ")
        else:
            password = getpass.getpass("Enter password: ")

        print
        project_code = raw_input("Project (%s): " % old_project_code)
        if not project_code:
            project_code = old_project_code

        my.set_server(server_name)


        # do the actual work
        if login != old_login or password:
            ticket = my.get_ticket(login, password)
            print "Got ticket [%s] for [%s]" % (ticket, login)
        else:
            ticket = old_ticket

        # commit info to a file
        paths = my.create_resource_paths(login)
        # this is needed when running get_ticket.py
        my.login = login

        for path in paths:
            file = open(path, 'w')
            file.write("login=%s\n" % login)
            file.write("server=%s\n" % server_name)
            file.write("ticket=%s\n" % ticket)
            if project_code:
                file.write("project=%s\n" % project_code)

            file.close()
            print "Saved to [%s]" % path

        # set up the server with the new information
        my._setup(my.protocol)




    #
    # Simple Ping Test
    #
    def ping(my):
        return my.server.ping(my.ticket)

    def fast_ping(my):
        return my.server.fast_ping(my.ticket)

    def fast_query(my, search_type, filters=[], limit=None):
        results = my.server.fast_query(my.ticket, search_type, filters, limit)
        return eval(results)



    def test_speed(my):
        return my.server.test_speed(my.ticket)




    def get_connection_info(my):
        '''simple test to get connection info'''
        return my.server.get_connection_info(my.ticket)


    #
    # Logging facilities
    #
    def log(my, level, message, category="default"):
        '''API Function: log(level, message, category="default")
        Log a message in the logging queue.  It is often difficult to see output
        of a trigger unless you are running the server in debug mode.
        In production mode, the server sends the output to log files.
        The log files are general buffered.
        It cannot be predicted exactly when buffered output will be dumped to a file.

        This log() method will make a request to the server.
        The message will be immediately stored in the database in the debug log table.
        

        @param:
        level - critical|error|warning|info|debug - arbitrary debug level category
        message - freeform string describing the entry

        @keyparam:
        category - a label for the type of message being logged.
            It defaults to "default"
        '''
        return my.server.log(my.ticket, level,message, category)



    def log_message(my, key, message, status="", category="default"):
        '''API Function: log_message(key, message, status=None, category="default")

        Log a message which will be seen by all who are subscribed to
        the message "key".  Messages are often JSON strings of data.

        @params
        key - unique key for this message
        message - the message to be sent

        @keyparam
        status - arbitrary status for this message
        category - value to categorize this message

        @return
        string - "OK"
        '''
        return my.server.log_message(my.ticket, key, message, status, category)


    def subscribe(my, key, category="default"):
        '''API Function: subscribe(key, category="default")

        Allow a user to subscribe to this message key.  All messages
        belonging to the corresponding key will be available to users
        subscribed to it.

        @params
        key - unique key for this message

        @keyparam
        category - value to categorize this message

        @return
        subscription sobject
        '''
        return my.server.subscribe(my.ticket, key, category)




    #
    # Transaction methods
    #
    def set_state(my, name, value):
        '''Set a state for this transaction
       
        @params
        name: name of state variable
        value: value of state variable
        '''
        return my.server.set_state(my.ticket, name, value)


    def set_project_state(my, project):
        '''Covenience function to set the project state

        @params
        project: code of the project to set the state to
        '''
        return my.set_state("project", project)

    def generate_ticket(my):
        '''API Function: generate_ticket()
        Ask the server to generate a ticket explicity used for your own commands 
            
        @return - a string representing the transaction ticket
        '''
        return my.server.generate_ticket(my.ticket)


    def start(my, title='', description='', transaction_ticket=''):
        '''API Function: start(title, description='')
        Start a transaction.  All commands using the client API are bound
        in a transaction.  The combination of start(), finish() and abort()
        makes it possible to group a series of API commands in a single
        transaction.  The start/finish commands are not necessary for
        query operations (like query(...), get_snapshot(...), etc).


        @keyparam:
        title - the title of the command to be executed.  This will show up on
            transaction log
        description - the description of the command. This is more detailed. 
        transaction_ticket - optionally, one can provide the transaction ticket sequence

        @example:
        A full transaction inserting 10 shots.  If an error occurs, all 10
        inserts will be aborted.
        [code]
        server.start('Start adding shots')
        try:
            for i in range(0,10):
                server.insert("prod/shot", { 'code': 'XG%0.3d'%i } )
        except:
            server.abort()
        else:
            server.finish("10 shots added")
        [/code]
        '''
        my.get_info_from_user()

        if not my.has_server:
            raise TacticApiException("No server connected.  If running a command line script, please execute get_ticket.py")

        ticket = my.server.start(my.login_ticket, my.project_code, \
            title, description, transaction_ticket)
        my.set_transaction_ticket(ticket)

        #client_version = my.get_client_version()
        #server_version = my.get_server_version()

        # Switch to using api versions
        client_api_version = my.get_client_api_version()
        server_api_version = my.get_server_api_version()
        if client_api_version != server_api_version:
            raise TacticApiException("Server version [%s] does not match client api version [%s]" % (server_api_version, client_api_version) )

        my.set_server(my.server_name)
        # clear the handoff dir
        my.handoff_dir = None

        return ticket



    def finish(my, description=''):
        '''API Function: finish()
        End the current transaction and cleans it up
        
        @params:
        description: this will be recorded in the transaction log as the
            description of the transction

        @example:
        A full transaction inserting 10 shots.  If an error occurs, all 10
        inserts will be aborted.
        [code]
        server.start('Start adding shots')
        try:
            for i in range(0,10):
                server.insert("prod/shot", { 'code': 'XG%0.3d'%i } )
        except:
            server.abort()
        else:
            server.finish("10 shots added")
        [/code]
       
        '''
        if my.protocol == "local":
            return

        result = my.server.finish(my.ticket, description)
        my.set_login_ticket(my.login_ticket)
        #my.ticket = None
        #my.transaction_ticket = None
        return result


    def abort(my, ignore_files=False):
        '''API Function: abort(ignore_files=False)
        Abort the transaction.  This undos all commands that occurred
        from the beginning of the transactions
        
        @keyparam:
        ignore_files: (boolean) - determines if any files moved into the
            repository are left as is.  This is useful for very long processes
            where it is desireable to keep the files in the repository
            even on abort.

        @example:
        A full transaction inserting 10 shots.  If an error occurs, all 10
        inserts will be aborted.
        [code]
        server.start('Start adding shots')
        try:
            for i in range(0,10):
                server.insert("prod/shot", { 'code': 'XG%0.3d'%i } )
        except:
            server.abort()
        else:
            server.finish("10 shots added")
        [/code]
        '''
        if my.protocol == "local":
            return
        result = my.server.abort(my.ticket, ignore_files)
        my.ticket = None
        my.transaction_ticket = None
        return result



    # FIXME: have to fix these because these are post transaction!!
    def undo(my, transaction_ticket=None, transaction_id=None, ignore_files=False):
        '''API Function: undo(transaction_ticket=None, transaction_id=None, ignore_files=False)
        undo an operation.  If no transaction id is given, then the last
        operation of this user on this project is undone

        @keyparam:
        transaction_ticket - explicitly undo a specific transaction
        transaction_id - explicitly undo a specific transaction by id
        ignore_files - flag which determines whether the files should
            also be undone.  Useful for large preallcoated checkins.
        '''
        if my.protocol == "local":
            return
        return my.server.undo(my.ticket, transaction_ticket, transaction_id, ignore_files)



    def redo(my, transaction_ticket=None, transaction_id=None):
        '''API Function: redo(transaction_ticket=None, transaction_id=None)
        Redo an operation.  If no transaction id is given, then the last
        undone operation of this user on this project is redone

        @keyparam:
        transaction_ticket - explicitly redo a specific transaction
        transaction_id - explicitly redo a specific transaction by id
        '''
        if my.protocol == "local":
            return
        return my.server.redo(my.ticket, transaction_ticket, transaction_id)



    #
    # Low Level Database methods
    #
    def get_column_info(my, search_type):
        '''API Function: get_column_info(search_type)
        Get column information of the table given a search type

        @param:
        search_type - the key identifying a type of sobject as registered in
                      the search_type table.

      
        @return - a dictionary of info for each column

        '''
        results = my.server.get_column_info(my.ticket, search_type)
        return results


    def get_table_info(my, search_type):
        '''API Function: get_table_info(search_type)
        Get column information of the table given a search type

        @param:
        search_type - the key identifying a type of sobject as registered in
                      the search_type table.

      
        @return - a dictionary of info for each column

        '''
        results = my.server.get_table_info(my.ticket, search_type)
        return results



    def get_related_types(my, search_type):
        '''API Function: get_related_types(search_type)
        Get related search types given a search type

        @param:
        search_type - the key identifying a type of sobject as registered in
                      the search_type table.

      
        @return - list of search_types 

        '''
        results = my.server.get_related_types(my.ticket, search_type)
        return results

    def query(my, search_type, filters=[], columns=[], order_bys=[], show_retired=False, limit=None, offset=None, single=False, distinct=None, return_sobjects=False):
        '''API Function: query(search_type, filters=[], columns=[], order_bys=[], show_retired=False, limit=None, offset=None, single=False, distinct=None, return_sobjects=False) 
        General query for sobject information

        @param:
        search_type - the key identifying a type of sobject as registered in
                      the search_type table.

        @keyparam:
        filters -  an array of filters to alter the search
        columns -  an array of columns whose values should be
                    retrieved
        order_bys -  an array of order_by to alter the search
        show_retired - sets whether retired sobjects are also
                    returned
        limit - sets the maximum number of results returned
        single - returns only a single object
        distinct - specify a distinct column
        return_sobjects - return sobjects instead of dictionary.  This
                works only when using the API on the server.
        @return:
        list of dictionary/sobjects - Each array item represents an sobject
               and is a dictionary of name/value pairs

        @example:
        [code]
            filters = []
            filters.append( ("code", "XG002") )
            order_bys = ['timestamp desc']
            columns = ['code']
            server.query(ticket, "prod/shot", filters, columns, order_bys)
        [/code]

        The arguments "filters", "columns", and "order_bys" are optional

        The "filters" argument is a list.  Each list item represents an
        individual filter.  The forms are as follows:

        [code]
        (column, value)             -> where column = value
        (column, (value1,value2))   -> where column in (value1, value2)
        (column, op, value)         -> where column op value
            where op is ('like', '<=', '>=', '>', '<', 'is', '~', '!~','~*','!~*)
        (value)                     -> where value
        [/code]
        '''
        #return my.server.query(my.ticket, search_type, filters, columns, order_bys, show_retired, limit, offset, single, return_sobjects)
        results = my.server.query(my.ticket, search_type, filters, columns, order_bys, show_retired, limit, offset, single, distinct, return_sobjects)
        if not return_sobjects and isinstance(results, basestring):
            results = eval(results)
        return results

        
    def insert(my, search_type, data, metadata={}, parent_key=None,  info={}, use_id=False, triggers=True):
        '''API Function: insert(search_type, data, metadata={}, parent_key=None,  info={}, use_id=False, triggers=True)
        General insert for creating a new sobject

        @param:
        search_type - the search_type attribute of the sType
        data - a dictionary of name/value pairs which will be used to update
               the sobject defined by the search_key.
        parent_key - set the parent key for this sobject
        

        @keyparam:
        metadata - a dictionary of values that will be stored in the metadata attribute 
                   if available
        info - a dictionary of info to pass to the ApiClientCmd
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on insert

        @return:
        dictionary - represent the sobject with it's current data

        @example:
        insert a new asset
        [code]
        search_type = "prod/asset"
        
	data = {
            'code': chr001,
            'description': 'Main Character'
        }
        
	server.insert( search_type, data )
        [/code]
        insert a new note with a shot parent
        [code] 
        # get shot key
        shot_key = server.build_search_key(search_type='prod/shot',code='XG001')

        data = {
            'context': 'model',
            'note': 'This is a modelling note',
            'login': server.get_login()
        }

        server.insert( search_type, data, parent_key=shot_key)
        [/code]

        insert a note without firing triggers
        [code]
        
        search_type = "sthpw/note"
        
        data = {
            'process': 'roto',
            'context': 'roto',
            'note': 'The keys look good.',
            'project_code': 'art'
        }
        
        server.insert( search_type, data, triggers=False )
        [/code]
        '''
        return my.server.insert(my.ticket, search_type, data, metadata, parent_key, info, use_id, triggers)


    def update(my, search_key, data={}, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):
        '''API Function: update(search_key, data={}, metadata={}, parent_key=None, info={}, use_id=False, triggers=True)

        General update for updating sobject

        @param:
        search_key - a unique identifier key representing an sobject.
            Note: this can also be an array, in which case, the data will
            be updated to each sobject represented by this search key

        @keyparam:
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
        parent_key - set the parent key for this sobject
        info - a dictionary of info to pass to the ApiClientCmd

        metadata - a dictionary of values that will be stored in the metadata attribute if available
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on update


        @return:
        dictionary - represent the sobject with its current data.
            If search_key is an array, This will be an array of dictionaries
        '''
        return my.server.update(my.ticket, search_key, data, metadata, parent_key, info, use_id, triggers)

        
    def update_multiple(my, data, triggers=True):
        '''API Function: update_multiple(data, triggers=True) 

        Update for several sobjects with different data in one function call.  The
        data structure contains all the information needed to update and is
        formated as follows:

        data = {
            search_key1: { column1: value1, column2: value2 }
            search_key2: { column1: value1, column2: value2 }
        }


        @params:
        data - data structure containing update information for all
            sobjects

        @keyparam:
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
        triggers - boolean to fire trigger on insert


        @return:
        None
        '''
        return my.server.update_multiple(my.ticket, data, triggers)

    def insert_multiple(my, search_type,  data, metadata=[], parent_key=None, use_id=False, triggers=True):
        '''API Function: insert_multiple(data, metadata=[], parent_key=None, use_id=False, triggers=True)
        Insert for several sobjects in one function call.  The
        data structure contains all the infon needed to update and is
        formated as follows:

        data = [
            { column1: value1, column2: value2,  column3: value3 },
            { column1: value1, column2: value2,  column3: value3 }
        }

        metadata =  [
            { color: blue, height: 180 },
            { color: orange, height: 170 }
        ]


        @params:
        search_type - the search_type attribute of the sType
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
       
        @keyparam:
        parent_key - set the parent key for this sobject
        use_id - boolean to control if id is used in the search_key in returning sobject dict
        triggers - boolean to fire trigger on insert

        @return:
            a list of all the inserted sobjects
        '''
        return my.server.insert_multiple(my.ticket, search_type, data, metadata, parent_key, use_id, triggers)


    def insert_update(my, search_key, data, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):
        '''API Function: insert_update(search_key, data, metadata={}, parent_key=None, info={}, use_id=False, triggers=True)

        Insert if the entry does not exist, update otherwise

        @param:
        search_key - a unique identifier key representing an sobject.
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key

        @keyparam:
        metadata - a dictionary of values that will be stored in the metadata attribute if available
        parent_key - set the parent key for this sobject
        info - a dictionary of info to pass to the ApiClientCmd
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on insert

        
        @return:
        dictionary - represent the sobject with its current data.
        '''
        return my.server.insert_update(my.ticket, search_key, data, metadata, parent_key, info, use_id, triggers)


    def get_unique_sobject(my, search_type, data={}):
        '''API Function: get_unique_sobject(search_type, data={})

        This is a special convenience function which will query for an
        sobject and if it doesn't exist, create it.  It assumes that this
        object should exist and spares the developer the logic of having to
        query for the sobject, test if it doesn't exist and then create it.

        @param:
        search_type - the type of the sobject
        data - a dictionary of name/value pairs that uniquely identify this
            sobject

        @return:
        sobject - unique sobject matching the critieria in data
        '''
        results = my.server.get_unique_sobject(my.ticket, search_type, data)
        return results


    def get_column_names(my, search_type):
        '''API Function: get_column_names(search_type)
        This method will get all of the column names associated with a search
        type
       
        @param:
        search_type - the search type used to query the columns for

        @return
        list of columns names
        '''
        return my.server.get_column_names(my.ticket, search_type)




    #
    # Expression methods
    #
    def eval(my, expression, search_keys=[], mode=None, single=False, vars={}, show_retired=False):
        '''API Function: eval(expression, search_keys=[], mode=None, single=False, vars={}, show_retired=False)
        
        Evaluate the expression.  This expression uses the TACTIC expression
        language to retrieve results.  For more information, refer to the
        expression language documentation.

        @param:
        expression - string expression
        
        @keyparam:
        search_keys - the starting point for the expression.
        mode - string|expression - determines the starting mode of the expression
        single - True|False - True value forces a single return value
        vars - user defined variable
        show_retired - defaults to False to not return retired items

        @return:
        results of the expression.  The results depend on the exact nature
        of the expression.

        @example:
        #1. Search for snapshots with context beginning with 'model' for the asset with the search key 'prod/asset?project=sample3d&id=96'

        [code]
        server = TacticServerStub.get()
        exp = "@SOBJECT(sthpw/snapshot['context','EQ','^model'])"
        result = server.eval(exp, search_keys=['prod/asset?project=sample3d&id=96'])
        [/code]

        Please refer to the expression language documentation for numerous
        examples on how to use the expression language.

        '''
        #return my.server.eval(my.ticket, expression, search_keys, mode, single, vars)
        results = my.server.eval(my.ticket, expression, search_keys, mode, single, vars, show_retired)
        try:
            return eval(results)
        except:
            return results



    #
    # Higher Level Object methods
    #
    def create_search_type(my, search_type, title, description="", has_pipeline=False):
        '''API Function: create_search_type(search_type, title, description="", has_pipeline=False)
        Create a new search type

        @param:
            search_type - Newly defined search_type
            title - readable title to display this search type as

        @keyparam:
            description - a brief description of this search type
            has_pipeline - determines whether this search type goes through a
                           pipeline.  Simply puts a pipeline_code column in the table.

        @return
            string - the newly created search type

        '''
        return my.server.create_search_type(my.ticket, search_type, title, description, has_pipeline)



    def add_column_to_search_type(my, search_type, column_name, column_type):
        '''Adds a new column to the search type
        
        @params
        search_type - the search type that the new column will be added to
        column_name - the name of the column to add to the database
        column_type - the type of the column to add to the database

        @return
        True if column was created, False if column exists
        '''

        return my.server.add_column_to_search_type(my.ticket, search_type, column_name, column_type)



    def get_by_search_key(my, search_key):
        '''API Function: get_by_search_key(search_key)
        Get the info on an sobject based on search key
        @param:
            search_key - the key identifying a type of sobject as registered in
                          the search_type table.

        @return:
            list of dictionary - sobjects that represent values of the sobject in the
                form of name:value pairs
        '''
        return my.server.get_by_search_key(my.ticket, search_key)



    def get_by_code(my, search_type, code):
        '''API Function: get_by_code(search_type, search_code)
        Get the info on an sobject based on search code

        @param:
            search_type - the search_type of the sobject to search for
            code - the code of the sobject to search for

        @return:
            sobject - a dictionary that represents values of the sobject in the
                form name/value pairs
        '''
        return my.server.get_by_code(my.ticket, search_type, code)



    def delete_sobject(my, search_key, include_dependencies=False):
        '''API Function: delete_sobject(search_key, include_dependencies=False)
        Invoke the delete method.  Note: this function may fail due
        to dependencies.  Tactic will not cascade delete.  This function
        should be used with extreme caution because, if successful, it will
        permanently remove the existence of an sobject

        @param:
            search_key - a unique identifier key representing an sobject.
            Note: this can also be an array.

        @keyparam:
            include_dependencies - True/False

        @return:
            dictionary - a sobject that represents values of the sobject in the
            form name:value pairs
        '''

        return my.server.delete_sobject(my.ticket, search_key, include_dependencies)



    def retire_sobject(my, search_key):
        '''API Function: retire_sobject(search_key)
        Invoke the retire method. This is preferred over delete_sobject if 
        you are not sure whether other sobjects has dependency on this.

        @param:
            search_key - the unige key identifying the sobject.

        @return:
            dictionary - sobject that represents values of the sobject in the
            form name:value pairs
        '''
        return my.server.retire_sobject(my.ticket, search_key)



    def reactivate_sobject(my, search_key):
        '''API Function: reactivate_sobject(search_key)
        Invoke the reactivate method.

        @param:
        search_key - the unige key identifying the sobject.

        @return:
        dictionary - sobject that represents values of the sobject in the
            form name:value pairs
        '''
        return my.server.reactivate_sobject(my.ticket, search_key)



    def set_widget_setting(my, key, value):
        '''API Function: set_widget_settings(key, value)
        Set widget setting for current user and project

        @param
        key - unique key to identify this setting
        value - value the setting should be set to

        @return
        None
        '''
        my.set_widget_setting(my.ticket, key, value)

    def get_widget_setting(my, key):
        '''API Function: set_widget_settings(key, value)
        Get widget setting for current user and project

        @param
        key - unique key to identify this setting

        @return
        value of setting
        '''
        return my.get_widget_setting(my.ticket, key)



    #
    # sType Hierarchy methods
    #

    def get_parent(my, search_key, columns=[], show_retired=False):
        '''API Function: get_parent(search_key, columns=[],  show_retired=True)
        Get the parent of an sobject.

        @param:
        search_key - a unique identifier key representing an sobject
        
        @keyparam:
        columns - the columns that will be returned in the sobject
        show_retired - it defaults to False so it does not show retired parent if that's the case

        @return:
        dictionary - the parent sobject
        '''
        return my.server.get_parent(my.ticket, search_key, columns, show_retired)



    def get_all_children(my, search_key, child_type, filters=[], columns=[]):
        '''API Function: get_all_children(search_key, child_type, filters=[], columns=[])
        Get all children of a particular child type of an sobject

        @param:
            search_key - a unique identifier key representing an sobject
            child_type - the search_type of the children to search for

        @keyparam:
            filters - extra filters on the query : see query method for examples
            columns - list of column names to be included in the returned dictionary

        @return:
            list of dictionary - a list of sobjects dictionaries
        '''
        #filters = []
        return my.server.get_all_children(my.ticket, search_key, child_type, filters, columns)



    def get_parent_type(my, search_key):
        '''API Function: get_parent_type(search_key)
        Get of the parent search type

        @param:
            search_key - a unique identifier key representing an sobject

        @return:
            list - a list of child search_types
        '''
        return my.server.get_parent_type(my.ticket, search_key)


    def get_child_types(my, search_key):
        '''API Function: get_child_types(search_key)
        Get all the child search types

        @param:
            search_key - a unique identifier key representing an sobject

        @return:
            list - the child search types
        '''
        return my.server.get_child_types(my.ticket, search_key)



    def get_types_from_instance(my, instance_type):
        '''API Function: get_types_from_instance(instance_type)
        
        Get the connector types from an instance type

        @param:
            instance_type - the search type of the instance

        @return:
            tuple - (from_type, parent_type)
                a tuple with the from_type and the parent_type.  The from_type is
                the connector type and the parent type is the search type of the
                parent of the instance
        '''
        return my.server.get_types_from_instance(my.ticket, instance_type)




    def connect_sobjects(my, src_sobject, dst_sobject, context='default'):
        '''API Function: connect_sobjects(src_sobject, dst_sobject, context='default')
        Connect two sobjects together

        @param: 
        src_sobject - the original sobject from which the connection starts
        dst_sobject - the sobject to which the connection connects to

        @keyparam:
        context - an arbirarty parameter which defines type of connection

        @return:
        dictionary - the last connection sobject created
        '''
        return my.server.connect_sobjects(my.ticket, src_sobject, dst_sobject, context)



    def get_connected_sobjects(my, src_sobject, context='default'):
        '''API Function: get_connected_sobjects(src_sobject, context='default')
        Get all of the connected sobjects

        @param:
        src_sobject - the original sobject from which the connection starts

        @keyparam:
        context - an arbitrary parameter which defines type of connection

        @return:
        list - a list of connected sobjects
        '''
        return my.server.get_connected_sobjects(my.ticket, src_sobject, context)



    def get_connected_sobject(my, src_sobject, context='default'):
        '''API Function: get_connected_sobject(src_sobject, context='default')
        Get the connected sobject

        @params
        src_sobject - the original sobject from which the connection starts
           
        @keyparam:
        context - an arbirarty parameter which defines type of connection

        @return:
        dict - a single connected sobject
        '''
        return my.server.get_connected_sobject(my.ticket, src_sobject, context)




    #
    # upload/download methods
    #
    def download(my, url, to_dir=".", filename='', md5_checksum=""):
        '''API Function: download(my, url, to_dir=".", filename='', md5_checksum="")
        Download a file from a given url

        @param:
            url - the url source location of the file

        @keyparam:
            to_dir - the directory to download to
            filename - the filename to download to, defaults to original filename
            md5_checksum - an md5 checksum to match the file against

        @return:
            string - path of the file donwloaded
        '''

        # use url filename by default
        if not filename:
            filename = os.path.basename(url)

        # download to temp_dir
        #if not to_dir:
        #    to_dir = my.get_tmpdir()


        # make sure the directory exists
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        to_path = "%s/%s" % (to_dir, filename)


        # check if this file is already downloaded.  if so, skip
        if os.path.exists(to_path):
            # if it exists, check the MD5 checksum
            if md5_checksum:
                if my._md5_check(to_path, md5_checksum):
                    print "skipping '%s', already exists" % to_path
                    return to_path
            else:
                # always download if no md5_checksum available
                pass


        f = urllib.urlopen(url)
        file = open(to_path, "wb")
        file.write( f.read() )
        file.close()
        f.close()

        # check for downloaded file
        # COMMENTED OUT for now since it does not work well with icons
        #if md5_checksum and not my._md5_check(to_path, md5_checksum):
        #    raise TacticException('Downloaded file [%s] in local repo failed md5 check. This file may be missing on the server or corrupted.'%to_path)

        """
        print "starting download"
        try:
            import urllib2
            file = open(to_path, "wb")
            req = urllib2.urlopen(url)
            try:
                while True:
                    buffer = req.read(1024*100)
                    print "read: ", len(buffer)
                    if not buffer:
                        break
                    file.write( buffer )
            finally:
                print "closing ...."
                req.close()
                file.close()
        except urllib2.URLError, e:
            raise Exception('%s - %s' % (e,url))

        print "... done download"
        """


        return to_path




    def upload_file(my, path, base_dir=None):
        '''API Function: upload_file(path)
        Use http protocol to upload a file through http

        @param:
        path - the name of the file that will be uploaded
        
        '''
        from common import UploadMultipart
        upload = UploadMultipart()
        upload.set_ticket(my.transaction_ticket)
        if my.server_name.startswith("http://") or my.server_name.startswith("https://"):
            upload_server_url = "%s/tactic/default/UploadServer/" % my.server_name
        else:
            upload_server_url = "http://%s/tactic/default/UploadServer/" % my.server_name


        if base_dir:
            basename = os.path.basename(path)
            dirname = os.path.dirname(path)
            if not path.startswith(dirname):
                raise TacticApiException("Path [%s] does not start with base_dir [%s]" % (path, base_dir))
            base_dir = base_dir.rstrip("/")
            sub_dir = dirname.replace("%s/" % base_dir, "")
            if sub_dir:
                upload.set_subdir(sub_dir)



        upload.set_upload_server(upload_server_url)
        #upload.set_subdir("blah")
        upload.execute(path)

        # upload a file
        #filename = os.path.basename(path)
        #file = open(path, 'rb')
        #data = xmlrpclib.Binary( file.read() )
        #file.close()
        #return my.server.upload_file(my.transaction_ticket, filename, data)


    def upload_group(my, path, file_range):
        '''uses http protocol to upload a sequences of files through HTTP

        @params
        path - the name of the file that will be uploaded
        file_range - string describing range of frames in the form '1-5/1'
        '''

        start, end = file_range.split("-")
        start = int(start)
        end = int(end)

        if path.find("####") != -1:
            path = path.replace("####", "%0.4d")

        # TODO: add full range functionality here
        for frame in range(start, end+1):
            full_path = path % frame
            my.upload_file(full_path)

    # file group functions
    def _get_file_range(my, file_range):
        '''get the file_range'''
        frame_by = 1
        if file_range.find("/") != -1:
            file_range, frame_by = file_range.split("/")
            frame_by = int(frame_by)

        frame_start, frame_end = file_range.split("-")
        frame_start = int(frame_start)
        frame_end = int(frame_end)
        return frame_start, frame_end, frame_by

    def _expand_paths(my, file_path, file_range):
        '''expands the file paths, replacing # as specified in the file_range
           @param - file_path with #### or %0.4d notation
           @file_range - a tuple'''
        file_paths = []
        
        frame_start, frame_end, frame_by = my._get_file_range(file_range)
        # support %0.4d notation
        if file_path.find('#') == -1:
            for i in range(frame_start, frame_end+1, frame_by):
                expanded = file_path % i
                file_paths.append( expanded )
        else: 
            # find out the number of #'s in the path
            padding = len( file_path[file_path.index('#'):file_path.rindex('#')] )+1

            for i in range(frame_start, frame_end+1, frame_by):
                expanded = file_path.replace( '#'*padding, str(i).zfill(padding) )
                file_paths.append(expanded)

        return file_paths
    #
    # Checkin/out methods
    #
    def create_snapshot(my, search_key, context, snapshot_type="file",
            description="No description", is_current=True, level_key=None,
            is_revision=False, triggers=True):
        '''API Function: create_snapshot(search_key, context, snapshot_type="file", description="No description", is_current=True, level_key=None, is_revision=False, triggers=True )
        Create an empty snapshot
        
        @param:
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin

        @keyparam:
        snapshot_type - [optional] descibes what kind of a snapshot this is.
            More information about a snapshot type can be found in the
            prod/snapshot_type sobject
        description - [optional] optional description for this checkin
        is_current - flag to determine if this checkin is to be set as current
        is_revision - flag to set this as a revision instead of a version
        level_key - the unique identifier of the level that this
            is to be checked into
        triggers - boolean to fire triggers on insert

        @return:
        dictionary - representation of the snapshot created for this checkin
        '''
        return my.server.create_snapshot(my.ticket, search_key, context, snapshot_type, description, is_current, level_key, is_revision, triggers)
        




    def simple_checkin(my, search_key, context, file_path,
            snapshot_type="file", description="No description",
            use_handoff_dir=False, file_type="main", is_current=True,
            level_key=None, breadcrumb=False, metadata={}, mode='upload',
            is_revision=False, info={} ,
            keep_file_name=False, create_icon=True, 
            checkin_cls='pyasm.checkin.FileCheckin',
            context_index_padding=None,
            checkin_type="strict", source_path=None,
            version=None
    ):
        '''API Function: simple_checkin( search_key, context, file_path, snapshot_type="file", description="No description", use_handoff_dir=False, file_type="main", is_current=True, level_key=None, breadcrumb=False, metadata={}, mode=None, is_revision=False, info={}, keep_file_name=False, create_icon=True, checkin_cls='pyasm.checkin.FileCheckin', context_index_padding=None, checkin_type="strict", source_path=None, version=None )

        
        Simple method that checks in a file.
       
        @param:
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin
        file_path - path of the file that was previously uploaded

        @keyparam:
        snapshot_type - [optional] descibes what kind of a snapshot this is.
            More information about a snapshot type can be found in the
            prod/snapshot_type sobject
        description - [optional] optional description for this checkin
        file_type - [optional] optional description for this file_type
        is_current - flag to determine if this checkin is to be set as current
        level_key - the unique identifier of the level that this
            is to be checked into
        breadcrumb - flag to leave a .snapshot breadcrumb file containing
            information about what happened to a checked in file
        metadata - a dictionary of values that will be stored as metadata
            on the snapshot
        mode - inplace, upload, copy, move
        is_revision - flag to set this as a revision instead of a version
        create_icon - flag to create an icon on checkin
        info - dict of info to pass to the ApiClientCmd
        keep_file_name - keep the original file name
        checkin_cls - checkin class
        context_index_padding - determines the padding used for context
            indexing: ie: design/0001
        checkin_type - auto or strict which controls whether to auto create versionless
        source_path - explicitly give the source path
        version - force a version for this check-in

        @return:
        dictionary - representation of the snapshot created for this checkin
        '''
        mode_options = ['upload', 'uploaded', 'copy', 'move', 'local','inplace']
        if mode:
            if mode not in mode_options:
                raise TacticApiException('Mode must be in %s' % mode_options)

            if mode == 'upload':
                my.upload_file(file_path)
            elif mode == 'uploaded':
                # remap file path: this mode is only used locally.
                from pyasm.common import Environment
                upload_dir = Environment.get_upload_dir()
                file_path = "%s/%s" % (upload_dir, file_path)
            elif mode in ['copy', 'move']:
                handoff_dir = my.get_handoff_dir()
                use_handoff_dir = True
                # make sure that handoff dir is empty
                try:
                    shutil.rmtree(handoff_dir)
                    os.makedirs(handoff_dir)
                    os.chmod(handoff_dir, 0777)
                except OSError, e:
                    sys.stderr.write("WARNING: could not cleanup handoff directory [%s]: %s" % (handoff_dir, e.__str__()))


                # copy or move the tree
                basename = os.path.basename(file_path)

                if mode == 'move':
                    
                    shutil.move(file_path, "%s/%s" % (handoff_dir, basename))
                    mode = 'create'
                elif mode == 'copy':
                    shutil.copy(file_path, "%s/%s" % (handoff_dir, basename))
                    # it moves to repo from handoff dir later
                    mode = 'create'

            elif mode in ['local']:
                # do nothing
                pass

        # check in the file to the server
       
        snapshot = my.server.simple_checkin(my.ticket, search_key, context, file_path, snapshot_type, description, use_handoff_dir, file_type, is_current, level_key, metadata, mode, is_revision, info, keep_file_name, create_icon, checkin_cls, context_index_padding, checkin_type, source_path, version)

        if mode == 'local':
            # get the naming conventions and move the file to the local repo
            files = my.server.eval(my.ticket, "@SOBJECT(sthpw/file)", snapshot)

            # FIXME: this only works on the python implementation .. should
            # use JSON
            files = eval(files)

            # TODO: maybe cache this??
            base_dirs = my.server.get_base_dirs(my.ticket)
            if os.name == 'nt':
                client_repo_dir = base_dirs.get("win32_local_repo_dir")
            else:
                client_repo_dir = base_dirs.get("linux_local_repo_dir")

            if not client_repo_dir:
                raise TacticApiException('No local_repo_dir defined in server config file')


            for file in files:
                rel_path = "%s/%s" %( file.get('relative_dir'), file.get('file_name'))
                repo_path = "%s/%s" % (client_repo_dir, rel_path)
                repo_dir = os.path.dirname(repo_path)
                if not os.path.exists(repo_dir):
                    os.makedirs(repo_dir)
                basename = os.path.basename(repo_path)
                dirname = os.path.dirname(repo_path)
                temp_repo_path = "%s/.%s.temp" % (dirname, basename)
                shutil.copy(file_path, temp_repo_path)
                shutil.move(temp_repo_path, repo_path)



        # leave a breadcrumb
        if breadcrumb:
            snapshot_code = snapshot.get('code')
            full_snapshot_xml = my.get_full_snapshot_xml(snapshot_code)

            snapshot_path = "%s.snapshot" % file_path
            file = open(snapshot_path, 'wb')
            file.write(full_snapshot_xml)
            file.close()

        return snapshot


    def group_checkin(my, search_key, context, file_path, file_range, snapshot_type="sequence", description="", file_type='main', metadata={}, mode=None, is_revision=False , info={} ):
        '''API Function: group_checkin(search_key, context, file_path, file_range, snapshot_type="sequence", description="", file_type='main', metadata={}, mode=None, is_revision=False, info={} )

        Check in a range of files.  A range of file is defined as any group
        of files that have some sequence of numbers grouping them together.
        An example of this includes a range frames that are rendered.

        Although it is possible to add each frame in a range using add_file,
        adding them as as sequence is lightweight, often significantly reducing
        the number of database entries required.  Also, it is understood that
        test files form a range of related files, so that other optimizations
        and manipulations can be operated on these files accordingly.

       
        @param:
        search_key - a unique identifier key representing an sobject
        file_path - expression for file range: ./blah.####.jpg
        file_type - the typ of file this is checked in as. Default = 'main'
        file_range - string describing range of frames in the form '1-5/1'

        @keyparam:
        snapshot_type - type of snapshot this checkin will have
        description - description related to this checkin
        file_type - the type of file that will be associated with this group
        metadata - add metadata to snapshot
        mode - determines whether the files passed in should be copied, moved
            or uploaded.  By default, this is a manual process (for backwards
            compatibility)
        is_revision - flag to set this as a revision instead of a version
        info - dict of info to pass to the ApiClientCmd

        @return:
        dictionary - snapshot
        '''
        mode_options = ['upload', 'copy', 'move', 'inplace']
        if mode:
            if mode not in mode_options:
                raise TacticApiException('Mode must be in %s' % mode_options)

            # brute force method
            
            if mode == 'move':
                handoff_dir = my.get_handoff_dir()
                expanded_paths = my._expand_paths(file_path, file_range)
                for path in expanded_paths:
                    basename = os.path.basename(path)
                    shutil.move(path, '%s/%s' %(handoff_dir, basename))
                use_handoff_dir = True
                mode = 'create'
            elif mode == 'copy':
                handoff_dir = my.get_handoff_dir()
                expanded_paths = my._expand_paths(file_path, file_range)
                for path in expanded_paths:
                    basename = os.path.basename(path)
                    shutil.copy(path, '%s/%s' %(handoff_dir, basename))
                use_handoff_dir = True
                # it moves to repo from handoff dir later
                mode = 'create'
            elif mode == 'upload':
                expanded_paths = my._expand_paths(file_path, file_range)
                for path in expanded_paths:
                    my.upload_file(path)
                use_handoff_dir = False
            elif mode == 'inplace':
                use_handoff_dir = False

                # get the absolute path
                file_path = os.path.abspath(file_path)


        return my.server.group_checkin(my.ticket, search_key, context, file_path, file_range, snapshot_type, description, file_type, metadata, mode, is_revision, info )



    def directory_checkin(my, search_key, context, dir, snapshot_type="directory", description="No description", file_type='main', is_current=True, level_key=None, metadata={}, mode="copy", is_revision=False, checkin_type='strict'):
        '''API Function: directory_checkin(search_key, context, dir, snapshot_type="directory", description="No description", file_type='main', is_current=True, level_key=None, metadata={}, mode="copy", is_revision=False, checkin_type="strict")

        Check in a directory of files.  This informs TACTIC to treat the 
        entire directory as single entity without regard to the structure
        of the contents.  TACTIC will not know about the individual files
        and the directory hierarchy within the base directory and it it left
        up to the and external program to intepret and understand this.

        This is often used when logic on the exact file structure exists in
        some external source outside of TACTIC and it is deemed too complicated
        to map this into TACTIC's snapshot definition.

        @param:
        search_key - a unique identifier key representing an sobject
        dir - the directory that needs to be checked in

        @keyparam:
        snapshot_type - type of snapshot this checkin will have
        description - description related to this checkin
        file_type - the type of file that will be associated with this group
        is_current - makes this snapshot current
        level_key - the search key of the level if used
        metadata - add metadata to snapshot
        mode - determines whether the files passed in should be copied, moved
            or uploaded.  By default, this is 'copy'
        is_revision - flag to set this as a revision instead of a version
        checkin_type - auto or strict which controls whether to auto create versionless

        @return:
        dictionary - snapshot 
        '''
        if mode not in ['copy', 'move', 'inplace', 'local']:
            raise TacticApiException('mode must be either [move] or [copy]')

        handoff_dir = my.get_handoff_dir()
        # make sure that handoff dir is empty
        try:
            shutil.rmtree(handoff_dir)
            os.makedirs(handoff_dir)
            os.chmod(handoff_dir, 0777)
        except OSError, e:
            sys.stderr.write("WARNING: could not cleanup handoff directory [%s]: %s" % (handoff_dir, e.__str__()))

        # strip the trailing / or \ if any
        m = re.match(r'(.*)([/|\\]$)', dir)
        if m:
            dir = m.groups()[0]
        
        # copy or move the tree to the handoff directory
        basename = os.path.basename(dir)

        if mode == 'move':
            shutil.move(dir, "%s/%s" % (handoff_dir, basename))
            mode = 'create'
        elif mode == 'copy':
            shutil.copytree(dir, "%s/%s" % (handoff_dir, basename))
            # it moves to repo from handoff dir later
            mode = 'create'

        use_handoff_dir = True


        # some default data
        info = {}
        keep_file_name = False
        create_icon = False
        checkin_cls = "pyasm.checkin.FileCheckin"
        context_index_padding = None
        source_path = None
        version = None

        snapshot = my.server.simple_checkin(my.ticket, search_key, context,
            dir, snapshot_type, description, use_handoff_dir, file_type,
            is_current, level_key, metadata, mode, is_revision, info, keep_file_name, create_icon, \
                checkin_cls, context_index_padding, checkin_type, source_path, version)

        if mode == 'local':
            # get the naming conventions and move the file to the local repo
            files = my.server.eval(my.ticket, "@SOBJECT(sthpw/file)", snapshot)

            # FIXME: this only works on the python implementation
            files = eval(files)
            for file in files:
                rel_path = "%s/%s" %( file.get('relative_dir'), file.get('file_name'))
                base_dirs = my.server.get_base_dirs(my.ticket)
                if os.name == 'nt':
                    client_repo_dir = base_dirs.get("win32_local_base_dir")
                else:
                    client_repo_dir = base_dirs.get("linux_local_base_dir")

                repo_path = "%s/%s" % (client_repo_dir, rel_path)
                repo_dir = os.path.dirname(repo_path)
                if not os.path.exists(repo_dir):
                    os.makedirs(repo_dir)
                shutil.copytree(dir,repo_path)

        return snapshot

 



    def add_dependency(my, snapshot_code, file_path, type='ref', tag='main'):
        '''API Function: add_dependency(snapshot_code, file_path, type='ref')
       
        Append a dependency referent to an existing check-in.
        All files are uniquely containe by a particular snapshot.  Presently,
        this method does a reverse lookup by file name.  This assumes that
        the filename is unique within the system, so it is not recommended
        unless it is known that naming conventions will produce unique
        file names for every this particular file.  If this is not the
        case, it is recommended that add_dependency_by_code() is used.
       
        @param:
        snapshot_code - the unique code identifier of a snapshot
        file_path - the path of the dependent file.  This function is able
            reverse map the file_path to the appropriate snapshot

        @keyparam:
        type - type of dependency.  Values include 'ref' and 'input_ref'
            ref = hierarchical reference:   ie A contains B
            input_ref = input reference:    ie: A was used to create B
        tag - a tagged keyword can be added to a dependency to categorize
            the different dependencies that exist in a snapshot

        @return:
        dictionary - the resulting snapshot
        '''
        return my.server.add_dependency(my.ticket, snapshot_code, file_path, type, tag)

    def add_dependency_by_code(my, to_snapshot_code, from_snapshot_code, type='ref', tag='main'):
        '''API Function: add_dependency_by_code(to_snapshot_code, from_snapshot_code, type='ref')

        Append a dependency reference to an existing checkin.  This dependency
        is used to connect various checkins together creating a separate
        dependency tree for each checkin.
       
        @param:
        to_snapshot_code: the snapshot code which the dependency will be
            connected to
        from_snapshot_code: the snapshot code which the dependency will be
            connected from
        type - type of dependency.  Values include 'ref' and 'input_ref'
            ref = hierarchical reference:   ie A contains B
            input_ref - input reference:    ie: A was used to create B
        tag - a tagged keyword can be added to a dependency to categorize
            the different dependencies that exist in a snapshot

        @return:
        dictionary - the resulting snapshot
        '''
        return my.server.add_dependency_by_code(my.ticket, to_snapshot_code, from_snapshot_code, type, tag)


    def add_file(my, snapshot_code, file_path, file_type='main', use_handoff_dir=False, mode=None, create_icon=False, dir_naming='', file_naming='', checkin_type='strict'):
        '''API Function: add_file(snapshot_code, file_path, file_type='main', use_handoff_dir=False, mode=None, create_icon=False)
        Add a file to an already existing snapshot.  This method is used in
        piecewise checkins.  A blank snapshot can be created using
        create_snapshot().  This method can then be used to successively
        add files to the snapshot.

        In order to check  in the file, the server will need to have access
        to these files.  There are a number of ways of getting the files
        to the server.  When using copy or move mode, the files are either
        copied or moved to the "handoff_dir".  This directory
        is an agreed upon directory in which to handoff the files to the
        server.  This mode is generally used for checking in user files.
        For heavy bandwidth checkins, it is recommended to user preallocated
        checkins.

        @param:
        snapshot_code - the unique code identifier of a snapshot
        file_path - path of the file to add to the snapshot.
            Optional: this can also be an array to add multiple files at once.
            This has much faster performance that adding one file at a time.
            Also, note that in this case, file_types must be an array
            of equal size.
            

        @keyparam:
        file_type - type of the file to be added.
            Optional: this can also be an array.  See file_path argument
            for more information.
        use_handoff_dir - DEPRECATED: (use mode arg) use handoff dir to checkin
            file.  The handoff dir is an agreed upon directory between the
            client and server to transfer files.
        mode - upload|copy|move|manual|inplace - determine the protocol which delievers
            the file to the server.
        create_icon - (True|False) determine whether to create an icon for
            this appended file.  Only 1 icon should be created for each
            snapshot.
        dir_naming - explicitly set a dir_naming expression to use
        file_naming - explicitly set a file_naming expression to use
        checkin_type - auto or strict which controls whether to auto create versionless and adopt some default dir/file naming

        @return:
        dictionary - the resulting snapshot

        @example:
        This will create a blank model snapshot for character chr001 and
        add a file
        [code]
        search_type = 'prod/asset'
        code = 'chr001'
        search_key = server.build_search_type(search_type, code)
        context = 'model'
        path = "./my_model.ma"

        snapshot = server.create_snapshot(search_key, context)
        server.add_file( snapshot.get('code'), path )
        [/code]

        Different files should be separated by file type.  For example,
        to check in both a maya and houdin file in the same snapshot:
        [code]
        maya_path = "./my_model.ma"
        houdini_path = "./my_model.hip"

        server.add_file( snapshot_code, maya_path, file_type='maya' )
        server.add_file( snapshot_code, houdini_path, file_type='houdini' )
        [/code]

        To transfer files by uploading (using http protocol):
        [code]
        server.add_file( snapshot_code, maya_path, mode='upload' )
        [/code]

        To create an icon for this file
        [code]
        path = 'image.jpg'
        server.add_file( snapshot_code, path, mode='upload', create_icon=True )
        [/code]

        To add multiple files at once
        [code]
        file_paths = [maya_path, houdini_path]
        file_types ['maya', 'houdini']
        server.add_file( snapshot_code, file_paths, file_types=file_types, mode='upload')
        [/code]

        '''
        if type(file_path) != types.ListType:
            file_paths = [file_path]
        else:
            file_paths = file_path
        if type(file_type) != types.ListType:
            file_types = [file_type]
        else:
            file_types = file_type

        mode_options = ['upload', 'copy', 'move', 'preallocate','inplace']
        if mode:
            if mode in ['copy', 'move']:
                handoff_dir = my.get_handoff_dir()
                use_handoff_dir = True
                # make sure that handoff dir is empty
                try:
                    shutil.rmtree(handoff_dir)
                    os.makedirs(handoff_dir)
                except OSError, e:
                    sys.stderr.write("WARNING: could not cleanup handoff directory [%s]: %s" % (handoff_dir, e.__str__()))

            for i, file_path in enumerate(file_paths):
                file_type = file_types[i]
                
                if mode not in mode_options:
                    raise TacticApiException('Mode must be in %s' % mode_options)

                if mode == 'upload':
                    my.upload_file(file_path)
                    use_handoff_dir = False
                elif mode in ['copy', 'move']:
                    # copy or move the tree
                    basename = os.path.basename(file_path)
                    if mode == 'move':
                        shutil.move(file_path, "%s/%s" % (handoff_dir, basename))
                    elif mode == 'copy':
                        shutil.copy(file_path, "%s/%s" % (handoff_dir, basename))
                    mode = 'create'

        return my.server.add_file(my.ticket, snapshot_code, file_paths, file_types, use_handoff_dir, mode, create_icon, dir_naming, file_naming, checkin_type)


    def remove_file(my, snapshot_code, file_type):
        return my.server.remove_file(my.ticket, snapshot_code, file_type)
        


    def add_group(my, snapshot_code, file_path, file_type, file_range, use_handoff_dir=False, mode=None):
        '''API Function: add_group(snapshot_code, file_path, file_type, file_range, use_handoff_dir=False, mode=None)
        Add a file range to an already existing snapshot

        @param:
        snapshot_code - the unique code identifier of a snapshot
        file_path - path of the file to add to the snapshot
        file_type - type of the file to be added.
        file_range - range with format s-e/b

        @keyparam:
        use_handoff_dir - use handoff dir to checkin file
        mode - one of 'copy','move','preallocate'

        @return:
        dictionary - the resulting snapshot
        '''

        mode_options = ['upload', 'copy', 'move', 'preallocate']
        if mode:
            if mode not in mode_options:
                raise TacticApiException('Mode must be in %s' % mode_options)

            #dir = os.path.dirname(file_path)
            handoff_dir = my.get_handoff_dir()
            if mode == 'move':
                expanded_paths = my._expand_paths(file_path, file_range)
                for path in expanded_paths:
                    basename = os.path.basename(path)
                    shutil.move(path, '%s/%s' %(handoff_dir, basename))
                use_handoff_dir = True
                mode = 'create'
            elif mode == 'copy':
                expanded_paths = my._expand_paths(file_path, file_range)
                for path in expanded_paths:
                    basename = os.path.basename(path)
                    shutil.copy(path, '%s/%s' %(handoff_dir, basename))
                use_handoff_dir = True
                mode = 'create'
            elif mode == 'upload':
                my.upload_group(file_path, file_range)
                use_handoff_dir = False
            elif mode == 'preallocate':
                use_handoff_dir = True

        return my.server.add_group(my.ticket, snapshot_code, file_path, file_type, file_range, use_handoff_dir, mode)



    def add_directory(my, snapshot_code, dir, file_type='main', mode="copy", dir_naming='', file_naming=''):
        '''API Function: add_directory(snapshot_code, dir, file_type='main', mode="copy", dir_naming='', file_naming='')
        Add a full directory to an already existing checkin.
        This informs TACTIC to treat the entire directory as single entity
        without regard to the structure of the contents.  TACTIC will not
        know about the individual files and the directory hierarchy within
        the base directory and it it left up to the and external program
        to intepret and understand this.

        This is often used when logic on the exact file structure exists in
        some external source outside of TACTIC and it is deemed to complictaed
        to map this into TACTIC's snapshot definition.

        @param:
        snapshot_code - a unique identifier key representing an sobject
        dir - the directory that needs to be checked in

        @keyparam:
        file_type - file type is used more as snapshot type here
        mode - copy, move, preallocate, manual, inplace
        dir_naming - explicitly set a dir_naming expression to use
        file_naming - explicitly set a file_naming expression to use

        @return:
        dictionary - snapshot

        @example:
        This will create a new snapshot for a search_key and add a directory using manual mode
        
        [code]
        dir = 'C:/images'
        handoff_dir = my.server.get_handoff_dir()
        shutil.copytree('%s/subfolder' %dir, '%s/images/subfolder' %handoff_dir)

        snapshot_dict = my.server.create_snapshot(search_key, context='render')
        snapshot_code = snapshot_dict.get('code')
        my.server.add_directory(snapshot_code, dir, file_type='dir', mode='manual')
        [/code]
        '''
        if mode not in ['copy', 'move', 'preallocate', 'manual', 'inplace']:
            raise TacticApiException('Mode must be one of [move, copy, preallocate]')

        if mode in ['copy', 'move']:
            handoff_dir = my.get_handoff_dir()
            # make sure that handoff dir is empty
            try:
                shutil.rmtree(handoff_dir)
                os.makedirs(handoff_dir)
            except OSError, e:
                sys.stderr.write("WARNING: could not cleanup handoff directory [%s]: %s" % (handoff_dir, e.__str__()))

            # copy or move the tree
            basename = os.path.basename(dir)

            if mode == 'move':
                shutil.move(dir, "%s/%s" % (handoff_dir, basename))
            elif mode == 'copy':
                shutil.copytree(dir, "%s/%s" % (handoff_dir, basename))

            mode = 'create'

        use_handoff_dir = True
        create_icon = False
        return my.server.add_file(my.ticket, snapshot_code, dir, file_type, use_handoff_dir, mode, create_icon, dir_naming, file_naming )
 




    def checkout(my, search_key, context="publish", version=-1, file_type='main', to_dir=".", level_key=None, to_sandbox_dir=False, mode='copy'):
        '''API Function: checkout(search_key, context, version=-1, file_type='main', dir='', level_key=None, to_sandbox_dir=False, mode='copy')
        Check out files defined in a snapshot from the repository.  This
        will copy files to a particular directory so that a user can work
        on them.

        @param:
            search_key - a unique identifier key representing an sobject
            context - context of the snapshot

        @keyparam:
            version - version of the snapshot
            file_type - file type defaults to 'main'. If set to '*', all paths are checked out
            level_key - the unique identifier of the level in the form of a search key
            to_dir - destination directory defaults to '.'
            to_sandbox_dir - (True|False) destination directory defaults to
                sandbox_dir (overrides "to_dir" arg)

            mode - (copy|download) - determines the protocol that will be used
                to copy the files to the destination location

        @return:
            list - a list of paths that were checked out

        '''
        if not os.path.isdir(to_dir):
            raise TacticApiException("[%s] does not exist or is not a directory" % to_dir)

        to_dir = to_dir.replace("\\","/")
        #repo_paths = my.server.checkout(my.ticket, search_key, context, version, file_type, level_key)
        paths = my.server.checkout(my.ticket, search_key, context, version, file_type, level_key)

        client_lib_paths = paths['client_lib_paths']
        sandbox_paths = paths['sandbox_paths']
        web_paths = paths['web_paths']


        to_paths = []
        for i, client_lib_path in enumerate(client_lib_paths):
            if to_sandbox_dir:
                to_path = sandbox_paths[i]
                filename = os.path.basename(to_path)
            else:
                filename = os.path.basename(client_lib_path)
                to_path = "%s/%s" % (to_dir, filename)

            to_paths.append(to_path)

            # copy the file from the repo
            to_dir = os.path.dirname(to_path)
            if not os.path.exists(to_dir):
                os.makedirs(to_dir)

            if mode == 'copy':
                if os.path.exists(client_lib_path):
                    if os.path.isdir(client_lib_path):
                        shutil.copytree(client_lib_path, to_path)
                    else:
                        shutil.copy(client_lib_path, to_path)
                else:
                    raise TacticApiException("Path [%s] does not exist" % client_lib_path)

            elif mode == 'download':
                web_path = web_paths[i]
                my.download(web_path, to_dir=to_dir, filename=filename)
            else:
                raise TacticApiException("Checkout mode [%s] not supported" % mode)

        return to_paths

 
    def lock_sobject(my, search_key, context):
        '''Locks the context for checking in and out.  Locking a context
        prevents the ability to checkout or checkin to that context for a
        particular sobject.

        @params
        search_key - the search key of the sobject
        context - the context that will be blocked

        @return
        None
        '''
        return my.server.lock_sobject(my.ticket, search_key, context)

 
    def unlock_sobject(my, search_key, context):
        '''Unocks the context for checking in and out.  Locking a context
        prevents the ability to checkout or checkin to that context for a
        particular sobject.

        @params
        search_key - the search key of the sobject
        context - the context that will be unblocked

        @return
        None
 
        '''
        return my.server.unlock_sobject(my.ticket, search_key, context)



    def query_snapshots(my, filters=None, columns=None, order_bys=[], show_retired=False, limit=None, offset=None, single=False, include_paths=False, include_full_xml=False, include_paths_dict=False, include_parent=False, include_files=False):
        '''API Function:  query_snapshots(filters=None, columns=None, order_bys=[], show_retired=False, limit=None, offset=None, single=False, include_paths=False, include_full_xml=False, include_paths_dict=False, include_parent=False, include_files=False)

        thin wrapper around query, but is specific to querying snapshots
        with some useful included flags that are specific to snapshots

        @params:
        ticket - authentication ticket
        filters - (optional) an array of filters to alter the search
        columns - (optional) an array of columns whose values should be
                    retrieved
        order_bys - (optional) an array of order_by to alter the search
        show_retired - (optional) - sets whether retired sobjects are also
                    returned
        limit - sets the maximum number of results returned
        single - returns a single sobject that is not wrapped up in an array
        include_paths - flag to specify whether to include a __paths__ property
            containing a list of all paths in the dependent snapshots
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            dependent snapshots
        include_full_xml - flag to return the full xml definition of a snapshot
        include_parent - includes all of the parent attributes in a __parent__ dictionary
        include_files - includes all of the file objects referenced in the
                    snapshots

        @return:
        list of snapshots
        '''
        return my.server.query_snapshots(my.ticket, filters, columns, order_bys, show_retired, limit, offset, single, include_paths, include_full_xml, include_paths_dict, include_parent, include_files)



    def get_snapshot(my, search_key, context="publish", version='-1', revision=None, level_key=None, include_paths=False, include_full_xml=False, include_paths_dict=False, include_files=False, include_web_paths_dict=False, versionless=False, process=None):
        '''API Function:  get_snapshot(search_key, context="publish", version='-1', level_key=None, include_paths=False, include_full_xml=False, include_paths_dict=False, include_files=False, include_web_paths_dict=False, versionless=False)

        Method to retrieve an sobject's snapshot
        Retrieve the latest snapshot
        
        @param:
        search_key - unique identifier of sobject whose snapshot we are
                looking for

        @keyparam:
        process - the process of the snapshot
        context - the context of the snapshot
        version - snapshot version
        revision - snapshot revision
        level_key - the unique identifier of the level in the form of a search key
        include_paths - flag to include a list of paths to the files in this
            snapshot.
        include_full_xml - whether to include full xml in the return
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            dependent snapshots
        include_web_paths_dict - flag to specify whether to include a
            __web_paths_dict__ property containing a dict of all web paths in
            the returned snapshots

        include_files - includes all of the file objects referenced in the
            snapshots
        versionless - boolean to return the versionless snapshot, which takes a version of -1 (latest)  or 0 (current)

        @return:
        dictionary - the resulting snapshot

        @example:
        [code]
            search_key = 'prod/asset?project=sample3d&code=chr001'
            snapshot = server.get_snapshot(search_key, context='icon', include_files=True)
        [/code]

        [code]
            # get the versionless snapshot
            search_key = 'prod/asset?project=sample3d&code=chr001'
            snapshot = server.get_snapshot(search_key, context='anim', include_paths_dict=True, versionless=True)
        [/code]
        '''
        return my.server.get_snapshot(my.ticket, search_key, context, version, revision, level_key, include_paths, include_full_xml, include_paths_dict, include_files, include_web_paths_dict, versionless, process)




    def get_full_snapshot_xml(my, snapshot_code):
        '''API Function: get_full_snapshot_xml(snapshot_code)
        
        Retrieve a full snapshot xml.  This snapshot definition
        contains all the information about a snapshot in xml
        
        @param:
        snapshot_code - unique code of snapshot

        @return:
        string - the resulting snapshot xml
        '''
        return my.server.get_full_snapshot_xml(my.ticket, snapshot_code)


    def set_current_snapshot(my, snapshot_code):
        '''API Function: set_current_snapshot(snapshot_code)

        Set this snapshot as a "current" snapshot
        
        @param:
        snapshot_code - unique code of snapshot

        @return:
        string - the resulting snapshot xml
        '''
        return my.server.set_current_snapshot(my.ticket, snapshot_code)


    def get_dependencies(my, snapshot_code, mode='explicit', tag='main', include_paths=False, include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        '''API Function: get_dependencies(snapshot_code, mode='explicit', tag='main', include_paths=False, include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        
        Return the dependent snapshots of a certain tag

        @params:
        snapshot_code - unique code of a snapshot

        @keyparams:
        mode - explict (get version as defined in snapshot)
             - latest
             - current
        tag - retrieve only dependencies that have this named tag
        include_paths - flag to specify whether to include a __paths__ property
            containing all of the paths in the dependent snapshots
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            dependent snapshots
        include_files - includes all of the file objects referenced in the
            snapshots
        repo_mode - client_repo, web, lib, relative
        show_retired - defaults to False so that it doesn't show retired dependencies


        @return:
        a list of snapshots
        '''
        return my.server.get_dependencies(my.ticket, snapshot_code, mode, tag, include_paths, include_paths_dict, include_files, repo_mode, show_retired)


    def get_all_dependencies(my, snapshot_code, mode='explicit', type='ref', include_paths=False,  include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        '''API Function: get_all_dependencies(snapshot_code, mode='explicit', type='ref', include_paths=False, include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        
        Retrieve the latest dependent snapshots of the given snapshot
        
        @param:
        snapshot_code - the unique code of the snapshot

        @keyparam:
        mode - explicit (get version as defined in snapshot)
             - latest
             - current

        type - one of ref or input_ref
        include_paths - flag to specify whether to include a __paths__ property
            containing all of the paths in the dependent snapshots
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            dependent snapshots
        include_files - includes all of the file objects referenced in the
            snapshots
        repo_mode - client_repo, web, lib, relative
        show_retired - defaults to False so that it doesn't show retired dependencies

        @return:
        list - snapshots
        '''
        return my.server.get_all_dependencies(my.ticket, snapshot_code, mode, type,\
                include_paths, include_paths_dict, include_files, repo_mode, show_retired)



    #
    # Task methods
    #
    def create_task(my, search_key, process="publish", subcontext=None, description=None, bid_start_date=None, bid_end_date=None, bid_duration=None, assigned=None):
        '''API Function:  create_task(search_key, process="publish", subcontext=None, description=None, bid_start_date=None, bid_end_date=None, bid_duration=None, assigned=None)

        Create a task for a particular sobject

        @param:
        search_key - the key identifying a type of sobject as registered in
                    the search_type table.
        
        @keyparam:
        process - process that this task belongs to
        subcontext - the subcontext of the process (context = procsss/subcontext)
        description - detailed description of the task
        bid_start_date - the expected start date for this task
        bid_end_date - the expected end date for this task
        bid_duration - the expected duration for this task
        assigned - the user assigned to this task

        @return:
        dictionary - task created
        ''' 

        return my.server.create_task(my.ticket, search_key, process, subcontext, description, bid_start_date, bid_end_date, bid_duration, assigned)



    def add_initial_tasks(my, search_key, pipeline_code=None, processes=[], skip_duplicate=True, offset=0):
        '''API Function: add_initial_tasks(search_key, pipeline_code=None, processes=[], skip_duplicate=True, offset=0)
        
        Add initial tasks to an sobject

        @param:
        search_key - the key identifying a type of sobject as registered in
                    the search_type table.

        
        @keyparam:
        pipeline_code - override the sobject's pipeline and use this one instead
        processes - create tasks for the given list of processes
        skip_duplicate - boolean to skip duplicated task
        offset - a number to offset the start date from today's date

        @return:
        list - tasks created
        '''
        return my.server.add_initial_tasks(my.ticket, search_key, pipeline_code, processes, skip_duplicate, offset)



    def get_input_tasks(my, search_key):
        '''API Function: get_input_tasks(search_key)
        
        Get the input tasks of a task based on the pipeline
        associated with the sobject parent of the task

        @param:
        search_key - the key identifying an sobject as registered in
                    the search_type table.
 
        @return:
        list of input tasks
        '''
        return my.server.get_input_tasks(my.ticket, search_key)



    def get_output_tasks(my, search_key):
        '''API Function: get_output_tasks(search_key)
        
        Get the output tasks of a task based on the pipeline
        associated with the sobject parent of the task

        @param:
        search_key - the key identifying an sobject as registered in
                    the search_type table.
 
        @return:
        list of output tasks
        '''
        return my.server.get_input_tasks(my.ticket, search_key)




    #
    # Note methods
    #
    def create_note(my, search_key, note, process="publish", subcontext=None, user=None):
        ''''API Function: create_note(search_key, note, process="publish", subcontext=None, user=None)

        Add a note for a particular sobject

        @params:
        search_key - the key identifying a type of sobject as registered in
                    the search_type table.
        note - detailed description of the task
        process - process that this task belongs to
        subcontext - the subcontex of the process (context = procsss/subcontext
        user - the user the note is attached to

        @return
        note that was created
        ''' 
        return my.server.create_note(my.ticket, search_key, process, subcontext, note, user)


    #
    # Pipeline methods
    #
    def get_pipeline_xml(my, search_key):
        '''API Function: get_pipeline_xml(search_key)
        DEPRECATED: use get_pipeline_xml_info()

        Retrieve the pipeline of a specific sobject.  The pipeline
        return is an xml document and an optional dictionary of information.
       
        @param:
        search_key - a unique identifier key representing an sobject

        @return:
        dictionary - xml and the optional hierarachy info
        '''
        return my.server.get_pipeline_xml(my.ticket, search_key)

    def get_pipeline_processes(my, search_key, recurse=False):
        '''API Function: get_pipeline_processes(search_key, recurse=False)
        DEPRECATED: use get_pipeline_processes_info()

        Retrieve the pipeline processes information of a specific sobject.
       
        @param:
        search_key - a unique identifier key representing an sobject
        
        @keyparams:
        recurse - boolean to control whether to display sub pipeline processes
        
        @return:
        list - process names of the pipeline 
        '''
        return my.server.get_pipeline_processes(my.ticket, search_key, recurse)

    def get_pipeline_xml_info(my, search_key, include_hierarchy=False):
        '''API Function: get_pipeline_xml_info(search_key, include_hierarchy=False)

        Retrieve the pipeline of a specific sobject.  The pipeline
        returned is an xml document and an optional dictionary of information.
       
        @param:
        search_key - a unique identifier key representing an sobject

        @keyparam:
        include_hierarchy - include a list of dictionary with key info on each process of the pipeline

        @return:
        dictionary - xml and the optional hierarachy info
        '''
        return my.server.get_pipeline_xml_info(my.ticket, search_key, include_hierarchy)

    def get_pipeline_processes_info(my, search_key, recurse=False, related_process=None):
        '''API Function: get_pipeline_processes_info(search_key, recurse=False, related_process=None)

        Retrieve the pipeline processes information of a specific sobject. It provides information from the perspective of a particular process if related_process is specified.
       
        @param:
        search_key - a unique identifier key representing an sobject
        
        @keyparams:
        recurse - boolean to control whether to display sub pipeline processes
        related_process - given a process, it shows the input and output processes and contexts
        
        @return:
        dictionary - process names of the pipeline or a dictionary if related_process is specified
        '''
        return my.server.get_pipeline_processes_info(my.ticket, search_key, recurse, related_process)

    def execute_pipeline(my, pipeline_xml, package):
        '''API Function:  execute_pipeline(pipeline_xml, package)

        Spawn an execution of a pipeline as delivered from
        'get_pipeline_xml()'.  The pipeline is a xml document that describes
        a set of processes and their handlers

        @param:
        pipeline_xml - an xml document describing a standard Tactic pipeline.
        package - a dictionary of data delivered to the handlers
        @return:
        instance - a reference to the interpreter
        '''

        # execute the pipeline
        from interpreter import PipelineInterpreter
        interpreter = PipelineInterpreter(pipeline_xml)
        interpreter.set_server(my)
        interpreter.set_package(package)
        interpreter.execute()

        return interpreter


    def commit_session(my, session_xml, pid):
        '''Takes a session xml and commits it.  Also handles transfer to old
        style xml data.  Generally, this is executed through the application
        package: tactic_client_lib/application/common/introspect.py. However,
        this can be done manually if the proper session xml is provided.

        @params
        ticket - authentication ticket
        session_xml - an xml document representing the session. This document
            format is described below

        @return
        session_content object

        The session_xml takes the form:

        <session>
          <ref search_key="prod/shot?project=bar&code=joe" context="model" version="3" revision="2" tactic_node="tactic_joe"/>
        </session>
        '''
        return my.server.commit_session(my.ticket, session_xml, pid)


    #
    # Directory methods
    #
    def get_paths(my, search_key, context="publish", version=-1, file_type='main', level_key=None, single=False, versionless=False):
        '''API Function: get_paths( search_key, context="publish", version=-1, file_type='main', level_key=None, single=False, versionless=False)
        Get paths from an sobject

        @params:
        search_key - a unique identifier key representing an sobject

        @keyparams:
        context - context of the snapshot
        version - version of the snapshot
        file_type - file type defined for the file node in the snapshot
        level_key - the unique identifier of the level that this
            was checked into
        single - If set to True, the first of each path set is returned
        versionless - boolean to return the versionless snapshot, which takes a version of -1 (latest)  or 0 (current)

        @return
        A dictionary of lists representing various paths.  The paths returned
        are as follows:
        - client_lib_paths: all the paths to the repository relative to the client
        - lib_paths: all the paths to the repository relative to the server
        - sandbox_paths: all of the paths mapped to the sandbox
        - web: all of the paths relative to the http server
 

        '''
        return my.server.get_paths(my.ticket, search_key, context, version, file_type, level_key, single, versionless)




    def get_base_dirs(my):
        ''''API Function: get_base_dirs()

        Get all of the base directories defined on the server

        @return:
        dictionary of all the important configured base directories
        with their keys
        '''

        return my.server.get_base_dirs(my.ticket)



    def get_plugin_dir(my, plugin):
        '''API Function: get_plugin_dir(plugin)
        
        Return the web path for the specfied plugin

        @params:
        plugin - plugin name
        
        @return:
        string - the web path for the specified plugin
        '''
        return my.server.get_plugin_dir(my.ticket, plugin)




    def get_handoff_dir(my):
        '''API Function: get_handoff_dir()
        
        Return a temporary path that files can be copied to

        @return:
        string - the directory to copy a file to handoff to TACTIC
        without having to go through http protocol
        '''
        if my.handoff_dir:
            return my.handoff_dir

        handoff_dir = my.server.get_handoff_dir(my.ticket)
        if not os.path.exists(handoff_dir):
            os.makedirs(handoff_dir)

        my.handoff_dir = handoff_dir
        return handoff_dir




    def clear_upload_dir(my):
        '''API Function: clear_upload_dir()
        
        Clear the upload directory to ensure clean checkins
       
        @param:
        None

        @keyparam:
        None

        @return:
        None
        '''
        return my.server.clear_upload_dir(my.ticket)



    def get_client_dir(my, snapshot_code, file_type='main', mode='client_repo'):
        '''API Function: get_client_dir(snapshot_code, file_type='main', mode='client_repo')
        
        Get a dir segment from a snapshot
       
        @param:
        snapshot_code - the unique code of the snapshot

        @keyparam:
        file_type - each file in a snapshot is identified by a file type.
            This parameter specifies which type.  Defaults to 'main'
        mode - Forces the type of folder path returned to use the value from the
            appropriate tactic_<SERVER_OS>-conf.xml configuration file.
            Values include 'lib', 'web', 'local_repo', 'sandbox', 'client_repo', 'relative'
            lib = the NFS asset directory from the server point of view
            web = the http asset directory from the client point of view
            local_repo = the local sync of the TACTIC repository
            sandbox = the local sandbox (work area) designated by TACTIC
            client_repo (default) = the asset directory from the client point of view
            If there is no value for win32_client_repo_dir or linux_client_repo_dir
            in the config, then the value for asset_base_dir will be used instead.
            relative = the relative direcory without any base

        @return:
        string - directory segment for a snapshot and file type

        @example:
        If the tactic_<SERVER_OS>-conf.xml configuration file contains the following:
        [code]
        <win32_client_repo_dir>T:/assets</win32_client_repo_dir>
        [/code]

        and if the call to the method is as follows:
        [code]
        snapshot = server.create_snapshot(search_key, context)
        code = snapshot.get('code')
        server.get_path_from_snapshot(snapshot.get('code'))
        [/code]

        Then, on a Windows client, get_client_dir() will return:
        [code]
        T:/assets/sample3d/asset/chr/chr003/scenes
        [/code]
        
        '''
        return my.server.get_client_dir(my.ticket, snapshot_code, file_type, mode)

    def get_path_from_snapshot(my, snapshot_code, file_type='main', mode='client_repo'):
        '''API Function: get_path_from_snapshot(snapshot_code, file_type='main', mode='client_repo')
        
        Get a full path from a snapshot
       
        @param:
        snapshot_code - the unique code / search_key of the snapshot

        @keyparam:
        file_type - each file in a snapshot is identified by a file type.
            This parameter specifies which type.  Defaults to 'main'
        mode - Forces the type of folder path returned to use the value from the
            appropriate tactic_<SERVER_OS>-conf.xml configuration file.
            Values include 'lib', 'web', 'local_repo', 'sandbox', 'client_repo', 'relative'
            lib = the NFS asset directory from the server point of view
            web = the http asset directory from the client point of view
            local_repo = the local sync of the TACTIC repository
            sandbox = the local sandbox (work area) designated by TACTIC
            client_repo (default) = the asset directory from the client point of view
            If there is no value for win32_client_repo_dir or linux_client_repo_dir
            in the config, then the value for asset_base_dir will be used instead.
            relative = the relative direcory without any base

        @return:
        string - the directory to copy a file to handoff to Tactic without having to
        go through http protocol

        @example:
        If the tactic_<SERVER_OS>-conf.xml configuration file contains the following:
        [code]
        <win32_client_repo_dir>T:/assets</win32_client_repo_dir>
        [/code]

        and if the call to the method is as follows:
        [code]
        snapshot = server.create_snapshot(search_key, context)
        code = snapshot.get('code')
        server.get_path_from_snapshot(snapshot.get('code'))

        # in a trigger
        snapshot_key = my.get_input_value("search_key")
        server.get_path_from_snapshot(snapshot_key)
        [/code]

        Then, on a Windows client, get_path_from_snapshot() will return:
        [code]
        T:/assets/sample3d/asset/chr/chr003/scenes/chr003_rig_v003.txt
        [/code]

        '''
        return my.server.get_path_from_snapshot(my.ticket, snapshot_code, file_type, mode)


    def get_expanded_paths_from_snapshot(my, snapshot_code, file_type='main'):
        '''API Function: get_expanded_paths_from_snapshot(snapshot_code, file_type='main')
        
        Return the expanded path of a snapshot (used for 
        ranges of files)
       
        @param:
        snapshot_code - the unique code of the snapshot

        @keyparam:
        file_type - each file in a snapshot is identified by a file type.
            This parameter specifies which type.  Defaults to 'main'

        @return:
        string - path
        '''
        return my.server.get_expanded_paths_from_snapshot(my.ticket, snapshot_code, file_type)




    def get_all_paths_from_snapshot(my, snapshot_code, mode='client_repo', expand_paths=False, filename_mode='',file_types=[]):
        '''API Function: get_all_paths_from_snapshot(snapshot_code, mode='client_repo', expand_paths=False, filename_mode='')
        
        Get all paths from snapshot
       
        @param:
        snapshot_code - the unique code of the snapshot

        @keyparam:
        mode - forces the type of folder path returned to use the value from the
            appropriate tactic_<SERVER_OS>-conf.xml configuration file.
            Values include 'lib', 'web', 'local_repo', 'sandbox', 'client_repo', 'relative'
            lib = the NFS asset directory from the server point of view
            web = the http asset directory from the client point of view
            local_repo = the local sync of the TACTIC repository
            sandbox = the local sandbox (work area) designated by TACTIC
            client_repo (default) = the asset directory from the client point of view
            If there is no value for win32_client_repo_dir or linux_client_repo_dir
            in the config, then the value for asset_base_dir will be used instead.
            relative = the relative direcory without any base

        expand_paths - expand the paths of a sequence check-in or for a directory check-in, it will list the contents of the directory as well

        filename_mode - source or '', where source reveals the source_path of the check-in
        file_types - list: only return files in snapshot with these types

        @return:
        list - paths
        '''

        return my.server.get_all_paths_from_snapshot(my.ticket, snapshot_code, mode, expand_paths, filename_mode, file_types)


    def get_preallocated_path(my, snapshot_code, file_type='main', file_name='', mkdir=True, protocol='client_repo', ext=''):
        '''API Function: get_preallocated_path(snapshot_code, file_type='main', file_name='', mkdir=True, protocol='client_repo', ext='')
        
        Get the preallocated path for this snapshot.  It assumes that
        this checkin actually exists in the repository and will create virtual
        entities to simulate a checkin.  This method can be used to determine
        where a checkin will go.  However, the snapshot must exist 
        using create_snapshot() or some other method.  For a pure virtual naming
        simulator, use get_virtual_snapshot_path().

        @param:
            snapshot_code - the code of a preallocated snapshot.  This can be
                create by get_snapshot()
        
        @keyparam:
            file_type - the type of file that will be checked in.  Some naming
                conventions make use of this information to separate directories
                for different file types
            file_name - the desired file name of the preallocation.  This information
                may be ignored by the naming convention or it may use this as a
                base for the final file name
            mkdir - an option which determines whether the directory of the
                preallocation should be created
            protocol - It's either client_repo, sandbox, or None. It determines whether the
                path is from a client or server perspective
            ext - force the extension of the file name returned

        @return:
            string - the path where add_file() expects the file to be checked into
        @example:

        it saves time if you get the path and copy it to the final destination first. 

        [code]
        snapshot = my.server.create_snapshot(search_key, context)
        snapshot_code = snapshot.get('code')
        file_name = 'input_file_name.txt'
        orig_path = 'C:/input_file_name.txt'
        path = my.server.get_preallocated_path(snapshot_code, file_type, file_name)

        # the path where it is supposed to go is generated
        new_dir = os.path.dirname(path)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        shutil.copy(orig_path, path)
        my.server.add_file(snapshot_code, path, file_type, mode='preallocate')
        [/code]
           
        '''
        return my.server.get_preallocated_path(my.ticket, snapshot_code, file_type, file_name, mkdir, protocol, ext)




    def get_virtual_snapshot_path(my, search_key, context="publish", snapshot_type="file", level_key=None, file_type='main', file_name='', mkdirs=False, protocol='client_repo', ext=''):
        '''API Function: get_virtual_snapshot_path(search_key, context, snapshot_type="file", level_key=None, file_type='main', file_name='', mkdirs=False, protocol='client_repo', ext='')
        Create a virtual snapshot and returns a path that this snapshot
        would generate through the naming conventions.  This is most useful
        testing naming conventions.

        @param:
        snapshot creation:
        -----------------
            search_key - a unique identifier key representing an sobject
            context - the context of the checkin

        @keyparam:
            snapshot_type - [optional] descibes what kind of a snapshot this is.
                More information about a snapshot type can be found in the
                prod/snapshot_type sobject
            description - [optional] optional description for this checkin
            level_key - the unique identifier of the level that this
                is to be checked into
        
        @keyparam:
        path creation:
        --------------
            file_type - the type of file that will be checked in.  Some naming
                conventions make use of this information to separate directories
                for different file types
            file_name - the desired file name of the preallocation.  This information
                may be ignored by the naming convention or it may use this as a
                base for the final file name
            mkdir - an option which determines whether the directory of the
                preallocation should be created
            protocol - It's either client_repo, sandbox, or None. It determines whether the
                path is from a client or server perspective
            ext - force the extension of the file name returned


        @return:
            string - path as determined by the naming conventions
        '''
        return my.server.get_virtual_snapshot_path(my.ticket, search_key, context, snapshot_type, level_key, file_type, file_name, mkdirs, protocol, ext)



    # NOTE: this is very specific to the Maya tools and can be considered
    # deprecated

    def get_md5_info(my, md5_list, new_paths, parent_code, texture_cls, file_group_dict, project_code, mode):
        '''API Function: get_md5_info(md5_list, texture_codes, new_paths, parent_code, texture_cls, file_group_dict, project_code)
        Get md5 info for a given list of texture paths, mainly returning if this md5 is a match or not
        @param: 
            md5_list - md5_list
            new_paths - list of file_paths
            parent_code - parent code
            texture_cls - Texture or ShotTexture
            file_group_dict - file group dictionary storing all the file groups
            project_code - project_code
                mode - texture matching mode (md5, file_name)

        @return:
            dictionary - a dictionary of path and a subdictionary of is_match, repo_file_code, repo_path, repo_file_range
        '''
        return my.server.get_md5_info(my.ticket, md5_list, new_paths, parent_code, texture_cls, file_group_dict, project_code, mode )

    #
    # UI methods
    #
    def get_widget(my, class_name, args={}, values={}):
        '''API Function: get_widget(class_name, args={}, values={})
        Get a defined widget

        @params:
            class_name - the fully qualified class name of the widget

        @keyparams:
            args - keyword arguments required to create a specific widget
            values - form values that are passed in from the interface

        @return:
            string - html form of the widget

        @example:
        class_name = 'TableLayoutWdg'

        args = {
                'view': 'manage',
                'search_type': 'prod/asset',
               }

        widget = server.get_widget(class_name, args))
        '''
        return my.server.get_widget(my.ticket, class_name, args)



    def class_exists(my, class_path):
        '''determines if a class exists on the server
       
        @params
        class_path - fully qualified python class path

        @return
        boolean: true if class exists and can be seen
        '''
        return my.server.class_exists(my.ticket, class_path)



    def execute_python_script(my, script_path, kwargs={}):
        '''API Function: execute_python_script(script_path, kwargs) 
        Execute a python script defined in Script Editor

        @param:
            script_path - script path in Script Editor, e.g. test/eval_sobj
        @keyparam:
            kwargs  - keyword arguments for this script

        @return:
            dictionary - returned data structure
        '''
        return my.server.execute_python_script(my.ticket, script_path, kwargs)


    def execute_cmd(my, class_name, args={}, values={}):
        '''API Function: execute_cmd(class_name, args={}, values={}) 
        Execute a command

        @param:
            class_name - the fully qualified class name of the widget
            
        @keyparam:
            args - keyword arguments required to create a specific widget
            values - form values that are passed in from the interface

        @return:
            string - description of command
        '''
        return my.server.execute_cmd(my.ticket, class_name, args, values)



    def execute_transaction(my, transaction_xml, file_mode=None):
        '''Run a tactic transaction a defined by the instructions in the
        given transaction xml.  The format of the xml is identical to
        the format of how transactions are stored internally
       
        @params
        ticket - authentication ticket
        transaction_xml - transction instructions

        @return
        None

        @usage
        transaction_xml = """<?xml version='1.0' encoding='UTF-8'?>
         <transaction>
           <sobject search_type="project/asset?project=gbs"
                search_code="shot01" action="update">
             <column name="description" from="" to="Big Money Shot"/>
           </sobject>
         </transaction>
         """

        server.execute_transaction(transaction_xml)

        '''
        return my.server.execute_transaction(my.ticket, transaction_xml, file_mode)




    #
    # Widget Config methods
    #
    def set_config_definition(my, search_type, element_name, config_xml="", login=None):
        '''API Function: set_config_definition(search_type, element_name, config_xml="", login=None)
        Set the widget configuration definition for an element

        @param:
            search_type - search type that this config relates to
            element_name - name of the element

        @keyparam:
            config_xml - The configuration xml to be set
            login - A user's login name, if specifically choosing one

        @return:
            True on success, exception message on failure
        '''
        return my.server.set_config_definition(my.ticket, search_type, element_name, config_xml, login)

    def get_config_definition(my, search_type, view, element_name, personal=False):
        '''API Function: get_config_definition(search_type, view, element_name, personal=False)
        Get the widget configuration definition for an element

        @param:
            search_type - search type that this config relates to
            view - view to look for the element
            element_name - name of the element

        @keyparam:
            personal - True if it is a personal definition

        @return:
            string - xml of the configuration
        '''
        return my.server.get_config_definition(my.ticket, search_type, view, element_name, personal)

    def update_config(my, search_type, view, element_names):
        '''API Function: update_config(search_type, view, element_names)
        Update the widget configuration like ordering for a view

        @param:
            search_type - search type that this config relates to
            view - view to look for the element
            element_names - element names in a list

        @return:
            string - updated config xml snippet
        '''
        return my.server.update_config(my.ticket, search_type, view, element_names)

    def add_config_element(my, search_type, view, name, class_name=None, display_options={}, action_class_name=None, action_options={}, element_attrs={},login=None,  unique=True, auto_unique_name=False, auto_unique_view=False):

        '''API Function: add_config_element(search_type, view, name, class_name=None, display_options={},  action_class_name=None, action_options={}, element_attrs={},login=None,  unique=True, auto_unique_name=False, auto_unique_view=False)

        This method adds an element into a config.  It is used by various
        UI components to add new widget element to a particular view.
        
        @param:
            search_type - the search type that this config belongs to
            view - the specific view of the search type
            name - the name of the element

        @keyparam:
            class_name - the fully qualified class of the display
            action_class_name - the fully qualified class of the action
            display_options - keyward options in a dictionary to construct the specific display
            action_options - keyward options in a dictionary to construct the specific action

            element_attrs - element attributes in a dictionary
            login - login name if it is for a specific user
            unique - add an unique element if True. update the element if False.
            auto_unique_name - auto generate a unique element and display view name
            auto_unique_view - auto generate a unique display view name

        @return:
            boolean - True

        @example:
        This will add a new element to the "character" view for a 3D asset
        [code]
        search_type = 'prod/asset'
        view = 'characters'
        class_name = 'tactic.ui.common.SimpleElementWdg'
        server.add_config_element(search_type, view, class_name)
        [/code]
        This will add a new element named "user" to the "definition" view. It contains detailed display and action nodes
        
        [code]
        data_dict = {} # some data here
        search_type = 'prod/asset'
        server.add_config_element(search_type, 'definition', 'user',  class_name = data_dict['class_name'], display_options=data_dict['display_options'], element_attrs=data_dict['element_attrs'], unique=True, action_class_name=data_dict['action_class_name'], action_options=data_dict['action_options'])
        [/code]

        '''
        return my.server.add_config_element(my.ticket, search_type, view, name,\
                class_name, display_options, action_class_name, action_options, element_attrs, login, unique, auto_unique_name, auto_unique_view)

    def _setup(my, protocol="xmlrpc"):

        # if this is being run in the tactic server, have the option
        # to use TACTIC code directly
        if protocol == 'local':
            # import some server libraries
            from pyasm.biz import Project
            from pyasm.common import Environment
            from pyasm.prod.service import ApiXMLRPC
            from pyasm.web import WebContainer

            # set the ticket
            security = Environment.get_security()
            if not security:
                raise TacticApiException("Security not initialized.  This may be because you are running the client API in 'local' mode without run initializing Batch")


            # set the project
            project_code = Project.get_project_code()
            my.set_project(project_code)

            # set the ticket
            ticket = security.get_ticket_key()
            my.set_ticket(ticket)

            # set the protocol to local for the api class
            # note ticket has to be set first
            my.server = ApiXMLRPC()
            my.server.set_protocol(protocol)


            # if server name has already been set, use that one
            if my.server_name:
                my.has_server = True
                return

            web = WebContainer.get_web()
            if web:
                my.server_name = web.get_http_host()
                if my.server_name:
                    my.has_server = True
            else:
                # else guess that it is localhost
                my.server_name = "localhost"
                my.has_server = True
            return


        elif protocol =='xmlrpc':
            # get the env variables
            env_user = os.environ.get('TACTIC_USER')
            env_password = os.environ.get('TACTIC_PASSWORD')

            env_server = os.environ.get('TACTIC_SERVER')
            env_ticket = os.environ.get('TACTIC_TICKET')
            env_project = os.environ.get('TACTIC_PROJECT')

            # if all three are set, then it is not necessary to look at
            # the resource file
            if not (env_server and (env_user or env_ticket) and env_project):

                # need to scope by user
                # this is dealt with in get_resource_path already
                #if not my.login:
                #    my.login = getpass.getuser()
                file_path = my.get_resource_path()
                if not os.path.exists(file_path):
                    msg = "[%s] does not exist yet.  There is not enough information to authenticate the server. Either set the appropriate environment variables or run get_ticket.py" %file_path
                    raise TacticApiException(msg)

                # try to open the resource file
                file = open(file_path)
                lines = file.readlines()
                file.close()

                rc_server = None
                rc_ticket = None
                rc_project = None
                rc_login = None

                for line in lines:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    name, value = line.split("=")
                    if name == "server":
                        #my.set_server(value)
                        rc_server = value
                    elif name == "ticket":
                        #my.set_ticket(value)
                        rc_ticket = value
                    elif name == "project":
                        #my.set_project(value)
                        rc_project = value
                    elif name == "login":
                        #my.set_project(value)
                        rc_login = value


                # these have to be issued in the correct order
                if rc_server:
                    my.set_server(rc_server)
                if rc_project:
                    my.set_project(rc_project)
                if rc_ticket:
                    # get the project
                    project = my.get_project()
                    # set a default if one does not exist
                    if not project:
                        my.set_project("admin")
                    my.set_ticket(rc_ticket)
                if rc_login:
                    my.login = rc_login


            # override with any environment variables that are set
            if env_server:
                my.set_server(env_server)
            if env_project:
                my.set_project(env_project)
            if env_user:
                # try to get a ticket with a set password
                ticket = my.get_ticket(env_user, env_password)
                my.set_ticket(ticket)
            if env_ticket:
                my.set_ticket(env_ticket)

            #my.server.set_protocol(protocol)


    #
    # Doc methods
    #

    def get_doc_link(my, alias):
        return my.server.get_doc_link(my.ticket, alias);



    #
    # API/Server Version functions
    #
    def get_release_version(my):
        # DEPRECATED
        print "WARNING: Deprecated function 'get_release_version'"
        return my.server.get_release_version(my.ticket)

    def get_server_version(my):
        '''API Function: get_server_version()
        
        @return: 
            string - server version'''
        return my.server.get_server_version(my.ticket)


    def get_server_api_version(my):
        '''API Function: get_server_api_version()
        
        @return: 
            string - server API version'''
        version = my.server.get_server_api_version(my.ticket)
        return version



    def get_client_version(my):
        '''API Function: get_client_version()
        
        @return: 
            string - Version of TACTIC that this client came from'''

        # may use pkg_resources in 2.6
        if '.zip' in __file__:
            import zipfile
            parts = __file__.split('.zip') 
            zip_name  = '%s.zip'%parts[0]
            if zipfile.is_zipfile(zip_name):
                z = zipfile.ZipFile(zip_name)
                version = z.read('pyasm/application/common/interpreter/tactic_client_lib/VERSION')
                version = version.strip()
                z.close()
        else:
            dir = os.path.dirname(__file__)
            f = open('%s/VERSION' % dir, 'r')
            version = f.readline().strip()
            f.close()
        return version


    def get_client_api_version(my):
        '''API Function: get_client_api_version()
        
        @return: 
            string - client api version'''

        # may use pkg_resources in 2.6
        if '.zip' in __file__:
            import zipfile
            parts = __file__.split('.zip') 
            zip_name  = '%s.zip'%parts[0]
            if zipfile.is_zipfile(zip_name):
                z = zipfile.ZipFile(zip_name)
                version = z.read('pyasm/application/common/interpreter/tactic_client_lib/VERSION_API')
                version = version.strip()
                z.close()
        else:
            dir = os.path.dirname(__file__)
            f = open('%s/VERSION_API' % dir, 'r')
            version = f.readline().strip()
            f.close()
        return version


    
    server = None
    def get(cls, protocol='', setup=True):
        '''get function which treats the server stub as a singleton'''
        try:
            from pyasm.common import Container
            server = Container.get("TacticServerStub")
            if not server:
                from pyasm.common import Environment
                app_server = Environment.get_app_server()
                if protocol:
                    server = TacticServerStub(protocol=protocol, setup=setup)
                elif app_server in ["batch", "xmlrpc"]:
                    server = TacticServerStub(protocol='local', setup=setup)
                else:
                    server = TacticServerStub(setup=setup)
                Container.put("TacticServerStub", server)

            return server

        except ImportError, e:
            if not cls.server:
                cls.server = TacticServerStub(protocol='xmlrpc', setup=setup)
            return cls.server
    get = classmethod(get)

    def set(cls, server=None):
        try:
            from pyasm.common import Container
            Container.put("TacticServerStub", server)
        except ImportError:
            cls.server = server
    set = classmethod(set)





#
# Objects
#


class Command(object):
    def get_description(my):
        return "No description"

    def execute_cmd(my):
        my.server = TacticServerStub()
        my.server.start(my.get_description())
        try:
            my.execute()
        except Exception, e:
            my.server.abort()
            raise
        else:
            my.server.finish()


    def execute(my):
        my.execute()




class Search(object):
    pass



class SObject(dict):
    def get_search_key(my):
        return my['__search_key__']



