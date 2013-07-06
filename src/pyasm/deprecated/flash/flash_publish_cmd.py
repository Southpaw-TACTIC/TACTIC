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

__all__ = ["FlashLayerPublishCmd", "FlashAssetPublishCmd", 'FlashShotPublishCmd',
        'FlashAssetSObjectPublishCmd', 'FlashShotSObjectPublishCmd']

from pyasm.common import Xml, Environment
from pyasm.search import SObject
from pyasm.prod.web import SObjectUploadCmd
from pyasm.prod.biz import Layer
from pyasm.biz import File, IconCreator
from pyasm.checkin import FileCheckin
import os

'''Wrapper classes to allow triggers to be set'''

class FlashLayerPublishCmd(SObjectUploadCmd):
    pass

class FlashAssetPublishCmd(SObjectUploadCmd):

    def execute(my):
        my.add_description("Flash Publish")
        
        super(FlashAssetPublishCmd, my).execute()
        
        # this replaces the default response to a script response
        post_cmd_scripts = ['<script>pyflash.copy(%s)</script>'%file \
            for file in my.repo_file_list]

        # this delimiter is used in DynamicLoader.js
        my.set_response('\n'.join(post_cmd_scripts)) 
        
        

    def get_response_list(my):
        ''' define a list of file extensions that we want to display in 
            commmand's response'''
        return ['.fla']
    
    def postprocess(my):
        super(FlashAssetPublishCmd, my).postprocess()

        # parse the introspect file
        code = my.sobject.get_code()
       
        upload_dir = my.get_upload_dir()
        introspect_path = "%s/%s.xml" % (upload_dir, code)

        xml = Xml()
        xml.read_file(introspect_path)

        flash_layer_names = xml.get_values("introspect/layers/layer/@name")
        if not flash_layer_names:
            return

        # extract the layers from the flash layer_names
        layer_names = []
        for flash_layer_name in flash_layer_names:
            if flash_layer_name.find(":") == -1:
                continue
            layer_name, instance_name = flash_layer_name.split(":")

            # make sure it is unique
            if layer_name not in layer_names:
                layer_names.append(layer_name)

        base_key = my.sobject.get_search_type_obj().get_base_key()

        # TODO: make the flash shot tab run FlashShotPublishCmd instead
        # and move this postprocess there
        # this is not meant for flash/asset, but for flash/shot
        if base_key == 'flash/asset' or not layer_names:
            return

        # get all of the layers in this shot and compare to the session
        existing_layers = my.sobject.get_all_children("prod/layer")
        existing_layer_names = SObject.get_values(existing_layers,"name")
        for layer_name in layer_names:
            if layer_name not in existing_layer_names:
                print "creating ", layer_name
                Layer.create(layer_name, code)

        
    def get_upload_dir(cls, ticket=''):
        if not ticket:
            from pyasm.web import WebContainer
            ticket = WebContainer.get_security().get_ticket().get_key()
        dir = "%s/upload/%s" % (Environment.get_tmp_dir(), ticket)
        return dir
    get_upload_dir = classmethod(get_upload_dir)


class FlashShotPublishCmd(FlashAssetPublishCmd):
    pass


class FlashAssetSObjectPublishCmd(FlashAssetPublishCmd):

    def __init__(my, sobject, context='publish', comment='', ticket=''):
        super(FlashAssetSObjectPublishCmd, my).__init__()
        my.sobject = sobject
        my.filenames = []
        #my.file_paths = []
        my.comment = comment
        my.context = context
        my.snapshot = None
        my.ticket = ticket

    def check(my):
        return True

    


    def _read_ref_file(my):
        '''read the reference file containing extra node information'''
        dir = my.get_upload_dir()
        xml = Xml()
        key = my.sobject.get_code()

        # make this filename good for the file system
        filename = File.get_filesystem_name(key)
        xml.read_file( "%s/%s-ref.xml" % (dir,filename) )
        return xml

    def preprocess(my):
        '''prepare all the files for publish'''
        xml = my._read_ref_file()
        print xml.to_string()
        paths = xml.get_values("session/file/@path")
        for path in paths:
            filename = os.path.basename(path)
            if filename.endswith('.xml'):
                continue
            my.filenames.append(filename)

    def execute(my):
        my.add_description("Flash Publish")
        my.checkin_files()
        
        # this replaces the default response to a script response
        post_cmd_scripts = ['<script>pyflash.copy(%s)</script>'%file \
            for file in my.repo_file_list]

        # this only works when executed thru a web browser
        # this delimiter is used in DynamicLoader.js
        my.set_response('\n'.join(post_cmd_scripts)) 

        my.sobjects = [my.sobject]

    def checkin_files(my):
        basedir = my.get_upload_dir(my.ticket)
        file_types = []
        for filename in my.filenames:

            file_path = "%s/%s" % (basedir, filename)
            my.file_paths.append(file_path)
            # for now, use the extension as the type
            basename, ext = os.path.splitext(filename)
            
            file_types.append(ext)

            # should create an icon here
            if ext == ".png":
                creator = IconCreator(file_path)
                creator.create_icons()

                icon_path = creator.get_icon_path()
                my.file_paths.append(icon_path)
                file_types.append("icon")
                
                # remove the web file
                try:
                    os.unlink(creator.get_web_path())
                except OSError, e:    
                    print e

        snapshot_type = "flash"
       
        checkin = FileCheckin( my.sobject, my.file_paths, file_types,
             context=my.context, snapshot_type=snapshot_type )
        
        checkin.set_description(my.comment)
        
        
        checkin.execute()
        my.snapshot = checkin.get_snapshot()
        local_repo_dir = my.snapshot.get_local_repo_dir()

        # update the files to reference back to the snapshot
        # FIXME: this access private members of checkin
        file_dict = {}
        for idx, file_object in enumerate(checkin.file_objects):
            # populate file_dict
            local_repo_path = '%s/%s' %( local_repo_dir,file_object.get_full_file_name())
            file_dict[os.path.basename(checkin.files[idx])] = local_repo_path

        checkin_info = []
        for key, value in file_dict.items():
            if not my.get_response_list(): 
                checkin_info.append("'%s=%s'" %(key, value))
            else:
                for type in my.get_response_list():
                    if type in key:
                        checkin_info.append("'%s=%s'" %(key, value))
                        break
                    
        my.repo_file_list.append(','.join(checkin_info))

    

class FlashShotSObjectPublishCmd(FlashAssetSObjectPublishCmd):
    pass
       
