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

__all__ = ["Login", "LoginInGroup", "LoginGroup", "Site", "Ticket", "TicketHandler", "Security", "NoDatabaseSecurity", "License", "LicenseException", "get_security_version"]

import hashlib, os, sys, types, six
#import tacticenv
from pyasm.common import *
from pyasm.search import *

from .access_manager import *
from .access_rule import *

IS_Pv3 = sys.version_info[0] > 2

from .drupal_password_hasher import DrupalPasswordHasher

if Config.get_value("install", "shutil_fix") in ["enabled"]:
    # disabling copystat method for windows shared folder mounted on linux
    def copystat_dummy(src, dst):
        pass

    import shutil
    shutil.copystat = copystat_dummy

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

    def get_defaults(self):
        '''specifies the defaults for this sobject'''

        defaults = super(Login, self).get_defaults()
        # add the password "tactic" to any user that does not have one
        # specified
        defaults['password']= "39195b0707436a7ecb92565bf3411ab1"
        defaults['code'] = self.get_value('login')
        defaults['upn'] = self.get_value('login')

        return defaults


    def update_trigger(self):
        # the login groups are cached, so when an update has been made,
        # this cache has to be refreshed
        security = Environment.get_security()
        security.reset_access_manager()



    def get_primary_key(self):
        return "login"

    def get_foreign_key(self):
        return "login"

    def get_icon_context(self, context=None):
        return "icon"

    def get_description(self):
        return self.get_full_name()

    def get_login(self):
        return self.get_value("login")

    def get_full_name(self):
        full_name = "%s %s" % (self.get_value("first_name"), self.get_value("last_name"))
        full_name = full_name.strip()
        return full_name

    def get_full_email(self):
        email = self.get_value("email")
        if email:
            first_name = self.get_value("first_name") or ""
            last_name = self.get_value("last_name") or ""
            value = "%s %s <%s>" % (first_name, last_name, email)
            return value
        else:
            return ""

    def has_user_license(self):
        '''determines if this user has a user level license'''
        license_type = self.get_value('license_type', no_exception=True)
        return license_type in ['', 'user']



    def add_to_group(self, group_name):
        '''Adds a user to the specified group'''
        if isinstance(group_name, six.string_types):
            self.__validate_group(group_name)
        else:
            group_name = group_name.get_value("login_group")

        # use the sobject as well
        LoginInGroup.create_by_name( self.get_value("login"), group_name )

    def remove_from_group(self, group_name):
        '''removes the user from a specfied group'''

        if isinstance(group_name, six.string_types):
            self.__validate_group(group_name)
        else:
            group_name = group_name.get_value("login_group")

        # use the sobject as well
        login_in_group = LoginInGroup.get_by_names( \
                self.get_value("login"), group_name)
        if login_in_group != None:
            login_in_group.delete()


    def remove_all_groups(self, except_list=[]):
        '''Remove the user from a specfied group. Return a list of skipped login_in_group'''
        connectors = LoginInGroup.get_by_login_name(self.get_value("login"))
        remaining = []
        for login_in_group in connectors:
            if login_in_group.get_value("login_group") in except_list:
                remaining.append(login_in_group)
                continue
            login_in_group.delete()
        return remaining




    def __validate_group(self, group_name):
        group = LoginGroup.get_by_group_name(group_name)
        if not group:
            raise LoginInGroupException('This group [%s] does not exist' % group_name)


    def get_sub_group_names(self):
        '''Returns all of the names as a list of strings
        of the sub_groups a group contains'''

        connectors = LoginInGroup.get_by_login_name(self.get_login() )
        group_names = [ x.get_value("login_group") for x in connectors ]
        return group_names


    def get_sub_groups(self):
        sub_group_names = self.get_sub_group_names()
        if not sub_group_names or sub_group_names == ['']:
            return []

        tmp = ["'%s'" % x for x in sub_group_names ]
        # add the default group
        #tmp.append("'default'")
        tmp = ", ".join(tmp)

        search = Search("sthpw/login_group")
        search.add_where("\"login_group\" in (%s)" % tmp )
        groups = search.get_sobjects()


        # look access level rules for this user
        access_level = LoginGroup.NONE
        project_codes = set()
        for group in groups:
            group_access_level = group.get_value("access_level", no_exception=True)
            project_code = group.get_value("project_code")
            if project_code:
                project_codes.add(project_code)

            group_access_level = LoginGroup.ACCESS_DICT.get(group_access_level)
            if group_access_level == None:
                group_access_level = LoginGroup.LOW

            if group_access_level > access_level:
                access_level = group_access_level
        groups.append(self.get_security_level_group(access_level, project_codes))

        return groups


    def get_default_security_level():
        ''' this should match the default in get_sub_group()'''
        return "low"
    get_default_security_level = staticmethod(get_default_security_level)


    def get_security_level_group(access_level, project_codes=[]):

        xml = LoginGroup.get_default_access_rule(access_level, project_codes, add_root=True)

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

    def get_by_login(login_name, namespace=None, use_upn=False):

        if not login_name:
            return None

        # find the ticket in the database
        cached = Login.get_cached_obj(login_name)
        if cached:
            return cached

        # This function runs as Sudo
        from pyasm.security import Sudo
        sudo = Sudo()
        user = Environment.get_user_name()
        try:

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

                    columns = SearchType.get_columns("sthpw/login")

                    login.set_value("login", "admin")
                    login.set_value("code", "admin")
                    login.set_value("first_name", "Adminstrator")
                    login.set_value("last_name", "")
                    login.set_value("display_name", "Administrator")

                    data = login.get_data()
                    for column in columns:
                        if data.get(column) == None:
                            login.set_value(column, "")

                    password = Config.get_value("security", "password")
                    if not password:
                        password = "39195b0707436a7ecb92565bf3411ab1"
                    login.set_value("password", password)


                elif not login.get("password"):
                    password = Config.get_value("security", "password")
                    if not password:
                        password = "39195b0707436a7ecb92565bf3411ab1"
                    login.set_value("password", password)

                if not login.get_value("email"):
                    default_admin_email = Config.get_value("services", "mail_default_admin_email")
                    login.set_value("email", default_admin_email)

            else:
                search = Search("sthpw/login")
                # make sure it's case insensitive
                if use_upn:
                    search.add_op("begin")
                if case_insensitive:
                    search.add_op("begin")
                    search.add_regex_filter("login", '^%s'%login_name, op='EQI')
                    search.add_regex_filter("login", '%s$'%login_name, op='EQI')
                    search.add_op("and")
                else:
                    search.add_filter("login", login_name)
                    if use_upn:
                        search.add_filter("upn", login_name)
                if use_upn:
                    search.add_op("or")

                if namespace:
                    search.add_filter("namespace", namespace)
                search.set_show_retired(True)
                login = search.get_sobject()

        finally:
            sudo.exit()


        dict = Container.get(SObject._get_cached_key(Login.SEARCH_TYPE))
        dict[login_name] = login
        return login
    get_by_login = staticmethod(get_by_login)



    def set_password(self, password):
        encrypted = self.encrypt_password(password)
        self.set_value("password", encrypted)
        self.commit()



    def create(cls, user_name, password, first_name=None, last_name=None, groups=None, namespace=None, display_name=None, project_code=None):

        login = SearchType.create("sthpw/login")
        login.set_value("login", user_name)
        login.set_value("upn", user_name)

        # encrypt the password
        encrypted = cls.encrypt_password(password)
        login.set_value("password", encrypted)

        if first_name:
            login.set_value("first_name", first_name)
        if last_name:
            login.set_value("last_name", last_name)

        if display_name:
            login.set_value("display_name", display_name)

        # DEPRECATED: this is no longed supported
        #if groups != None:
        #    login.set_value("groups", groups)

        if namespace != None:
            login.set_value("namespace", namespace)


        login.commit()

        if groups:
            for group in groups:
                login.add_to_group(group)
        else:
            default_group = LoginGroup.get_project_default(project_code=project_code)
            if default_group:
                login.add_to_group(default_group)

        return login

    create = classmethod(create)


    def get_default_encrypted_password():
        return "39195b0707436a7ecb92565bf3411ab1"
    get_default_encrypted_password = staticmethod(get_default_encrypted_password)

    def get_default_password():
        return "tactic"
    get_default_password = staticmethod(get_default_password)




    def encrypt_password(password):
        salt = Common.generate_alphanum_key(num_digits=8, mode='alpha')
        iter_code = 'D'
        encrypted = DrupalPasswordHasher().encode(password, salt, iter_code)
        return encrypted
    encrypt_password = staticmethod(encrypt_password)






class LoginGroup(Login):

    SEARCH_TYPE = "sthpw/login_group"
    (NONE, MIN, LOW, MED, HI) = range(5)

    ACCESS_DICT = {'high': HI, 'medium': MED, 'low': LOW, 'min': MIN, 'none': NONE}

    def get_defaults(self):
        defaults = {}
        if self.get_value("name"):
            defaults['login_group'] = self.get_value("name")
            defaults['code'] = defaults['login_group']
        else:
            defaults['code'] = self.get_value("login_group")
        # LoginGroupTrigger handles the update event
        return defaults

    def is_admin(self):
        group = self.get_value("login_group")
        return group == "admin"


    def get_primary_key(self):
        return "login_group"

    def get_foreign_key(self):
        return "login_group"

    def get_description(self):
        return self.get_value('description')

    def get_login_group(self):
        return self.get_value("login_group")

    def get_sub_group_names(self):
        sub_groups_str = self.get_value("sub_groups")
        return sub_groups_str.split("|")

    def get_access_rules(self):
        return self.get_value("access_rules")

    def get_xml_root(self, name):
        if name == "access_rules":
            return "rules"



    def get_logins(self):
        connectors = LoginInGroup.get_by_group_name(self.get_login_group())
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
                #print("This group [%s] no longer exists" %group_name)
                pass

        results = list(login_codes)
        groups_dict[login_name] = results

        return results
    get_login_codes_in_group = classmethod(get_login_codes_in_group)



    def get_by_project(cls, project_code=None):

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

            # this column complete determines if a login is in a project or not
            group_project_code = group.get_value("project_code")
            if group_project_code:
                if project_code == group_project_code:
                    project_groups.append(group)
                continue

            elif access_level in ['high', 'medium']:
                project_groups.append(group)
                continue


            access_rules = group.get_xml_value("access_rules")
            node = access_rules.get_node("rules/rule[@group='project' and @code='%s' and @access='allow']" % project_code)
            if node is not None:
                project_groups.append( group )

            else:
                node = access_rules.get_node("rules/rule[@group='project' and @code='*' and @access='allow']")
                if node is not None:
                    print("added2")
                    project_groups.append( group )


        return project_groups
    get_by_project = classmethod(get_by_project)


    def get_project_default(cls, project_code=None):
        groups = cls.get_by_project(project_code)
        for group in groups:
            if group.get_value("is_default", no_exception=True):
                return group
        return None
    get_project_default = classmethod(get_project_default)




    def get_access_level(self):
        level = self.get_value('access_level')
        if not level:
            level = Login.get_default_security_level()
        level = self.ACCESS_DICT.get(level)
        return level



    def get_default_access_rule(access_level, project_codes=[], add_root=True):
        ''' Get the default xml rule for a paricular access level'''
        #(NONE, MIN, LOW, MED, HI) = range(5)
        assert access_level in [LoginGroup.NONE, LoginGroup.MIN, LoginGroup.LOW, LoginGroup.MED, LoginGroup.HI]
        xml = []

        if add_root:
            xml.append('''<rules>''')

        xml.append('''<rule group="builtin" default="deny"/>''')
        xml.append('''<rule category="secure_wdg" default="deny"/>''')
        xml.append('''<rule category="public_wdg" default="edit"/>''')

        if access_level == LoginGroup.HI:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            else:
                xml.append('''<rule group="project" code="*" access="allow"/>''')
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="link" element="*" access="allow"/>''')
            xml.append('''<rule group="gear_menu" submenu="*" label="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" pipeline="*" access="allow"/>''')
            xml.append('''<rule group="builtin" key="edit" access="allow"/>''')
            xml.append('''<rule group="builtin" key="view_side_bar" access="allow"/>''')


        elif access_level == LoginGroup.MED:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            else:
                xml.append('''<rule group="project" code="*" access="allow"/>''')

            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" pipeline="*" access="allow"/>''')
            xml.append('''<rule group="builtin" key="edit" access="allow"/>''')


        elif access_level == LoginGroup.LOW:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" access="allow"/>''')
            xml.append('''<rule group="process" process="*" pipeline="*" access="allow"/>''')

        elif access_level == LoginGroup.MIN:
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)
            xml.append('''<rule group="search_type" code="*" access="allow"/>''')

        else: # no security access
            if project_codes:
                for project_code in project_codes:
                    xml.append('''<rule group="project" code="%s" access="allow"/>''' % project_code)

        if add_root:
            xml.append('''</rules>''')
        xml = "\n".join(xml)

        return xml

    get_default_access_rule = staticmethod(get_default_access_rule)




class LoginInGroup(SObject):

    SEARCH_TYPE = "sthpw/login_in_group"


    def get_by_names(login_name, group_name):
        search = Search( LoginInGroup.SEARCH_TYPE, sudo=True )
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





class Site(object):
    '''This is used to manage various "sites" (databases) within a single
    TACTIC installation.  Tickets are scoped by site which determines
    the location of database.'''


    # HACK: Some functions to spoof an sobject
    def get_project_code(self):
        return "admin"

    def get_base_search_type(self):
        return "sthpw/virtual"

    def get_search_type(self):
        return "sthpw/virtual"

    def get(self, name, no_exception=True):
        return self.get_value(name)

    def get_value(self, name, no_exception=True):
        # This is just to spoof the Site object into being an sobject for
        # the purposes of using expressions to configure the "asset_dir"
        # for sites.  Ideally, this class should be derived from sobject,
        # but this is not yet implemented.
        if name == "code":
            site = Site.get_site()
            return site


    def get_request_path_info(self):
        from pyasm.web import WebContainer
        web = WebContainer.get_web()
        path = web.get_request_path()
        return self.break_up_request_path(path)




    #
    # Virtual methods
    #


    def get_max_users(self, site):
        return

    def get_authenticate_class(self):
        return

    def get_site_root(self):
        return ""

    def break_up_request_path(self, path):
        return {}

    def get_site_redirect(self):
        return

    def register_sites(self, startup, config):
        return

    def handle_ticket(self, ticket):
        return


    def get_guest_hashes(self):
        return []

    def get_guest_wdg(self, hash):
        return None


    def get_by_login(cls, login):
        return ""
    get_by_login = classmethod(get_by_login)


    def build_ticket(cls, ticket):
        return ticket
    build_ticket = classmethod(build_ticket)

    def get_by_ticket(cls, ticket):
        return ""
    get_by_ticket = classmethod(get_by_ticket)


    def validate_ticket(cls, ticket):
        return True
    validate_ticket = classmethod(validate_ticket)

    def get_connect_data(cls, site):
        return {}
    get_connect_data = classmethod(get_connect_data)

    def get_site_dir(cls, site):
        return
    get_site_dir = classmethod(get_site_dir)

    def get_asset_dir(cls, file_object=None, alias=None):
        return
    get_asset_dir = classmethod(get_asset_dir)


    def get_web_dir(cls, file_object=None, alias=None):
        return
    get_web_dir = classmethod(get_web_dir)


    def get_default_project(cls):
        return Config.get_value("install", "default_project")
    get_default_project = classmethod(get_default_project)


    def get_login_wdg(cls, hash=None):
        from tactic.ui.panel import HashPanelWdg
        web_wdg = HashPanelWdg.get_widget_from_hash("/login", return_none=True)
        return web_wdg
    get_login_wdg = classmethod(get_login_wdg)


    def allow_guest(cls, url=None):
        return None


    def init_site(cls, site, options={}):
        pass
    init_site = classmethod(init_site)



    def start_site(cls, site):
        return False
    start_site = classmethod(start_site)

    def get_api_mode(cls):
        return
    get_api_mode = classmethod(get_api_mode)




    #######################

    def get(cls):
        class_name = Config.get_value("security", "site_class")
        if not class_name:
            class_name = "pyasm.security.Site"
        #class_name = "spt.modules.portal.PortalSite"
        try:
            site = Common.create_from_class_path(class_name)
        except Exception as e:
            print("WARNING: ", e)
            site = Site()
        return site
    get = classmethod(get)


    def get_site(cls):
        '''Get the global site for this "session"'''
        sites = Container.get("sites")
        if sites == None or sites == []:
            return ""
        return sites[-1]
    get_site = classmethod(get_site)


    def get_first_site(cls):
        '''Get the initial site'''
        sites = Container.get("sites")
        if sites == None or sites == []:
            return ""
        return sites[0]
    get_first_site = classmethod(get_first_site)


    def get_sites(cls):
        '''Get the initial site'''
        sites = Container.get("sites")
        return sites
    get_sites = classmethod(get_sites)



    def set_site(cls, site, store_security=True, options={}):
        '''Set the global site for this "session"'''

        if not site:
            return


        # first get the site object
        site_obj = Site.get()
        site_obj.init_site(site, options=options)


        sites = Container.get("sites")

        is_redundant = False
        if sites == None:
            sites = []
            Container.put("sites", sites)
        elif sites and sites[-1] == site:
            is_redundant = True




        security_list = Container.get("Environment:security_list")
        if not security_list:
            security_list = []
            Environment.set_security_list(security_list)


        # add this site to the stack
        sites.append(site)

        if not store_security:
            return

        try:
            sql = DbContainer.get("sthpw")
        except Exception as e:
            # try to start the site
            site_obj = Site.get()
            state = site_obj.start_site(site)
            if state == "OK":
                pass
            else:
                print("WARNING: ", e)
                Site.pop_site()
                raise Exception("WARNING: site [%s] does not exist" % site)



        # if site is different from current, renew security instance
        cur_security = Environment.get_security()


        if is_redundant:
            security_list.append(cur_security)
            return

        if cur_security and cur_security._login:

            sudo = Sudo()
            try:

                # create a new security
                security = Security()
                security._is_logged_in = True
                security._login = cur_security._login
                LoginInGroup.clear_cache()
                security._find_all_login_groups()

                # copy the ticket 
                ticket = cur_security.get_ticket()
                security._ticket = ticket
                security.add_access_rules()

                # initialize a new security
                Environment.set_security(security)
                # store the current security
                security_list.append(cur_security)
            finally:
                sudo.exit()

        try:
            # check if user is allowed to see the site
            #from pyasm.search import Search
            #search = Search("sthpw/login")
            pass
        except:
            Site.pop_site()
            raise Exception("WARNING: permission denied to set to site [%s]" % site)

    set_site = classmethod(set_site)


    def pop_site(cls, pop_security=True):
        '''Set the global site for this "session"'''
        sites = Container.get("sites")

        if sites == None:
            return ""
        site = None
        if sites:
            site = sites.pop()

        if not pop_security:
            return site


        security_list = Container.get("Environment:security_list")

        if security_list:

            security = security_list.pop()

            if security:
                Environment.set_security(security)


        return site

    pop_site = classmethod(pop_site)


    def clear_sites(cls):
        '''Clear all of the sites'''
        Container.put("sites", [])
    clear_sites = classmethod(clear_sites)



    def get_db_resource(cls, site, database):
        if not site:
            return None
        site_obj = cls.get()
        data = site_obj.get_connect_data(site)
        if data:
            host = data.get('host')
            port = data.get('port')
            vendor = data.get('vendor')
            user = data.get('user')
            password = data.get('password')
        else:
            return None

        db_resource = DbResource(database, host=host, port=port, vendor=vendor, user=user, password=password)
        return db_resource

    get_db_resource = classmethod(get_db_resource)


class TicketHandler(object):
    '''This is a base class to handle the generation, creation or validation of authentication
    tickets'''


    def generate_key(login, expiry, category):
        '''By default TACTIC generates a random key on login, however, this can be overridden here
        to generate any external method to generate a new key'''
        ticket_key = Common.generate_random_key()
        return ticket_key
    generate_key = staticmethod(generate_key)


    def create(key, login, expiry=None, interval=None, category=None):
        '''On login (with a name and password, for example), this function will be called.
        At this point a ticket can be created that will be reused for authentication
        '''
        # ticket = Ticket.create(ticket_key,login_name, expiry, category=category)
        return None
    create = staticmethod(create)


    def validate_key(cls, key):
        '''validate a ticket key using some external source.  Simply return the key to create a
        standard TACTIC ticket in the database or create a ticket directly in the function below
        using the following create function:

            return Ticket.create(key, login, expiry=None, interval=None, category=None)

        Return None is the ticket is not valid'''

        return None

    validate_key = classmethod(validate_key)




class Ticket(SObject):
    '''When a user logins, a ticket is created.  This ticket is stored in the
    database as a long unique string of alpha-numeric characters.  It is stored
    on the browser as a cookie and allows the user to login with a password.
    The ticket has an expiry date set in the Tactic config file'''

    def get_key(self):
        '''get the alphanumeric unique code for the session'''
        return self.get_value("ticket")


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

        from pyasm.security import Site
        site = Site.get_site()
        if site:
            Site.set_site("default")


        ticket = None
        try:
            # get the ticket from the database
            search = Search("sthpw/ticket")
            search.add_filter("ticket", key)
            now = search.get_database_impl().get_timestamp_now()
            search.add_where('("expiry" > %s or "expiry" is NULL)' % now)
            ticket = search.get_sobject()

            # if it can't find the key in the database, then it is possible to use
            # some external source to get the ticket.  If just the key is returned,
            # then default, in memory one will be created.  However, the validate function
            # can create ticket itself.  If the ticket was committed, then this would be
            # found by the above search
            if not ticket:
                # check an external source whether the key is valid.  If so, create a ticket
                handler_class = Config.get_value("security", "authenticate_ticket_class")
                if handler_class:
                    handler = Common.create_from_class_path(handler_class)
                    ticket = handler.validate_key(key)
                    if isinstance(ticket, six.string_types):
                        ticket = Ticket.create(ticket, commit=None)

        finally:
            if site:
                Site.pop_site()

        if not ticket:
            print("WARNING: Ticket [%s] is not valid" % key)

        # This is an extra test which we may enable later.
        # if we have a ticket, then look for the user in the login table.  It ensures
        # that the ticket belongs to a valid user.
        """
        search = Search("sthpw/login")
        search.add_filter("login", ticket.get("login") )
        user = search.get_sobject()
        if not ticket:
            raise Exception("Permission denied for site [%s]" % site)
        """

        return ticket
    get_by_valid_key = staticmethod(get_by_valid_key)




    def create(key, login, expiry=None, interval=None, category=None, commit=True):
        '''creation function to create a new ticket
            @keyparam:
                expiry: exact expiry timestamp
                interval: 5 day or 24 hour from now
                category: type of ticket
        '''
        # For now, tickets always come from the default database
        impl = Sql.get_default_database_impl()
        now = impl.get_timestamp_now()

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
        ticket.set_auto_code()
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

        from datetime import datetime
        from pyasm.search import SqlException
	# it makes no sense for Sqlite sessions to expire
        # FIXME: this is a bit of a hack until we figure out how
        # timestamps work in sqlite (all are converted to GMT?!)
        if impl.get_database_type() in ['Sqlite', 'MySQL']:
            print("WARNING: no expiry on ticket for Sqlite and MySQL")
            ticket.set_value("expiry", 'NULL', quoted=0)
        elif isinstance(expiry, datetime):
            ticket.set_value("expiry", expiry)
        else:
            ticket.set_value("expiry", expiry, quoted=0)

        if commit:
            try:
                ticket.commit(triggers="none")
            except SqlException as e:
                print("Sql error has occured.")

        return ticket
    create = staticmethod(create)

    def update_session_expiry():
        security = Environment.get_security()
        login_ticket = security.get_ticket()
        impl = Sql.get_default_database_impl()
        timeout = Config.get_value("security","inactive_ticket_expiry")
        if not timeout:
            return
        offset,type = timeout.split(" ")
        expiry = impl.get_timestamp_now(offset=offset, type=type)
        Ticket.update_expiry(login_ticket,expiry)

    update_session_expiry = staticmethod(update_session_expiry)



    def update_expiry(ticket,expiry):


        ticket.set_value("expiry", expiry, quoted=0)
        ticket.commit(triggers="none")

    update_expiry = staticmethod(update_expiry)



# DEPRECATED
class NoDatabaseSecurity(Base):
    def __init__(self):
        #self._login = SearchType.create("sthpw/login")
        self._access_manager = AccessManager()
        self.is_logged_in_flag = False
        pass

    def is_logged_in(self):
        return self.is_logged_in_flag
    def get_license(self):
        return License()
    def login_with_ticket(self, key, add_access_rules=True, allow_guest=False):
        None
    def login_user(self, login_name, password, expiry=None, domain=None):
        self.is_logged_in_flag = True
    def get_login(self):
        return None
    def get_user_name(self):
        return None
    def get_group_names(self):
        return ['admin']
    def add_access_rules(self):
        pass
    def get_ticket(self):
        return None
    def check_access(self, group, key, access, value=None, is_match=False, default="edit"):
        return True
    def get_access(self, group, key, default=None):
        return "edit"
    def alter_search(self, search):
        pass
    def get_access_manager(self):
        return self._access_manager



class Security(Base):
    '''main class dealing with user identification'''

    def __init__(self, verify_license=False):
        self._login_var = None
        self._is_logged_in = 0
        self._groups = []
        self._group_names = []
        self._ticket = None
        self._admin_login = None

        self.add_access_rules_flag = True

        # define an access manager object
        self._access_manager = AccessManager()

        self.license = License.get(verify=verify_license)

        self.login_cache = None


    def _get_my_login(self):
        return self._login_var
    def _set_my_login(self, login):
        self._login_var = login
        if self._login_var and self._login_var.get_value("login") == 'admin':
            self._access_manager.set_admin(True)
    _login = property(_get_my_login, _set_my_login)




    def get_version(cls):
        return get_security_version()
    get_version = classmethod(get_version)

    def is_logged_in(self):
        return self._is_logged_in

    def is_admin(self):
        return self._access_manager.is_admin()

    def set_admin(self, flag):

        if flag == self._access_manager.is_admin_flag:
            return
        return self._access_manager.set_admin(flag)

    def get_license(self):
        return self.license

    def reread_license(self):
        self.license = License.get()
        return self.license

    def get_groups(self):
        return self._groups

    def get_group_names(self):
        group_names = self._group_names
        group_names.sort()
        return group_names

    def is_in_group(self, group_name):
        if group_name == "admin" and self.get_user_name() == "admin":
            return True

        return group_name in self._group_names


    def get_login(self):
        return self._login

    def get_user_name(self):
        if not self._login:
            return None
        return self._login.get_login()

    def get_ticket(self):
        return self._ticket

    def get_ticket_key(self):
        if self._ticket:
            return self._ticket.get_key()
        else:
            return ""

    def clear_ticket(self):
        my_ticket = ""


    def get_access_manager(self):
        return self._access_manager


    def reset_access_manager(self):
        self._access_manager = AccessManager()
        self.add_access_rules()

    def sign_out(self):
        self._is_logged_in = 0
        self._login = None
        self._groups = []
        self._group_names = []
        self._ticket = None


    def get_start_link(self):
        for group in self._groups:
            start_link = group.get_value("start_link")
            if start_link:
                return start_link


    def _do_login(self):
        '''function to actually log in the user'''
        # get from cache
        #from pyasm.biz import LoginCache
        #self.login_cache = LoginCache.get("logins")

        # find all of the groups for this login
        self._groups = None
        if self._groups == None:
            self._groups = []
            self._group_names = []

            sudo = Sudo()
            try:
                self._find_all_login_groups()
            finally:
                sudo.exit()


            # set the results to the cache
            #self.login_cache.set_attr("%s:groups" % login, self._groups)
            #self.login_cache.set_attr("%s:group_names" % login, self._group_names)


        # Setup the access manager and access rules
        # Admin and admin group do not get access rules
        is_admin = self.setup_access_manager()
        if not is_admin and self.add_access_rules_flag:
            self.add_access_rules()

        # record that the login is logged in
        self._is_logged_in = 1


    def login_as_batch(self, login_name=None, ticket=None):
        '''function that logs in through a batch command'''

        # default to admin.  Generally batch is run as admin.
        if not login_name:
            login_name = "admin"

        # login must exist in the database
        self._login = Login.get_by_login(login_name, use_upn=True)
        if not self._login:
            raise SecurityException("Security failed: Unrecognized user: '%s'" % login_name)

        # create a new ticket for the user
        sudo = Sudo()
        try:
            if ticket:
                if isinstance(ticket, six.string_types):
                    self._ticket = Ticket.get_by_valid_key(ticket)
                else:
                    self._ticket = ticket
            else:
                self._ticket = self._generate_ticket(login_name)
        except:
            sudo.exit()

        self.add_access_rules_flag = True

        self._do_login()



    def login_as_guest(self):
        '''function that logs in as guest'''

        login_name = "guest"
        group_name = "guest"

        sudo = Sudo()
        try:

            search = Search("sthpw/login")
            search.add_filter("login", login_name)
            search.set_show_retired(True)
            self._login = search.get_sobject()
            if not self._login:
                # login must exist in the database
                self._login = SearchType.create("sthpw/login")
                self._login.set_value("code", login_name)
                self._login.set_value("login", login_name)
                self._login.set_value("upn", login_name)
                self._login.set_value("first_name", "Guest")
                self._login.set_value("last_name", "User")
                self._login.set_value("display_name", "Guest")
                self._login.commit()

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

        finally:
            sudo.exit()

        # clear the login_in_group cache
        LoginInGroup.clear_cache()
        #self._find_all_login_groups()

        # create a new ticket for the user
        self._ticket = self._generate_ticket(login_name)

        self._do_login()





    def login_with_ticket(self, key, add_access_rules=True, allow_guest=False):
        '''login with the alpha numeric ticket key found in the Ticket
        sobject.'''

        if key == "":
            return None

        sudo = Sudo()

        # set the site if the key has one
        #site = Site.get().get_by_ticket(key)
        #Site.get().set_site(site)

        self.add_access_rules_flag = add_access_rules

        #from pyasm.biz import CacheContainer
        #cache = CacheContainer.get("sthpw/ticket")
        #cache.build_cache_by_column("ticket")
        #ticket = cache.get_sobject_by_key("ticket", key)
        ticket = Ticket.get_by_valid_key(key)
        if ticket is None:
            # if ticket does not exist, make sure we are signed out and leave
            return None


        # make sure the ticket is valid for this site
        site = Site.get()
        if not site.validate_ticket(ticket):
            return None


        # try getting from global cache
        from pyasm.biz import CacheContainer
        login_word = ticket.get_value("login")

        cache = CacheContainer.get("sthpw/login")
        if cache:
            self._login = cache.get_sobject_by_key("login", login_word)

        # if it doesn't exist, try the old method
        if not self._login:
            self._login = Login.get_by_login( login_word, use_upn=True )

        if self._login is None:
            return None

        # store the ticket
        self._ticket = ticket

        if self._login.get("login") == "guest" and not allow_guest:
            return None

        self._do_login()

        if self._login.get("login") == "guest":
            access_manager = self.get_access_manager()
            xml = Xml()
            xml.read_string('''
            <rules>
              <rule column="login" value="$LOGIN" search_type="sthpw/login" group="search_filter"/>
            </rules>
            ''')
            access_manager.add_xml_rules(xml)

        return self._login



    def login_with_session(self, sid, add_access_rules):

        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()

        # TEST: this is a test authentication with Drupal
        self.add_access_rules_flag = add_access_rules

        from pyasm.security import Sudo
        sudo = Sudo()

        # authenticate use some external method
        if sid:
            expr = '''@SOBJECT(table/sessions?project=drupal['sid','%s'])''' % sid
            #print("expr: ", expr)
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
        #print("login: ", user_name)

        # if the user doesn't exist, then autocreate one

        self._login = Search.get_by_code("sthpw/login", user_name)
        if not self._login:
            self._login = SearchType.create("sthpw/login")

            self._login.set_value("code", user_name)
            self._login.set_value("login", user_name)
            self._login.set_value("first_name", user_name)
            self._login.set_value("password", drupal_user.get('pass'))
            self._login.set_value("email", drupal_user.get('mail'))
            self._login.commit()

        # do we need a tactic ticket as well ...?
        #self._ticket = self._generate_ticket(user_name, expiry=None)

        search = Search("sthpw/ticket")
        search.add_filter("ticket", sid)
        self._ticket = search.get_sobject()
        if not self._ticket:
            self._ticket = SearchType.create("sthpw/ticket")
            self._ticket.set_value("login", user_name)
            self._ticket.set_value("ticket", sid)
            self._ticket.commit()

        self._do_login()







    def login_user_without_password(self, login_name, expiry=None):
        '''login a user without a password.  This should be used sparingly'''

        search = Search("sthpw/login")
        search.add_filter("login", login_name)
        self._login = search.get_sobject()

        # user still has to exist
        if not self._login:
            raise SecurityException("Login [%s] does not exist" % login_name)

        # Search for unexpired ticket
        search = Search("sthpw/ticket")
        search.add_filter("login", login_name)
        now = search.get_database_impl().get_timestamp_now()
        search.add_where('("expiry" > %s or "expiry" is NULL)' % now)
        ticket = search.get_sobject()
        if ticket:
            self._ticket = ticket
        else:
            self._ticket = self._generate_ticket(login_name, expiry)

        self._do_login()



    def login_user(self, login_name, password, expiry=None, domain=None):
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

        site = Site.get_site()
    
        if login_name == 'admin':
            if site == "" or site == "default":
                auth_class = "pyasm.security.TacticAuthenticate"
            else:
                raise SecurityException("Login/Password combination incorrect")

        # verify using the specified authenticate class
        if not auth_class:
            auth_class = Config.get_value("security", "authenticate_class",
                no_exception=True)
        if not auth_class:
            auth_class = "pyasm.security.TacticAuthenticate"


        #from security import Site
        #site_obj = Site.get()
        #site_auth_class = site_obj.get_authenticate_class()
        #if site_auth_class:
        #    auth_class = site_auth_class


        # handle the windows domain, manually typed in domain overrides
        if login_name.find('\\') != -1:
            domain, login_name = login_name.split('\\', 1)
        if domain and login_name !='admin':
            auth_login_name = "%s\\%s" % (domain, login_name)
        else:

            auth_login_name = login_name


        sudo = Sudo()

        authenticate = Common.create_from_class_path(auth_class)
        try:
            is_authenticated = authenticate.verify(auth_login_name, password)
        except Exception as e:
            print("WARNING: ", e)
            raise

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
            self._login = Login.get_by_login(login_name, use_upn=True)
            if not self._login:
                self._login = SearchType.create("sthpw/login")
                if SearchType.column_exists('sthpw/login','upn'):
                    self._login.set_value('upn', login_name)
                self._login.set_value('login', login_name)
                authenticate.add_user_info( self._login, password)

                self._login.commit(triggers=False)

        # when mode is cache, it does autocreate and update user_info every time
        # this is called
        elif mode == 'cache':
            # get the login from the authentication class
            self._login = Login.get_by_login(login_name, use_upn=True)
            if not self._login:
                self._login = SearchType.create("sthpw/login")
                if SearchType.column_exists('sthpw/login','upn'):
                    self._login.set_value('upn', login_name)
                self._login.set_value('login', login_name)

            try:
                authenticate.add_user_info( self._login, password)
            except Exception as e:
                raise SecurityException("Error updating user info: %s" % e.__str__())

            # verify that this won't create too many users.  Floating licenses
            # can have any number of users
            if self._login.has_user_license():
                num_left = self.license.get_num_licenses_left()
                if num_left <= 0:
                    raise SecurityException("Number of active users exceeds licenses")

            self._login.commit()

        else:
            # get the login from database and don't bother updating
            self._login = authenticate.get_login()
            if not self._login:
                self._login = Login.get_by_login(login_name, use_upn=True)


        # if it doesn't exist, then the login fails
        if not self._login:
            raise SecurityException("Login/Password combination incorrect")


        # if the user is disabled, then they cannot log in
        license_type = self._login.get_value("license_type", no_exception=True)
        if license_type == "disabled":
            raise SecurityException("User [%s] is disabled" % self._login.get_value('login'))

        # check if the user has a floating license
        elif license_type == 'float':
            try:
                self.license.verify_floating(login_name)
            except LicenseException as e:
                raise SecurityException(str(e))


        # create a new ticket for the user
        self._ticket = self._generate_ticket(login_name, expiry, category="gui")
        # clear the login_in_group cache
        LoginInGroup.clear_cache()

        self._do_login()

        # allow for some postprocessing
        authenticate.postprocess(self._login, self._ticket)





    def generate_ticket(self, login_name, expiry=None, category=None):
        return self._generate_ticket(login_name, expiry, category)


    def _generate_ticket(self, login_name, expiry=None, category=None):

        handler = None

        handler_class = Config.get_value("security", "authenticate_ticket_class")
        if handler_class:
            handler = Common.create_from_class_path(handler_class)
            ticket_key = handler.generate_key(login_name, expiry, category)
        else:
            # create a new ticket for the user
            ticket_key = Common.generate_random_key()

        ticket_key = Site.get().build_ticket(ticket_key)


        # make sure the ticket is always generated on the default site
        site = Site.get_site()
        if site:
            Site.set_site("default")
        sudo = Sudo()
        try:

            if handler:
                ticket = handler.create(ticket_key,login_name, expiry, category=category)
                if not ticket:
                    # use default method if not implemented
                    ticket = Ticket.create(ticket_key,login_name, expiry, category=category)
            else:
                ticket = Ticket.create(ticket_key,login_name, expiry, category=category)

        finally:
            sudo.exit()
            if site:
                Site.pop_site()

        return ticket



    def compare_access(self, user_access, required_access):
        return self._access_manager.compare_access(user_access, required_access)


    def check_access(self, group, key, access, value=None, is_match=False, default="edit"):
        '''convenience function to check the security level to the access
        manager'''
        return self._access_manager.check_access(group, key, access, value, is_match, default=default)

    def get_access(self, group, key, default=None):
        return self._access_manager.get_access(group, key, default=None)





    def alter_search(self, search):
        '''convenience function to alter a search for security reasons'''
        # set that the security filter has been added
        search.set_security_filter()
        return self._access_manager.alter_search(search)






    def is_login_in_group(self, group):
        '''returns whether the user is in the give group'''
        if group in self._group_names:
            return True
        else:
            return False


    def _find_all_login_groups(self, group=None):

        if not group:
            groups = self._login.get_sub_groups()
            for group in groups:

                group_name = group.get_login_group()
                if group_name in self._group_names:
                    continue

                self._groups.append(group)
                self._group_names.append(group.get_login_group())

                self._find_all_login_groups(group)

        else:
            # break any circular loops
            group_name = group.get_login_group()
            if group_name in self._group_names:
                return

            self._groups.append(group)
            self._group_names.append(group.get_login_group())

            # go through the subgroups
            sub_groups = group.get_sub_groups()
            for sub_group in sub_groups:
                self._find_all_login_groups(sub_group)


        # make sure self._groups is an array
        if self._groups == None:
            self._groups = []

        #for x  in self._groups:
        #    print(x.get_login_group())


    def add_access_rules(self):
        '''Add access rules for each group to the access manager.'''
        for group in self._groups:
            self._access_manager.add_xml_rules(group)


    def setup_access_manager(self):
        '''Setup access manager for admin access.'''
        if self._login and self._login.get_value("login") == 'admin':
            self._access_manager.set_admin(True)
            return True

        for group in self._groups:
            login_group = group.get_value("login_group")
            if login_group == "admin":
                self._access_manager.set_admin(True)
                return True

        return False



import pickle, os, base64

try:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Hash import MD5, SHA256
    from Cryptodome.Signature import pkcs1_15
except ImportError:
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
    def __init__(self, public_key, version="2"):
        self.version = version
        
        # unwrap the public key (for backwards compatibility)
        unwrapped_key = self.unwrap("Key", public_key)
        
        if version == "1":
            try:
                # get the size and key object
                haspass, self.size, keyobj = pickle.loads(unwrapped_key)
                self.algorithm, self.keyobj = pickle.loads(keyobj.encode())
            except Exception as e:
                raise LicenseException("License key corrupt. Please verify license file. %s" %e.__str__())
        elif version == "2":
            try:
                self.keyobj = RSA.import_key(unwrapped_key)
            except Exception as e:
                raise LicenseException("License key corrupt. Please verify license file. %s" %e.__str__())
        else:
            raise LicenseException("License version not recognized.")


    def verify_string(self, raw, signature):
        # unwrap the signature
        unwrapped_signature = self.unwrap("Signature", signature)

        if self.version == "1":
            # deconstruct the signature
            algorithm, raw_signature = pickle.loads(unwrapped_signature)
            assert self.algorithm == algorithm

            # MD5 the raw text
            m = MD5.new()
            m.update(raw.encode())
            d = m.digest()
            
            if self.keyobj.verify(d, raw_signature):
                return True
            else:
                return False
        else:
            msg = raw.encode('utf-8')
            h = SHA256.new(msg)
            try:
                pkcs1_15.new(self.keyobj).verify(h, unwrapped_signature)
                return True
            except (ValueError, TypeError):
                return False


    def unwrap(self, key_type, msg):
        msg = msg.replace("<StartPycrypto%s>" % key_type, "")
        msg = msg.replace("<EndPycrypto%s>" % key_type, "")

        # python3 requires bytes
        if IS_Pv3:
            binary = base64.decodebytes(msg.encode())
        else:
            binary = base64.decodestring(msg.encode())
        return binary



class LicenseException(Exception):
    pass


class License(object):
    license_path = "%s/tactic-license.xml" % Environment.get_license_dir()
    NO_LICENSE = 'no_license'

    def __init__(self, path=None, verify=True):
        self.message = ""
        self.status = "NOT FOUND"
        self.licensed = False
        self.xml = None

        if path:
            self.license_path = path

        self.verify_flag = verify

        try:
            self.parse_license()
        except LicenseException as e:
            self.message = e.__str__()
            print("WARNING: ", self.message)
            self.licensed = False

            # this is the minimal acceptable data for self.xml, dont't set to None
            # this should be the place to redefine it if applicable
            if not self.xml:
                self.xml = Xml('<%s/>'%self.NO_LICENSE)
        else:
            self.licensed = True


    def parse_license(self, check=False):
        '''check = True is only used for creation verification'''
        if not os.path.exists(self.license_path):
            raise LicenseException("Cannot find license file [%s]" % self.license_path )

        self.xml = Xml()

        try:
            self.xml.read_file(self.license_path, cache=False)
        except XmlException as e:
            self.xml.read_string("<license/>")
            raise LicenseException("Error parsing license file: malformed xml license file [%s] e: %s" % (self.license_path, e))

        # verify signature
        signature = str(self.xml.get_value("license/signature"))
        signature = signature.strip()
        data_node = self.xml.get_node("license/data")
        data = self.xml.to_string(data_node).strip()
        public_key = str(self.xml.get_value("license/public_key"))
        
        version = self.xml.get_value("license/data/version")

        # the data requires a very specific spacing.  4Suite puts out a
        # different dump and lxml and unfortunately, the license key is
        # dependent on the spacing.
        #print("data: [%s]" % data)
        data = data.replace("    ", "  ")
        data = data.replace("  </data>", "</data>")
        #print("data: [%s]" % data)


        # verify the signature
        if self.verify_flag:
            key = LicenseKey(public_key, version=version)
            if not key.verify_string(data, signature):
                # will be redefined in constructor
                self.xml = None
                if check ==True:
                    raise TacticException("Data and signature in license file do not match in [%s]" % self.license_path)
                else:
                    raise LicenseException("Data and signature in license file do not match in [%s]" % self.license_path)
            self.verify_license()
            #self.verify()



    def is_licensed(self):
        return self.licensed


    def is_licensed_for(self, product, version=None):
        self.licensed = False
        self.message = "No valid license for %s found." % product

        products = self.xml.get_value("license/data/products")
        if not products:
            return


        products = products.split(",")
        if product in products:
            self.message = ""
            self.licensed = True

        return self.licensed




    def get_message(self):
        return self.message


    def verify(self):
        try:
            self.verify_license()
            self.licensed = True
            return True
        except LicenseException as e:
            self.message = e.__str__()
            self.licensed = False
            self.LICENSE = None
            return False


    def verify_floating(self, login_name=None):
        # check if the user has a floating license
        floating_max = self.get_max_floating_users()
        if not floating_max:
            raise LicenseException("No floating licenses are available")
        floating_current_users = self.get_current_floating_users()
        floating_current = len(floating_current_users)

        #print("foating_max: ", floating_max)
        #print("foating_current: ", floating_current))
        #print("login_name: ", login_name)
        #print("floating_current_users: ", floating_current_users)

        # if the user is in the list, then this user is already logged in
        if login_name and login_name in floating_current_users:
            return True

        if floating_current >= floating_max:
            raise LicenseException("Too many users. Please try again later")


    def get_data(self, key):
        value = self.xml.get_value("license/data/%s" % key)
        return value


    def get_max_users(self):
        site = Site.get_site()
        site_obj = Site.get()
        value = site_obj.get_max_users(site)
        if not value:
            value = self.xml.get_value("license/data/max_users")
        try:
            value = int(value)
        except ValueError:
            value = 10
        return value


    def get_max_floating_users(self):
        value = self.xml.get_value("license/data/max_floating_users")
        try:
            value = int(value)
        except ValueError:
            value = 0
        return value



    def get_num_licenses_left(self):
        max_users = self.get_max_users()
        current_users = self.get_current_users()
        left = max_users - current_users
        return left


        floating_current_users = self.get_current_floating_users()
        floating_current = len(floating_current_users)


    def get_expiry_date(self):
        value = self.xml.get_value("license/data/expiry_date")
        return value

    def get_current_users(self):
        sql = DbContainer.get("sthpw")
        select = Select()
        select.set_database("sthpw")
        #select.set_database(db_resource)
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
        #print("statement: ", statement)
        #num_users = sql.get_value(statement)
        #num_users = int(num_users)
        return num_users


    def get_current_floating_users(self):
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
        #print("statement: ", statement)

        login_names = sql.do_query(statement)
        login_names = [x[0] for x in login_names]
        #num_float = len(login_names)

        return login_names
        #return num_float





    def verify_license(self):
        '''Reads the license file.'''

        # go through the checks
        if not self.xml:
            raise LicenseException(self.message)
            #raise LicenseException("Parsing of licensing file [%s] failed. Renew it in the Projects tab." % self.license_path )


        node = self.xml.get_node("license")
        if node is None:
            no_lic_node = self.xml.get_node(self.NO_LICENSE)
            if no_lic_node is not None:
                raise LicenseException(self.message)
            else:
                raise LicenseException("Parsing of license file [%s] failed." % self.license_path )

        version = self.xml.get_value("license/version")
        # for now, there is only one version of the license
        if 1:
            # check for mac address, if it exists in license
            license_mac = self.xml.get_value("license/data/mac_address")
            license_mac = license_mac.strip()
            if license_mac:
                mac = self.get_mac_address()
                if mac != license_mac:
                    raise LicenseException("License mac address do not match")

            # check for expiry date, if it exists
            license_expiry = self.xml.get_value("license/data/expiry_date")
            license_expiry = license_expiry.strip()
            if license_expiry:
                current = Date().get_db_time()
                if current> license_expiry:
                    raise LicenseException("License expired on [%s] in [%s]" % (license_expiry, self.license_path))




            # check for tactic version
            license_version = self.xml.get_value("license/data/tactic_version")
            release_version = Environment.get_release_version()
            if not license_version:
                # This is no longer an issue.  License should be time based, not
                # version based
                #raise LicenseException("License file not locked to a specific version of TACTIC")
                pass

            else:
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
            license_users = self.get_max_users()
            if license_users:
                license_users = int(license_users)
                try:
                    current = self.get_current_users()
                except DatabaseException:
                    # set it to zero.  If there is a database error, then
                    # it doesn't really matter because nobody can use the
                    # software anways
                    current = 0

                #print("current: ", current, license_users, current > license_users)
                if current > license_users:
                    raise LicenseException("Too many users for license [%s].  Max Users [%s] - Current [%s]" % (self.license_path, license_users, current))
        #print("License verified ... ")



    def get_mac_address(self):
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

    def get(cls, verify=True):
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
            if verify:
                cls.LICENSE.verify()

        cls.LAST_CHECK = now
        cls.LAST_MTIME = mtime

        return cls.LICENSE


    get = classmethod(get)

if __name__ == '__main__':
    from pyasm.security import Batch
    Batch(login_code='wendy20', site='wendy20')
    sec = Environment.get_security()

    Site.set_site('default')
    Site.set_site('wendy20')
    Site.pop_site()
    Site.pop_site()
    Site.pop_site()

