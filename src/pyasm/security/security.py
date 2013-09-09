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

__all__ = ["Login", "LoginInGroup", "LoginGroup", "Ticket", "Security", "NoDatabaseSecurity", "License", "LicenseException", "get_security_version"]

import hashlib, os, sys, types

from pyasm.common import *
from pyasm.search import *

from access_manager import *
from access_rule import *



def get_security_version():
    version = Config.get_value("security", "version")
    if version:
        version = int(version)
    else:
        # default to version 2 beginning in 4.0
        version = 2

    return version




class LoginInGroupException(Exception):
    pass

class Login(SObject):

    SEARCH_TYPE = "sthpw/login"

    def get_defaults(my):
        '''specifies the defaults for this sobject'''

        defaults = super(Login, my).get_defaults()
        # add the password "tactic" to any user that does not have one
        # specified
        defaults['password']= "39195b0707436a7ecb92565bf3411ab1"
        defaults['code'] = my.get_value('login')

        return defaults


    def update_trigger(my):
        # the login groups are cached, so when an update has been made,
        # this cache has to be refreshed
        security = Environment.get_security()
        security.reset_access_manager()



    def get_primary_key(my):
        return "login"
    
    def get_foreign_key(my):
        return "login"
   
    def get_icon_context(my, context=None):
        return "icon"
    
    def get_description(my):
        return my.get_full_name()

    def get_login(my):
        return my.get_value("login")
   
    def get_full_name(my):
        return "%s %s" % (my.get_value("first_name"), my.get_value("last_name"))

    def get_full_email(my):
        return "%s %s <%s>" % (my.get_value("first_name"), \
            my.get_value("last_name"), my.get_value("email") )

    def has_user_license(my):
        '''determines if this user has a user level license'''
        license_type = my.get_value('license_type', no_exception=True)
        return license_type in ['', 'user']



    def add_to_group(my, group_name):
        '''Adds a user to the specified group'''
        if type(group_name) in types.StringTypes:
            my.__validate_group(group_name)
        else:
            group_name = group_name.get_value("login_group")

        # use the sobject as well
        LoginInGroup.create_by_name( my.get_value("login"), group_name )

    def remove_from_group(my, group_name):
        '''removes the user from a specfied group'''
        
        if type(group_name) in types.StringTypes:
            my.__validate_group(group_name)
        else:
            group_name = group_name.get_value("login_group")

        # use the sobject as well
        login_in_group = LoginInGroup.get_by_names( \
                my.get_value("login"), group_name)
        if login_in_group != None:
            login_in_group.delete()


    def remove_all_groups(my, except_list=[]):
        '''removes the user from a specfied group'''
        connectors = LoginInGroup.get_by_login_name(my.get_value("login")) 
        remaining = []
        for login_in_group in connectors:
            if login_in_group.get_value("login_group") in except_list:
                remaining.append(login_in_group)
                continue
            login_in_group.delete()
        return remaining
        



    def __validate_group(my, group_name):
        group = LoginGroup.get_by_group_name(group_name)
        if not group:
            raise LoginInGroupException('This group [%s] does not exist' % group_name)


    def get_sub_group_names(my):
        '''Returns all of the names as a list of strings
        of the sub_groups a group contains'''
        connectors = LoginInGroup.get_by_login_name(my.get_login() ) 
        group_names = [ x.get_value("login_group") for x in connectors ]
        return group_names


    def get_sub_groups(my):
        sub_group_names = my.get_sub_group_names()
        if not sub_group_names or sub_group_names == ['']:
            return []
        
        tmp = ["'%s'" % x for x in sub_group_names ]
        # add the default group
        #tmp.append("'default'")
        tmp = ", ".join(tmp)
        
        search = Search("sthpw/login_group")
        search.add_where("\"login_group\" in (%s)" % tmp )
        groups = search.get_sobjects()


        # check to see if the default is there
        """
        has_default = False
        for group in groups:
            if group.get_login_group() == 'default':
                has_default = True

        if not has_default:
            default_group = SearchType.create("sthpw/login_group")
            default_group.set_value("login_group", "default")
            groups.append(default_group)
        """

        (NONE, MIN, LOW, MED, HI) = range(5)
        access_level = NONE
        project_codes = set()
        for group in groups:
            group_access_level = group.get_value("access_level", no_exception=True)
            project_code = group.get_value("project_code")
            if project_code:
                project_codes.add(project_code)

            if group_access_level == 'high':
                group_access_level = HI
            elif group_access_level == 'medium':
                group_access_level = MED
            elif group_access_level == 'low':
                group_access_level = LOW
            elif group_access_level == 'min':
                group_access_level = MIN
            elif group_access_level == 'none':
                group_access_level = NONE
            else:
                group_access_level = LOW

            if group_access_level > access_level:
                access_level = group_access_level
        groups.append(my.get_security_level_group(access_level, project_codes))

        return groups


    def get_default_security_level():
        ''' this should match the default in get_sub_group()'''
        return "low"
    get_default_security_level = staticmethod(get_default_security_level)


    def get_security_level_group(access_level, project_codes=[]):
        (NONE, MIN, LOW, MED, HI) = range(5)
        assert access_level in [NONE, MIN, LOW, MED, HI]

        xml = []
        xml.append('''<rules>''')
        if access_level == HI:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            else:
                xml.append('''<rule group="project" code="*" access="allow"/>''')
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="link" element="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')


        elif access_level == MED:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            else:
                xml.append('''<rule group="project" code="*" access="allow"/>''')

            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')


        elif access_level == LOW:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')

        elif access_level == MIN:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')

        else: # no security access
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)


        xml.append('''</rules>''')
        xml = "\n".join(xml)

        default_group = SearchType.create("sthpw/login_group")
        default_group.set_value("login_group", "default")
        default_group.set_value("access_rules", xml)
        return default_group

    get_security_level_group = staticmethod(get_security_level_group)




    # static methods

    def get_search():
        return Search("sthpw/login")
    get_search = staticmethod(get_search)


    def get_by_code(code):
        return  Login.get_by_login(code)
    get_by_code = staticmethod(get_by_code)
    
    def get_by_login(login_name, namespace=None):
        if not login_name:
            return None
        
        # find the ticket in the database
        cached = Login.get_cached_obj(login_name)
        if cached:
            return cached

        case_insensitive = False
        # handle admin as a special virtual user
        if Config.get_value("security", "case_insensitive_login", no_exception=True) == 'true':
            login_name = login_name.lower()
            case_insensitive = True
        if login_name == "admin":
            search = Search("sthpw/login")
            search.set_show_retired(True)
            if case_insensitive:
                search.add_regex_filter("login", '^%s'%login_name, op='EQI')
                search.add_regex_filter("login", '%s$'%login_name, op='EQI')
            else:
                search.add_filter("login", login_name)
            login = search.get_sobject()
            if not login:
                login = SearchType.create("sthpw/login")
                login.set_force_insert()

                # MySQL does not support table ID's at 0
                if Sql.get_default_database_type() != 'MySQL':
                    login.set_value("id", 0)
                    login.set_id(0)

                login.set_value("login", "admin")
                login.set_value("first_name", "Adminstrator")
                login.set_value("last_name", "")
                login.set_value("display_name", "Administrator")

                password = Config.get_value("security", "password")
                if not password:
                    password = "39195b0707436a7ecb92565bf3411ab1"
                login.set_value("password", password)

        else:
            search = Search("sthpw/login")
            # make sure it's case insensitive
            if case_insensitive:
                search.add_regex_filter("login", '^%s'%login_name, op='EQI')
                search.add_regex_filter("login", '%s$'%login_name, op='EQI')
            else:
                search.add_filter("login", login_name)
            
            if namespace:
                search.add_filter("namespace", namespace)
            search.set_show_retired(True)
            login = search.get_sobject()
        
        dict = Container.get(SObject._get_cached_key(Login.SEARCH_TYPE))
        dict[login_name] = login
        return login
    get_by_login = staticmethod(get_by_login)



    def set_password(my, password):
        encrypted = hashlib.md5(password).hexdigest()
        my.set_value("password", encrypted)
        my.commit()



    def create(user_name, password, first_name, last_name, groups=None, namespace=None):

        login = SearchType.create("sthpw/login")
        login.set_value("login", user_name)

        # encrypt the password
        encrypted = hashlib.md5(password).hexdigest()
        login.set_value("password", encrypted)

        login.set_value("first_name", first_name)
        login.set_value("last_name", last_name)

        if groups != None:
            login.set_value("groups", groups)
        if namespace != None:
            login.set_value("namespace", namespace)

        login.commit()

        return login

    create = staticmethod(create)


    def get_default_encrypted_password():
        return "39195b0707436a7ecb92565bf3411ab1"
    get_default_encrypted_password = staticmethod(get_default_encrypted_password)

    def get_default_password():
        return "tactic"
    get_default_password = staticmethod(get_default_password)




    def encrypt_password(password):
        encrypted = hashlib.md5(password).hexdigest()
        return encrypted
    encrypt_password = staticmethod(encrypt_password)






class LoginGroup(Login):

    SEARCH_TYPE = "sthpw/login_group"

    
    def get_defaults(my):
        defaults = {}
        defaults['code'] = my.get_value("login_group")
        # LoginGroupTrigger handles the update event
        return defaults

    def is_admin(my):
        group = my.get_value("login_group")
        return group == "admin"


    def get_primary_key(my):
        return "login_group"
    
    def get_foreign_key(my):
        return "login_group"
    
    def get_description(my):
        return my.get_value('description')

    def get_login_group(my):
        return my.get_value("login_group")

    def get_sub_group_names(my):
        sub_groups_str = my.get_value("sub_groups")
        return sub_groups_str.split("|")

    def get_access_rules(my):
        return my.get_value("access_rules")

    def get_xml_root(my, name):
        if name == "access_rules":
            return "rules"

    

    def get_logins(my):
        connectors = LoginInGroup.get_by_group_name(my.get_login_group())
        if not connectors:
            return []

        tmp = ["'%s'" % x.get_value("login") for x in connectors ]
        tmp = ", ".join(tmp)

        search = Search("sthpw/login")
        search.add_where( "\"login\" in (%s)" % tmp )
        logins = search.get_sobjects()
        return logins



    # static methods

    def get_by_code(code):
        return LoginGroup.get_by_group_name(code)
    get_by_code = staticmethod(get_by_code)
    
    def get_by_group_name(group_name):
         # find the group in the database
        search = Search("sthpw/login_group")
        search.add_filter("login_group", group_name)
        group = search.get_sobject()
        return group
    get_by_group_name = staticmethod(get_by_group_name)

    def get(namespace, group_names):
        assert isinstance(group_names, list)
        search = Search("sthpw/login_group")
        search.add_filter("namespace", namespace)
        search.add_filters("login_group", group_names)
        
        return search.get_sobjects()
    get = staticmethod(get)

    def get_group_names(cls, login_name=''):
        if not login_name:
            login_name = Environment.get_user_name()
        
        group_names = []
        login_in_groups = LoginInGroup.get_by_login_name(login_name)
        if login_in_groups:
            group_names = SObject.get_values(login_in_groups, 'login_group')
        return group_names
    get_group_names = classmethod(get_group_names)



    def get_login_codes_in_group(cls, login_name=None):
        if not login_name:
            login_name = Environment.get_user_name()

        key = "LoginGroup:Groups_in_login" 
        groups_dict = Container.get(key)
        if groups_dict == None:
            groups_dict = {}
            Container.put(key, groups_dict)

        results = groups_dict.get(login_name)
        if results != None:
            return results

        group_names = cls.get_group_names(login_name)

        login_codes = set()
        for group_name in group_names:
            group = LoginGroup.get_by_code(group_name)
            if group:
                logins = group.get_logins()

                for login in logins:
                    login_code = login.get_value("login")
                    login_codes.add(login_code)
            else:
                print "This group [%s] no longer exists" %group_name

        results = list(login_codes)
        groups_dict[login_name] = results

        return results
    get_login_codes_in_group = classmethod(get_login_codes_in_group)



    def get_by_project(project_code=None):

        if not project_code:
            from pyasm.biz import Project
            project = Project.get()
            project_code = project.get_code()

        # at the moment, the only way to tell if a group is "in" a project
        # is by the security rules
        search = Search("sthpw/login_group")
        groups = search.get_sobjects()

        project_groups = []
        for group in groups:

            access_level = group.get_value("access_level")
            group_project_code = group.get_value("project_code")

            if group_project_code:
                if project_code == group_project_code:
                    project_groups.append(group)
                    continue

            elif access_level in ['high', 'medium']:
                project_groups.append(group)
                continue

            access_rules = group.get_xml_value("access_rules")
            node = access_rules.get_node("rules/rule[@group='project' and @code='%s']" % project_code)
            if node is not None:
                project_groups.append( group )

            else:
                node = access_rules.get_node("rules/rule[@group='project' and @code='*']")
                if node is not None:
                    project_groups.append( group )


        return project_groups
    get_by_project = staticmethod(get_by_project)




class LoginInGroup(SObject):

    SEARCH_TYPE = "sthpw/login_in_group"


    def get_by_names(login_name, group_name):
        search = Search( LoginInGroup.SEARCH_TYPE )
        search.add_filter("login", login_name)
        search.add_filter("login_group", group_name)
        sobject = search.get_sobject()
        return sobject
    get_by_names = staticmethod(get_by_names)


    def get_by_login_name(cls, login_name):
        search = Search( LoginInGroup.SEARCH_TYPE )
        search.add_filter("login", login_name)
        sobjects = cls.get_by_search(search, "%s|%s" %(cls.SEARCH_TYPE, login_name), is_multi=True)  
        return sobjects
    get_by_login_name = classmethod(get_by_login_name)

    def get_by_group_name(login_name):
        search = Search( LoginInGroup.SEARCH_TYPE )
        search.add_filter("login_group", login_name)
        sobjects = search.get_sobjects()
        return sobjects
    get_by_group_name = staticmethod(get_by_group_name)



    def create(login, login_group):
        return LoginInGroup.create_by_name( \
            login.get_value("login"), login_group.get_value("login_group") )
    create = staticmethod(create)



    def create_by_name(login_name, group_name):
        sobject = SearchType.create( LoginInGroup.SEARCH_TYPE )
        sobject.set_value( "login", login_name)
        sobject.set_value( "login_group", group_name)
        sobject.commit()
        return sobject
    create_by_name = staticmethod(create_by_name)










class Ticket(SObject):
    '''When a user logins, a ticket is created.  This ticket is stored in the
    database as a long unique string of alpha-numeric characters.  It is stored
    on the browser as a cookie and allows the user to login with a password.
    The ticket has an expiry date set in the Tactic config file'''

    def get_key(my):
        '''get the alphanumeric unique code for the session'''
        return my.get_value("ticket")


    def get_by_key(key):
        '''class method to get Ticket sobject by it's key'''
        # find the ticket in the database
        search = Search("sthpw/ticket")
        search.add_filter("ticket", key)
        ticket = search.get_sobject()
        return ticket
    get_by_key = staticmethod(get_by_key)


    def get_by_valid_key(key):
        '''class method to get Ticket sobject by it's key.  The key must be
        valid in that it has not yet expired.'''
        # find the ticket in the database
        search = Search("sthpw/ticket")
        search.add_filter("ticket", key)
        now = search.get_database_impl().get_timestamp_now()
        search.add_where('("expiry" > %s or "expiry" is NULL)' % now)
        ticket = search.get_sobject()
        return ticket
    get_by_valid_key = staticmethod(get_by_valid_key)

       

      


    def create(key, login, expiry=None, interval=None, category=None):
        '''creation function to create a new ticket
            @keyparam: 
                expiry: exact expiry timestamp
                interval: 5 day or 24 hour from now
                category: type of ticket
        '''
        # For now, tickets always come from the default database
        impl = Sql.get_default_database_impl()
        now = impl.get_timestamp_now()

        # expire in 1 hour
        if expiry == -1:
            expiry = "NULL"
        elif not expiry:
            if not interval: 
                interval = Config.get_value("security","ticket_expiry")
                if not interval:
                    interval = "10 hour"
            #expiry = "%s + '%s'" % (now, interval)
            offset, type = interval.split(" ")
            expiry = impl.get_timestamp_now(offset=offset, type=type)

        ticket = SearchType.create("sthpw/ticket")
        ticket.set_value("ticket", key)
        ticket.set_value("login", login)
        ticket.set_value("timestamp", now, quoted=0)
        if category:
            ticket.set_value("category", category)
        """
        if category == 'gui':
            search = Search("sthpw/ticket")
            search.add_filter("login", login)
            search.add_filter("category", category)
            cur_tickets = search.get_sobjects()
            for cur_ticket in cur_tickets:
                #cur_ticket.set_value("expiry", "now()", quoted=False)
                #cur_ticket.commit()
                cur_ticket.delete()
        """

        # it makes no sense for Sqlite sessions to expire
        # FIXME: this is a bit of a hack until we figure out how
        # timestamps work in sqlite (all are converted to GMT?!)
        if impl.get_database_type() in ['Sqlite', 'MySQL']:
            print "WARNING: no expiry on ticket for Sqlite and MySQL"
            ticket.set_value("expiry", 'NULL', quoted=0)
        else:
            ticket.set_value("expiry", expiry, quoted=0)
        ticket.commit(triggers=False)
   

        return ticket
    create = staticmethod(create)
        



# DEPRECATED
class NoDatabaseSecurity(Base):
    def __init__(my):
        #my._login = SearchType.create("sthpw/login")
        my._access_manager = AccessManager()
        my.is_logged_in_flag = False
        pass

    def is_logged_in(my):
        return my.is_logged_in_flag
    def get_license(my):
        return License()
    def login_with_ticket(my, key, add_access_rules=True):
        None
    def login_user(my, login_name, password, expiry=None, domain=None):
        my.is_logged_in_flag = True
    def get_login(my):
        return None
    def get_user_name(my):
        return None
    def get_group_names(my):
        return ['admin']
    def add_access_rules(my):
        pass
    def get_ticket(my):
        return None
    def check_access(my, group, key, access, value=None, is_match=False, default="edit"):
        return True
    def get_access(my, group, key, default=None):
        return "edit"
    def alter_search(my, search):
        pass
    def get_access_manager(my):
        return my._access_manager



class Security(Base):
    '''main class dealing with user identification'''

    def __init__(my):
        my._login_var = None
        my._is_logged_in = 0
        my._groups = []
        my._group_names = []
        my._ticket = None

        my.add_access_rules_flag = True

        # define an access manager object
        my._access_manager = AccessManager()

        my.license = License.get()


        my.login_cache = None


    def _get_my_login(my):
        return my._login_var
    def _set_my_login(my, login):
        my._login_var = login
        if my._login_var and my._login_var.get_value("login") == 'admin':
            my._access_manager.set_admin(True)
        else:
            my._access_manager.set_admin(False)

    _login = property(_get_my_login, _set_my_login)





    def get_version(cls):
        return get_security_version()
    get_version = classmethod(get_version)

    def is_logged_in(my):
        return my._is_logged_in

    def is_admin(my):
        return my._access_manager.is_admin()

    def set_admin(my, flag):
        return my._access_manager.set_admin(flag)

    def get_license(my):
        return my.license

    def reread_license(my):
        my.license = License.get()
        return my.license

    def get_groups(my):
        return my._groups

    def get_group_names(my):
        group_names = my._group_names
        group_names.sort()
        return group_names

    def is_in_group(my, group_name):
        return group_name in my._group_names


    def get_login(my):
        return my._login

    def get_user_name(my):
        return my._login.get_login()

    def get_ticket(my):
        return my._ticket

    def get_ticket_key(my):
        if my._ticket:
            return my._ticket.get_key()
        else:
            return ""


    def get_access_manager(my):
        return my._access_manager


    def reset_access_manager(my):
        my._access_manager = AccessManager()
        my.add_access_rules()

    def sign_out(my):
        my._is_logged_in = 0
        my._login = None
        my._groups = []
        my._group_names = []
        my._ticket = None


    def get_start_link(my):
        for group in my._groups:
            start_link = group.get_value("start_link")
            if start_link:
                return start_link


    def _do_login(my):
        '''function to actually log in the user'''

        # get from cache 
        #from pyasm.biz import LoginCache
        #my.login_cache = LoginCache.get("logins")

        # find all of the groups for this login
        
        #login = my._login.get_login()
        #my._groups = my.login_cache.get_attr("%s:groups" % login)
        #my._groups = my.login_cache.get_attr("%s:groups" % login)
        #my._groups = my.login_cache.get_attr("%s:groups" % login)
        #my._group_names = my.login_cache.get_attr("%s:group_names" % login)
        my._groups = None
        if my._groups == None:
            #print "recaching!!!!"
            my._groups = []
            my._group_names = []
            my._find_all_login_groups()

            # set the results to the cache
            #my.login_cache.set_attr("%s:groups" % login, my._groups)
            #my.login_cache.set_attr("%s:group_names" % login, my._group_names)



        # go through all of the group names and add their respective
        # rules to the access manager
        if my.add_access_rules_flag:
            my.add_access_rules()

        # record that the login is logged in
        my._is_logged_in = 1


    def login_as_batch(my, login_name=None):
        '''function that logs in through a batch command'''

        # default to admin.  Generally batch is run as admin.
        if not login_name:
            login_name = "admin"

        # login must exist in the database
        my._login = Login.get_by_login(login_name)
        if not my._login:
            raise SecurityException("Security failed: Unrecognized user: '%s'" % login_name)

        # create a new ticket for the user
        my._ticket = my._generate_ticket(login_name)

        my._do_login()



    def login_as_guest(my):
        '''function that logs in as guest'''

        login_name = "guest"
        group_name = "guest"

        search = Search("sthpw/login")
        search.add_filter("login", login_name)
        my._login = search.get_sobject()
        if not my._login:
            # login must exist in the database
            my._login = SearchType.create("sthpw/login")
            my._login.set_value("code", login_name)
            my._login.set_value("login", login_name)
            my._login.set_value("first_name", "Guest")
            my._login.set_value("last_name", "User")
            my._login.set_value("display_name", "Guest")
            my._login.commit()

        # create a login group
        search = Search("sthpw/login_group")
        search.add_filter("login_group", login_name)
        group = search.get_sobject()
        if not group:
            group = SearchType.create("sthpw/login_group")
            group.set_value("login_group", group_name)
            group.commit()

            login_in_group = SearchType.create("sthpw/login_in_group")
            login_in_group.set_value("login", login_name)
            login_in_group.set_value("login_group", group_name)
            login_in_group.commit()



        my._find_all_login_groups()

        # create a new ticket for the user
        my._ticket = my._generate_ticket(login_name)

        my._do_login()

        access_manager = my.get_access_manager()
        xml = Xml()
        xml.read_string('''
        <rules>
          <rule column="login" value="cow" search_type="sthpw/login" op="!=" group="search_filter"/>
        </rules>
        ''')
        access_manager.add_xml_rules(xml)





    def login_with_ticket(my, key, add_access_rules=True):
        '''login with the alpha numeric ticket key found in the Ticket
        sobject.'''

        if key == "":
            return None

        my.add_access_rules_flag = add_access_rules

        #from pyasm.biz import CacheContainer
        #cache = CacheContainer.get("sthpw/ticket")
        #cache.build_cache_by_column("ticket")
        #ticket = cache.get_sobject_by_key("ticket", key)
        ticket = Ticket.get_by_valid_key(key)

        if ticket is None:
            # if ticket does not exist, make sure we are signed out and leave
            return None


        # try getting from global cache
        from pyasm.biz import CacheContainer
        login_code = ticket.get_value("login")
        cache = CacheContainer.get("sthpw/login")
        if cache:
            my._login = cache.get_sobject_by_key("login", login_code)

        # if it doesn't exist, try the old method
        if not my._login:
            my._login = Login.get_by_login( ticket.get_value("login") )

        if my._login is None:
            return None

        # store the ticket
        my._ticket = ticket

        my._do_login()

        #print "done: ", time.time() - start
        #print "--- end security - login_with_ticket"

        if my._login.get("login") == "guest":
            access_manager = my.get_access_manager()
            xml = Xml()
            xml.read_string('''
            <rules>
              <rule column="login" value="$LOGIN" search_type="sthpw/login" group="search_filter"/>
            </rules>
            ''')
            access_manager.add_xml_rules(xml)

        return my._login



    def login_with_session(my, sid, add_access_rules):

        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()

        # TEST: this is a test authentication with Drupal
        my.add_access_rules_flag = add_access_rules

        print "sid: ", sid

        from pyasm.security import Sudo
        sudo = Sudo()

        # authenticate use some external method
        if sid:
            expr = '''@SOBJECT(table/sessions?project=drupal['sid','%s'])''' % sid
            print "expr: ", expr
            session = server.eval(expr, single=True)
        else:
            session = {}


        if session:
            uid = session.get("uid")
            expr = '''@SOBJECT(table/users?project=drupal['uid','%s'])''' % uid
            drupal_user = server.eval(expr, single=True)
        else:
            drupal_user = {}

        if not drupal_user:
            return None


        sudo.exit()

        # at this point, the user is authenticated

        user_name = drupal_user.get("name")
        print "login: ", user_name

        # if the user doesn't exist, then autocreate one
        
        my._login = Search.get_by_code("sthpw/login", user_name)
        if not my._login:
            my._login = SearchType.create("sthpw/login")

            my._login.set_value("code", user_name)
            my._login.set_value("login", user_name)
            my._login.set_value("first_name", user_name)
            my._login.set_value("password", drupal_user.get('pass'))
            my._login.set_value("email", drupal_user.get('mail'))
            my._login.commit()

        # do we need a tactic ticket as well ...?
        #my._ticket = my._generate_ticket(user_name, expiry=None)

        search = Search("sthpw/ticket")
        search.add_filter("ticket", sid)
        my._ticket = search.get_sobject()
        if not my._ticket:
            my._ticket = SearchType.create("sthpw/ticket")
            my._ticket.set_value("login", user_name)
            my._ticket.set_value("ticket", sid)
            my._ticket.commit()

        my._do_login()







    def login_user_without_password(my, login_name, expiry=None):
        '''login a user without a password.  This should be used sparingly'''

        search = Search("sthpw/login")
        search.add_filter("login", login_name)
        my._login = search.get_sobject()

        # user still has to exist
        if not my._login:
            raise SecurityException("Login [%s] does not exist" % login_name)

        my._ticket = my._generate_ticket(login_name, expiry)
        my._do_login()



    def login_user(my, login_name, password, expiry=None, domain=None):
        '''login user with a name and password combination
       
        The login has the following modes:

        autocreate : this autocreates the user if it does not exist
        cache : this caches the user in the login table, but information
            is always pulled from the source when thes method is called
        '''
        # check for backwards compatibility
        authenticate_version = Config.get_value(
            "security", "authenticate_version", no_exception=True)
        if authenticate_version == '1':
            return login_user_version_1(login_name, password, expiry)


        # admin always uses the standard authenticate class
        auth_class = None
        if login_name == 'admin':
            auth_class = "pyasm.security.TacticAuthenticate"

        # verify using the specified authenticate class
        if not auth_class:
            auth_class = Config.get_value("security", "authenticate_class",
                no_exception=True)
        if not auth_class:
            auth_class = "pyasm.security.TacticAuthenticate"


        # handle the windows domain
        if domain and login_name !='admin':
            auth_login_name = "%s\\%s" % (domain, login_name)
        else:
            auth_login_name = login_name



        authenticate = Common.create_from_class_path(auth_class)
        is_authenticated = authenticate.verify(auth_login_name, password)
        if is_authenticated != True:
            raise SecurityException("Login/Password combination incorrect")

        mode = authenticate.get_mode()
        if not mode:
            mode = Config.get_value( "security", "authenticate_mode", no_exception=True)
        if not mode:
            mode = 'default'
        
        # lowercase name if case-insensitive is set to true
        if Config.get_value("security", "case_insensitive_login", no_exception=True) == 'true':
            login_name = login_name.lower()
        # when mode is autocreate, then the user entry is created automatically
        # on first entry.  Future verifies will use the login in stored in the
        # database.
        if mode == 'autocreate':
            # get the login from the authentication class
            my._login = Login.get_by_login(login_name)
            if not my._login:
                my._login = SearchType.create("sthpw/login")
                my._login.set_value('login', login_name)
                authenticate.add_user_info( my._login, password)
 
                my._login.commit(triggers=False)

        # when mode is cache, it does autocreate and update user_info every time
        # this is called
        elif mode == 'cache':
            # get the login from the authentication class
            my._login = Login.get_by_login(login_name)
            if not my._login:
                my._login = SearchType.create("sthpw/login")
                my._login.set_value('login', login_name)
            authenticate.add_user_info( my._login, password)

            # verify that this won't create too many users.  Floating licenses
            # can have any number of users
            if my._login.has_user_license():
                num_left = my.license.get_num_licenses_left()
                if num_left <= 0:
                    raise SecurityException("Number of active users exceeds licenses")

            my._login.commit()

        else:
            # get the login from database and don't bother updating
            my._login = Login.get_by_login(login_name)



        # if it doesn't exist, then the login fails
        if not my._login:
            raise SecurityException("Login/Password combination incorrect")


        # if the user is disabled, then they cannot log in
        license_type = my._login.get_value("license_type", no_exception=True)
        if license_type == "disabled":
            raise SecurityException("User [%s] is disabled" % my._login.get_value('login'))

        # check if the user has a floating license
        elif license_type == 'float': 
            try:
                my.license.verify_floating(login_name)
            except LicenseException, e:
                raise SecurityException(str(e))


        # create a new ticket for the user
        my._ticket = my._generate_ticket(login_name, expiry, category="gui")

        my._do_login()





    # DEPRECATED as 2.5
    def login_user_version_1(my, login_name, password, expiry=None):
        '''login user with a name and password combination
       
        The login has the following modes:

        autocreate : this autocreates the user if it does not exist
        cache : this caches the user in the login table, but information
            is always pulled from the source when thes method is called
        '''

        # check to see if this user exists
        test_login = Login.get_by_login(login_name)
        if test_login:
            autocreate = False
        else:
            # if the user does not already exist, check to see if the user
            # is autocreated
            autocreate = Config.get_value("security", "auto_create_user", no_exception=True)
            if autocreate == 'true':
                autocreate = True
            else:
                autocreate = False

        auth_class = Config.get_value("security", "authenticate_class", no_exception=True)
        if not auth_class:
            auth_class = "pyasm.security.TacticAuthenticate"

        # get once again (why??)
        my._login = Login.get_by_login(login_name)

        if not my._login:
            if autocreate:
                # if autocreate is on, create a "virtual" user
                my._login = SearchType.create("sthpw/login")
                my._login.set_value("login", login_name)

            else:
                raise SecurityException("Login/Password combination incorrect")


        authenticate = Common.create_from_class_path(auth_class)
        is_authenticated = authenticate.authenticate(my._login, password)
        if is_authenticated != True:
            raise SecurityException("Login/Password combination incorrect")


        # if the user is disabled, then they cannot log in
        if my._login.get_value("license_type", no_exception=True) == "disabled":
            raise SecurityException("User [%s] is disabled" % my._login.get_value('login'))


        # if no exception has occured the user is authenticated.
        # If autocreate is on, then the user is created in Tactic as well
        if autocreate:
            # put this in a transaction
            from pyasm.command import Command
            class CreateUser(Command):
                def execute(my):
                    # FIXME: should probably centralize password encryption
                    #encrypted = md5.new(password).hexdigest()
                    encrypted = hashlib.md5(password).hexdigest()
                    my._login.set_value("password", encrypted)

                    # provide the opportunity for authenticate to set values
                    # on creation
                    authenticate.add_user_info(my._login)

                    my._login.commit()
            cmd = CreateUser()
            cmd._login = my._login
            Command.execute_cmd(cmd)

        else:
            # allow the authentication class to add specific user info
            authenticate.add_user_info(my._login)

        # create a new ticket for the user
        my._ticket = my._generate_ticket(login_name, expiry)

        my._do_login()





    def _generate_ticket(my, login_name, expiry=None, category=None):
        # create a new ticket for the user
        ticket_key = Common.generate_random_key()

        # Guest does not get a ticket
        #if login_name == "guest":
        #    return None

        ticket = Ticket.create(ticket_key,login_name, expiry, category=category)
        return ticket



    def compare_access(my, user_access, required_access):
        return my._access_manager.compare_access(user_access, required_access)


    def check_access(my, group, key, access, value=None, is_match=False, default="edit"):
        '''convenience function to check the security level to the access
        manager'''
        return my._access_manager.check_access(group, key, access, value, is_match, default=default)

    def get_access(my, group, key, default=None):
        return my._access_manager.get_access(group, key, default=None)





    def alter_search(my, search):
        '''convenience function to alter a search for security reasons'''
        # set that the security filter has been added
        search.set_security_filter()
        return my._access_manager.alter_search(search)






    def is_login_in_group(my, group):
        '''returns whether the user is in the give group'''
        if group in my._group_names:
            return True
        else:
            return False


    def _find_all_login_groups(my, group=None):

        if not group:
            groups = my._login.get_sub_groups()
            for group in groups:

                group_name = group.get_login_group()
                if group_name in my._group_names:
                    continue

                my._groups.append(group)
                my._group_names.append(group.get_login_group())
                my._find_all_login_groups(group)

        else:
            # break any circular loops
            group_name = group.get_login_group()
            if group_name in my._group_names:
                return

            my._groups.append(group)
            my._group_names.append(group.get_login_group())

            # go through the subgroups
            sub_groups = group.get_sub_groups()
            for sub_group in sub_groups:
                my._find_all_login_groups(sub_group)


        # make sure my._groups is an array
        if my._groups == None:
            my._groups = []

        #for x  in my._groups:
        #    print x.get_login_group()



    def add_access_rules(my):
        if my._login and my._login.get_value("login") == 'admin':
            my._access_manager.set_admin(True)
            return

        for group in my._groups:
            login_group = group.get_value("login_group")
            if login_group == "admin":
                my._access_manager.set_admin(True)
                return

        # go through all of the groups and add access rules
        for group in my._groups:
            access_rules_xml = group.get_xml_value("access_rules")
            my._access_manager.add_xml_rules(access_rules_xml)

        # DEPRECATED
        # get all of the security rules
        #security_rules = AccessRule.get_by_groups(my._groups)
        #for rule in security_rules:
        #    access_rules_xml = rule.get_xml_value("rule")
        #    my._access_manager.add_xml_rules(access_rules_xml)



import pickle, os, base64
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5

# HACK:  From PyCrypto-2.0.1 to PyCrypt-2.3, the install datastructure: RSAobj
# was changed to _RSAobj.  This means that the unwrapped key, which is basically
# a pickled tuple has a the RSAobj in it.  This causes a stack trace when
# doing a pickle.loads.  The following remaps the module to have the old
# RSAobj so that everything maps correctly.
#
try:
    RSA.RSAobj = RSA._RSAobj
except:
    # Skipping
    pass


class LicenseKey(object):
    def __init__(my, public_key):
        # unwrap the public key (for backwards compatibility
        unwrapped_key = my.unwrap("Key", public_key)
        try:
            # get the size and key object
            haspass, my.size, keyobj = pickle.loads(unwrapped_key)
            my.algorithm, my.keyobj = pickle.loads(keyobj)
        except Exception, e:
            raise LicenseException("License key corrupt. Please verify license file. %s" %e.__str__())



    def verify_string(my, raw, signature):
        # unwrap the signature
        unwrapped_signature = my.unwrap("Signature", signature)
   
        # deconstruct the signature
        algorithm, raw_signature = pickle.loads(unwrapped_signature)
        assert my.algorithm == algorithm

        # MD5 the raw text
        m = MD5.new()
        m.update(raw)
        d = m.digest()

        if my.keyobj.verify(d, raw_signature):
            return True
        else:
            return False

    def unwrap(my, type, msg):
        msg = msg.replace("<StartPycrypto%s>" % type, "")
        msg = msg.replace("<EndPycrypto%s>" % type, "")
        binary = base64.decodestring(msg)
        return binary
        




class LicenseException(Exception):
    pass

class License(object):
    license_path = "%s/tactic-license.xml" % Environment.get_license_dir()
    NO_LICENSE = 'no_license'

    def __init__(my, path=None, verify=True):
        my.message = ""
        my.status = "NOT FOUND"
        my.licensed = False
        my.xml = None

        if path:
            my.license_path = path

        my.verify_flag = verify

        try:
            my.parse_license()
        except LicenseException, e:
            my.message = e.__str__()
            print "WARNING: ", my.message
            my.licensed = False

            # this is the minimal acceptable data for my.xml, dont't set to None
            # this should be the place to redefine it if applicable
            if not my.xml:
                my.xml = Xml('<%s/>'%my.NO_LICENSE)
        else:
            my.licensed = True
            

    def parse_license(my, check=False):
        '''check = True is only used for creation verification'''
        if not os.path.exists(my.license_path):
            raise LicenseException("Cannot find license file [%s]" % my.license_path )

        my.xml = Xml()

        try:
            my.xml.read_file(my.license_path, cache=False)
        except XmlException, e:
            my.xml.read_string("<license/>")
            raise LicenseException("Error parsing license file: malformed xml license file [%s] e: %s" % (my.license_path, e))

        # verify signature
        signature = str(my.xml.get_value("license/signature"))
        signature = signature.strip()
        data_node = my.xml.get_node("license/data")
        data = my.xml.to_string(data_node).strip()
        public_key = str(my.xml.get_value("license/public_key"))

        # the data requires a very specific spacing.  4Suite puts out a
        # different dump and lxml and unfortunately, the license key is
        # dependent on the spacing.
        #print "data: [%s]" % data
        data = data.replace("    ", "  ")
        data = data.replace("  </data>", "</data>")
        #print "data: [%s]" % data

    
        # verify the signature
        if my.verify_flag:
            key = LicenseKey(public_key)
            if not key.verify_string(data, signature):
                # will be redefined in constructor
                my.xml = None
                if check ==True:
                    raise TacticException("Data and signature in license file do not match in [%s]" % my.license_path)
                else:
                    raise LicenseException("Data and signature in license file do not match in [%s]" % my.license_path)
            my.verify_license()
            #my.verify()



    def is_licensed(my):
        return my.licensed


    def get_message(my):
        return my.message


    def verify(my):
        try:
            my.verify_license()
            my.licensed = True
            return True
        except LicenseException, e:
            my.message = e.__str__()
            my.licensed = False
            my.LICENSE = None
            return False


    def verify_floating(my, login_name=None):
        # check if the user has a floating license
        floating_max = my.get_max_floating_users()
        if not floating_max:
            raise LicenseException("No floating licenses are available")
        floating_current_users = my.get_current_floating_users()
        floating_current = len(floating_current_users)

        #print "foating_max: ", floating_max
        #print "foating_current: ", floating_current
        #print "login_name: ", login_name
        #print "floating_current_users: ", floating_current_users

        # if the user is in the list, then this user is already logged in
        if login_name and login_name in floating_current_users:
            return True

        if floating_current >= floating_max:
            raise LicenseException("Too many users. Please try again later")


    def get_data(my, key):
        value = my.xml.get_value("license/data/%s" % key)
        return value           


    def get_max_users(my):
        value = my.xml.get_value("license/data/max_users")
        try:
            value = int(value)
        except ValueError:
            value = 10
        return value


    def get_max_floating_users(my):
        value = my.xml.get_value("license/data/max_floating_users")
        try:
            value = int(value)
        except ValueError:
            value = 0
        return value



    def get_num_licenses_left(my):
        max_users = my.get_max_users()
        current_users = my.get_current_users()
        left = max_users - current_users
        return left


        floating_current_users = my.get_current_floating_users()
        floating_current = len(floating_current_users)


    def get_expiry_date(my):
        value = my.xml.get_value("license/data/expiry_date")
        return value

    def get_current_users(my):
        # FIXME: hard coded database
        sql = DbContainer.get("sthpw")
        select = Select()
        select.set_database("sthpw")
        select.add_table("login")

        columns = sql.get_column_info("login").keys()
        if 'license_type' in columns:
            select.add_op('begin')
            select.add_filter("license_type", 'user')
            select.add_filter("license_type", "NULL", quoted=False, op="is")
            select.add_op('or')

        select.add_op('begin')
        select.add_filter("s_status", "NULL", quoted=False, op="is")
        select.add_filter("s_status", "retired", op="!=")
        select.add_op('or')
        #select.add_filter("login", "('admin','guest')", quoted=False, op="not in")
        select.add_filters("login", ['admin','guest'], op="not in")

        num_users = select.execute_count()
        #statement = select.get_count()
        #print "statement: ", statement
        #num_users = sql.get_value(statement)
        #num_users = int(num_users)
        return num_users


    def get_current_floating_users(my):
        '''Get the current floating licenses used

        The definition of a used floating license is a user who has an
        unexpired ticket
        '''
        #import time
        #start = time.time()
        sql = DbContainer.get("sthpw")
        impl = sql.get_database_impl()

        # use users
        select = Select()
        select.set_database(sql)
        select.add_table("login")
        select.add_join("ticket", column="login", column2="login", join="INNER")
        select.add_where('"expiry" is not NULL')
        select.add_filter("expiry", impl.get_timestamp_now(), quoted=False, op=">")
        select.add_column("login", distinct=True)

        # only count float licenses
        columns = sql.get_columns("login")
        if 'license_type' in columns:
            select.add_where("\"license_type\" = 'float'")

        #statement = select.get_count()
        statement = select.get_statement()
        #print "statement: ", statement

        login_names = sql.do_query(statement)
        login_names = [x[0] for x in login_names]
        #num_float = len(login_names)

        return login_names
        #return num_float





    def verify_license(my):
        '''Reads the license file.'''

        # go through the checks
        if not my.xml:
            raise LicenseException(my.message)
            #raise LicenseException("Parsing of licensing file [%s] failed. Renew it in the Projects tab." % my.license_path )


        node = my.xml.get_node("license")
        if node is None:
            no_lic_node = my.xml.get_node(my.NO_LICENSE)
            if no_lic_node is not None:
                raise LicenseException(my.message)
            else:
                raise LicenseException("Parsing of license file [%s] failed." % my.license_path )

        version = my.xml.get_value("license/version")
        # for now, there is only one version of the license
        if 1:
            # check for mac address, if it exists in license
            license_mac = my.xml.get_value("license/data/mac_address")
            license_mac = license_mac.strip()
            if license_mac:
                mac = my.get_mac_address()
                if mac != license_mac:
                    raise LicenseException("License mac address do not match")

            # check for expiry date, if it exists
            license_expiry = my.xml.get_value("license/data/expiry_date")
            license_expiry = license_expiry.strip()
            if license_expiry:
                current = Date().get_db_time()
                if current> license_expiry:
                    raise LicenseException("License expired on [%s] in [%s]" % (license_expiry, my.license_path))




            # check for tactic version
            license_version = my.xml.get_value("license/data/tactic_version")
            release_version = Environment.get_release_version()
            if not license_version:
                raise LicenseException("License file not locked to a specific version of TACTIC")
            try:
                if license_version in ["EPL", "ALL"]:
                    # really big
                    license_version = 10**6
                else:
                    parts = license_version.split(".")
                    license_version = float("%s.%s" % (parts[0],parts[1])) 

                parts = release_version.split(".")
                release_version = float("%s.%s" % (parts[0],parts[1])) 

            except:
                raise LicenseException("Incorrect format for version in license file")

            else:
                if release_version > license_version:
                    raise LicenseException("License not valid for this version of TACTIC. License is for v%s" % license_version)






            # check for max users
            license_users = my.get_max_users()
            if license_users:
                license_users = int(license_users)
                try:
                    current = my.get_current_users()
                except DatabaseException:
                    # set it to zero.  If there is a database error, then
                    # it doesn't really matter because nobody can use the
                    # software anways
                    current = 0
                    
                if current > license_users:
                    raise LicenseException("Too many users for license [%s]" % my.license_path)
        #print "License verified ... "



    def get_mac_address(my):
        '''copied from Newsgroup somewhere'''
        if sys.platform == 'win32':
            for line in os.popen("ipconfig /all"):
                if line.lstrip().startswith('Physical Address'):
                    mac = line.split(':')[1].strip().replace('-',':')
                    break
        else:
            for line in os.popen("/sbin/ifconfig"):
                if line.find('Ether') > -1:
                    mac = line.split()[4]
                    break
        return mac 


    # global license variable
    LICENSE = None
    LAST_CHECK = None
    LAST_MTIME = None

    def get(cls):
        # reparse every hour
        now = Date()
        now = now.get_db_time()
        last = Date(db=cls.LAST_CHECK)
        last.add_hours(1)
        next = last.get_db_time()

        # reparse if the license file has been modified
        exists = os.path.exists(cls.license_path)
        if exists:
            mtime = os.path.getmtime(cls.license_path)
        else:
            mtime = None

        if not exists or not cls.LICENSE \
                or not cls.LAST_CHECK \
                or now > next \
                or not cls.LAST_MTIME \
                or mtime > cls.LAST_MTIME:
            cls.LICENSE = License()
        else:
            cls.LICENSE.verify()

        cls.LAST_CHECK = now
        cls.LAST_MTIME = mtime

        return cls.LICENSE


    get = classmethod(get)



