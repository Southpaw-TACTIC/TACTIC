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


__all__ = ['Common']


gl = globals()
lc = locals()


class Common(object):
    '''class which defines a series of commonly used base level functions.'''

    def create_from_class_path(class_path, args=[]):
        '''dynamically creats an object from a string class path.

        @params:
        class_path: fully qualified python class path
        args: list of arguments to be used in the constructor

        @return
        instance of the dynamically created object
        '''
        assert class_path 
        parts = class_path.split(".")
        module_name = ".".join(parts[0:len(parts)-1])
        class_name = parts[len(parts)-1]
        exec( "from %s import %s" % (module_name,class_name), gl, lc )
        if args:
            object = eval("%s(%s)" % (class_name, args) )
        else:
            object = eval("%s()" % (class_name) )
        return object
    create_from_class_path = staticmethod(create_from_class_path)
 


