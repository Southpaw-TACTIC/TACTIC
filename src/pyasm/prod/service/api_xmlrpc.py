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

__all__ = ["ApiXMLRPC", 'profile_execute', 'ApiClientCmd','ApiException']

import decimal
import shutil, os, types, sys, thread
import re, random
import datetime, time

from pyasm.common import jsonloads, jsondumps

from pyasm.common import Environment, Xml, Common, Config, Container, SecurityException, SObjectSecurityException, TacticException, System
from pyasm.command import Command, UndoCmd, RedoCmd, Trigger, CommandExitException
from pyasm.checkin import FileCheckin, FileGroupCheckin, SnapshotBuilder, FileAppendCheckin, FileGroupAppendCheckin
from pyasm.biz import IconCreator, Project, FileRange, Pipeline, Snapshot, DebugLog, File, FileGroup, Schema, ExpressionParser
from pyasm.search import *
from pyasm.security import XmlRpcInit, XmlRpcLogin, Ticket, LicenseException, Security

from pyasm.web import WebContainer, Palette
#from pyasm.web import EventContainer, CommandDelegator
#from pyasm.widget import IframeWdg, IframePlainWdg, WidgetConfigView
from pyasm.widget import WidgetConfigView
from pyasm.web.app_server import XmlrpcServer

MAXINT =  2L**31-1

class ApiClientCmd(Command):
    def get_title(my):
        return "Client API"
    


class ApiException(Exception):
    pass




# methods that only query.  These do not need the overhead of a transaction
# so run outside of transaction, increasing performance. 

REQUEST_COUNT = 1
LAST_RSS = System().memory_usage().get('rss')

# wrap in a low level mock command without a transaction
def get_simple_cmd(my, meth, ticket, args):
    class ApiClientCmd(Command):

        def get_title(my):
            return "Client API"

        def check(my):
            duration = time.time() - my.start_time
            print "Checking ... (%0.3f)" % duration

        def execute(my2):
            my2.start_time = time.time()
            global REQUEST_COUNT, LAST_RSS
            request_id = "%s - #%0.7d" % (thread.get_ident(), REQUEST_COUNT)
           
            if my.get_protocol() != "local":
                print "request_id: ", request_id
                now = datetime.datetime.now()
                
                def print_info(my2, args):
                    from pyasm.security import Site
                    if Site.get_site():
                        print "site: ", Site.get_site()
                    print "timestamp: ", now.strftime("%Y-%m-%d %H:%M:%S")
                    print "user: ", Environment.get_user_name()
                    print "simple method: ", meth
                    print "ticket: ", ticket
                    Container.put("CHECK", my2.check)
                    Container.put("NUM_SOBJECTS", 1)
                    Common.pretty_print(args)
                
                if meth.__name__ == 'get_widget':
                    first_arg = args[0]
                    if first_arg and isinstance(first_arg, basestring) and first_arg.find("tactic.ui.app.message_wdg.Subscription") == -1:
                        print_info(my2, args)
                else:
                    print_info(my2, args)
                
                    
            try:
                # actually execute the method
                my2.results = exec_meth(my, ticket, meth, args)
            finally:
                if my.get_protocol() != "local":
                    duration = time.time() - my2.start_time
                    print "Duration: %0.3f seconds (request_id: %s)" % (duration, request_id)
                    REQUEST_COUNT += 1
                    rss = System().memory_usage().get("rss")
                    increment = rss - LAST_RSS
                    print "Memory: %s KB" % rss
                    print "Increment: %s KB" % increment
                    #print "Num SObjects: %s" % Container.get("NUM_SOBJECTS")
                    LAST_RSS = rss



        def execute_cmd(cls, cmd):
            try:
                cmd.execute()
            finally:
                if not my.get_protocol() == "local":
                    DbContainer.release_thread_sql()
        execute_cmd = classmethod(execute_cmd)

    return ApiClientCmd()




# wrap in a transaction
def get_full_cmd(my, meth, ticket, args):
    class ApiClientCmd(Command):

        def get_title(my):
            return "Client API"

        def check(my2):
            return True

        def get_transaction(my2):
            if my.get_protocol() == "local":
                transaction = super(ApiClientCmd,my2).get_transaction()
                return transaction

            state = TransactionState.get_by_ticket(ticket)
            # FIXME: do we really need to restore the state?  This is not needed
            # becasue the ticket now has a project
            #state.restore_state()

            transaction_id = state.get_state("transaction")
            if not transaction_id:
                return Command.get_transaction(my2)

            # continue the transaction
            transaction_log = TransactionLog.get_by_id(transaction_id)
            if transaction_log:
                transaction = Transaction.resume(transaction_log)
            else:
                raise Exception( "Can't resume transaction" )

            #transaction = Transaction.get(create=True)

            return transaction

        def execute(my2):
            start = time.time()
            global REQUEST_COUNT
            request_id = "%s - #%0.7d" % (thread.get_ident(), REQUEST_COUNT)

            debug = True
            if meth.func_name == "execute_cmd":
                if len(args) > 1:
                    _debug = args[1].get("_debug")
                    if _debug == False:
                        debug = False


            if my.get_protocol() != "local" and debug:
                print "---"
                print "user: ", Environment.get_user_name()
                now = datetime.datetime.now()
                print "timestamp: ", now.strftime("%Y-%m-%d %H:%M:%S")
                print "method: ", meth.func_name
                print "ticket: ", ticket
                Common.pretty_print(args)
            
            #my2.results = meth(my, ticket, *args)
            
            my2.results = exec_meth(my, ticket, meth, args)
            if isinstance(my2.results, dict) and my2.results.get("description"):
                my2.add_description( my2.results.get("description") )

            my2.sobjects = my.get_sobjects()
            my2.info = my.get_info()
            my2.info['function_name'] = meth.func_name
            my2.info['args'] = args


            if my.get_protocol() != "local" and debug:
                duration = time.time() - start
                print "Duration: %0.3f seconds (request_id: %s)" % (duration, request_id)




    return ApiClientCmd()


def exec_meth(my, ticket, meth, args):

    #print "Server Port: ", WebContainer.get_web().get_env("SERVER_PORT")

    if my.get_language() == "javascript":
        # the last argument is always kwargs
        new_args = [x for x in args]
        kwargs = new_args.pop()

        if kwargs == {}:
            results = meth(my, ticket, *new_args)
        else:
            results = meth(my, ticket, *new_args, **kwargs)
    else:
        results = meth(my, ticket, *args)
    
    return results




# methods that only query.  These do not need the overhead of a transaction
# so run outside of transaction, increasing performance
QUERY_METHODS = {
    'ping': 0,
    'get_connection_info': 0,
    'get_release_version': 0, 'get_server_version': 0, 'get_server_api_version': 0,
    'query': 0,'get_by_search_key': 0,
    'get_all_children': 0,'get_parent': 0,'get_child_types': 0,'get_parent_type': 0,
    'get_types_from_instance': 0,
    'get_snapshot': 0, 'get_full_snapshot_xml': 0,
    'get_handoff_dir': 0,
    'get_path_from_snapshot': 0, 'expanded_paths_from_snapshot': 0,
    'get_all_paths_from_snapshot': 0,
    'get_dependencies': 0, 'get_all_dependencies': 0,
    'get_preallocated_path': 0,
    'get_pipeline_xml': 0,
    'get_pipeline_processes': 0,
    'get_pipeline_xml_info': 0,
    'get_pipeline_processes_info': 0,
    'get_widget': 0, 'get_column_widgets': 0,
    'get_client_dir': 0,
    'get_md5_info': 0,
    'eval': 0,
    'get_column_info': 0,
    'get_related_types': 0,
    #'get_related_sobjects': 0,
    #'get_related_attrs': 0,
    #'get_related_relationship': 0,
    'test_speed': 0,
    'get_upload_file_size': 0,
    'get_doc_link': 0,
    'get_interaction_count': 0,
}

TRANS_OPTIONAL_METHODS = {
    'execute_cmd': 3
}

def xmlrpc_decorator(meth):
    '''initialize the XMLRPC environment and wrap the command in a transaction
    '''
    def preprocess(ticket):
        '''store the state when the ticket comes from the web'''
        data_key = "%s:%s" % (XMLRPC_DATA_KEY, my.__hash__())
        init_data_key = "%s:%s" % (XMLRPC_INIT_DATA_KEY, my.__hash__())

        if isinstance(ticket, dict):
            lang = ticket.get('language')
            if lang == 'javascript':
                state  = Container.get(data_key).copy()
                Container.put(init_data_key, state)

    def postprocess(ticket):
        '''restore the state when the ticket comes from the web'''
        data_key = "%s:%s" % (XMLRPC_DATA_KEY, my.__hash__())
        init_data_key = "%s:%s" % (XMLRPC_INIT_DATA_KEY, my.__hash__())

        if isinstance(ticket, dict):
            state  = Container.get(init_data_key)
            if state:
                Container.put(data_key, state) 



    def new(my, original_ticket, *args, **kwargs):
        results = None
        try:
            ticket = my.init(original_ticket)

            try:
                #if meth.__name__ in QUERY_METHODS:
                if QUERY_METHODS.has_key(meth.__name__):
                    cmd = get_simple_cmd(my, meth, ticket, args)
                elif TRANS_OPTIONAL_METHODS.has_key(meth.__name__):
                    idx =  TRANS_OPTIONAL_METHODS[meth.__name__]
                    if len(args) - 1 == idx and args[idx].get('use_transaction') == False:
                        cmd = get_simple_cmd(my, meth, ticket, args)
                    else:
                        cmd = get_full_cmd(my, meth, ticket, args)

                else:
                    cmd = get_full_cmd(my, meth, ticket, args)

                profile_flag = False

                if Container.get("profile") == True:
                    profile_flag = False

                if profile_flag:
                    Container.put("profile", True)

                    global profile_cmd
                    profile_cmd = cmd
                    import profile, pstats
                    if os.name == 'nt':
                        path = "C:/sthpw/profile"
                    else:
                        path = "/tmp/sthpw/profile"
                    profile.run( "from pyasm.prod.service import profile_execute; profile_execute()", path)
                    p = pstats.Stats(path)
                    p.sort_stats('cumulative').print_stats(30)
                    print "*"*30
                    p.sort_stats('time').print_stats(30)

                else:
                    if my.get_protocol() == 'local':
                        transaction = Transaction.get()
                        if not transaction:
                            cmd.execute_cmd(cmd)
                        else:
                            cmd.execute()
                    else:
                        cmd.execute_cmd(cmd)

                if not cmd.get_description():
                    cmd.add_description(meth.__name__)

                #postprocess(original_ticket)
                results = cmd.results

            except Exception, e:

                # make sure all sqls are aborted
                if not my.get_protocol() == "local":
                    DbContainer.abort_thread_sql(force=True)


                #print "Error: ", e.message
                import traceback
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print "-"*50
                print stacktrace_str
                message = e.message
           
                if not message:
                    message = e.__str__()

                if isinstance(message, unicode):
                    error_msg = message.encode('utf-8')
                elif isinstance(message, str):
                    error_msg = unicode(message, errors='ignore').encode('utf-8')
                else:
                    error_msg = message
                print "Error: ", error_msg  
                print "-"*50
                raise

        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
            

        # reformat the data to JSON if going to the browser
        try:
            # NOTE: add in a special requirement for get_widget() because
            # of the bizarre 4096 byte limitation on responseXML in the browser
            web = WebContainer.get_web()
            if (web and web.get_app_name() == "Browser" \
                    and meth.__name__ not in ['get_widget'] \
                    and my.get_language() == 'javascript'):
                results = jsondumps(results)

            # handle special cases for c#
            #elif my.get_language() == 'c#':
            #    results = jsondumps(results)


        except Exception, e:
            print e.__str__()

        return results

    new.exposed = True
    return new


profile_cmd = None
def profile_execute():
    profile_cmd.execute_cmd(profile_cmd)



def trace_decorator(meth):
    def new(my, *args):
        
        print "method: ", meth.__name__, args

        try:
            #my.language = 'python'
            my.set_language('python')
            ticket = args[0]
            args = args[1:]

            # TODO: this should move to a common ticket handling function
            # This code is similar to init()
            if type(ticket) == types.DictType:
                language = ticket.get("language")
                if language:
                    my.set_language(language)

            try:
                results = exec_meth(my, ticket, meth, args)
            finally:
                if not my.get_protocol() == "local":
                    DbContainer.release_thread_sql()

            return results
        except Exception, e:

            # make sure all sqls are aborted. 
            DbContainer.abort_thread_sql(force=True) 

            print "Exception: ", e.__str__()
            import traceback
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print "-"*50
            print stacktrace_str
            print str(e)
            
            print "-"*50
            raise
    new.exposed = True
    
    return new



XMLRPC_DATA_KEY = "XMLRPC:data"
XMLRPC_INIT_DATA_KEY = "XMLRPC:init_data"

class BaseApiXMLRPC(XmlrpcServer):
    '''Client Api'''

    # a store house for all of the containers used by the API
    session_containers = {}

    def __init__(my):

        super(BaseApiXMLRPC,my).__init__()


    # DEPRECATED: this was to be used to obtain true transactions for client
    # api ... it was never full implemented
    '''
    def xxdefault(my, ticket, *args):
        func = args[0]
        args = args[1:]
        expr = "my.%s%s" % (func, args)
        return eval(expr)
    xxdefault2.exposed = True
    '''


   
    #
    # Thread safe data storage using Container
    #
    def _get_data(my):
        data_key = "%s:%s" % (XMLRPC_DATA_KEY, my.__hash__())
        data = Container.get(data_key)
        if data == None:
            # put in some defaults
            data = {
                "protocol": "xmlrpc",
                "language": "python",
                "is_in_transaction": False,
                "sobjects": [],
                "info": {}
            }
            Container.put(data_key, data)
        return data


    def get_value(my, name):
        data = my._get_data()
        return data.get(name)

    def set_value(my, name, value):
        data = my._get_data()
        data[name] = value


    def set_protocol(my, protocol):
        #my.protocol = protocol
        my.set_value("protocol", protocol)

    def get_protocol(my):
        #my.protocol = protocol
        return my.get_value("protocol")


    def set_language(my, language):
        my.set_value("language", language)

    def get_language(my):
        return my.get_value("language")


    def set_sobjects(my, sobjects):
        my.set_value("sobjects", sobjects)
        #my.sobjects = sobjects

    def set_sobject(my, sobject):
        my.set_value("sobjects", [sobject])
        ##my.set_sobjects([sobject])

    def get_sobjects(my):
        return my.get_value('sobjects')


    def update_info(my, dict):
        info = my.get_info()
        info.update(dict)
        my.set_value('info', info)

    def get_info(my):
        return my.get_value('info')

    def set_transaction_state(my, flag):
        my.set_value("is_in_transaction", flag)
   

   
    def is_in_transaction(my):
        return my.get_value("is_in_transaction")


 

    # gets called if there is a method missing
    def missing_method(my, func, args):
        # FIXME: makes no sense at all!!!  If an exception occurs
        # in this function, then the Container is cleared?????
        print "No such function [%s]" % func
        # abort on missing method
        #ticket = args[0]
        #my.abort(ticket)
        return False
    missing_method.exposed = True

    '''
    def missing_method(my, func, args):
        try:
            return True
            custom = CustomApi()
            expr = "custom.%s(*args)" % func
            print expr
            print "custom: ", custom.__dict__
            print dir(custom)
            if func in dir(custom):
                retval = eval(expr)
            else:
                raise ApiException("Cannot execute [%s]" % expr)
                retval = None
            return retval
        except Exception, e:
            print e
            msg = e.__str__()
            expr = "custom.%s(%s)" % (func, args)
            # remap useless error
            if msg.startswith("new() takes at least 2 arguments"):
                msg = "Wrong number of arguments"
            print("Failed to execute [%s]: %s" % (expr, msg))
        return None
        '''



    def init(my, ticket, reuse_container=True):

        assert ticket
      
        # if the project code is in the ticket, then set the project
        if type(ticket) == types.DictType:
            site = ticket.get("site")
            project_code = ticket.get("project")
            language = ticket.get("language")
            palette = ticket.get("palette")
            ticket = ticket.get("ticket")

        else:
            # DEPRECATED
            if ticket.find(":") != -1:
                project_code, ticket = ticket.split(":")
            else:
                project_code = None
            language = "python"
            palette = None
            site = None



        if my.get_protocol() == "local":
            if project_code:
                Project.set_project(project_code)
            return ticket

        # if a session container has been cached, use that
        key = ticket

        # start a new session and store the container
        container = Container.create()
        #my.session_containers[key] = container

        # need to set site
        from pyasm.security import Site
        if site:
            Site.set_site(site)

        XmlRpcInit(ticket)

        if project_code:
            Project.set_project(project_code)
            Project.get()

        # initialize the web environment object and register it
        adapter = my.get_adapter()
        WebContainer.set_web(adapter)


        # now that we have a container, set up the information
        my.set_language(language)
        #my.set_protocol(protocol)

        if palette:
            #Palette.push_palette(palette)
            Palette.get().set_palette(palette)


        return ticket


    def _get_sobjects(my, search_keys, no_exception=False):
        '''for a give input search key, return the sobjects.  Note that search
        key and can an array or a string'''
       
        # make sure search_keys is value
        if not search_keys:
            raise ApiException("Search key [%s] is None" % search_keys)

        if type(search_keys) != types.ListType:
            search_keys = [search_keys]

        sobjects = []
        for search_key in search_keys:
            # if it is a dict type, the extract the search type
            if type(search_key) == types.DictType:
                search_key = search_key.get('__search_key__')
                if not search_key:
                    raise ApiException("Not a valid search key [%s]" % search_key)


            # fix this as a precaution ... if appears from xml occasionally
            while search_key.find("&amp;") != -1:
                search_key = search_key.replace("&amp;", "&")


            #print "search_key: ", search_key
            sobject = SearchKey.get_by_search_key(search_key)
            if not sobject:
                if no_exception:
                    return []
                else:
                    raise ApiException("SObject [%s] does not exist" % search_key)

            sobjects.append(sobject)

        if not sobjects:
            if no_exception:
                return []
            else:
                raise ApiException("No SObject exist in [%s]" % search_keys)

        return sobjects


    # changing it to a public function
    def get_sobject_dict(my, sobject, columns=None, use_id=False):
        return my._get_sobject_dict(sobject,columns,use_id)
    def _get_sobject_dict(my, sobject, columns=None, use_id=False):

        sobjects = my._get_sobjects_dict([sobject], columns=columns, use_id=use_id)
        if not sobjects:
            return {}
        else:
            return sobjects[0]


        #########################
        """ 
        if not sobject:
            return {}

        search_type = sobject.get_search_type()
        column_info = SearchType.get_column_info(search_type)

        if not columns:
            search = Search(search_type)
            columns = search.get_columns()
        result = {}

        language = my.get_language()
        for column in columns:
            if column == 'metadata':
                value = sobject.get_metadata_dict()
            else:
                value = sobject.get_value(column)
                if language == 'c#':
                    if value == '':
                        value = None

                info = column_info.get(column)
                data_type = info.get("data_type")

                # This type is specific to sql server and is not a data
                # element that in TACTIC (at the moment)
                if data_type == 'sqlserver_timestamp':
                    continue
                elif isinstance(value, datetime.datetime):
                    try:
                        value = str(value)
                    except Exception, e:
                        print "WARNING: Value [%s] can't be processed" % value
                        continue
                elif isinstance(value, long) and value > MAXINT:
                    value = str(value)
                elif isinstance(value, basestring):
                    try:
                        value = value.encode("UTF8")
                    except Exception, e:
                        print "WARNING: Value [%s] can't be processed" % value
                        continue

            result[column] = value
        result['__search_key__'] = SearchKey.build_by_sobject(sobject, use_id=use_id)
        return result
        """



    def _get_sobjects_dict(my, sobjects, columns=None, use_id=False):
        '''get dictionary versions of the sobjects.  this is optimized
        for lots of sobjects'''

        if not sobjects:
            return []

        language = my.get_language()

        info = {}
        
        results = []

        for sobject in sobjects:
            result = {}
            results.append( result )

            if not sobject:
                continue

            result['__search_key__'] = SearchKey.build_by_sobject(sobject, use_id=use_id)
            result['__search_type__'] = sobject.get_search_type()

            search_type = sobject.get_search_type()
            column_info = info.get(search_type)
            if column_info == None:
                column_info = SearchType.get_column_info(search_type)
                info[search_type] = column_info

            if not columns:
                columns = column_info.keys()

            for column in columns:
                if column == 'metadata':
                    value = sobject.get_metadata_dict()

                else:
                    value = sobject.get_value(column)

                    if language == 'c#':
                        if value == '':
                            value = None

                    info = column_info.get(column)
                    data_type = info.get("data_type")
                    # This type is specific to sql server and is not a data
                    # element that in TACTIC (at the moment)
                    if data_type == 'sqlserver_timestamp':
                        continue
                    elif isinstance(value, datetime.datetime):
                        try:
                            value = str(value)
                        except Exception, e:
                            print "WARNING: Value [%s] can't be processed" % value
                            continue
                    elif isinstance(value, long) and value > MAXINT:
                        value = str(value)
                    elif isinstance(value, decimal.Decimal):
                        # use str to avoid loss of precision
                        value = str(value)
                    elif isinstance(value, unicode):
                        try:
                            # don't reassign to value, keep it as unicode object
                            value.encode("utf-8")

                        except Exception, e:
                            print "WARNING: Value [%s] can't be encoded in utf-8" % value
                            raise 
                            continue
                    elif isinstance(value, str):
                        # this could be slow, but remove bad characters
                        value = unicode(value, errors='ignore')
                result[column] = value

        return results





    def _add_filters(my, search, filters):
        '''method to add filters to a search'''
        search.add_op_filters(filters)
        return




class CustomApi(BaseApiXMLRPC):
    @xmlrpc_decorator
    def pig(my, ticket, first, second, third):
        return first+"1", second+"2", third+"3"




class ApiXMLRPC(BaseApiXMLRPC):
    '''Client Api'''

    #@trace_decorator
    def get_ticket(my, login_name, password, site=None):
        '''simple test to verify that the xmlrpc connection is working

        @params
        login_name - unique name of the user
        password - unencrypted password of the user
        '''
        from pyasm.security import Site
        if site:
            Site.set_site(site)

        ticket = ""
        try:
            XmlRpcLogin(login_name, password)

            # initialize the web environment object and register it
            adapter = my.get_adapter()
            WebContainer.set_web(adapter)

            security = WebContainer.get_security()
            ticket = security.get_ticket_key()

        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()

        return ticket
    get_ticket.exposed = True


    @xmlrpc_decorator
    def generate_ticket(my, ticket):
        return Common.generate_random_key()
    #generate_ticket.exposed = True



    @xmlrpc_decorator
    def set_palette(my, palette):
        Palette.push_palette(palette)


    #
    # Logging
    #
    @xmlrpc_decorator
    def log(my, ticket, level, message, category="default"):
        '''Log a message in the logging queue

        @params
        ticket - authentication ticket
        level - debug level ....
        message - freeform string describing the entry
        '''
        log = DebugLog.log(level,message,category)
        return True




    #
    # Preferences
    #
    @xmlrpc_decorator
    def get_preference(my, ticket, key):
        '''Get the users preference for this project

        @params
        ticket - authentication ticket
        key - unique key to identify preference

        @return
        current value of preference
        '''
        project_code = Project.get_project_code()

        from pyasm.biz import PrefSetting
        value = PrefSetting.get_value_by_key(key, project_code=project_code)
        return value


    @xmlrpc_decorator
    def set_preference(my, ticket, key, value):
        '''Set the users preference for this project

        @params
        ticket - authentication ticket
        key - unique key to identify preference
        value - value to set the preference

        '''
        project_code = Project.get_project_code()

        from pyasm.biz import PrefSetting
        PrefSetting.create(key, value, project_code=project_code)



    #
    # Messaging and Subscriptions
    #


    @xmlrpc_decorator
    def get_message(my, ticket, key):
        message = Search.get_by_code("sthpw/message", key)
        sobject_dict = my._get_sobject_dict(message)
        return sobject_dict


    @xmlrpc_decorator
    def get_messages(my, ticket, keys):
        search = Search("sthpw/message")
        search.add_filters("code", keys)
        messages = search.get_sobjects()

        results = []
        for message in messages:
            sobject_dict = my._get_sobject_dict(message)
            results.append(sobject_dict)

        return results




    @xmlrpc_decorator
    def log_message(my, ticket, key, message=None, status=None, category="default"):
        '''Log a message which will be seen by all who are subscribed to
        the message "key".

        @params
        ticket - authentication ticket
        key - unique key for this message

        @keyparams
        status - arbitrary status for this message
        category - value to categorize this message

        @return
        string - "OK"
        '''


        if type(message) == types.DictType:
            message = jsondumps(message)

        # go low level
        from pyasm.security import Site
        site = Site.get_site()
        if site:
            db_resource = Site.get_db_resource(site, "sthpw")
        else:
            db_resource = "sthpw"
        sql = Sql(db_resource)
        sql.connect()

        project_code = Project.get_project_code()

        from pyasm.search import Update, Select, Insert
        select = Select()
        select.add_table("message")
        select.set_database(sql)
        select.add_filter("code", key)
        statement = select.get_statement()
        last_message = sql.do_query(statement)
        if not last_message:
            update = Insert()
            update.set_database(sql)
            update.set_table("message")
            update.set_value("code", key)
            update.set_value("project_code", project_code)
        else:
            update = Update()
            update.set_database(sql)
            update.set_table("message")
            update.add_filter("code", key)
        update.set_value("category", category)

        if message != None:
            update.set_value("message", message)
        if status != None:
            update.set_value("status", status)

        login = Environment.get_user_name()
        update.set_value("login", login)
        update.set_value("timestamp", "NOW")

        statement = update.get_statement()
        sql.do_update(statement)


        # repeat with update the message log
        update = Insert()
        update.set_database(sql)
        update.set_table("message_log")
        update.set_value("message_code", key)
        if message != None:
            update.set_value("message", message)
        if status != None:
            update.set_value("status", status)

        login = Environment.get_user_name()
        update.set_value("login", login)
        update.set_value("project_code", project_code)
        update.set_value("timestamp", "NOW")

        statement = update.get_statement()
        sql.do_update(statement)

        sql.close()

        #return last_message
        return "OK"

        # FIXME: this does not work anymore because Sql objects are take from
        # the thread and not the transaction
        transaction = Transaction.get(force=True)
        transaction.set_record(False)
        sobject = Search.eval("@SOBJECT(sthpw/message['code','%s'])" % key, single=True)
        if not sobject:
            sobject = SObjectFactory.create("sthpw/message")
            sobject.set_value("code", key)
        #sobject.set_value("login", user_name)
        sobject.set_value("category", category)
        sobject.set_value("message", message )
        sobject.set_value("message", message )
        sobject.set_value("project_code", project_code)
        sobject.commit(triggers=False)
        transaction.commit()
        transaction.remove_from_stack()


    @xmlrpc_decorator
    def subscribe(my, ticket, key, category=None):
        '''Allow a user to subscribe to this message key.  All messages
        belonging to the corresponding key will be available to users
        subscribed to it.

        @params
        ticket - authentication ticket
        key - unique key for this message in the message_code column

        @keyparam
        category - value to categorize this message

        @return
        subscription sobject
        '''

        search = Search("sthpw/subscription")
        search.add_user_filter()
        search.add_filter("message_code", key)
        subscription  = search.get_sobject()

        if subscription:
            raise ApiException('[%s] has already been subscribed to.'%key)
            # nothing to do ... already subscribed
            #sobject_dict = my._get_sobject_dict(subscription)
            #return sobject_dict

        project_code = Project.get_project_code()

        subscription = SearchType.create("sthpw/subscription")
        subscription.set_value("message_code", key)
        subscription.set_value("project_code", project_code)
        subscription.set_user()
        if category:
            subscription.set_value("category", category)
        subscription.commit()

        sobject_dict = my._get_sobject_dict(subscription)
        return sobject_dict


    @xmlrpc_decorator
    def unsubscribe(my, ticket, key):
        '''Allow a user to unsubscribe from this message key.

        @params
        ticket - authentication ticket
        key - unique key for this message in the message_code column

        @return:
        dictionary - the values of the subscription sobject in the
        form name:value pairs
        '''

        project_code = Project.get_project_code()

        search = Search("sthpw/subscription")
        search.add_user_filter()
        search.add_filter("message_code", key)
        search.add_filter("project_code", project_code)
        subscription  = search.get_sobject()

        if not subscription:
            raise ApiException('[%s] is not subscribed to.'%key)
            # nothing to do ... item is not subscribed to

        subscription.delete()

        return my._get_sobject_dict(subscription)



    #
    # user interaction
    #
    @xmlrpc_decorator
    def add_interaction(my, ticket, key, data={}):

        interaction = SearchType.create("sthpw/interaction")
        interaction.set_value("key", key)
        if data:
            interaction.set_value("data", jsondumps(data))

        interaction.set_user()
        project_code = Project.get_project_code()
        interaction.set_value("project_code", project_code)

        interaction.commit()
        sobject_dict = my._get_sobject_dict(interaction)
        return sobject_dict


    @xmlrpc_decorator
    def get_interaction_count(my, ticket, key):
        interaction = Search("sthpw/interaction")
        interaction.add_filter("key", key)
        return interaction.get_count()



 

    #
    # Undo/Redo functionality
    #
    @trace_decorator
    def undo(my, ticket, transaction_ticket=None, transaction_id=None, ignore_files=False):
        '''undo an operation.  If no transaction id is given, then the last
        operation of this user on this project is undone

        @params
        ticket - authentication ticket
        transaction_ticket - explicitly undo a specific transaction
        transaction_id - explicitly undo a specific transaction by id
        ignore_files - flag which determines whether the files should
            also be undone.  Useful for large preallcoated checkins.
        '''
        try:
            ticket = my.init(ticket)

            cmd = UndoCmd(ignore_files=ignore_files)

            if transaction_ticket:
                state = TransactionState.get_by_ticket(transaction_ticket)
                project_code = state.get_state("project")
                state.restore_state()

                # get the transaction_id
                transaction_id = state.get_state("transaction")
                if transaction_id:
                    cmd.set_transaction_id(transaction_id)
            elif transaction_id:
                cmd.set_transaction_id(transaction_id)


            Command.execute_cmd(cmd)
        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
        return True
    undo.exposed = True



    @trace_decorator
    def redo(my, ticket, transaction_ticket=None, transaction_id=None):
        '''redo an operation.  If no transaction id is given, then the last
        undone operation of this user on this project is redone

        @params
        ticket - authentication ticket
        transaction_id - explicitly undo a specific transaction
        '''
        try:
            ticket = my.init(ticket)

            cmd = RedoCmd()

            if transaction_ticket:
                state = TransactionState.get_by_ticket(transaction_ticket)
                project_code = state.get_state("project")
                state.restore_state()

                # get the transaction_id
                transaction_id = state.get_state("transaction")
                if transaction_id:
                    cmd.set_transaction_id(transaction_id)
            elif transaction_id:
                cmd.set_transaction_id(transaction_id)
            Command.execute_cmd(cmd)
        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()

        return True
    redo.exposed = True



    @xmlrpc_decorator
    def ping(my, ticket):
        '''simple test to verify that the xmlrpc connection is working'''
        return "OK"

    def fast_ping(my, ticket):
        '''simple test to verify that the xmlrpc connection is working'''
        return "OK"
    fast_ping.exposed = True



    @xmlrpc_decorator
    def test_speed(my, ticket):
        '''simple test to verify that the xmlrpc connection is working'''
        search = Search("sthpw/ticket")
        #search.add_limit(10)
        sobjects = search.get_sobjects()
        sobject_dicts = []
        for sobject in sobjects:
            #sobject_dict = my._get_sobject_dict(sobject)
            sobject_dict = sobject.get_data()
            sobject_dicts.append(sobject_dict)
        return str(sobject_dicts)
    test_speed.exposed = True


    #@trace_decorator
    #def test_speed(my, ticket):
    #    '''simple test to verify that the xmlrpc connection is working'''
    #    return "OK"


    #@xmlrpc_decorator
    #def test_speed(my, ticket):
    #    '''simple test to verify that the xmlrpc connection is working'''
    #    return "OK"





    @xmlrpc_decorator
    def get_connection_info(my, ticket):
        '''simple test to get connection info'''
        import thread
        data = {}
        data['thread'] = thread.get_ident()

        web = WebContainer.get_web()
        keys = web.get_env_keys()
        data['keys'] = keys

        # get the current port
        port = web.get_env("SERVER_PORT")
        data['port'] = port

        # get the connection pool
        num_db_connections = 0
        databases = {}
        global_pool = DbContainer.get_global_connection_pool()
        if global_pool:
            global_databases = global_pool.keys()
            data['global_pool'] = global_databases
            num_db_connections = len(global_databases)
            for database in global_databases:
                num = databases.get(database)
                if num == None:
                    num = 0
                databases[database] = num + 1


        # get the connection pool
        import thread
        containers = Container.get_all_instances()
        for thread_id, cont in containers.items():
            thread_pool = cont.info.get("DbContainer::thread_pool")
            if thread_pool:
                #print "thread: ", thread_id, thread_pool, thread_id == thread.get_ident()
                thread_databases = thread_pool.keys()
                data['thread_pool'] = global_databases
                num_db_connections += len(thread_databases)

                for database in global_databases:
                    num = databases.get(database)
                    if num == None:
                        num = 0
                    databases[database] = num + 1



        data['num_database_connections'] = num_db_connections
        data['databases'] = databases

        print data

        return data



    @xmlrpc_decorator
    def test_error(my, ticket):
        '''simple test to verify that the xmlrpc connection is working'''
        big_fat_error

    @xmlrpc_decorator
    def get_release_version(my, ticket):
        '''DEPRECATED: use get_server_version()'''
        return Environment.get_release_version()


    @xmlrpc_decorator
    def get_server_version(my, ticket):
        '''get the server version'''
        return Environment.get_release_version()


    @xmlrpc_decorator
    def get_server_api_version(my, ticket):
        '''get the server version'''
        return Environment.get_release_api_version()





    #
    # Basic update and query methods
    #
    @xmlrpc_decorator
    def get_column_info(my, ticket, search_type):
        search_type_obj = SearchType.get(search_type)
        return search_type_obj.get_column_info(search_type)

    @xmlrpc_decorator
    def get_related_types(my, ticket, search_type):
        schema = Schema.get()
        return schema.get_related_search_types(search_type)




    @xmlrpc_decorator
    def query(my, ticket, search_type, filters=None, columns=None, order_bys=None, show_retired=False, limit=None, offset=None, single=False, distinct=None, return_sobjects=False, parent_key=None):
        return my._query(search_type, filters, columns, order_bys, show_retired, limit, offset, single, distinct, return_sobjects, parent_key)
    def _query(my, search_type, filters=None, columns=None, order_bys=None, show_retired=False, limit=None, offset=None, single=False, distinct=None, return_sobjects=False, parent_key=None):
        '''
        General query for sobject information

        @params
        ticket - authentication ticket
        search_type - the key identifying a type of sobject as registered in
                    the search_type table.
        filters - (optional) an array of filters to alter the search
        columns - (optional) an array of columns whose values should be
                    retrieved
        order_bys - (optional) an array of order_by to alter the search
        show_retired - (optional) - sets whether retired sobjects are also
                    returned
        limit - sets the maximum number of results returned
        single - returns a single sobject that is not wrapped up in an array
        distinct - specify a distinct column
        return_sobjects - return sobjects instead of dictionary.  This
                works only when using the API on the server.
        parent_key - parent filter

        @return
        data - an array of dictionaries.  Each array item represents an sobject
               and is a dictionary of name/value pairs

        @usage:
            filters = []
            filters.append( ("code", "XG002") )
            columns = ['code']
            order_bys = ['timestamp desc']

            server.query(ticket, "prod/shot", filters, columns, order_bys)

            The arguments "filters",  "columns", "distinct", and "order_bys" are optional

            Each element in the filter array represent an expression or which
            all are joined together with "and".

            Examples of filters:

            ('code', 'jack')                   -> code = 'jack'
            ('code', ('jack', 'jill'))         -> code in ('jack','jill')
            ('code', 'like', 'rv_%')           -> code like 'rv_%'
            ('code', '~', 'rv')                -> code ~ 'rv'
            "(code ='jill' or code = 'jack')"  -> full where clause 

        '''
        results = []

        project = Project.get_project_code()
        search = Search(search_type)

        if filters:
            my._add_filters(search, filters)
        
        if distinct:
            search.add_column(distinct, distinct=True)

        if order_bys:
            if isinstance(order_bys, basestring):
                order_bys = [order_bys]
            for order_by in order_bys:
                search.add_order_by(order_by)

        if limit:
            search.set_limit(limit)

        if offset:
            search.set_offset(offset)

        if show_retired:
            search.set_show_retired(True)

        if parent_key:
            search.add_parent_filter(parent_key)

        #import time
        #start = time.time()
        sobjects = search.get_sobjects()
        if return_sobjects:
            if single:
                if sobjects:
                    single_sobj = sobjects[0]
                else:
                    single_sobj = {}
                return single_sobj
            else:
                return sobjects

        # NOT NEEDED as it assumes all columns by default
        #if not columns:
        #    columns = search.get_columns()
            
        # convert
        search_keys = SearchKey.get_by_sobjects(sobjects,use_id=False)

        for i, sobject in enumerate(sobjects):
            #result = my._get_sobject_dict(sobject, columns)
            result = sobject.get_data()
            if columns:
                result = Common.subset_dict(result, columns)

            # if distinct is used, no search_key is obtained
            if not distinct:
                result['__search_key__'] = search_keys[i]
            results.append(result)

        if not single:
            ret_results = results
        else:
            if results:
                ret_results = results[0]
            else:
                # return a single empty sobject (empty dict)
                ret_results = {}
        

        if my.get_language() == 'python':
            if my.get_protocol() == 'local':
                return ret_results
            else:
                if isinstance(ret_results, unicode):
                    return ret_results.encode('utf-8')
                elif isinstance(ret_results, basestring):
                    return unicode(ret_results, errors='ignore').encode('utf-8')
                else: 
                    # could be a list or dictionary, for quick operation, str struction is the best 
                    # for xmlrpc transfer
                    return str(ret_results)
        else:
            return ret_results


    def fast_query(my, ticket, search_type, filters=None, limit=None):
        '''optimized query that does not take security into accunt.
        '''
        #if Config.get_value("security", "enable_fast_query") != 'true':
        #    raise TacticException("Cannot call fast_query() without enabling in TACTIC config file")
        security = Security()
        Environment.set_security(security)

        project_code = ticket.get("project")
        language = ticket.get("language")
        ticket = ticket.get("ticket")

        Project.set_project(project_code)
        my.set_language(language)

        return my._query(search_type=search_type, filters=filters, limit=limit)
 
    fast_query.exposed = True




    @xmlrpc_decorator
    def update(my, ticket, search_key, data={}, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):
        return my._update(search_key, data, metadata, parent_key, info, use_id, triggers)
    def _update(my, search_key, data={}, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):

        '''General update for updating sobject
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject.
            Note: this can also be an array, in which case, the data will
            be updated to each sobject represented by this search key
        @keyparam:
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
        metadata - metadata for the sobject
        parent_key - parent search key
        info - dictionary for ApiClientCmd
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on update


        @return:
        a dictionary representing the sobject with its current data.
           If search_key is an array, This will be an array of dictionaries
        '''
        assert(search_key)
        sobjects = my._get_sobjects(search_key)
        results = []
        for i, sobject in enumerate(sobjects):
            if type(data) == types.ListType:
                cur_data = data[i]
            else:
                cur_data = data

            if type(metadata) == types.ListType:
                cur_metadata = metadata[i]
            else:
                cur_metadata = metadata


            # set the values
            for name, value in cur_data.items():
                # ignore calculated attributes
                if name.startswith("__") and name.endswith("__"):
                    continue

                if name == "metadata":
                    sobject.add_metadata(value)
                else:
                    sobject.set_value(name, value)

            # set the meta data
            for name, value in cur_metadata.items():
                if name.startswith("__") and name.endswith("__"):
                    continue

                sobject.set_metadata_value(name, value)


            # set the parent
            if parent_key:
                parent = SearchKey.get_by_search_key(parent_key)
                if not parent:
                    raise ApiException("Parent [%s] does not exist" % parent_key)
                sobject.set_parent(parent)

            sobject.commit(triggers=triggers)
            

            # get the dictionary back
            sobject_dict = my._get_sobject_dict(sobject, use_id=use_id)
            results.append(sobject_dict)

        my.set_sobjects(sobjects)
        my.update_info(info)

        if type(search_key) == types.ListType:
            return results
        else:
            return results[0]

 
    @xmlrpc_decorator
    def update_multiple(my, ticket, data, triggers=True):
        '''Update for several sobjects in one function call.  The
        data structure contains all the infon needed to update and is
        formated as follows:

        data = {
            search_key1: { column1: value1, column2: value2 }
            search_key2: { column1: value1, column2: value2 }
        }


        @params:
        ticket - authentication ticket
        data - data structure containing update information for all
            sobjects
        triggers - boolean to fire trigger on update

        @keyparam:
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
        triggers - boolean to fire trigger on insert


        @return:
        a list of all the update sobjects
 
        '''

        if isinstance(data, basestring):
            data = jsonloads(data)

        search_keys = data.keys()
        use_id_list = []
        # auto detects use_id or not
        for search_key in search_keys:
            if search_key.find('id') != -1:
                use_id_list.append(True)
            else:
                use_id_list.append(False)

        sobjects = Search.get_by_search_keys(search_keys, keep_order=True)

        if len(sobjects) < len(search_keys):
            raise TacticException('Not all search keys have equivalent sobjects in the system.')

        results = []

        for idx, sobject in enumerate(sobjects):
            search_key = sobject.get_search_key(use_id=use_id_list[idx])
            sobject_data = data.get(search_key)
            if not sobject_data:
                print "search key [%s] does not exist in the system." %search_key
                continue
            for key, value in sobject_data.items():
                sobject.set_value(key, value)
            sobject.commit(triggers=triggers)

            sobject_dict = my._get_sobject_dict(sobject, use_id=use_id_list[idx])
            results.append(sobject_dict)

        return results


    @xmlrpc_decorator
    def insert_multiple(my, ticket, search_type, data, metadata=[], parent_key=None, use_id=False, triggers=True):
        '''Insert for several sobjects in one function call.  The
        data structure contains all the infon needed to update and is
        formated as follows:

        data = [
            { column1: value1, column2: value2,  column3: value3 },
            { column1: value1, column2: value2,  column3: value3 }
        ]

        metadata =  [
            { color: blue, height: 180 },
            { color: orange, height: 170 }
        ]


        @params:
        ticket - authentication ticket
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
            Note: this can also be an array.  Each data dictionary element in
            the array will be applied to the corresponding search key
       
        @keyparam:
       
        triggers - boolean to fire trigger on insert
        use_id - boolean to control if id is used in the search_key in returning sobject dict

        @return:
        a list of all the update sobjects
 
        '''

        if isinstance(data, basestring):
            data = jsonloads(data)



        if isinstance(metadata, basestring):
            metadata = jsonloads(metadata)

        if not isinstance(data, list):
            raise TacticException('data must be a list')

        if metadata:
            if len(metadata) != len(data):
                raise TacticException('If specified, metadata length has to match data length [%s]'%len(data))
            if not isinstance(metadata, list):
                raise TacticException('metadata must be a list')

        results = []
        metadata_item = {}


        # they all share the same parent_key if exists
        for idx,  data_item in enumerate(data):
            if metadata:
                metadata_item = metadata[idx]
                
            result = my._insert(search_type, data_item, metadata=metadata_item, parent_key=parent_key, use_id=use_id, triggers=triggers)
            results.append(result)

        return results


    @xmlrpc_decorator
    def insert(my, ticket, search_type, data, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):
        return my._insert(search_type, data, metadata, parent_key, info, use_id, triggers)
    def _insert(my, search_type, data, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):

        '''General insert for creating a new sobject
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        data - a dictionary of name/value pairs which will be used to update
               the sobject defined by the search_key.

        @keyparam:
        parent - set the parent key for this sobject
        info - info dictionary passed to the ApiClientCmd
        
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on insert

        @return:
        a single dictionary representing the sobject with it's current data
        ''' 

        # set the values
        sobject = SearchType.create(search_type)
        for name, value in data.items():
            if name == "metadata":
                sobject.set_metadata_value(name, value)
            else:
                #if name == "search_type" and value.find("?") == -1:
                #    raise SearchException("Improper search_type format for [%s]" % value)
                sobject.set_value(name, value)

        # set the meta data
        for name, value in metadata.items():
            sobject.set_metadata_value(name, value)

        # handle the parent
        if parent_key:
            parent = SearchKey.get_by_search_key(parent_key)
            if not parent:
                raise ApiException("Parent [%s] does not exist" % parent_key)
            sobject.set_parent(parent)

        sobject.commit(triggers=triggers)
        my.set_sobject(sobject)
        my.update_info(info)

        # return the data for this sobject
        sobject_dict = my._get_sobject_dict(sobject, use_id=use_id)
        return sobject_dict

    @xmlrpc_decorator
    def insert_update(my, ticket, search_key, data={}, metadata={}, parent_key=None, info={}, use_id=False, triggers=True):

        '''insert if the entry does not exist, update otherwise

        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject.

        @keyparams:
        data - a dictionary of name/value pairs which will be used to update
            the sobject defined by the search_key
        parent_key - parent search_key
        info - a dictionary of info passed to ApiClientCmd
        use_id - use id in the returned search key
        triggers - boolean to fire trigger on insert

        @return
        a dictionary representing the sobject with its current data.
        '''
        # search to see if the search_key exits
        assert(search_key)
        sobjects = my._get_sobjects(search_key, no_exception=True)

        # if it exists, the update
        if sobjects:
            return my._update(search_key, data, metadata, parent_key, info, use_id, triggers)

        # otherwise insert
        else:
            search_type = SearchKey.extract_search_type(search_key)
            # add code attribute
            code = SearchKey.extract_code(search_key)
            if code:
                data['code'] = code
            return my._insert(search_type, data, metadata, parent_key, info, use_id, triggers)



    @xmlrpc_decorator
    def get_unique_sobject(my, ticket, search_type, data={}):
        '''This is a special convenience function which will query for an
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
        filters = []
        for key, value in data.items():
            # assume all items are 'name = value' expressions
            filter = [key, value]
            filters.append(filter)

        sobject = my._query(search_type, filters, single=True, return_sobjects=True)
        if not sobject:
            sobject = my._insert(search_type, data)

        if isinstance(sobject, dict):
            sobject_dict = sobject
        else: # for the queried sobject
            sobject_dict = my._get_sobject_dict(sobject, use_id=False)
        
        return sobject_dict



    @xmlrpc_decorator
    def get_column_names(my, ticket, search_type):
        '''This method will get all of the column names associated with a search
        type'''
        search = Search(search_type)
        column_names = search.get_columns()
        return column_names





    @xmlrpc_decorator
    def get_table_info(my, ticket, search_type):
        '''This method will get all of the tables names associated with project
        of this search type'''

        from pyasm.biz import Project
        db_resource = Project.get_db_resource_by_search_type(search_type)
        impl = db_resource.get_database_impl()
        table_info = impl.get_table_info(db_resource)
        return table_info


    #
    # Instance methods
    #
    @xmlrpc_decorator
    def add_instance(my, ticket, search_key1, search_key2):
        '''Add an instance between two sobjects.  This requires that there
        is a instance relationship between the two sobjects defined in the
        schema

        @param:
        search_key1: the search_key to the first sobject
        search_key2: the search_key to the first sobject

        @return:
        the instance sobject created
        '''

        sobjects = my._get_sobjects(search_key1)
        if sobjects:
            sobject1 = sobjects[0]
        else:
            raise ApiException("SObject [%s] does not exist" % search_key1)

        sobjects = my._get_sobjects(search_key2)
        if sobjects:
            sobject2 = sobjects[0]
        else:
            raise ApiException("SObject [%s] does not exist" % search_key2)

        instance = sobject1.add_instance(sobject2)
        sobject_dict = my._get_sobject_dict(instance)
        return sobject_dict


    @xmlrpc_decorator
    def get_instances(my, ticket, search_key, search_type):
        '''Get all the instances of an sobject of a certain stype.  There
        must be an instance relationship between the sobject and the search
        type

        @param:
        search_key: the search_key to the sobject to get the instances
        search_type: the search_type of the related sobjects that the instances
            are attached to

        @return:
        the instance sobject created
        '''
        sobjects = my._get_sobjects(search_key)
        if sobjects:
            sobject = sobjects[0]
        else:
            raise ApiException("SObject [%s] does not exist" % search_key1)

        instances = sobject.get_instances(search_type)

        instance_dicts = []
        for instance in instances:
            instance_dict = my._get_sobject_dict(instance)

            instance_dicts.append(instance_dict)
        return instance_dicts


    @xmlrpc_decorator
    def remove_instance(my, ticket, search_key1, search_key2):
        '''Removes the instances between these two sobjects

        @param:
        search_key1: the search_key to the first sobject
        search_key2: the search_key to the first sobject

        @return:
        the instance sobject created
        '''

        sobjects = my._get_sobjects(search_key1)
        if sobjects:
            sobject1 = sobjects[0]
        else:
            raise ApiException("SObject [%s] does not exist" % search_key1)

        sobjects = my._get_sobjects(search_key2)
        if sobjects:
            sobject2 = sobjects[0]
        else:
            raise ApiException("SObject [%s] does not exist" % search_key2)


        sobject1.remove_instance(sobject2)


 
    #
    # Expression methods
    #
    @xmlrpc_decorator
    def eval(my, ticket, expression, search_keys=[], mode=None, single=False, vars={}, show_retired=False):
        '''Evaluate the expression.  This expression uses the TACTIC expression
        language to retrieve results.  For more information, refer to the
        expression language documentation.

        @param:
        expression: string expression
        search_keys: the starting point for the expression.
        mode: string|expression - determines the starting mode of the expression
        single: True|False - True value forces a single return value
        show_retired: True|False - Flag which determines whether to
            return retired sobjects

        @return:
        results of the expression.  The results depend on the exact nature
        of the expression.
        
        '''

        if search_keys:
            sobjects = my._get_sobjects(search_keys)
        else:
            sobjects = None

        parser = ExpressionParser()
        results = parser.eval(expression, sobjects, mode=mode, single=single, vars=vars, show_retired=show_retired)
        import pyasm
        if type(results) == types.ListType:
            if not results:
                pass
            elif isinstance(results[0], pyasm.search.SObject):
                new_results = []
                import time
                start = time.time()
                results = my._get_sobjects_dict(results)
                #for sobject in results:
                #    sobject_dict = my._get_sobject_dict(sobject)
                #    new_results.append(sobject_dict)
                #results = new_results

        else:
            if isinstance(results, pyasm.search.SObject):
                results = my._get_sobject_dict(results)

        if my.get_language() == 'python':
            if my.get_protocol() == 'local':
                return results
            else:
                if isinstance(results, unicode):
                    return results.encode('utf-8')
                elif isinstance(results, basestring):
                    return unicode(results, errors='ignore').encode('utf-8')
                else: 
                    # could be a list or dictionary, for quick operation, str struction is the best 
                    # for xmlrpc transfer
                    return str(results)
            
        else:
            return results


    # FIXME: need to test this first
    """
    @xmlrpc_decorator
    def get_rest_data(my, ticket, url):
        conn = urllib.open(url)
        data = conn.read()
        jsondumps(data)
        return data
    """


    #
    # Higher level SObject methods
    #
    @xmlrpc_decorator
    def create_search_type(my, ticket, search_type, title, description='', has_pipeline=False):
        '''Method to create a new search type

        @params:
        search_type - Newly defined search_type
        title - readable title to display this search type as
        description - a brief description of this search type
        has_pipeline - determines whether this search type goes through a
            pipeline.  Simply puts a pipeline_code column in the table.

        @return
        the newly created search type

        '''
        from tactic.ui.app import SearchTypeCreatorCmd

        project_code = Project.get_project_code()
        kwargs = {
            'database': project_code,
            'namespace': project_code,
            'schema': 'public',

            'search_type_name': search_type,
            'asset_description': description,
            'asset_title': title,
            'sobject_pipeline': has_pipeline,
        }

        creator = SearchTypeCreatorCmd(**kwargs)
        creator.execute()

        sobject = creator.get_sobject()
        sobject_dict = my._get_sobject_dict(sobject)
        return sobject_dict


    @xmlrpc_decorator
    def add_column_to_search_type(my, ticket, search_type, column_name, column_type):
        '''Adds a new column to the search type
        
        @params
        ticket - authentication ticket
        search_type - the search type that the new column will be added to
        column_name - the name of the column to add to the database
        column_type - the type of the column to add to the database

        @return
        True if column was created, False if column exists
        '''

        search_type_sobj = SearchType.get(search_type)
        table = search_type_sobj.get_table()

        db_resource = Project.get_db_resource_by_search_type(search_type)
        database = search_type_sobj.get_database()

        sql = DbContainer.get(db_resource)

        # Check to see if column exists
        table_info = sql.get_column_info(table)
        if table_info.get(column_name):
            return False

        if sql.get_database_type() == 'SQLServer':
            statement = 'ALTER TABLE [%s] ADD "%s" %s' % \
                (table, column_name, column_type)
        else:
            statement = 'ALTER TABLE "%s" ADD COLUMN "%s" %s' % \
                (table, column_name, column_type)
        sql.do_update(statement)
    
        return True




    @xmlrpc_decorator
    def get_by_search_key(my, ticket, search_key):
        '''Gets the info on an sobject based on search key

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        #sobject = SearchKey.get_by_search_key(search_key)
        sobjects = my._get_sobjects(search_key)
        if not sobjects:
            raise ApiException("SObject [%s] does not exist" % search_key)

        if type(search_key) == types.ListType:
            sobject_dicts = []
            for sobject in sobjects:
                sobject_dict = my._get_sobject_dict(sobject)
                sobject_dicts.append(sobject_dict)
            return sobject_dicts
        else:
            sobject = sobjects[0]
            # return the data for this sobject
            return my._get_sobject_dict(sobject)

    @xmlrpc_decorator
    def get_by_code(my, ticket, search_type, code):
        '''Gets the info on an sobject based on search_type and code

        @params
        ticket - authentication ticket
        search_type - the search_type of the sobject to search for
        code - the code of the sobject to search for

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        #sobject = SearchKey.get_by_search_key(search_key)
        sobject = Search.get_by_code(search_type, code)
        if sobject:
            return my._get_sobject_dict(sobject)
        else:
            return {}



    @xmlrpc_decorator
    def delete_sobject(my, ticket, search_key, include_dependencies=False):
        '''Invokes the delete method.  Note: this function may fail due
        to dependencies.  Tactic will not cascade delete.  This function
        should be used with extreme caution because, if successful, it will
        permenently remove the existence of an sobject

        @params
        ticket - authentication ticket
        search_key - the key identifying 
                      the search_type table.
        include_dependencies - true/false

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        sobjects = my._get_sobjects(search_key)
        if not sobjects:
            raise ApiException("SObject [%s] does not exist" % search_key)
        sobject = sobjects[0]

        # delete this sobject
        if include_dependencies:
            from tactic.ui.tools import DeleteCmd
            cmd = DeleteCmd(sobject=sobject, auto_discover=True)
            cmd.execute()
        else:
            sobject.delete()

        return my._get_sobject_dict(sobject)


    @xmlrpc_decorator
    def retire_sobject(my, ticket, search_key):
        '''Invokes the retire method of the sobject

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject [%s] does not exist" % search_key)

        # retire this sobject
        sobject.retire()

        return my._get_sobject_dict(sobject)


    @xmlrpc_decorator
    def reactivate_sobject(my, ticket, search_key):
        '''Invokes the reactivate method of the sobject

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject [%s] does not exist" % search_key)

        # reactivate this sobject
        sobject.reactivate()

        return my._get_sobject_dict(sobject)


    @xmlrpc_decorator
    def clone_sobject(my, ticket, search_key, data={}):
        '''Clone an sobject.

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        data - a dictionary of data to update the sobject with

        @return
        sobject - a dictionary that represents values of the sobject in the
            form name/value pairs
        '''
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject [%s] does not exist" % search_key)

        clone = sobject.clone()

        for name, value in data.items():
            clone.set_value(name, value)
        clone.commit()

        return my._get_sobject_dict(clone)



    @xmlrpc_decorator
    def set_widget_setting(my, ticket, key, value):
        '''API Function: set_widget_settings(key, value)
        Set widget setting for current user and project

        @param
        key - unique key to identify this setting
        value - value the setting should be set to

        @return
        None
        '''
        from pyasm.web import WidgetSettings
        WidgetSettings.set_value_by_key(key, value)
        return True


    @xmlrpc_decorator
    def get_widget_setting(my, ticket, key):
        '''API Function: set_widget_settings(key, value)
        Get widget setting for current user and project

        @param
        key - unique key to identify this setting

        @return
        value of setting
        '''
        from pyasm.web import WidgetSettings
        return WidgetSettings.get_value_by_key(key)






    #
    # sType Hierarchy methods
    #

    @xmlrpc_decorator
    def get_parent(my, ticket, search_key, columns=[], show_retired=False):
        '''gets the parent of an sobject

        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @keyparam:
        columns - the columns that will be returned in the sobject
        show_retired - it defaults to False so it does not show retired parent if that's the case

        @return
        sobject - the parent sobject
        '''

        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject [%s] does not exist" % search_key)

        parent = sobject.get_parent(show_retired=show_retired)
        # this check is for the condition if parent_type is * and the parent is retrieved by Search.get_by_id()
        if show_retired == False and parent and parent.is_retired():
            parent = None

        return my._get_sobject_dict(parent, columns)





    @xmlrpc_decorator
    def get_all_children(my, ticket, search_key, child_type, filters=[], columns=[]):
        '''Get all children of a particular child type of an sobject

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        child_type - the search_type of the children to search for
        filters - extra filters on the query : see query method for examples
        columns - columns of sobject

        @return
        sobjects - a list of child sobjects 
        '''
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject [%s] does not exist" % search_key)

        #children = sobject.get_all_children(child_type)
        search = sobject.get_all_children_search(child_type)
        my._add_filters(search, filters)
        children = search.get_sobjects()
        

        # go through get_value which handles security filters
        results = []
        for child in children:
            results.append( my._get_sobject_dict(child, columns))

        return results



    @xmlrpc_decorator
    def get_parent_type(my, ticket, search_key):
        '''gets of the parent search type

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @return
        the parent search_type
        '''
        schema = Schema.get()
        if not schema:
            return []

        return schema.get_parent_type(search_key)


    @xmlrpc_decorator
    def get_child_types(my, ticket, search_key):
        '''gets of the child search types

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @return
        a list of child search_types
        '''
        schema = Schema.get()
        if not schema:
            return []

        return schema.get_child_types(search_key)



    @xmlrpc_decorator
    def get_types_from_instance(my, ticket, instance_type):
        '''gets the connector types from an instance type

        @params
        ticket - authentication ticket
        instance_type - the search type of the instance

        @return
        (from_type, parent_type)
            a tuple with the from_type and the parent_type.  The from_type is
            the connector type and the parent type is the search type of the
            parent of the instance
        '''
        schema = Schema.get()
        if not schema:
            return []

        return schema.get_types_from_instance(instance_type)


    @xmlrpc_decorator
    def connect_sobjects(my, ticket, src_sobject, dst_sobject, context='default'):
        '''connect two sobjects together

        @params
        src_sobject: the original sobject from which the connection starts
        dst_sobject: the sobject to which the connection connects to
        context: an arbirarty parameter which defines type of connection

        @return
        the connection sobject
        '''
        from pyasm.biz import SObjectConnection

        if type(src_sobject) == types.DictType:
            src_sobject = src_sobject.get('__search_key__')
        if type(dst_sobject) == types.DictType:
            dst_sobject = dst_sobject.get('__search_key__')

        sobject_a = SearchKey.get_by_search_key(src_sobject)
        sobject_b = SearchKey.get_by_search_key(dst_sobject)
        if not sobject_a:
            raise ApiException('Source sObject [%s] is not found ' %src_sobject)
        if not sobject_b:
            raise ApiException('Destination sObject [%s] is not found ' %dst_sobject)
        connection = SObjectConnection.create(sobject_a, sobject_b, context)
        sobject_dict = my._get_sobject_dict(connection)
        return sobject_dict


    @xmlrpc_decorator
    def get_connected_sobjects(my, ticket, src_sobject, context=''):
        '''get all of the connected sobjects

        @params
        src_sobject: the original sobject from which the connection starts
        context: an arbirarty parameter which defines type of connection

        @return
        a list of connected sobjects
        '''
        from pyasm.biz import SObjectConnection
        if type(src_sobject) == types.DictType:
            src_sobject = src_sobject.get('__search_key__')

        sobject_a = SearchKey.get_by_search_key(src_sobject)

        if not sobject_a:
            raise ApiException('Source sObject [%s] is not found ' %src_sobject)

        connections, sobjects = SObjectConnection.get_connected_sobjects(sobject_a, context=context)
        sobject_list = []
        for sobject in sobjects:
            sobject_dict = my._get_sobject_dict(sobject)
            sobject_list.append(sobject_dict)
        return sobject_list


    @xmlrpc_decorator
    def get_connected_sobject(my, ticket, src_sobject, context=''):
        '''get all of the connected sobjects

        @params:
        src_sobject - the original sobject from which the connection starts
        context - an arbirarty parameter which defines type of connection

        @return:
        a single sobject
        '''
        from pyasm.biz import SObjectConnection
        if type(src_sobject) == types.DictType:
            src_sobject = src_sobject.get('__search_key__')

        sobject_a = SearchKey.get_by_search_key(src_sobject)
        if not sobject_a:
            raise ApiException('Source sObject [%s] is not found ' %src_sobject)

        sobject = SObjectConnection.get_connected_sobject(sobject_a, context=context)
        sobject_dict = my._get_sobject_dict(sobject)

        return sobject_dict



    #
    # Directory methods
    #
    @xmlrpc_decorator
    def get_paths(my, ticket, search_key, context="publish", version=-1, file_type='main', level_key=None, single=False, versionless=False, process=None):
        '''method to get paths from an sobject

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        @keyparams:
        context - context of the snapshot
        version - version of the snapshot
        level_key - the unique identifier of the level that this
            was checked into
        single - returns a single path for each category instead of a list
            this is useful if it is know that there is only one file in the
            snapshot
        versionless - boolean to return the versionless snapshot, which takes a version of -1 (latest)  or 0 (current)

        @return
        A dictionary of lists representing various paths.  The paths returned
        are as follows:
        - client_lib_paths: all the paths to the repository relative to the client
        - lib_paths: all the paths to the repository relative to the server
        - sandbox_paths: all of the paths mapped to the sandbox
        - web: all of the paths relative to the http server
    
        '''

        sobjects = my._get_sobjects(search_key)
        sobject = sobjects[0]

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        search_key = SearchKey.get_by_sobject(sobject)

        if process:
            context = None

        # get the level object
        if level_key:
            level = SearchKey.get_by_search_key(level_key)
            if not level:
                raise ApiException("Level SObject with key [%s] does not exist" % level_key)
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None

        if not versionless:
            snapshot = Snapshot.get_snapshot(search_type, search_id, context, version, level_type=level_type, level_id=level_id, process=process)
        else:
            if version in [-1, 'latest']:
                versionless_mode = 'latest'
            else:
                versionless_mode = 'current'
            snapshot = Snapshot.get_versionless(search_type, search_id, context , mode=versionless_mode, create=False, process=process)

        if not snapshot:
            # This is probaby to0 strict
            #raise ApiException("Snapshot for [%s] with context [%s], version [%s] does not exist" % (search_key, context, version))
            paths = {}
            return paths


        paths = {}
        if file_type == "*":
            client_lib_paths = snapshot.get_all_client_lib_paths()
            sandbox_paths = snapshot.get_all_sandbox_paths()
            web_paths = snapshot.get_all_remote_web_paths()
            lib_paths = snapshot.get_all_lib_paths()

            if single:
                paths['client_lib_path'] = client_lib_paths[0]
                paths['sandbox_path'] = sandbox_paths[0]
                paths['web_path'] = web_paths[0]
                paths['lib_path'] = lib_paths[0]
            else:
                paths['client_lib_paths'] = client_lib_paths
                paths['sandbox_paths'] = sandbox_paths
                paths['web_paths'] = web_paths
                paths['lib_paths'] = lib_paths


        else:
            client_lib_path = snapshot.get_client_lib_path_by_type(file_type)
            if not client_lib_path:
                raise ApiException("File of type [%s] does not exist in snapshot [%s]" % (file_type, snapshot.get_code()) )

            sandbox_path = snapshot.get_sandbox_path_by_type(file_type)
            web_path = snapshot.get_remote_web_path_by_type(file_type)
            lib_path = snapshot.get_lib_path_by_type(file_type)
            relative_path = snapshot.get_web_path_by_type(file_type)

            if single:
                paths['client_lib_path'] = client_lib_path
                paths['sandbox_path'] = sandbox_path
                paths['web_path'] = web_path
                paths['lib_path'] = lib_path
                paths['relative_path'] = relative_path
            else:
                paths['client_lib_paths'] = [client_lib_path]
                paths['sandbox_paths'] = [sandbox_path]
                paths['web_paths'] = [web_path]
                paths['lib_paths'] = [lib_path]
                paths['relative_path'] = [relative_path]
        return paths




    @xmlrpc_decorator
    def get_base_dirs(my, ticket):
        '''get all of the base directories defined on the server.'''
        
        from pyasm.security import Site
        site = Site.get()
        if site:
            data = {}
            data['asset_base_dir'] = site.get_asset_dir(alias="default")
            data['web_base_dir'] = site.get_web_dir(alias="default")
            return data
        
        data = Config.get_section_values("checkin")
        for key, value in data.items():
            if value.strip().startswith('{'):
                
                try:
                    sub_value = eval(value.strip())
                    value = sub_value
                    data[key] = value
                except:
                    pass

       
        return data


    @xmlrpc_decorator
    def get_handoff_dir(my, ticket):
        '''simple methods that returns a temporary path that files can be
        copied to
       
        @params
        ticket - authentication ticket

        @return
        the directory to copy a file to handoff to Tactic without having to
        go through http protocol
        
        '''
        #web = WebContainer.get_web()
        #return web.get_client_handoff_dir(ticket)
        if type(ticket) == types.DictType:
            ticket = ticket.get("ticket")
        env = Environment.get_env_object()

        if my.get_protocol() == 'local':
            return env.get_server_handoff_dir(ticket)
        else:
            return env.get_client_handoff_dir(ticket)



    @xmlrpc_decorator
    def get_plugin_dir(my, ticket, plugin_code):
        '''gets the plugin directory from the client perspective'''

        if isinstance(plugin_code, SObject):
            plugin = plugin_code
            plugin_code = plugin.get("code")
        elif isinstance(plugin_code, dict):
            plugin = plugin_code
            plugin_code = plugin.get("code")
        else:
            search = Search("config/plugin")
            search.add_filter("code", plugin_code)
            plugin = search.get_sobject()
        if not plugin:
            rel_dir = plugin_code
        else:
            rel_dir = plugin.get("rel_dir")

        if plugin_code.startswith("TACTIC"):
            return "/tactic/builtin_plugins/%s" % rel_dir
        else:
            return "/tactic/plugins/%s" % rel_dir



    @xmlrpc_decorator
    def clear_upload_dir(my, ticket):
        '''method to clear the temp directory where files will be uploaded to'''
        upload_dir = Environment.get_upload_dir()
        if not os.path.exists(upload_dir):
            return False

        if not os.path.isdir (upload_dir):
            return False

        # put in a failsafe
        tmp_dir = Environment.get_tmp_dir()
        assert upload_dir.startswith(tmp_dir)

        shutil.rmtree(upload_dir)
        return True




    @xmlrpc_decorator
    def get_client_dir(my, ticket, snapshot_code, file_type='main', mode='client_repo'):
        '''method that returns the directory segment of a snapshot for a particular
           file type and mode
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code of a snapshot
        file_type - each file in a snapshot is identified by a file type.
            This parameter specifies which file type to return.  Defaults to 'main'
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

        @return
        string - directory segment for a snapshot and file type

        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')

        if snapshot_code.find("?") == -1:
            snapshot = Snapshot.get_by_code(snapshot_code)
        else:
            snapshot = Search.get_by_search_key(snapshot_code)

        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)
        assert mode in ['lib', 'client_repo', 'sandbox', 'local_repo', 'web', 'relative']
        dir = ''
        if mode == 'lib':
            dir = snapshot.get_lib_dir(file_type=file_type)
        elif mode == 'client_repo':
            dir = snapshot.get_client_lib_dir(file_type=file_type)
        elif mode == 'sandbox':
            dir = snapshot.get_sandbox_dir(file_type=file_type)
        elif mode == 'local_repo':
            dir = snapshot.get_local_repo_dir(file_type=file_type)
        elif mode == 'web':
            dir = snapshot.get_web_dir(file_type=file_type)
        elif mode == 'relative':
            dir = snapshot.get_relative_dir(file_type=file_type)

        return dir


    @xmlrpc_decorator
    def get_path_from_snapshot(my, ticket, snapshot_code, file_type='main', mode='client_repo'):
        '''method that returns the checked in path of a file
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code or search_key of a snapshot
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

        @return
        string - the directory to copy a file to handoff to Tactic without having to
        go through http protocol

        '''

        if not snapshot_code:
            return ''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')

        if snapshot_code.find("?") == -1:
            snapshot = Snapshot.get_by_code(snapshot_code)
        else:
            snapshot = Search.get_by_search_key(snapshot_code)
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        assert mode in ['lib', 'client_repo', 'sandbox', 'local_repo', 'web', 'relative']
        dir = ''
        if mode == 'lib':
            dir = snapshot.get_lib_dir(file_type=file_type)
        elif mode == 'client_repo':
            dir = snapshot.get_client_lib_dir(file_type=file_type)
        elif mode == 'sandbox':
            dir = snapshot.get_sandbox_dir(file_type=file_type)
        elif mode == 'local_repo':
            dir = snapshot.get_local_repo_dir(file_type=file_type)
        elif mode == 'web':
            dir = snapshot.get_web_dir(file_type=file_type)
        elif mode == 'relative':
            dir = snapshot.get_relative_dir(file_type=file_type)
       
        filename = snapshot.get_file_name_by_type(file_type)
        if filename:
            path = "%s/%s" % (dir, filename)
        else:
            path = ""
        return path


    @xmlrpc_decorator
    def get_expanded_paths_from_snapshot(my, ticket, snapshot_code, file_type='main'):
        '''method that returns the expanded path of a snapshot (used for 
        ranges of files
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code of a snapshot
        file_type - each file in a snapshot is identified by a file type.
            This parameter specifies which type.  Defaults to 'main'


        @return
        the directory to copy a file to handoff to Tactic without having to
        go through http protocol
        
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        client_lib_dir = snapshot.get_client_lib_dir(file_type=file_type)

        file_names = snapshot.get_expanded_file_names(file_type)
        paths = []
        for file_name in file_names:
            path = "%s/%s" % (client_lib_dir, file_name)
            paths.append(path) 

        return paths



    @xmlrpc_decorator
    def get_all_paths_from_snapshot(my, ticket, snapshot_code, mode='client_repo', expand_paths=False, filename_mode='',file_types=[]):
        '''method that returns all the files in a snapshot
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code of a snapshot
        
        @return
        the directory to copy a file to handoff to Tactic without having to
        go through http protocol
        
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')

        if snapshot_code.find("?") == -1:
            snapshot = Snapshot.get_by_code(snapshot_code)
        else:
            snapshot = Search.get_by_search_key(snapshot_code)

        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        if file_types:
            paths = []
            for file_type in file_types:
                paths = snapshot.get_paths_by_type(file_type, mode=mode, filename_mode=filename_mode)
        else:
            paths = snapshot.get_all_lib_paths(expand_paths=expand_paths, mode=mode, filename_mode=filename_mode)

        return paths





    @xmlrpc_decorator
    def get_dependencies(my, ticket, snapshot_code, mode='explicit', tag='main', include_paths=False, include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        '''method that returns of the dependent snapshots of a certain tag
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code of a snapshot
        mode - explict (get version as defined in snapshot)
             - latest
             - current
        tag - retrieve only dependencies that have this named tag
        include_paths - flag to specify whether to include a __paths__ property
            containing a list of all paths in the dependent snapshots
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            dependent snapshots
        include_files - includes all of the file objects referenced in the
            snapshots
        repo_mode - client_repo, lib, web,...
        show_retired - show the retired results as well if applicable


        @return
        a list of snapshots
        
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        results = snapshot.get_ref_snapshots(name='tag', value=tag, mode=mode, show_retired=show_retired)
        snapshots = []

        # preprocess and get all file objects
        if include_files:
            all_files = Snapshot.get_files_dict_by_snapshots([snapshot])


        for result in results:
            snapshot = my._get_sobject_dict(result)

            if include_paths:
                paths = result.get_all_lib_paths(mode=repo_mode)
                snapshot['__paths__'] = paths

            if include_paths_dict:
                paths = result.get_all_paths_dict(mode=repo_mode)
                snapshot['__paths_dict__'] = paths

            if include_files:
                snapshot_code = snapshot.get('code')
                file_list = all_files.get(snapshot_code)
                file_dict_list = []
                if file_list:
                    for file in file_list:
                        file_dict = my._get_sobject_dict(file)
                        file_dict_list.append(file_dict)
                    snapshot['__files__'] = file_dict_list


            snapshots.append(snapshot)
        return snapshots


    @xmlrpc_decorator
    def get_all_dependencies(my, ticket, snapshot_code, mode='explicit', type='ref', include_paths=False, include_paths_dict=False, include_files=False, repo_mode='client_repo', show_retired=False):
        '''method that returns of the dependent snapshots for a given
        snapshot
       
        @params
        ticket - authentication ticket
        snapshot_code - unique code of a snapshot
        mode - explict (get version as defined in snapshot)
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
        repo_mode - client_repo, lib, web,...
        show_retired - show the retired results as well if applicable

        @return
        a list of snapshots
        
        '''

        if isinstance(snapshot_code, dict):
            snapshot_code = snapshot_code.get('code')

        if snapshot_code.find("?") == -1:
            snapshot = Snapshot.get_by_code(snapshot_code)
        else:
            snapshot = Search.get_by_search_key(snapshot_code)
        
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        results = snapshot.get_all_ref_snapshots(mode=mode, type=type, show_retired=show_retired)
        snapshots = []



        for result in results:
            snapshot = my._get_sobject_dict(result)

            if include_paths:
                paths = result.get_all_lib_paths(mode=repo_mode)
                snapshot['__paths__'] = paths

            if include_paths_dict:
                paths = result.get_all_paths_dict(mode=repo_mode)
                snapshot['__paths_dict__'] = paths


            snapshots.append(snapshot)


        # preprocess and get all file objects
        if include_files:
            all_files = Snapshot.get_files_dict_by_snapshots(results)
            for idx, result in enumerate(results):
                snapshot = snapshots[idx]
                
                snapshot_code = result.get_code()
                file_list = all_files.get(snapshot_code)
                file_dict_list = []
                # empty snapshot won't have file_list
                if file_list:
                    for file in file_list:
                        file_dict = my._get_sobject_dict(file)
                        file_dict_list.append(file_dict)
                snapshot['__files__'] = file_dict_list

        return snapshots




    @xmlrpc_decorator
    def get_preallocated_path(my, ticket, snapshot_code, file_type='main', file_name='', mkdirs=True, protocol='client_repo', ext='', checkin_type='strict'):
        '''Gets the preallocated path for this snapshot.  It not assumed that
        this checkin actually exists in the repository and will create virtual
        entities to simulate a checkin.  This method can be used to determine
        where a checkin will go.

        @params
        ticket - authentication ticket
        snapshot_code - the code of a preallocated snapshot.  This can be
            create by get_snapshot()
        file_type - the type of file that will be checked in.  Some naming
            conventions make use of this information to separate directories
            for different file types
        file_name - the desired file name of the preallocation.  This information
            may be ignored by the naming convention or it may use this as a
            base for the final file name
        mkdir - an option which determines whether the directory of the
            preallocation should be created
        protocol - It's either client_repo or None. It determines whether the
            path is from a client or server perspective
        ext - force the extension of the file name returned
        checkin_type - strict, auto , or '' can be used.. A naming entry in the naming, if found,  will be used to determine the checkin type

        @return
        the path where () expects the file to be checked into
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)

        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        parent = None
        path = snapshot.get_preallocated_path(file_type, file_name, mkdirs, protocol, ext, parent, checkin_type)
        return path

                    



    @xmlrpc_decorator
    def get_virtual_snapshot_path(my, ticket, search_key, context, snapshot_type="file", level_key=None, file_type='main', file_name='', mkdirs=False, protocol='client_repo', ext='', checkin_type=''):
        '''creates a virtual snapshot and returns a path that this snapshot
        would generate through the naming conventions''
        
        @params
        snapshot creation:
        -----------------
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin
        snapshot_type - [optional] descibes what kind of a snapshot this is.
            More information about a snapshot type can be found in the
            prod/snapshot_type sobject
        description - [optional] optional description for this checkin
        level_key - the unique identifier of the level that this
            is to be checked into

        path creation:
        --------------
        file_type: the type of file that will be checked in.  Some naming
            conventions make use of this information to separate directories
            for different file types
        file_name: the desired file name of the preallocation.  This information
            may be ignored by the naming convention or it may use this as a
            base for the final file name
        mkdir: an option which determines whether the directory of the
            preallocation should be created
        protocol: It's either client_repo, sandbox, or None. It determines whether the
            path is from a client or server perspective
        ext: force the extension of the file name returned
        checkin_type - strict, auto, '' can be used to predetermine the checkin_type for get_preallocated_path()


        @return
        path as determined by the naming conventions
        '''
        sobjects = my._get_sobjects(search_key)
        sobject = sobjects[0]

        # get the level object
        if level_key:
            levels = my._get_sobjects(level_key)
            level = levels[0]
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None

        description = "No description"

        # create a virtual snapshot
        snapshot = Snapshot.create(sobject, snapshot_type=snapshot_type, context=context, description=description, level_type=level_type, level_id=level_id, commit=False)

        path = snapshot.get_preallocated_path(file_type, file_name, mkdirs, protocol, ext=ext, checkin_type=checkin_type)
        return path




    @xmlrpc_decorator
    def upload_file(my, ticket, filename, data):
        '''uses http protocol to upload a file through XMLRPC

        @params
        ticket - authentication ticket
        filename - the name of the file that will be uploaded
        data - binary form of the data

        @usage
        file_path = "C:/test.jpg"
        file = open(file_path, 'rb')
        data = xmlrpclib.Binary( file.read() )
        file.close()
        server.upload_file(ticket, file_path, data)
        '''

        filename = os.path.basename(filename)
        filename = filename.replace("\\", "/")
        upload_dir = Environment.get_upload_dir()
        upload_path = "%s/%s" % (upload_dir, filename)
        file = open(upload_path, 'wb')
        file.write(data.data)
        file.close()
        return True



    @xmlrpc_decorator
    def get_upload_file_size(my, ticket, filename):
        '''get the current file size of a file that is uploading'''

        filename = os.path.basename(filename)

        env = Environment.get()
        handoff_dir = env.get_server_handoff_dir()
        if handoff_dir:
            handoff_path = "%s/%s" % (handoff_dir, filename)
            print "FIXME: check handoff_path: ", handoff_path


        upload_dir = Environment.get_upload_dir()
        upload_path = "%s/%s" % (upload_dir, filename)
        print "Upload path: [%s]" % upload_path
        if not os.path.exists(upload_path):

            print "WARNING: does not exist."
            return 0
        return os.path.getsize(upload_path)


    #
    # Checkin/checkout methods / snapshot methods
    #

    @xmlrpc_decorator
    def create_snapshot(my, ticket, search_key, context, snapshot_type="file",
            description="No description", is_current=True, level_key=None,
            is_revision=False, triggers=True):
        '''creates an empty snapshot
        
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin
        snapshot_type - [optional] descibes what kind of a snapshot this is.
            More information about a snapshot type can be found in the
            prod/snapshot_type sobject
        description - [optional] optional description for this checkin
        is_current - flag to determine if this checkin is to be set as current
        is_revision - flag to set this as a revision instead of a version
        level_key - the unique identifier of the level that this
            is to be checked into

        @keyparam:
        triggers - boolean to fire triggers on insert

        @return
        dictionary representation of the snapshot created for this checkin
        '''
        sobjects = my._get_sobjects(search_key)
        sobject = sobjects[0]

        if level_key:
            levels = my._get_sobjects(level_key)
            level = levels[0]
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None

        snapshot = Snapshot.create(sobject, snapshot_type=snapshot_type, context=context, description=description, is_current=is_current, level_type=level_type, level_id=level_id, is_revision=is_revision, triggers=triggers)
        return my._get_sobject_dict(snapshot)



    @xmlrpc_decorator
    def simple_checkin(my, ticket, search_key, context, file_path, snapshot_type="file", description="No description",use_handoff_dir=False, file_type='main',is_current=True, level_key=None, metadata={}, mode=None, is_revision=False, info={}, keep_file_name=False, create_icon=True, checkin_cls='pyasm.checkin.FileCheckin', context_index_padding=None, checkin_type="strict", source_path=None, version=None, process=None):

        '''simple methods that checks in a previously uploaded file
       
        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin
        file_path - path of the file that was previously uploaded
        snapshot_type - [optional] descibes what kind of a snapshot this is.
            More information about a snapshot type can be found in the
            prod/snapshot_type sobject
        descripton - [optional] optional description for this checkin
        file_type - [optional] optional description for this checkin
        level_key - unique identifier for the level to check this into
        metadata - a dictionary of values that will be stored as metadata
            on the snapshot
        mode - the mode in which files are moved: inplace, upload, copy, move
        is_revision - flag to set this as a revision instead of a version
        info - dictionary for ApiClientCmd
        keep_file_name - keep the original file name
        create_icon - Create an icon by default
        context_index_padding - determines the padding used for context
            indexing: ie: design/0001
        checkin_type - auto or strict which controls whether to auto create versionless
        source_path - explicitly give the source path
        version - force a version for this check-in

        @return
        dictionary representation of the snapshot created for this checkin
        '''
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        file_path = file_path.replace("\\", "/")
        # store the source file_path
        if not source_path:
            source_paths = [file_path]
        else:
            source_paths = [source_path]

        old_filename = os.path.basename(file_path)
        #filename = File.get_filesystem_name(old_filename)
        filename = old_filename


        env = Environment.get()
        if mode == 'inplace':
            upload_path = file_path
        else:
            if use_handoff_dir:
                dir = env.get_server_handoff_dir()
            else:
                dir = env.get_upload_dir()


            if checkin_type == 'auto' or not checkin_type:
                # In "auto" mode, we can make some assumptions: the file
                # location is based on the context
                parts = context.split("/")
                if len(parts) > 2:
                    subcontext = "/".join( parts[1:-1] )
                    auto_dir = "%s/%s" % (dir, subcontext)
                    if os.path.exists(auto_dir):
                        dir = auto_dir



            upload_path = "%s/%s" % (dir, filename)
            old_path = '%s/%s' %(dir, old_filename)
            # the upload logic may have already done the conversion
            if filename != old_filename and os.path.exists(old_path):
                shutil.move(old_path, '%s/%s' %(dir, filename))

        file_paths = [upload_path]
        file_types = [file_type]

        # if this is a file, then try to create an icon
        if os.path.isfile(upload_path) and create_icon:
            icon_creator = IconCreator(upload_path)
            icon_creator.execute()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()
            if web_path:
                # if this is pure icon context, then don't check in icon
                # as the main file.  It's a big waste of space to keep
                # original around
                if context == 'icon':
                    shutil.copy(web_path, upload_path)

                file_paths = [upload_path, web_path, icon_path]
                file_types = [file_type, 'web', 'icon']

                source_paths.append(web_path)
                source_paths.append(icon_path)


        # get the level object
        if level_key:
            level = SearchKey.get_by_search_key(level_key)
            if not level:
                raise ApiException("Level SObject with key [%s] does not exist" % level_key)
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None


        checkin_args = [sobject, file_paths]
        checkin_kwargs = {'file_types': file_types, 'context': context,
            'snapshot_type': snapshot_type, 'description': description,
            'is_current': is_current, 'source_paths': source_paths,
            'level_type': level_type, 'level_id': level_id,
            'mode': mode, 'is_revision': is_revision,
            'keep_file_name': keep_file_name,
            'context_index_padding': context_index_padding,
            'checkin_type': checkin_type, 'version': version,
            'process': process
        }

        checkin = Common.create_from_class_path(checkin_cls, checkin_args, checkin_kwargs)


        checkin.execute()

        

        # get values from snapshot
        snapshot = checkin.get_snapshot()
        file_sobjs = checkin.get_file_objects()
        file_dicts = []
        for file_sobj in file_sobjs:
            file_dict = my._get_sobject_dict(file_sobj)
            file_dicts.append(file_dict)



        # NOTE: this might need to be an argument for FileCheckin?
        if metadata:
            snapshot.add_metadata(metadata, replace=True)
            snapshot.commit()
        
        my.set_sobject(sobject)

        info['snapshot'] = snapshot
        my.update_info(info)

        snapshot_dict = my._get_sobject_dict(snapshot)
        snapshot_dict['__file_sobjects__'] = file_dicts

        # include paths for all the files that are checked in
        if mode == 'local':
            local_paths = snapshot.get_all_local_repo_paths()
            snapshot_dict['__paths__'] = local_paths

        #print "SQL Commit Count: ", Container.get('Search:sql_commit')
        return snapshot_dict



    @xmlrpc_decorator
    def group_checkin(my, ticket, search_key, context, file_path, file_range_val, snapshot_type='sequence', description="", file_type='main', metadata={}, mode=None, is_revision=False, info={}):
        '''checkin a range of files

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        context - the context of the checkin
        file_path - expression for file range: ./blah.####.jpg
        file_range - string describing range of frames in the from '1-5/1'
        snapshot_type - the snapshot type of the checkin
        description - a descriptive comment that pertains to this checkin
        file_type - the type of file this is checked in as. Default = 'main'
        metadata - a dictionary of values that will be stored as metadata
            on the snapshot
        mode - determines whether the files passed in should be preallocate, copied, move
            or uploaded.  By default, this is a manual process (for backwards
            compatibility)
        metadata - add metadata to snapshot
        is_revision - flag to set this as a revision instead of a version
        info - dictionary for ApiClientCmd


        @return
        snapshot dictionary
        '''

        if not file_range_val:
            # try to extract from paths
            file_path, file_range_val = FileGroup.extract_template_and_range(file_path)

        file_range = FileRange.get(file_range_val)


        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        # get the handoff dir and remap
        web = WebContainer.get_web()

        if mode == 'inplace':
            base_dir = os.path.dirname(file_path)

        elif mode in ['upload','uploaded']:
            base_dir = web.get_upload_dir()
        else:
            base_dir = web.get_server_handoff_dir()


        if type(file_path) != types.ListType:
            file_path = file_path.replace("\\", "/")
            filename = os.path.basename(file_path)
            file_paths = ["%s/%s" % (base_dir, filename)]
        else:
            file_paths = [x.replace("\\", "/") for x in file_path]


        # if file type is not specified, use file_type
        if not file_type:
            file_type = "main"


        file_types = []
        for file_path in file_paths:
            file_types.append(file_type)


        if not description:
            if file_range:
                description = 'File Group Publish [%s] files' %file_range.get_num_frames()
            else:
                description = 'File Group Publish [%s] files' % len(file_paths)

        checkin = FileGroupCheckin(sobject, file_paths, file_types,\
            file_range, context=context, snapshot_type=snapshot_type, \
            description=description, is_revision=is_revision, mode=mode)
        
        checkin.execute()

        # cleanup
        expanded_paths = checkin.get_expanded_paths()
        for path in expanded_paths:
            if os.path.exists(path):
                os.unlink(path)

        # get values from snapshot
        snapshot = checkin.get_snapshot()

        
        # add metadata to the snapshot
        if metadata:
            snapshot.add_metadata(metadata)
            snapshot.commit()

        my.set_sobject(sobject)

        info['snapshot'] = snapshot

        my.update_info(info)

        search = Search("sthpw/snapshot")
        columns = search.get_columns()
        result = {}
        for column in columns:
            value = str(snapshot.get_value(column))
            result[column] = value
        result['__search_key__'] = SearchKey.build_by_sobject(snapshot)

        return result


    @xmlrpc_decorator
    def add_dependency(my, ticket, snapshot_code, file_path, type='ref', tag='main'):
        '''method to append a dependency reference to an existing checkin.
        The snapshot that this is attached will be auto-discovered
       
        @params
        ticket - authentication ticket
        snapshot_code - the unique code identifier of a snapshot
        file_path - the path of the dependent file
        type - type of dependency.  Values include 'ref' and 'input_ref'
            ref = hierarchical reference:   ie A contains B
            input_ref - input reference:    ie: A was used to create B
        tag - a tagged keyword can be added to a dependency to categorize
            the different dependencies that exist in a snapshot

        @return
        the resulting snapshot
        '''
        if isinstance(snapshot_code, dict):
            snapshot_code = snapshot_code.get('code')
        elif snapshot_code.startswith("sthpw/snapshot?"):
            snapshot = Search.get_by_search_key(snapshot_code)
        else:
            snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException("Snapshot with code [%s] does not exist" % \
                snapshot_code)

        xml = snapshot.get_xml_value("snapshot")
        builder = SnapshotBuilder(xml)
        builder.add_ref_by_file_path(file_path, tag=tag)
        snapshot.set_value("snapshot", builder.to_string() )
        snapshot.commit()

        return my._get_sobject_dict(snapshot)



    @xmlrpc_decorator
    def add_dependency_by_code(my, ticket, to_snapshot_code, from_snapshot_code, type='ref', tag='main'):
        '''method to append a dependency reference to an existing checkin
        The snapshot that this is attached will be auto-discovered
       
        @params
        ticket - authentication ticket
        to_snapshot_code: the snapshot code which the dependency will be
            connected to
        from_snapshot_code: the snapshot code which the dependency will be
            connected from
        type - type of dependency.  Values include 'ref' and 'input_ref'
            ref = hierarchical reference:   ie A contains B
            input_ref - input reference:    ie: A was used to create B
        tag - a tagged keyword can be added to a dependency to categorize
            the different dependencies that exist in a snapshot

        @return
        the resulting snapshot
        '''
        if isinstance(to_snapshot_code, dict):
            to_snapshot_code = to_snapshot_code.get('code')
        if isinstance(from_snapshot_code, dict):
            from_snapshot_code = from_snapshot_code.get('code')

        snapshot = Snapshot.get_by_code(to_snapshot_code)
        if not snapshot:
            raise ApiException("Snapshot with code [%s] does not exist" % \
                to_snapshot_code)

        xml = snapshot.get_xml_value("snapshot")
        builder = SnapshotBuilder(xml)
        builder.add_ref_by_snapshot_code(from_snapshot_code, type=type, tag=tag)
        snapshot.set_value("snapshot", builder.to_string() )
        snapshot.commit()

        return my._get_sobject_dict(snapshot)



    @xmlrpc_decorator
    def add_file(my, ticket, snapshot_code, file_path, file_type='main', use_handoff_dir=False, mode=None, create_icon=False, dir_naming=None, file_naming=None, checkin_type='strict'):
        '''method to add a file to an already existing snapshot

        @param:
        ticket - authentication ticket
        snapshot_code - the unique code identifier of a snapshot
        file_path - path of the file to add to the snapshot
        file_type - type of the file to be added.
        dir_naming - explicitly set a dir_naming expression to use
        file_naming - explicitly set a file_naming expression to use
        checkin_type - auto or strict which controls whether to auto create versionless or some default file/dir naming

        @return:
        the resulting snapshot
        '''
        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException("Snapshot with code [%s] does not exist" % \
                snapshot_code)

        if mode:
            assert mode in ['move', 'copy','create', 'preallocate', 'upload', 'uploaded', 'manual', 'inplace']


        # file_path can be an array of files:
        if type(file_path) != types.ListType:
            is_array = False
            file_paths = [file_path]
        else:
            is_array = True
            file_paths = file_path
        if type(file_type) != types.ListType:
            file_types = [file_type]
        else:
            file_types = file_type

        assert len(file_paths) == len(file_types)
            
        snapshot_dicts = []

        for i, file_path in enumerate(file_paths):
            # store the passed in path as a source path
            source_paths = []
            source_paths.append(file_path)

            file_type = file_types[i]

            file_path = file_path.replace("\\", "/")
            old_filename = os.path.basename(file_path)
            #filename = File.get_filesystem_name(old_filename)
            filename = old_filename

            if mode == 'preallocate':
                keep_file_name = True
                # create a virtual file object for dir naming
                file_object = SearchType.create("sthpw/file")
                file_object.set_value("file_name", filename)

                lib_dir = snapshot.get_lib_dir(file_type=file_type, file_object=file_object)
                upload_path = "%s/%s" % (lib_dir, filename) 

            elif mode == 'inplace':
                upload_path = file_path
                keep_file_name = True

            else:
                keep_file_name = False

                #web = WebContainer.get_web()
                env = Environment.get_env_object()
                if use_handoff_dir:
                    dir = env.get_server_handoff_dir()
                else:
                    dir = env.get_upload_dir()

                upload_path = "%s/%s" % (dir, filename)
            
                if filename != old_filename:
                    shutil.move('%s/%s' %(dir, old_filename), upload_path)

            sub_file_paths = [upload_path]
            sub_file_types = [file_type]

            # if this is a file, then try to create an icon
            if create_icon and os.path.isfile(upload_path):
                icon_creator = IconCreator(upload_path)
                # this is icon only mode
                if file_type == 'icon':
                    icon_creator.set_icon_mode()
                    icon_creator.execute()
                    icon_path = icon_creator.get_icon_path()
                    if icon_path:
                        # we keep the source_path as the original file path instead of
                        # of icon_path
                        sub_file_paths = [icon_path]
                        sub_file_types = ['icon']
                else:
                    icon_creator.execute()

                    web_path = icon_creator.get_web_path()
                    icon_path = icon_creator.get_icon_path()
                    if web_path:
                        sub_file_paths = [upload_path, web_path, icon_path]
                        sub_file_types = [file_type, 'web', 'icon']
                        source_paths.append('')
                        source_paths.append('')

            #only update versionless for the last file
            do_update_versionless = False
            if i == len(file_paths)-1:
                do_update_versionless = True

            checkin = FileAppendCheckin(snapshot_code, sub_file_paths, sub_file_types, keep_file_name=keep_file_name, mode=mode, source_paths=source_paths, dir_naming=dir_naming, file_naming=file_naming, checkin_type=checkin_type, do_update_versionless=do_update_versionless)
            checkin.execute()
            snapshot = checkin.get_snapshot()

        snapshot_dict = my._get_sobject_dict(snapshot)
        return snapshot_dict


    @xmlrpc_decorator
    def remove_file(my, ticket, snapshot_code, file_type):
        '''method to remove a file from a snapshot

        @param:
        ticket - authentication ticket
        snapshot_code - the unique code identifier of a snapshot
        file_type - file type to remove

        @return:
        the resulting snapshot
        '''
        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException("Snapshot with code [%s] does not exist" % \
                snapshot_code)

        snapshot.remove_file(file_type)

        return my._get_sobject_dict(snapshot)



    @xmlrpc_decorator
    def add_group(my, ticket, snapshot_code, file_path, file_type, file_range, use_handoff_dir=False, mode=None):
        '''method to add a file range to an already existing snapshot

        @params
        ticket - authentication ticket
        snapshot_code - the unique code identifier of a snapshot
        file_path - path of the file to add to the snapshot
        file_type - type of the file to be added.
        file_range - range of files in the form of "start-end/by"
        use_handoff_dir - determines whether to get the files from the handoff
            directory
        mode - one of 'copy', move', 'preallocate', 'inplace'

        @return
        the resulting snapshot
        '''
        file_range = FileRange.get(file_range)

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException("Snapshot with code [%s] does not exist" % \
                snapshot_code)

        file_path = file_path.replace("\\", "/")
        filename = os.path.basename(file_path)
        #filename = File.get_filesystem_name(filename)

        if mode:
            assert mode in ['move', 'copy', 'create','preallocate', 'upload', 'inplace']
        if mode == 'preallocate':
            keep_file_name = True
            # create a virtual file object for dir naming
            file_object = SearchType.create("sthpw/file")
            file_object.set_value("file_name", filename)
            file_object.set_value("range", file_range)

            #lib_dir = snapshot.get_lib_dir(file_type=file_type, file_object=file_object)
            #upload_path = "%s/%s" % (lib_dir, filename) 
            upload_path = file_path
        elif mode == 'inplace':
            upload_path = os.path.dirname(file_path) + '/' + filename
            keep_file_name = True
        
        else:
            keep_file_name = False

            web = WebContainer.get_web()
            if use_handoff_dir:
                dir = web.get_server_handoff_dir()
            else:
                dir = web.get_upload_dir()

            upload_path = "%s/%s" % (dir, filename)

            

        checkin = FileGroupAppendCheckin(snapshot_code, [upload_path], [file_type], file_range, \
                keep_file_name=keep_file_name, mode=mode)
        checkin.execute()
        snapshot = checkin.get_snapshot()
        return my._get_sobject_dict(snapshot)




    @xmlrpc_decorator
    def checkout(my, ticket, search_key, context, version=-1, file_type='main', level_key=None):
        '''method to checkout a snapshot from the repository.  This method
        does not move files as the check out process is mostly a client side
        operation.

        @params
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject
        context - context of the snapshot
        version - version of the snapshot
        level_key - the unique identifier of the level that this
            was checked into

        @return
        a list of paths 
        '''

        #paths = my.get_paths(my, ticket, search_key, context="publish", version=-1, file_type='main', level_key=None):

        if not context:
            context = 'publish'

        sobjects = my._get_sobjects(search_key)
        sobject = sobjects[0]

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        search_key = SearchKey.get_by_sobject(sobject)
        # get the level object
        if level_key:
            level = SearchKey.get_by_search_key(level_key)
            if not level:
                raise ApiException("Level SObject with key [%s] does not exist" % level_key)
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None

        snapshot = Snapshot.get_snapshot(search_type, search_id, context, version, level_type=level_type, level_id=level_id)
        if not snapshot:
            raise ApiException("Snapshot for [%s] with context [%s] does not exist" % (search_key, context))


        is_locked = snapshot.is_locked(sobject, context)
        if is_locked:
            raise ApiException("Snapshot for [%s] with context [%s] is locked" % (search_key, context))

        paths = {}

        if file_type == "*":
            client_lib_paths = snapshot.get_all_client_lib_paths()
            paths['client_lib_paths'] = client_lib_paths

            sandbox_paths = snapshot.get_all_sandbox_paths()
            paths['sandbox_paths'] = sandbox_paths

            web_paths = snapshot.get_all_remote_web_paths()
            paths['web_paths'] = web_paths

        else:
            client_lib_path = snapshot.get_client_lib_path_by_type(file_type)
            if not client_lib_path:
                raise ApiException("File of type [%s] does not exist in snapshot [%s]" % (file_type, snapshot.get_code()) )

            sandbox_path = snapshot.get_sandbox_path_by_type(file_type)
            web_path = snapshot.get_remote_web_path_by_type(file_type)

            paths['client_lib_paths'] = [client_lib_path]
            paths['sandbox_paths'] = [sandbox_path]
            paths['web_paths'] = [web_path]



        # call some triggers
        base_search_type = sobject.get_base_search_type()
        output = {}
        snapshot_dict = my._get_sobject_dict(snapshot)
        output['snapshot'] = snapshot_dict
        output['paths'] = paths
        Trigger.call('checkout', output)
        Trigger.call('checkout|%s' % base_search_type, output)

        return paths



    @xmlrpc_decorator
    def lock_sobject(my, ticket, search_key, context):
        '''locks the context for checking in and out
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        Snapshot.lock(sobject, context)
        return True




    @xmlrpc_decorator
    def unlock_sobject(my, ticket, search_key, context):
        '''unlocks the context for checking in and out
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)


        Snapshot.unlock(sobject, context)
        return True






    @xmlrpc_decorator
    def query_snapshots(my, ticket, filters=None, columns=None, order_bys=[], show_retired=False, limit=None, offset=None, single=False, include_paths=False, include_full_xml=False, include_paths_dict=False, include_parent=False, include_files=False, include_web_paths_dict=False):
        '''thin wrapper around query, but is specific to querying snapshots
        with some useful included flags that are specific to snapshots

        @params
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
        include_web_paths_dict - flag to specify whether to include a
            __web_paths_dict__ property containing a dict of all web paths in
            the returned snapshots

        include_full_xml - flag to return the full xml definition of a snapshot
        include_parent - includes all of the parent attributes in a __parent__ dictionary
        include_files - includes all of the file objects referenced in the
            snapshots

        @return
        list of snapshots
        '''
        search_type = "sthpw/snapshot"
        snapshots = my._query(search_type=search_type, filters=filters, columns=columns, order_bys=order_bys, show_retired=show_retired, limit=limit, offset=offset, single=single, return_sobjects=True)

        if not snapshots:
            return []


        parents = {}

        if single:
            snapshots = [snapshots]

        parent_search_type = snapshots[0].get_value("search_type")
        if include_parent:
            # check to see if the parents are of all the same search_type
            is_same_search_type = True
            for snapshot in snapshots:
                tmp_search_type = snapshot.get_value("search_type")
                if parent_search_type != tmp_search_type:
                    is_same_search_type = False
                    break

            if is_same_search_type:
                # get all of the snapshots at once
                search = Search(parent_search_type)
                ids = SObject.get_values(snapshots, "search_id", unique=True)
                search.add_filters("id", ids)
                tmp_parents = search.get_sobjects()

                # create a tmp data structure for fast lookup
                tmp_parents_dict = {}
                for parent in tmp_parents:
                    parent_id = parent.get_id()
                    tmp_parents_dict[parent_id] = parent

                # add to the parents
                for snapshot in snapshots:
                    parent_id = snapshot.get_value("search_id")
                    search_key = SearchKey.build_by_sobject(snapshot)

                    parent = tmp_parents_dict.get(parent_id)
                    parents[search_key] = parent

            else:
                # get them one by one ???
                # TODO: this can be optimised!!!!
                for snapshot in snapshots:
                    search_key = SearchKey.build_by_sobject(snapshot)
                    parent = snapshot.get_parent()
                    parents[search_key] = parent


        # preprocess and get all file objects
        if include_files:
            all_files = Snapshot.get_files_dict_by_snapshots(snapshots)

        results = []
        for snapshot in snapshots:
            snapshot_dict = my._get_sobject_dict(snapshot, columns)
            # include a paths attribute
            if include_paths:
                paths = snapshot.get_all_client_lib_paths()
                snapshot_dict['__paths__'] = paths

            # include a full xml attribute
            if include_full_xml:
                full_snapshot_xml = snapshot.get_full_snapshot_xml()
                snapshot_dict['__full_snapshot_xml__'] = full_snapshot_xml

            if include_paths_dict:
                paths = snapshot.get_all_client_lib_paths_dict()
                snapshot_dict['__paths_dict__'] = paths

            if include_web_paths_dict:
                paths = snapshot.get_all_web_paths_dict()
                snapshot_dict['__web_paths_dict__'] = paths

            if include_parent:
                search_key = snapshot_dict.get('__search_key__')
                parent = parents.get(search_key)
                parent_dict = my._get_sobject_dict(parent)
                snapshot_dict['__parent__'] = parent_dict

            if include_files:
                snapshot_code = snapshot.get_code()
                file_list = all_files.get(snapshot_code)
                file_dict_list = []
                if file_list:
                    for file in file_list:
                        file_dict = my._get_sobject_dict(file)
                        file_dict_list.append(file_dict)
                else:
                    print "Files not found for snapshot [%s]" %snapshot_code
                snapshot_dict['__files__'] = file_dict_list



            results.append(snapshot_dict)
        return results





    @xmlrpc_decorator
    def get_snapshots_by_relative_dir(my, ticket, relative_dir, base_dir_alias=""):
        '''Get all of the snapshots associated with a particular relative
        directory.

        @params
        ticket - authentication ticket
        relative_dir - the relative directory in the server

        @return
        list of snapshots
        '''


        search = Search("sthpw/file")
        search.add_op("begin")
        search.add_filter("relative_dir", "%s/%%" % relative_dir, op="like")
        search.add_filter("relative_dir", "%s" % relative_dir, op="=")
        search.add_op("or")

        search2 = Search("sthpw/snapshot")
        search2.add_relationship_search_filter(search)
        search2.add_filter("is_latest", True)

        sobjects = search2.get_sobjects()
        sobject_dicts = []
        for sobject in sobjects:
            sobject_dict = my._get_sobject_dict(sobject)
            sobject_dicts.append(sobject_dict)
        return sobject_dicts
 





    @xmlrpc_decorator
    def get_snapshot(my, ticket, search_key, context="publish", version='-1', revision=None, level_key=None, include_paths=False, include_full_xml=False, include_paths_dict=False, include_files=False, include_web_paths_dict=False, versionless=False, process=None):
        '''method to retrieve snapshots
        
        @params
        ticket - authentication ticket
        search_key - unique identifier of sobject whose snapshot we are
                looking for
        process - the process of the snapshot
        context - the context of the snapshot
        include_paths - flag to specify whether to include a __paths__ property
            containing a list of all paths in the dependent snapshots
        include_paths_dict - flag to specify whether to include a
            __paths_dict__ property containing a dict of all paths in the
            returned snapshots
        include_web_paths_dict - flag to specify whether to include a
            __web_paths_dict__ property containing a dict of all web paths in
            the returned snapshots
        include_full_xml - flag to return the full xml definition of a snapshot
        include_files - includes all of the file objects referenced in the
            snapshots


        @return
        the resulting snapshot
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        # if the sobject is a snapshot, then get the parent and use it as a base
        if sobject.get_base_search_type() == "sthpw/snapshot":
            sobject = sobject.get_parent()

        search_type = sobject.get_search_type() 
        search_id = sobject.get_id()
        search_code = sobject.get_value("code", no_exception=True)
        search_combo = search_code
        if not search_code:
            search_combo = search_id

        # get the level object
        if level_key:
            level = SearchKey.get_by_search_key(level_key)
            if not level:
                raise ApiException("Level SObject with key [%s] does not exist" % level_key)
            level_type = level.get_search_type()
            level_id = level.get_id()
        else:
            level_type = None
            level_id = None

        # if a process is given the context is overridden
        if process:
            context = None

        if not versionless:
            snapshot = Snapshot.get_snapshot(search_type, search_combo, context=context, version=version, revision=revision, level_type=level_type, level_id=level_id, process=process)
        else:
            if version in [-1, 'latest']:
                versionless_mode = 'latest'
            else:
                versionless_mode = 'current'
            snapshot = Snapshot.get_versionless(search_type, search_code, context=context , mode=versionless_mode, create=False)

        if not snapshot:
            return {}

        sobject_dict = my._get_sobject_dict(snapshot)

        # preprocess and get all file objects
        if include_files:
            all_files = Snapshot.get_files_dict_by_snapshots([snapshot])


        # include a paths attribute
        if include_paths:
            paths = snapshot.get_all_client_lib_paths()
            sobject_dict['__paths__'] = paths
        # include a full xml attribute
        if include_full_xml:
            full_snapshot_xml = snapshot.get_full_snapshot_xml()
            sobject_dict['__full_snapshot_xml__'] = full_snapshot_xml

        if include_paths_dict:
            paths = snapshot.get_all_client_lib_paths_dict()
            sobject_dict['__paths_dict__'] = paths

        if include_web_paths_dict:
            paths = snapshot.get_all_web_paths_dict()
            sobject_dict['__web_paths_dict__'] = paths


        if include_files:
            snapshot_code = snapshot.get_code()
            file_list = all_files.get(snapshot_code)
            file_dict_list = []
            for file in file_list:
                file_dict = my._get_sobject_dict(file)
                file_dict_list.append(file_dict)
            sobject_dict['__files__'] = file_dict_list

        return sobject_dict








    @xmlrpc_decorator
    def get_full_snapshot_xml(my, ticket, snapshot_code):
        '''method to retrieve a full snapshot xml.  This snapshot definition
        contains all the information about a snapshot in xml
        
        @params
        ticket - authentication ticket
        snapshot_code - unique code of snapshot

        @return
        the resulting snapshot xml
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        return snapshot.get_full_snapshot_xml()




    @xmlrpc_decorator
    def set_current_snapshot(my, ticket, snapshot_code):
        '''sets this snapshot as a "current" snapshot
        
        @params
        ticket - authentication ticket
        snapshot_code - unique code of snapshot

        @return
        the resulting snapshot xml
        '''

        if type(snapshot_code) == types.DictType:
            snapshot_code = snapshot_code.get('code')
        snapshot = Snapshot.get_by_code(snapshot_code)
        if not snapshot:
            raise ApiException( "Snapshot with code [%s] does not exist" % \
                snapshot_code)

        # let SnapshotisLatestTrigger handle the rest
        snapshot.set_value('is_current', True)
        snapshot.commit()
        #snapshot.set_current(update_versionless=False)
        return my._get_sobject_dict(snapshot)



    #
    # Task methods
    #
    @xmlrpc_decorator
    def create_task(my, ticket, search_key, process="publish", subcontext=None, description=None, bid_start_date=None, bid_end_date=None, bid_duration=None, assigned=None):
        '''Create a task for a particular sobject
        @params:
        ticket - authentication ticket
        search_key - the key identifying a type of sobject as registered in
                    the search_type table.
        process - process that this task belongs to
        subcontext - the subcontex of the process (context = procsss/subcontext
        description - detailed description of the task
        bid_start_date - the expected start date for this task
        bid_end_date - the expected end date for this task
        bid_duration - the expected duration for this task
        assigned - the user assigned to this task
        @return
        task that was created
        ''' 


        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)


        if subcontext:
            context = "%s/%s" % (process, subcontext)
        else:
            context = process

        task = SearchType.create("sthpw/task")
        task.set_value("process", process)
        task.set_value("context", context)

        task.set_parent(sobject)

        if bid_start_date and bid_end_date:
            if bid_start_date > bid_end_date:
                raise ApiException("bid_start_date should be before bid_end_date.")


        if description:
            task.set_value("description", description)

        if bid_start_date:
            task.set_value("bid_start_date", bid_start_date)
        if bid_end_date:
            task.set_value("bid_end_date", bid_end_date)
        if bid_duration:
            task.set_value("bid_duration", bid_duration)
        if assigned:
            task.set_value("assigned", assigned)


        task.commit()

        task_dict = my._get_sobject_dict(task)
        return task_dict





    @xmlrpc_decorator
    def add_initial_tasks(my, ticket, search_key, pipeline_code=None, processes=[], skip_duplicate=True, offset=0):
        '''This method will add initial task to an sobject

        @params:
        ticket - authentication ticket
        search_key - the key identifying an sobject as registered in
                    the search_type table.
        @keyparam:
        pipeline_code - override the sobject's pipeline and use this one instead
        processes - create tasks for the given list of processes
        skip_duplicate - boolean to skip duplicated task
        offset - a number to offset the start date from today's date
       
        @return:
        list of tasks created
        
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        from pyasm.biz import Task
        tasks = Task.add_initial_tasks(sobject, pipeline_code=pipeline_code, processes=processes, skip_duplicate=skip_duplicate, start_offset=offset)

        ret_tasks = []
        for task in tasks:
            task_dict = my._get_sobject_dict(task)
            ret_tasks.append(task_dict)

        return ret_tasks



    @xmlrpc_decorator
    def get_tasks(my, ticket, search_key, process=None):
        '''Get the tasks of an sobject

        ticket - authentication ticket
        search_key - the key identifying an sobject as registered in
                    the search_type table.
 
        @return:
        list of tasks
        '''

        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')
        sobject = Search.get_by_search_key(search_key)

        search = Search("sthpw/task")
        search.set_parent(sobject)
        if process:
            search.add_filter("process", process)
        tasks = search.get_sobjects()

        ret_tasks = []
        for task in tasks:
            task_dict = my._get_sobject_dict(task)
            ret_tasks.append(task_dict)

        return ret_tasks


    @xmlrpc_decorator
    def get_task_status_colors(my, ticket):
        '''Get all the colors for a task status

        ticket - authentication ticket
 
        @return:
        dictionary of colors
        '''
        from pyasm.biz import Task
        return Task.get_status_colors()






    @xmlrpc_decorator
    def get_input_tasks(my, ticket, search_key):
        '''Get the input tasks of a task based on the pipeline
        associated with the sobject parent of the task

        ticket - authentication ticket
        search_key - the key identifying an sobject as registered in
                    the search_type table.
 
        @return:
        list of input_tasks
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        task = SearchKey.get_by_search_key(search_key)
        if not task:
            raise ApiException("SObject for [%s] does not exist" % search_key)


        search_type = task.get_base_search_type()
        assert search_type == "sthpw/task"

        input_tasks = task.get_input_tasks()

        ret_tasks = []
        for task in input_tasks:
            task_dict = my._get_sobject_dict(task)
            ret_tasks.append(task_dict)

        return ret_tasks



    @xmlrpc_decorator
    def get_output_tasks(my, ticket, search_key):
        '''Get the output tasks of a task based on the pipeline
        associated with the sobject parent of the task

        ticket - authentication ticket
        search_key - the key identifying an sobject as registered in
                    the search_type table.
 
        @return:
        list of output
        '''
        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        task = SearchKey.get_by_search_key(search_key)
        if not task:
            raise ApiException("SObject for [%s] does not exist" % search_key)


        search_type = task.get_base_search_type()
        assert search_type == "sthpw/task"

        input_tasks = task.get_output_tasks()

        ret_tasks = []
        for task in input_tasks:
            task_dict = my._get_sobject_dict(task)
            ret_tasks.append(task_dict)

        return ret_tasks






    #
    # Note methods
    #
    @xmlrpc_decorator
    def create_note(my, ticket, search_key, note, process="publish", subcontext=None, user=None):
        '''Add a task for a particular sobject

        @params:
        ticket - authentication ticket
        search_key - the key identifying a type of sobject as registered in
                    the search_type table.
        note - detailed description of the task
        process - process that this task belongs to
        subcontext - the subcontex of the process (context = procsss/subcontext
        user - the user the note is attached to

        @return
        note that was created
        ''' 


        if type(search_key) == types.DictType:
            search_key = search_key.get('__search_key__')

        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)


        if subcontext:
            context = "%s/%s" % (process, subcontext)
        else:
            context = process

        note_obj = SearchType.create("sthpw/note")
        note_obj.set_value("process", process)
        note_obj.set_value("context", context)
        note_obj.set_parent(sobject)

        if note_obj:
            note_obj.set_value("note", note)

        note_obj.set_user(user)
        note_obj.commit()

        note_dict = my._get_sobject_dict(note_obj)
        return note_dict



    #
    # Pipeline methods
    #
    @xmlrpc_decorator
    def get_pipeline_xml(my, ticket, search_key):
        '''DEPRECATED: use get_pipeline_xml_info()
        method to retrieve the pipeline of a specific sobject.  The pipeline
        returned is an xml document.
       
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject


        @return:
        string - xml of pipeline
        '''

        # get the sobject
        from pyasm.search import SearchKey
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return "<pipeline/>"

        return pipeline.get_xml_value("pipeline").to_string()
       


    @xmlrpc_decorator
    def get_pipeline_processes(my, ticket, search_key, recurse=False):
        '''DEPRECATED: use get_pipeline_processes_info()
        method to retrieve the pipeline of a specific sobject.  The pipeline
        returned is a dictionary
       
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @keyparams:
        recurse - boolean to control whether to display sub pipeline processes
        
        @return:
        process names of the pipeline or a dictionary if related_process is specified
        '''

        # get the sobject
        from pyasm.search import SearchKey
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return []

        return pipeline.get_process_names(recurse=recurse)

    @xmlrpc_decorator
    def get_pipeline_xml_info(my, ticket, search_key, include_hierarchy=False):
        '''method to retrieve the pipeline of a specific sobject.  The pipeline
        returned is an xml document.
       
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @keyparam:
        include_hierarchy - include a list of dictionary with key info on each process of the pipeline

        @return:
        dictionary - xml and the optional hierarachy info
        '''

        # get the sobject
        from pyasm.search import SearchKey
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return "<pipeline/>"

        main_data = {}

        main_data['xml'] =  pipeline.get_xml_value("pipeline").to_string()
        if include_hierarchy:
            processes = pipeline.get_processes()
            info = []
            for process in processes:
                data = {'process' : process.get_name()}
                data['task_pipeline'] = process.get_task_pipeline()
                data['output_contexts'] = pipeline.get_output_contexts(process.get_name())
                data['input_contexts'] = pipeline.get_input_contexts(process.get_name())

                input_processes = pipeline.get_input_processes(process)
                input_processes = [x.get_name() for x in input_processes]
                data['input_processes'] = input_processes
                output_processes = pipeline.get_output_processes(process)
                output_processes = [x.get_name() for x in output_processes]
                data['output_processes'] = output_processes

                info.append(data)
            main_data['hierarchy'] = info

    
        
        return main_data


    @xmlrpc_decorator
    def get_pipeline_processes_info(my, ticket, search_key, recurse=False, related_process=None):
        '''method to retrieve the pipeline of a specific sobject.  The pipeline
        returned is a dictionary
       
        @params:
        ticket - authentication ticket
        search_key - a unique identifier key representing an sobject

        @keyparams:
        recurse - boolean to control whether to display sub pipeline processes
        related_process- given a process, it shows the input and output processes and contexts
        
        @return:
        dictionary - just the plain processes or more input and output info if related_process is specified
        '''

        # get the sobject
        from pyasm.search import SearchKey
        sobject = SearchKey.get_by_search_key(search_key)
        if not sobject:
            raise ApiException("SObject for [%s] does not exist" % search_key)

        pipeline = Pipeline.get_by_sobject(sobject)
        if not pipeline:
            return {}

        data = {}
        if related_process:
            input_processes = pipeline.get_input_processes(related_process)
            input_processes = [x.get_name() for x in input_processes]
            data['input_processes'] = input_processes
            output_processes = pipeline.get_output_processes(related_process)
            output_processes = [x.get_name() for x in output_processes]
            data['output_processes'] = output_processes
            
            input_contexts = pipeline.get_input_contexts(related_process)
            data['input_contexts'] = input_contexts
            output_contexts = pipeline.get_output_contexts(related_process)
            data['output_contexts'] = output_contexts
            return data
        else:
            process_names = pipeline.get_process_names(recurse=recurse)
            data['processes'] = process_names

        return data



    #
    # triger methods
    #
    def call_trigger(my, ticket, event, input):
        '''Calls a trigger with input package
        
        
        @params
        ticket - authentication ticket
        '''
        return Trigger.call(my, event, input)






    #
    # session methods
    #
    @xmlrpc_decorator
    def commit_session(my, ticket, session_xml, pid):
        ''' DEPRECATED: for internal use only
        takes a session xml and commits it.  Also handles transfer to old
        style xml data

        @params
        ticket - authentication ticket
        session_xml - an xml document representing the session. This document
            format is described below

        @return
        session sobject

        session_xml takes the form:

        <session>
          <ref search_key="prod/shot?project=bar&code=joe" context="model" version="3" revision="2" tactic_node="tactic_joe" snapshot_code="123BAR"/>
        </session>
        '''

        xml = Xml()
        xml.read_string(session_xml)

        old_xml = Xml()
        old_xml.create_doc("session")
        old_root = old_xml.get_root_node()

        # create a second xml and transform it to the old style
        nodes = xml.get_nodes("session/ref")
        for node in nodes:
            
            search_key = xml.get_attribute(node, "search_key")
            tactic_node = xml.get_attribute(node, "tactic_node")

            sobject = Search.get_by_search_key(search_key)

            code = sobject.get_code()

            old_node = old_xml.create_element("node")
            old_xml.set_attribute(old_node, "asset_code", code)
            old_xml.set_attribute(old_node, "instance", code)
            old_xml.set_attribute(old_node, "name", tactic_node)
            old_xml.set_attribute(old_node, "namespace", "")
            old_xml.set_attribute(old_node, "is_tactic_node", "true")
            old_xml.set_attribute(old_node, "type", "transform")

            #old_root.appendChild(old_node)
            old_xml.append_child(old_root, old_node)

        # create a new search_type
        sobject = SearchType.create("prod/session_contents")
        sobject.set_value("pid", pid)
        sobject.set_user()
        sobject.set_value("data", old_xml.to_string() )
        sobject.set_value("session", xml.to_string() )
        sobject.commit()

        sobject_dict = my._get_sobject_dict(sobject)
        return sobject_dict


    #
    # UI methods
    #
    def _init_web(my, ticket, values={}):
        '''Initialize the web engine'''

        # NOTE: setup is complicated here

        # clear the buffer
        WebContainer.clear_buffer()

        # initialize the web environment object and register it
        adapter = my.get_adapter()
        WebContainer.set_web(adapter)

        security = Environment.get_security()
        license = security.get_license()
        user_name = security.get_user_name()

        # too restrictive, disabled for now
        #if not user_name == "admin" and not license.is_licensed():
        #    raise LicenseException(license.get_message())


        # set the web form values
        web = WebContainer.get_web()
        if type(values) == types.DictType:
            for name, value in values.items():
                web.set_form_value(name, value)

        else:
            from tactic.ui.filter import FilterData
            filter_data = FilterData(values)
            filter_data.set_to_cgi()


        # initialize the translation module
        from pyasm.biz import ProdSetting
        from pyasm.biz import Translation
        language = ProdSetting.get_value_by_key("language")
        Translation.install(language)

        # NOTE: this is deprecated.  The state is in the ticket passed
        # in, so restoration of transaction state is not really necessary
        if my.get_protocol() == "xmlrpc" and not Project.get():
            state = TransactionState.get_by_ticket(ticket)
            state.restore_state()
 

    @xmlrpc_decorator
    def get_widget(my, ticket, class_name, args={}, values={}, libraries={}, interaction={}):
        '''get a defined widget

        @params
        ticket - authentication ticket
        class_name - the fully qualified class name of the widget
        args - keyword arguments required to create a specific widget
        values - form values that are passed in from the interface

        @return
        string: html form of the widget

        @example
        class_name = 'TableLayoutWdg',
        args = {
                'view': 'manage',
                'search_type': 'prod/asset',
               }
        widget = server.get_widget(class_name, args))
        '''

        '''
        from guppy import hpy
        hp = hpy()
        hp.setrelheap()
        '''
        try:
            Ticket.update_session_expiry()
        except:
            pass

        try:
            try:
                # switch projects code
                #project_code = args.get("__project__")
                #if project_code:
                #    Project.set_project(project_code)


                my._init_web(ticket, values)

                args_array = []
                widget = Common.create_from_class_path(class_name, args_array, args)
                if libraries.has_key("spt_help"):
                    from tactic.ui.app import HelpWdg
                    HelpWdg()

                Container.put("JSLibraries", libraries)
                Container.put("request_top_wdg", widget)

                html = widget.get_buffer_display()
                if class_name.find('tactic.ui.app.message_wdg.Subscription') == -1:
                    print "SQL Query Count: ", Container.get('Search:sql_query')
                    print "BVR Count: ", Container.get('Widget:bvr_count')
                    print "Sending: %s KB" % (len(html)/1024)
                    print "Num SObjects: %s" % Container.get("NUM_SOBJECTS")


                # add interaction, if any
                if interaction:
                    #interaction = SearchType.create("sthpw/interaction")
                    pass

                return html

            except LicenseException, e:
                # make sure all sqls are aborted
                DbContainer.abort_thread_sql(force=True)

                from pyasm.widget import ExceptionWdg
                #from pyasm.web import DivWdg
                #widget = DivWdg()

                from tactic.ui.app import LicenseManagerWdg
                license_manager = LicenseManagerWdg()
                widget.add(license_manager)
                return widget.get_buffer_display()
            except SecurityException, e:
                # make sure all sqls are aborted
                DbContainer.abort_thread_sql(force=True)

                from pyasm.web import DivWdg
                widget = DivWdg()
                if isinstance(e, SObjectSecurityException):
                    from pyasm.web import SpanWdg
                    widget.add(SpanWdg(e, css='warning'))
                else:
                    # Timed out, show login screen
                    from pyasm.widget import WebLoginWdg
                    web_login = WebLoginWdg()
                    widget.add(web_login)
                return widget.get_buffer_display()


               
            except Exception, e:
                # make sure all sqls are aborted
                DbContainer.abort_thread_sql(force=True)

                from pyasm.widget import ExceptionWdg
                widget = ExceptionWdg(e)
                return widget.get_buffer_display()

        finally:
            DbContainer.close_all()
            Environment.set_app_server('xmlrpc')

            WebContainer.clear_buffer()
            Container.delete()

            '''
            h = hp.heap()

            byrcs = h.byrcs
            byclodo = byrcs[0].byclodo
            print byclodo
            bysize = byrcs[0].bysize
            print bysize
            byid = byrcs[0].byid
            print byid
            byvia = byrcs[0].byvia
            print byvia
            #theone = byvia[0].theone
            #print len(theone)
            '''


        
    @xmlrpc_decorator
    def class_exists(my, ticket, class_path):
        '''determines if a class exists on the server
       
        @params
        ticket - authentication ticket
        class_path - fully qualified python class path

        @return
        boolean: true if class exists and can be seen
        '''

        module_path, class_name = Common.breakup_class_path(class_path)

        if not module_path:
            return False

        try:
            exec("import %s" % module_path)
        except Exception, e:
            return False

        module = eval(module_path)
        if not hasattr(module, class_name):
            return False

        try:
            check = eval(class_path)
        except Exception, e:
            return False


        return True



    @xmlrpc_decorator
    def execute_python_script(my, ticket, script_path, kwargs={}):
        '''execute a python script in the script editor

        @params
        ticket - authentication ticket
        script_path - script path in Script Editor, e.g. test/eval_sobj
      
        @return
        dictionary - returned data structure

        '''
        ret_val = {}
        try:
            from tactic.command import PythonCmd
            cmd = PythonCmd(script_path=script_path, **kwargs)
            Command.execute_cmd(cmd)
        
        except Exception, e:
            raise
        else:
            ret_val['status'] = 'OK'
            ret_val['description'] = cmd.get_description()

            info = cmd.get_info()
            ret_val['info'] = info

        return ret_val

   

    @xmlrpc_decorator
    def execute_js_script(my, ticket, script_path, kwargs={}):
        '''execute a js script in the script editor

        @params
        ticket - authentication ticket
        script_path - script path in Script Editor, e.g. test/eval_sobj
      
        @return
        dictionary - returned data structure

        '''
        ret_val = {}
        try:
            from tactic.command import JsCmd
            cmd = JsCmd(script_path=script_path, **kwargs)
            Command.execute_cmd(cmd)
        
        except Exception, e:
            raise
        else:
            ret_val['status'] = 'OK'
            ret_val['description'] = cmd.get_description()

            info = cmd.get_info()
            ret_val['info'] = info

        return ret_val


        
    @xmlrpc_decorator
    def execute_cmd(my, ticket, class_name, args={}, values={}, use_transaction=True):
        '''execute a command

        @params
        ticket - authentication ticket
        class_name - the fully qualified class name of the widget
        args - keyword arguments required to create a specific widget
        values - form values that are passed in from the interface
        use_transaction - True|False determines whether to put this command in a transaction.  Use with caution.  Generally all commands should be intransaction.

        @return
        string - return data structure
        '''
        try:
            Ticket.update_session_expiry()
        except:
            pass
        
        ret_val = {}

        try:
            # set the web form values
            web = WebContainer.get_web()
            if type(values) == types.DictType:
                for name, value in values.items():
                    web.set_form_value(name, value)
            else:
                # specifically for the search filter for now
                from tactic.ui.filter import FilterData
                filter_data = FilterData(values)
                filter_data.set_to_cgi()


            args_array = []
            cmd = Common.create_from_class_path(class_name, args_array, args)
            if use_transaction:
                Command.execute_cmd(cmd)
            else:
                cmd.execute()

        except Exception, e:
            '''
            import traceback
            tb = sys.exc_info()[2]
            stacktrace = traceback.format_tb(tb)
            stacktrace_str = "".join(stacktrace)
            print "-"*50
            print stacktrace_str
            print str(e)
            print "-"*50
            
            ret_val['status'] = 'ERROR'
            ret_val['stack'] = stacktrace_str
            ret_val['message'] = str(e)
            '''

            # NOTE: we can do one or the other (not both).  Either we
            # reraise the exception and let the API command handle it
            # or we have to rollback here.  Using raise for now because
            # it is simpler. This means that this whole exception handling
            # may not be necessary

            #transaction = Transaction.get()
            #if transaction.is_in_transaction():
            #    Transaction.get().rollback()

            raise
        else:
            ret_val['status'] = 'OK'
            ret_val['description'] = cmd.get_description()

            info = cmd.get_info()
            ret_val['info'] = info
        return ret_val


    @xmlrpc_decorator
    def execute_class_method(my, ticket, class_name, method, kwargs):
        ret_val = Common.create_from_method(class_name, method, kwargs)
        return ret_val



    #@xmlrpc_decorator
    #def execute(my, ticket, code):
    #    from tactic.command.python_cmd import PythonCmd
    #    cmd = PythonCmd(code=code)
    #    return cmd.execute()



    @xmlrpc_decorator
    def execute_transaction(my, ticket, transaction_xml, file_mode=None):
        '''Run a tactic transaction a defined by the instructions in the
        given transaction xml.  The format of the xml is identical to
        the format of how transactions are stored internally
        
        @params
        ticket - authentication ticket
        transaction_xml - transaction instructions

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
        # find out which server this came from
        web = WebContainer.get_web()
        remote_host = web.get_request_host()

        # TODO: verify that the ticket is a sync ticket (by category
        # in the ticket table


        # make a provision for localhost
        # NOTE: commenting out because the server is registered as a domain
        # name, but the remote server often sends an IP address
        """
        if remote_host not in ['xlocalhost', 'x127.0.0.1']:

            remote_hosts = [remote_host, 'http://%s'%remote_host, 'https://%s'%remote_host]

            # search in the list of hosts to ensure that it is known
            search = Search("sthpw/sync_server")
            search.add_filters("host", remote_hosts)
            servers = search.get_sobjects()
            if not servers:
                raise TacticException("No server [%s] is registered to deliver transactions" % remote_host)

            # TODO: need to add security to allow a remote server to push
            # or pull transactions
        """

        # actually execute the transaction
        try:
            from tactic.command import RunTransactionCmd
            cmd = RunTransactionCmd(transaction_xml=transaction_xml, file_mode=file_mode)
            cmd.execute()

            info = {
                'status': 'OK'
            }
        except Exception, e:
            raise

        return info

        

    @trace_decorator
    def execute_transactions(my, ticket, transactions, file_mode=None):
        '''Run a list of tactic transaction a defined by the instructions in
        the given transaction xml.  The format of the xml is identical to
        the format of how transactions are stored internally
        
        @params
        ticket - authentication ticket
        transaction_xml - transaction instructions

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

        server.execute_transactions([transaction_xml])

        '''
        # find out which server this came from
        web = WebContainer.get_web()
        remote_host = web.get_request_host()

        # each will run in their own transaction
        failed = []
        errors = []
        try:
            from tactic.command import RunTransactionCmd
            for index, transaction_xml in enumerate(transactions):
                cmd = RunTransactionCmd(transaction_xml=transaction_xml, file_mode=None)
                Command.execute_cmd()

        except Exception, e:
            failed.append(index)
            errors.append(str(e))

        if failed:
            info = {
                'status': 'ERROR',
                'failed': failed,
                'errors': errors
            }
        else:
            info = {
                'status': 'OK'
            }
        return info



    @xmlrpc_decorator
    def check_access(my, ticket, access_group, key, access, value=None, is_match=False, default="edit"):
        '''check the access for a specified access_group name like search_type, sobject, project, 
            or custom-defined '''
        security = Environment.get_security()
        return security.check_access(access_group, key, access, value, is_match, default = default)


    @xmlrpc_decorator
    def get_column_widgets(my, ticket, search_type, search_keys, element_name):
        '''a specialized method that gets all the widgets of a column of
        a table

        @params
        ticket - authentication ticket
        search_type - search type
        search_keys - a list of search keys to get widgets
        element_name - name of element to load

        @return
        list: html widgets
        '''
        try: 
            my._init_web(ticket)
            args_array = []
            view = "table"


            from pyasm.widget import WidgetConfig
            xml = '''
            <config><table>
              <element name='%s'/>
            </table></config>''' % element_name
            configx = WidgetConfig.get(view=view, xml=xml)
            config = WidgetConfigView.get_by_search_type(search_type, view)


            # add this config in
            #config.configs = config.configs[1:]
            config.configs.insert(0, configx)

            sobjects = []
            if search_keys:
                # if the first is an insert, ignore
                if search_keys[0].endswith("id=-1"):
                    search_keys = search_keys[1:]

                num_search_keys = len(search_keys)
                if num_search_keys > 1:
                    sobjects = SearchKey.get_by_search_keys(search_keys)
                    num_sobjects = len(sobjects)
                    assert num_search_keys == num_sobjects
            
            # simulate a table drawing with only one column
            from tactic.ui.panel import TableLayoutWdg
            table = TableLayoutWdg(search_type=search_type, view=view, config=config)
            table.set_sobjects(sobjects)
            for i, widget in enumerate(table.widgets):
                if widget.get_name() == element_name:
                    table.widgets = table.widgets[i:i+1]
                    break
            else:
                raise ApiException("Element name [%s] not in view [%s]" % (element_name, view) )
            table.get_display()
            table = table.table

            # grab all of the widgets without the table
            widgets = []
            for row in table.rows:
                row_widgets = []
                for j, row_widget in enumerate(row.widgets):
                    if j < 2:
                        continue
                    row_widgets.append( row_widget.get_buffer_display() )
                widgets.append(row_widgets)
            return widgets

        except Exception, e:
            # make sure all sqls are aborted
            DbContainer.abort_thread_sql(force=True)
            raise



    @xmlrpc_decorator
    def set_config_definition(my, ticket, search_type, element_name, config_xml="", login=None):
        '''set the definition of the particular element.  This definition
        is stored in the database.
        
        @params
        ticket - authentication ticket
        search_type - search type that this config relates to
        '''
        my._init_web(ticket, {})
        if not config_xml:
            title = element_name.split("_")
            title = " ".join( [x.capitalize() for x in title] )
            if element_name.startswith("new_folder"):
                config_xml = '''
<element name='%s' title='%s'>
  <display class='SideBarSectionLinkWdg'>
    <view>%s</view>
  </display>
</element>
''' % (element_name, title, element_name)
            elif element_name.startswith("separator") \
                and element_name.startswith("new_separator"):
                config_xml = '''
<element name='%s'>
  <display class='SeparatorWdg'/>
</element>
''' % (element_name)
            #elif element_name.startswith("new_entry"):
            else:
                config_xml = '''
<element name='%s' title='%s'>
  <display class='LinkWdg'/>
</element>
''' % (element_name, title)


        try:
            view = "definition"

            config_search_type = "config/widget_config"
            search = Search(config_search_type)
            search.add_filter("search_type", search_type)
            search.add_filter("view", view)
            search.add_filter("login", login)
            config = search.get_sobject()
            if not config:
                config = SearchType.create(config_search_type)
                config.set_value("search_type", search_type )
                config.set_value("view", view )

                # create a new document
                xml = Xml()
                xml.create_doc("config")
                root = xml.get_root_node()
                view_node = xml.create_element(view)
                #root.appendChild(view_node)
                xml.append_child(root, view_node)

                config.set_value("config", xml.to_string())
                config._init()


            # append the newly defined element
            config.append_xml_element(element_name,config_xml)
            config.commit_config()


        except Exception, e:
            # make sure all sqls are aborted
            DbContainer.abort_thread_sql(force=True)

            from pyasm.widget import ExceptionWdg
            widget = ExceptionWdg(e)
            return widget.get_buffer_display()

        return True


 




    @xmlrpc_decorator
    def get_config_definition(my, ticket, search_type, view, element_name, personal=False):
        '''get the configuration definition

        @params
        ticket - authentication ticket
        search_type - search type that this config relates to
        view - view to look for the element
        element - specific element configuration to return

        @return
        string: xml of the configuration
        '''
        my._init_web(ticket, {})
        args_array = []
        try:
            from tactic.ui.panel import SideBarBookmarkMenuWdg
            config = SideBarBookmarkMenuWdg.get_config(search_type, view, personal=personal)
            if not config:
                return ""
            config_string = ""
            node = config.get_element_node(element_name)
            if node is None:
                config_string = ""
            else:
                if config.get_xml():
                    config_string = config.get_xml().to_string(node)
            return config_string


        except Exception, e:
            # make sure all sqls are aborted
            DbContainer.abort_thread_sql(force=True)

            from pyasm.widget import ExceptionWdg
            widget = ExceptionWdg(e)
            return widget.get_buffer_display()


    @xmlrpc_decorator
    def update_config(my, ticket, search_type, view, element_names, login=None, deleted_element_names=[]):
        '''update a widget config for a view
        
        @params:
        search_type: the search type that this config belongs to
        view: the specific view of the search type
        element_names: all of the element names in this view
        '''

        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        # we don't have to filter out login is NULL and login is <user>
        # but we write it below for record purposes so someone
        # can easily query it
        #search.add_filter("login", login)
        config = search.get_sobject()
        if not config:
            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )
            if login:
                config.set_value("login", login)

        elif not element_names:
            element_names = config.get_element_names()

        # create a new document
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        #root.appendChild(view_node)
        xml.append_child(root, view_node)

        
        # build a new config
        for element_name in element_names:
            deleted_element_names = Common.get_unique_list(deleted_element_names)
            if element_name in deleted_element_names:
                continue

            # if the old xml has it defined, then keep it
            element = config.get_element_node(element_name)
            if element is not None:
                node = xml.import_node(element, True)
            else:
                # else create a new one
                element = xml.create_element("element")
                xml.set_attribute(element, "name", element_name)
            
            #view_node.appendChild(element)
            xml.append_child(view_node, element)

        config.set_value("config", xml.to_string())
        config.commit()


        # delete any unwanted items in definition
        config_search_type = "config/widget_config"
        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", "definition")
        search.add_filter("login", login)
        def_config = search.get_sobject()
        if def_config:
            def_xml = def_config.get_xml()
            deleted_element_names = Common.get_unique_list(deleted_element_names)
            for name in deleted_element_names:
                element = def_config.get_element_node(name)
                if element is not None:
                    # check if it is a folder and delete its view entry also
                    display_handler = def_config.get_display_handler(name)
                    
                    if display_handler == 'SideBarSectionLinkWdg':
                        options = def_config.get_display_options(name)
                        folder_view = options.get('view')
                        search = Search(config_search_type)
                        search.add_filter("search_type", 'SideBarWdg')
                        search.add_filter("view", folder_view)
                        folder_config = search.get_sobject()
                        if folder_config:
                            folder_config.delete()
                    #node = element.parentNode.removeChild(element)
                    parent_node = def_xml.get_parent(element)
                    def_xml.remove_child(parent_node, element)
                    

            def_config.commit_config()
        return xml.to_string()

    
    @xmlrpc_decorator
    def add_config_element(my, ticket, search_type, view, name, class_name=None, 
           display_options={}, action_class_name=None, action_options={}, element_attrs={},
           login=None, unique=True, auto_unique_name=False, auto_unique_view=False, view_as_attr=False):
        '''Add an element into a config
        
        @params:
        search_type - the search type that this config belongs to
        view - the specific view of the search type
        name - the name of the element
        class_name - the fully qualified class of the display
        action_class_name - the fully qualified class of the action
        display_options - keyward options in a dictionary to construct the specific display
        action_options - keyward options in a dictionary to construct the specific display
        element_attrs - element attributes in a dictionary
        login - login of the user specific to this view
        auto_unique_name - auto generate a unique element and display view name
        auto_unique_view - auto generate a unique display view name
        unique - a unique display view name is expected
        view_as_attr - view should be read or created as a name attribute
        '''
        
        assert view
        config_search_type = "config/widget_config"

        search = Search(config_search_type)
        search.add_filter("search_type", search_type)
        search.add_filter("view", view)
        search.add_filter("login", login)

        config = search.get_sobject()

        configs = []
        from tactic.ui.panel import SideBarBookmarkMenuWdg
        SideBarBookmarkMenuWdg.add_internal_config(configs, ['definition'])
        
        internal_names = ['search','publish','edit','insert','edit_definition','definition']
        existing_names = []
        for internal_config in configs:
            internal_names.extend(internal_config.get_element_names())
        if config:
            db_element_names = config.get_element_names()
            existing_names.extend(db_element_names)

        from pyasm.common import UserException
        # error on name starting with number
        pat = re.compile('^\d+.*')
        if pat.search(name):
            raise UserException('The name [%s] should not start with a number.'%name)
        
        if not view_as_attr and view.find('@') != -1:
            view_as_attr = True
        
        # error out on all special chars from name except .
        pat = re.compile('[\$\s,#~`\%\*\^\&\(\)\+\=\[\]\[\}\{\;\:\'\"\<\>\?\|\\\!]')
        if pat.search(name):
            raise UserException('The name [%s] contains special characters or spaces.'%name)
        
        if unique: 
            if name in existing_names:
                raise UserException('This view name [%s] has been taken.'%name)
            if name in internal_names:
                raise UserException('This view name [%s] is reserved for internal use.'%name)

        
        if config and auto_unique_name:
            # remove all special chars from name except .
            pat = re.compile('[\$\s,@#~`\%\*\^\&\(\)\+\=\[\]\[\}\{\;\:\'\"\<\>\?\|\\\!]')
            name = pat.sub('', name)
            
            import random
            suffix = random.randint(0, 100)
            existing_names = config.get_element_names()
            if name in existing_names:
                new_name = '%s%0.3d' %(name, suffix)
                while True:
                    if new_name in existing_names:
                        suffix += 1
                        new_name = '%s%0.3d' %(name, suffix)
                    else:
                        name = new_name
                        break
            # update the view only if it is a folder since the view is derived from the title
            if auto_unique_view:
                tmp_view = display_options.get('view')
                if tmp_view:
                    display_options['view'] = name
        # find a default for any views but definition
        if not config and view !='definition':
            view_node = WidgetConfigView.get_default_view_node(view) 
            if view_node:
                config = SearchType.create(config_search_type)
                config.set_value("search_type", search_type )
                config.set_value("view", view )
                xml = config.get_xml_value("config", "config")
                root = xml.get_root_node()
                #root.appendChild(view_node)
                xml.append_child(root, view_node)
                config.set_value("config", xml.get_xml())
                if login:
                    config.set_value("login", login)
                config._init()
        
        

        if not config:
            config = SearchType.create(config_search_type)
            config.set_value("search_type", search_type )
            config.set_value("view", view )
            xml = config.get_xml_value("config", "config")
            if login:
                config.set_value("login", login)
            config._init()
            root = xml.get_root_node()
    
   
            # build a new config
            if view_as_attr:
                # personal view uses the new view attr-based xml syntax
                view_node = xml.create_element("view", attrs= {'name': view})
            else:
                view_node = xml.create_element(view)
            #root.appendChild(view_node)
            xml.append_child(root, view_node)

        
            # view has been set from above otherwise
        '''
        xml = config.get_xml_value("config")
        view_node = xml.get_node("config/%s" % view )
        '''

        config.append_display_element(name, cls_name=class_name, options=display_options,
            element_attrs=element_attrs, action_options=action_options, action_cls_name=action_class_name,
            view_as_attr=view_as_attr)

        config.commit_config()
        # this name could be regenerated. so we return it to client
        dict = {'element_name': name}
        
        return dict
    



    #
    # Querying docs
    #
    @xmlrpc_decorator
    def get_doc_link(my, ticket, alias):

        install_dir = Environment.get_install_dir()
        alias_path = "%s/doc/alias.json" % install_dir
        if os.path.exists(alias_path):
            f = open(alias_path)
            aliases_str = f.read()
            f.close()
        else:
            aliases_str = "{}"

        aliases = jsonloads(aliases_str)
        path = aliases.get(alias)
        if not path:
            return "none_found"
        else:
            return path




    # FIXME: this method should not be in the API.  It is way too specific to
    # a single use and cannot be used for any other purpose.  We
    # need to either generalize this or make it part of some non API
    # method list.
    @xmlrpc_decorator
    def get_md5_info(my, ticket, md5_list, new_paths, parent_code, texture_cls, file_group_dict, project_code, mode):
        '''return a dict of {path: info} like is_match, repo_path, repo_file_code '''

        def _get_file_group_file_objects(filename, snapshot_codes):
            '''get the proper file object matching the file name for a file group'''
            search = Search('sthpw/file')
            search.add_filters('snapshot_code', snapshot_codes)
            search.add_filter('file_name', filename)
            project_code = Project.get_project_code()
            search.add_filter("project_code", project_code)
            search.add_order_by('timestamp desc')
            return search.get_sobjects()

        def _get_file_info_dict(new_paths, md5_list):
            '''map md5 to file path in a dict'''
            info = {}
            for idx, path in enumerate(new_paths):
                sub_info = info.get(path)
                md5 = md5_list[idx]
                if not sub_info:
                    info[path] = {'md5': md5}
            return info

        
        main_info = {}
        from pyasm.prod.biz import ShotTexture, Texture
        assert texture_cls in ['ShotTexture', 'Texture']
        Project.set_project(project_code)
        project_code = Project.get_project_code() 
        file_info_dict = _get_file_info_dict(new_paths, md5_list)

        # some path may relate to more than 1 potential texture code which may or may not be used
        texture_code = None
        texture_sobjs = eval("%s.get(texture_code, parent_code, project_code, is_multi=True)"%texture_cls)
        snapshots = Snapshot.get_by_sobjects(texture_sobjs)
        snapshot_codes = SObject.get_values(snapshots, 'code')
        
        file_codes = []
        for snapshot in snapshots:
            file_code = snapshot.get_file_code_by_type("main")
            file_codes.append(file_code)

        files = Search.get_by_code('sthpw/file', file_codes)
        
        for new_path in new_paths:
            
            new_md5 = file_info_dict.get(new_path).get('md5')
            # Cross-checking texture_nodes using the same texture file
            info = {}
            

            # always check for file_group first so it will get reused especially
            # in cases where original file name is kept
            # NOTE: file group or single, when a reuse occurs, it is tied to the existing texture sobject
            if not texture_sobjs:
                info['is_match'] = False
                main_info[new_path] = info
                continue

            if not snapshots:
                info['is_match'] = False
                main_info[new_path] = info
                continue
            
            # essentially file_name mode 
            if not new_md5 and file_group_dict.get(new_path):
                tactic_group_path, file_range = file_group_dict.get(new_path)
                info['is_file_group'] = True
                
                # this is needed otherwise os.path.basename doesn't work
                tactic_group_path = tactic_group_path.replace("\\", "/")
                filename = os.path.basename(tactic_group_path)
                file_objects = _get_file_group_file_objects(filename, snapshot_codes)
                if file_objects:
                    info['is_match'] = True
                    info['repo_path'] = file_objects[0].get_env_path()
                    info['repo_file_code'] = file_objects[0].get_code()
                    info['repo_file_range'] = file_objects[0].get_file_range()
                    #info['file_sobj'] = file_objects[0]
                    if len(file_objects) > 1:
                        print "WARNING: duplicated file groups \
                            for [%s]" %( parent_code)
                else:
                    info['is_match'] = False

                
                main_info[new_path] = info
                continue
                
             
            if mode == 'file_name':
                col_name = 'file_name'
                path  = new_path.replace('\\','/')
                compared_value = os.path.basename(path)
            else:
                col_name = 'md5'
                compared_value = new_md5
          
            for file in files:
                cur_value = file.get_value(col_name)
                if cur_value == compared_value:
                    info['is_match'] = True
                    info['repo_path'] = file.get_env_path()
                    info['repo_file_code'] = file.get_code()
                    break
                else:
                    info['is_match'] = False 
            main_info[new_path] = info
        return main_info

             
        
        


        

    @trace_decorator
    def set_application_state(my, ticket, key, panel_name, widget_class, options, values={}):
        '''Set the application state.  This is used to set the last viewed
        state.  When a user goes back to the Tactic, this info will be used
        to show the interface.
        
        @params
        key: unique key indentifying a particular layout name
        panel_name: name of a panel that is located within a layout
        widget_class: the class that draws the panel
        options: the various options that defined the instance of widget class
        '''
        ticket = my.init(ticket)
        if key == "top_layout":
            class_name = "tactic.ui.app.PageNavContainerWdg"
        else:
            raise ApiException("layout [%s] not supported" % key)

        # create the widget and set the state
        widget = Common.create_from_class_path(class_name)
        widget.set_state(panel_name, widget_class, options, values)

        return True
    set_application_state.exposed = True



    #
    # Transaction methods
    #
    @trace_decorator
    def set_state(my, ticket, name, value):
        return my._set_state(ticket, name, value)
    def _set_state(my, ticket, name, value):
        '''set state variables for this transaction'''
        try:
            ticket = my.init(ticket)
            state = TransactionState.get_by_ticket(ticket)
            state.set_state(name, value)
            state.commit()
        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
        return True
    set_state.exposed = True


    @trace_decorator
    def set_project(my, ticket, project):
        '''set the project state for this ticket'''
        return my._set_state(ticket, "project", project)
    set_project.exposed = True


    @trace_decorator
    def start(my, ticket, project_code, title='', description=None, transaction_ticket=''):
        '''Start an xmlrpc transaction.  This methods puts all of the
        following xmlrpc commands into a single transactions'''
        if not title:
            title = "No title"

        # in local mode, disable start and finish
        if my.get_protocol() == "local":
            # TO BE ENABLED
            #project = Project.get_by_code(project_code)
            #if project:
            #    Project.set_project(project_code)
            transaction = Transaction.get()
            if transaction:
                transaction.set_description(description)
                transaction.set_title(title)
            return ticket

        # otherwise use xmlrpc mode

        # if not new ticket has been specified, generate one
        if not transaction_ticket:
            transaction_ticket = Common.generate_random_key()

        try:
            ticket = my.init(ticket, reuse_container=False)

            from pyasm.security import Site
            transaction_ticket = Site.get().build_ticket(transaction_ticket)

            # set the server in transaction?
            my.set_transaction_state(True)

            # verify project exists
            project = Project.get_by_code(project_code)
            if not project and project_code != 'unittest':
                raise ApiException('Invalid project code [%s]'%project_code)
            Project.set_project(project_code)
            
            # create a transaction ticket
            user = Environment.get_user_name()
            Ticket.create(transaction_ticket, user, interval='7 day')

            if not description:
                description = "Client API (No description)"

            # set the state
            state = TransactionState.get_by_ticket(transaction_ticket)
            state.reset_state()

            # create a log outside of a transaction
            cmd_cls = "pyasm.prod.service.api_xmlrpc.ApiClientCmd" 
            log = TransactionLog.create(cmd_cls, "<transaction/>", description, title)
            log_id = log.get_id()
            state.set_state("transaction", log_id)

            # set the project_code
            state.set_state("project", project_code)
            state.commit()

            Container.put("API:xmlrpc_transaction", False)

        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
            DbContainer.close_all()
            Environment.set_app_server('xmlrpc')
        return transaction_ticket
    start.exposed = True



    @trace_decorator
    def finish(my, ticket, description=""):
        '''finish an xmlrpc transaction
        '''
        # in local mode, disable start and finish
        if my.get_protocol() == "local":
            return True

        try:
            ticket = my.init(ticket)

            state = TransactionState.get_by_ticket(ticket)

            # delete the transaction if it is empty
            transaction_id = state.get_state("transaction")
            if transaction_id:
                transaction = TransactionLog.get_by_id(transaction_id)
                xml = transaction.get_xml_value("transaction")
                nodes = xml.get_nodes("transaction/*")
                if not nodes:
                    transaction.delete()

                elif description:
                    transaction.set_value("description", description)
                    transaction.commit()

                # since this is the final commit for this transaction, record
                # the sobject log
                TransactionLog.create_sobject_log(transaction)

            project_code = state.get_state("project")

            # reset the state
            state.reset_state()

            # maintain the project
            state.set_state("project", project_code)

            state.commit()

            Container.put("API:xmlrpc_transaction", False)
        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
        return True
    finish.exposed = True


    @trace_decorator
    def abort(my, ticket, ignore_files=False):
        '''abort this transaction.  Basically runs undo and then finish

        @params
        ignore_files - flag which determines whether the files should
            also be undone.  Useful for large preallcoated checkins.
        '''
        try:
            try:
                if my.get_protocol() == "local":
                    raise CommandExitException('aborted.')

                ticket = my.init(ticket)
                Container.put("API:xmlrpc_transaction", False)

                state = TransactionState.get_by_ticket(ticket)
                project_code = state.get_state("project")

                state.restore_state()

                # get the transaction_id
                transaction_id = state.get_state("transaction")

                # undo the specific transaction for this ticket
                cmd = UndoCmd(ignore_files=ignore_files)
                cmd.set_transaction_id(transaction_id)
                Command.execute_cmd(cmd)

                # reset the state
                state.reset_state()

                # maintain the project
                state.set_state("project", project_code)

                state.commit()
            except Exception, e:
                print "Exception: ", e.__str__()
                import traceback
                tb = sys.exc_info()[2]
                stacktrace = traceback.format_tb(tb)
                stacktrace_str = "".join(stacktrace)
                print "-"*50
                print stacktrace_str
                print str(e)
                print "-"*50
                raise


        finally:
            if not my.get_protocol() == "local":
                DbContainer.release_thread_sql()
        return True
    abort.exposed = True





