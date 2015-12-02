###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['MayaModelValidate', 'MayaModelCheckin']

try:
    import maya.cmds as cmds
except ImportError, e:
    print "WARNING: examples.py requires Maya python libraries"

from pyasm.application.common.interpreter import Handler



class MayaModelValidate(Handler):
    def execute(my):

        # get the search key from the delivered package
        search_key = my.get_package_value("search_key")

        # get the sobject from the server
        sobject = my.server.get_by_search_key(search_key)
        if not sobject:
            raise Exception("SObject with search key [%s] does not exist" % \
                search_key)

        # code and verify in maya that the node is in session
        code = sobject.get('code')
        if not cmds.ls(code):
            raise Exception("Cannot checkin: [%s] does not exist" % code)

        my.set_output_value('sobject', sobject)


    def undo(my):
        # nothing to undo in session
        pass




class MayaModelCheckin(Handler):

    def execute(my):

        # get the sobject passed in
        sobject = my.get_input_value('sobject')
        code = sobject.get('code')
        search_key = my.get_package_value("search_key")

        # get the designated local directory to put temporary files
        tmp_dir = my.get_package_value("local_dir")
        path = "%s/%s.ma" % (tmp_dir, code)

        context = my.get_package_value("asset_context")
        # FIXME: ignore subcontext for now
        #subcontext = my.get_package_value("asset_sub_context")
        #if subcontext:
        #    context = "%s/%s" % (context, subcontext)

        # same out the file
        cmds.file( rename=path)
        cmds.file( save=True, type='mayaAscii')

        # checkin the file that was just saved
        my.server.upload_file(path)
        snapshot = my.server.simple_checkin(search_key, context, path)

        # add a mock dependency
        snapshot_code = snapshot.get("code")
        my.server.add_dependency(snapshot_code, "C:/tt.pdf")


 
    def undo(my):
        # nothing to undo in session
        pass





