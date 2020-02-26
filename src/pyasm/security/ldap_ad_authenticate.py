
import tacticenv

import re
import ldap

from pyasm.common import SecurityException, Config, Common, jsonloads
from pyasm.security import Login, LoginInGroup, Authenticate, Batch
from pyasm.search import Search

import six


__all__ = ['LdapADAuthenticate']

class LdapADAuthenticate(Authenticate):
    '''Authenticate using LDAP logins'''


    def verify(self, login_name, password):

        self.server = Config.get_value("security", "ldap_server")
        self.bind_dn = Config.get_value("security", "bind_dn")
        self.bind_password = Config.get_value("security", "bind_password")
        
        # TODO: Handle unencryption
        #self.bind_password = Common.unencrypt_password(self.bind_password)
        
        self.base_dn = Config.get_value("security", "base_dn")

        self.ad_info = {}
        self.tactic_groups = None
        self.groups = []


        try:
            # connect to AD server
            l = self.ad_authenticate()
        except Exception as e:
            print("Exception:")
            print(e)
            raise SecurityException("Cannot connect to authentication server: 203")

        try:
            self.login_now(l, login_name, password)
        except Exception as e:
            print("Exception:")
            print(e)
            raise SecurityException("Login/Password combination incorrect: 203")

        try:
            # search the user info in AD.
            self.search_ldap_info(login_name)

            return True
        except Exception as e:
            print("Exception:")
            print(e)
            raise SecurityException("User info issues: 203")


    def get_mode(self):
        return "cache"


    def ad_authenticate(self):
        '''Bind with the service account'''
        try:
            l = ldap.initialize(self.server)
            l.protocol_version = 3
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, 0)
            l.simple_bind_s(self.bind_dn, self.bind_password)
            return l

        except Exception as e:
            print("Exception:")
            print(e)
            raise SecurityException("LDAP: can't bind with service account.")

    def login_now(self, l, login_name, password):
        '''Login the user'''

        scope = ldap.SCOPE_SUBTREE
        filter = "(&(objectClass=user)(sAMAccountName=%s))" % login_name
        attrs = ['*']

        r = l.search(self.base_dn, scope, filter, attrs)
        Type, user = l.result(r,60)
        name, attrs = user[0]

        if isinstance(attrs,dict) and 'distinguishedName' in attrs:
            distinguishedName = attrs['distinguishedName'][0]
            if Common.IS_Pv3:
                distinguishedName = distinguishedName.decode()

            l.simple_bind_s(distinguishedName, password)

        return True


    def search_ldap_info(self, login, filter=None):

        scope = ldap.SCOPE_SUBTREE
        #filter = "objectClass=*"
        filter = "(&(objectClass=user)(sAMAccountName=%s))" % login
        attrs = ['*']

        try:
            l = self.ad_authenticate()
            results = l.search_s(self.base_dn, scope, filter)
            
            #TODO: What if results > 1 ?
            if len(results) > 1:
                pass


            info = {}
            login_map = self.get_user_mapping()
            for idx, result in enumerate(results):
                
                dn, entry = result
                dn = str(dn)
                if isinstance(entry, list):
                    pass
                else:
                    if dn:
                        dn_parts = ldap.dn.explode_dn(dn, flags=ldap.DN_FORMAT_LDAPV3)
                        ou_parts = [x for x in dn_parts if x.startswith('OU=')]
                        info['department'] = ','.join(ou_parts)
                    for ad_attr, tactic_attr in login_map.items():
                        if info.get(tactic_attr):
                            continue
                        value = entry.get(ad_attr)
                        if not value or value == ['']:
                            value = ''
                        elif isinstance(value, list) and len(value) == 1: value = value[0]
                        
                        try:
                            value = value.decode()
                        except (UnicodeDecodeError, AttributeError):
                            pass

                        info[tactic_attr] = value

            self.ad_info = info
            return info
        except Exception as e:
            print("Exception:")
            print(e)


    def get_user_mapping(self):
        '''return a dictionary of the mappings between AD attributes to
        login table attributes'''
        # NOTE: ensure this syncs up with the map in get_user_info()
        # in ad_get_user_info.py
        attrs_map = {
            'distinguishedName':'distinguishedName',
            'displayName':      'display_name',
            'name':             'name',
            'sn':               'last_name',
            'givenName':        'first_name',
            'mail':             'email',
            'telephoneNumber':  'phone_number',
            'department':       'department',
            'sAMAccountName':   'sAMAccountName',
            'memberOf':         'memberOf'

        }
        return attrs_map


    def add_user_info(self, login, password):
        
        handle_groups = Config.get_value("active_directory", "handle_groups")
        if handle_groups == "false":
            self.add_default_group(login)
        else:
            self.add_group_info(login)

        # User info handling
        first_name = self.ad_info.get('first_name')
        last_name = self.ad_info.get('last_name')
        display_name = self.ad_info.get('display_name')
        if not display_name:
            display_name = ''
        if not first_name and not last_name:
            name_parts = display_name.split(',')
            if len(name_parts) == 2:
                login.set_value("first_name", name_parts[1].strip())
                login.set_value("last_name", name_parts[0].strip())
            else:
                login.set_value("first_name", display_name)
        else:
            login.set_value("first_name", first_name)
            login.set_value("last_name", last_name)

        login.set_value("display_name", display_name)

        email = self.ad_info.get('email')
        if email:
            login.set_value("email", email)


    def build_group(self, value):
        '''populate self.groups with memberOf attr '''
        try:
            value = value.decode()
        except (UnicodeDecodeError, AttributeError):
            pass

        # some values have commas in them 
        value = value.replace("\\,", "|||")
        parts = value.split(",")

        # only deal with part 1 for now
        part = parts[0]
        name, value = part.split("=")

        ad_group_name = value.replace("|||", ",")

        tactic_group_dict = {}
        for group in self.tactic_groups:
            login_group_name = group.get_value("login_group")
            tactic_group_dict[login_group_name] = group

        group = None
        group_mapping = self.get_group_mapping()
        if group_mapping:
            tactic_group_name = group_mapping.get(ad_group_name)
            group = tactic_group_dict.get(tactic_group_name)
        else:
            group = tactic_group_dict.get(ad_group_name)
        
        if group:
            self.groups.append(group) 
        else:
            print("Could not find TACTIC group for AD group [%s]." % ad_group_name)


    def get_group_mapping(self):
        '''return a dictionary of the mappings between AD groups to
        tactic groups'''
        
        attrs_map = Config.get_value("security", "group_mapping")
        if attrs_map:
            attrs_map = jsonloads(attrs_map)
        
        return attrs_map


    def add_group_info(self, login):
        '''Add user to AD group.'''
        
        group_list = self.ad_info.get('memberOf')
        if not group_list:
            raise Exception("Unknown Group for the user.")
         
        self.tactic_groups = Search.eval("@SOBJECT(sthpw/login_group)")

        if isinstance(group_list, six.string_types):
            group_list = [group_list]
        
        for item in group_list:
            self.build_group(item)

        # if a user is not in any groups in AD
        if not self.groups:
            raise Exception("Unknown Group for the user.")

        login.remove_all_groups()
        for group in self.groups:
            login.add_to_group(group)


    def add_default_group(self, user):
        '''add the user to the default group only if he is groupless'''
        default_groups = self.get_default_groups()
        user_name = user.get_login()
        login_in_groups = LoginInGroup.get_by_login_name(user_name)

        if not login_in_groups:
            for group in default_groups:
                user.add_to_group(group)
    


    def get_default_groups(self):
        groups = Config.get_value("active_directory", "default_groups")
        if not groups:
            groups = []
        else:
            groups = groups.split("|")

        return groups


if __name__ == '__main__':

    site = ""
    project_code = "test_project_6"

    Batch(site=site, project_code=project_code)

    login_name = "jdoe"
    password = "Tactic123**"

    ad = LdapADAuthenticate()
    ad.verify(login_name, password)
    print("Success")




