###########################################################
#
# Copyright (c) 2005-2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['ADLookup', 'ADException']

'''Command line script to get user info.'''

import tacticenv

import os, sys, getopt


try: 
    import active_directory
except Exception, e:
    print "WARNING: cannot import active_directory"
    print
    #class active_directory:
    #    pass
    raise



def get_user_info(user_name, domain=None):
    # TEST
    """
    return '''
dn: whatver
l: Fort Worth
displayName: cow
mail: remko@southpawtech.com
    '''
    """

    user = active_directory.find_user(user_name, domain)
    if not user:
        print "WARNING: user [%s] cannot be found" % user_name
        return {}


    # TODO: need to find a way to get all properties
    #print "properties: ", user.properties
    #print "-"*20
    #print "xxx: ", user.dump()

    attrs_map = {
        'dn':               'dn',
        'displayName':      'first_name',
        'name':             'name',
        'mail':             'email',
        'telephoneNumber':  'phone_number',
        'department':       'department',
        'employeeID':       'employee_id',
        'sAMAccountName':   'sAMAccountName',
        # some extras
        'l':                'location',
        'title':            'title',
    }

    data = []
    for key in attrs_map.keys():
	try:
	    value = eval("user.%s" % key)
	    data.append("%s: %s" % (key, value))
        except AttributeError:
            #print "Attribute [%s] does not exist" % key
	    pass
    if hasattr(user,'memberOf'):
        for memberOf in user.memberOf:
            memberOf = str(memberOf).replace("LDAP://", "")
            data.append("memberOf: %s" % (memberOf))
    else:
        for memberOf in user:
            memberOf = str(memberOf).replace("LDAP://", "")
            data.append("memberOf: %s" % (memberOf))

    return "\n".join(data)



def get_group_info(group_name):

    group = active_directory.find_group(group_name)
    if not group:
        return {}

    group_attrs_map = {
        'dn':               'dn',
        'name':             'name',
    }


    data = []
    for key in group_attrs_map.keys():
        value = eval("group.%s" % key)
	data.append("%s: %s" % (key, value))

    return "\n".join(data)




def main(argv):
    try:
        opts, args = getopt.getopt(argv, "d:u:g:", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    #try:
    domain = None
    if len(opts) > 0:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt == '-d':
                domain = arg
            elif opt == '-u':
                try:
                    print get_user_info(arg, domain)
                except Exception, e:
                    print "ERROR: ", str(e)
                    raise

            elif opt == '-g':
                print get_group_info(arg)
            else:
                usage()
                sys.exit()
    else:
        print ("Try 'ad_get_user_info -h' for more information.")


def usage():
    print "Usage: python ad_get_user_info.py [Option]"
    print ""
    print "-d <name>            Set domain to use"
    print "-u <name>            Look up the user 'name'"
    print "-g <name>            Look up the group 'name'"
    print ""


if __name__ == '__main__':
    main(sys.argv[1:])

