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

__all__ = ['ProdNodeNaming']

import os, re

from pyasm.common import Base

from asset import ShotInstance

class ProdNodeNaming(Base):
    '''defines the callbacks for namespace naming of maya assets'''

    def __init__(my):
        my.sobject = None
        my.snapshot = None

    def set_sobject(my, sobject):
        my.sobject = sobject

    def set_snapshot(my, snapshot):
        my.snapshot = snapshot


    def get_name(my):
        return my.get_value()

    def get_value(my):
        assert my.sobject != None
        assert my.snapshot != None

        search_type = my.sobject.get_search_type_obj().get_base_key()
        func_name = search_type.replace("/", "_")
        func = my.__class__.__dict__.get(func_name)
        if func:
            value = func(my)
        else:
            value = my.get_default()

        # replace spaces with _
        if value:
            value = value.replace(' ', '_')
        return value



    def get_default(my):
        return my.sobject.get_name()


    def prod_asset(my):
        parts = []
        parts.append( my.sobject.get_value("name") )
        context = my.snapshot.get_value("context")
        new_context = re.sub(r'/|\||:|\?|=', '_', context)
        parts.append( new_context ) 
        
        return "_".join(parts)


    def prod_shot_instance(my):
        parts = []
        search_type = my.snapshot.get_value('search_type')
        if search_type.startswith('prod/asset'):
            context = my.snapshot.get_value("context")
            context = re.sub(r'/|\||:|\?|=', '_', context)
        else:
            context = my.snapshot.get_value("context").split("/")[0]
        parts.append( my.sobject.get_value("name") )
        parts.append( context )

        return "_".join(parts)


    def prod_shot(my):
        parts = []
        context = my.snapshot.get_value("context").split("/")[0]
        parts.append( my.sobject.get_value("code") )
        parts.append( context )
        return "_".join(parts)





    def get_shot_instance_name(my, shot, asset, current_instances):
        '''function that determines the instance name on creation'''
        instance_name = asset.get_value("name")

        return ShotInstance.get_instance_name(current_instances, instance_name)



    def get_sandbox_file_name(my, current_file_name, context, sandbox_dir=None, file_naming=None):
        '''function that determines the file name to be saved in the sandbox'''

        # get current file name of maya session and extract version.
        pattern = re.compile( r'v(\d+)[\.|_]')
        matches = pattern.findall(current_file_name)
        if not matches:
            version = 0

            # add a version to the name
            base, ext = os.path.splitext(current_file_name)
            file_name = "%s_%s_v%0.3d%s" % (base, context, version+1, ext)
        else:
            # add 1 to the version
            version = int(matches[0])
            padding = len(matches[0])

            old = "v%s" % str(version).zfill(padding)
            new = "v%s" % str(version+1).zfill(padding)
            file_name = current_file_name.replace(old, new )

        return file_name



