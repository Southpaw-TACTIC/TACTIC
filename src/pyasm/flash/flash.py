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


__all__= ['Flash', 'FlashLoad', 'FlashDownload', 'FlashStage', 'FlashImport']

from pyasm.common import Container
from pyasm.biz import Snapshot
from pyasm.web import WebContainer
from pyasm.biz import Template, File
import re

class Flash(object):
    '''Application wrapper to PyFlash, which does the client side procssing.
    All interactions to flash go through here.  This class creates javascript
    calls that can be attached to widgets in the page
    '''
    def __init__(my):
        pass
        #my.snapshot_dict = {}


    def get_close_docs(my):
        return "pyflash.close_docs()"


    """

    def set_cached_snapshots(my, snapshot_dict):
        '''This probably should not be here.  The caching should be handled
        through some hidden external mechanism'''
        my.snapshot_dict = snapshot_dict

    """



    def _get_file_info(my, sobject, snapshot=None):
        ''' return the web url and the file name with flash sobject'''
        web_dir = None
        if not sobject:
            return None, None


        if not snapshot:
	    key = sobject.get_search_key()
            # the latest snapshot
            snapshot = Snapshot.get_latest_by_sobject(sobject)
            
        if snapshot:
            fla = snapshot.get_name_by_type(".fla")
            fla_file_name = snapshot.get_file_name_by_type(".fla")
            web_dir = sobject.get_remote_web_dir()
            fla_link = "%s/%s" % (web_dir, fla_file_name)
            return fla_link, fla
        else:
            return None, None



class FlashDownload(Flash):
    
    PROGRESS_MSG_ID = "load_progress"
    def __init__(my, sobject, snapshot):
        super(FlashDownload,my).__init__()
        my.sobject = sobject
        my.flash_snapshot = snapshot
        my.progress_msg_id = ''

    def set_progress_msg_id(my, element_id):
        '''set the widget id of the progress message element'''
        my.progress_msg_id = element_id

    def get_script(my):
        '''generate the script that will perform the load on the client side'''

        # use the sobjects code
        sobject = my.sobject


        web_dir = sobject.get_remote_web_dir()
        code = sobject.get_code()

        # download to the local repo
        local_repo_dir = sobject.get_local_repo_dir()

        # get the flash path
        fla_link, fla = my._get_file_info(sobject, my.flash_snapshot)

        # use the full name
        import os
        if not fla_link:
            return "alert('Flash file location undetermined. Its snapshots may have all been retired.')"
        fla = os.path.basename(fla_link)
        to_path = "%s/%s" % (local_repo_dir, fla)

        return "pyflash.download('%s','%s','%s','%s')" \
                % ( fla_link, to_path, code, my.progress_msg_id)
            
            


class FlashLoad(Flash):
    '''Responsible for loading a single fla file into the session'''
    LOAD_MODE_ELEMENT = 'load_mode'
    PREFIX_MODE_ELEMENT = 'prefix_mode'
    PROGRESS_MSG_ID = "load_progress"

    def __init__(my, sobject, snapshot=None):
        super(FlashLoad,my).__init__()
        my.sobject = sobject
        my.flash_snapshot = snapshot
        # set some defaults
        my.load_mode_id = my.LOAD_MODE_ELEMENT
        my.prefix_mode_id = None
        my.load_msg_id = ''

        my.load_mode = None


    def set_load_mode_id(my, element_id):
        '''set the widget id that contains the load_mode'''
        my.load_mode_id = element_id


    def set_load_msg_id(my, element_id):
        '''set the widget id that contains the load_mode'''
        my.load_msg_id = element_id

    def set_load_mode(my, load_mode):
        '''use this value instead of looking at an element'''
        assert load_mode in ['simple', 'merge']
        my.load_mode = load_mode



    def get_script(my):
        '''generate the script that will perform the load on the client side'''

        # use the sobjects code
        sobject = my.sobject


        web_dir = sobject.get_remote_web_dir()
        code = sobject.get_code()

        # download to the local repo
        local_repo_dir = sobject.get_local_repo_dir()

        # get the flash path
        fla_link, fla = my._get_file_info(sobject, my.flash_snapshot)

        # use the full name
        import os
        if not fla_link:
            return "alert('Flash file location undetermined. Its snapshots may have all been retired.')"
        fla = os.path.basename(fla_link)
        to_path = "%s/%s" % (local_repo_dir,fla)


        search_type = my.sobject.get_search_type_obj().get_base_key()
        template_name = search_type.replace("/", "-")
        sandbox_path  =  my.sobject.get_sandbox_dir()

        # get the template paths and if a template does not exist, use the 
        # failsafe default
        tmpl_fla_link, tmpl_fla = my._get_file_info(my.get_template())
        if not tmpl_fla_link:
            tmpl_fla_link, tmpl_fla = my.get_default_template("flash-asset_default.fla")

        web = WebContainer.get_web()
        local_dir = web.get_local_dir() + "/download"
        #tmpl_fla = "flash_asset_tmpl.fla" 
        tmpl_to_path = "%s/%s" % (local_dir,tmpl_fla)

        # either use and element or a set a value 
        if my.load_mode:
            load_mode = my.load_mode
        else:
            load_mode = my.load_mode_id


        return "pyflash.load('%s','%s','%s','%s','%s',"  \
            "'%s','%s','%s','%s')" \
            % ( fla_link, to_path, code, sandbox_path,   \
            tmpl_fla_link, tmpl_to_path,    \
            my.load_msg_id, load_mode, my.PREFIX_MODE_ELEMENT) \
       
 
    def get_template(my):
        ''' get the template sobject '''
        search_type = my.sobject.get_search_type_obj().get_base_key()

        key = "Template:%s"
            
        template = Container.get(key)
        if template != None:
            return template
        else:
            template = Template.get_latest(search_type)
            if not template:
                    Container.put(key, "")
            else:
                    Container.put(key, template)

            return template 




    def get_default_template(my, name):
        '''get the default template'''
        search_type = my.sobject.get_search_type_obj().get_base_key()
        # convert / to a -
        key = search_type.replace("/", "-")

        default_name = "%s_default.fla" % key
        url = WebContainer.get_web().get_base_url()
        base = url.to_string()
        tmpl_fla_link = "%s/context/template/%s" %(base, name)
        return tmpl_fla_link, name
       



class FlashStage(FlashLoad):

    def get_script(my):
        web = WebContainer.get_web()
       
        tmpl_fla_link, tmpl_fla = my._get_file_info(my.get_template())
        
        if not tmpl_fla_link:
            tmpl_fla_link, tmpl_fla = my.get_default_template("flash-layer_default.fla")

        from pyasm.flash import FlashLayer

        if isinstance( my.sobject, FlashLayer):
            layer_name = my.sobject.get_value('name')
            shot_code = my.sobject.get_value('shot_code')
        
            # set up event
            return "pyflash.set_stage_mode(true); pyflash.publish_layer('%s', '%s', '%s', '%s', '', '%s')" \
                % (shot_code, layer_name, tmpl_fla_link, tmpl_fla, \
                my.PREFIX_MODE_ELEMENT)
        else:
            shot_code = my.sobject.get_code()
            return "pyflash.post_stage_script();pyflash.publish('%s','%s')" \
                % (shot_code, "Staging" )
  

class FlashImport(FlashLoad):

    TYPE_1 = 'main'
    TYPE_2 = 'icon_main'
    def __init__(my, sobject, snapshot=None):
        super(FlashImport, my).__init__(sobject, snapshot)
        my.importable = False
        
    def get_script(my, file_type=TYPE_1):
        ''' this imports the publish_main file, but may not be desirable due to its file size'''
        if not file_type:
            file_type = my.TYPE_1
        assert file_type in [my.TYPE_1, my.TYPE_2]
        # use the sobjects code
        sobject = my.sobject

        web_dir = sobject.get_remote_web_dir()
        code = sobject.get_code()

        # download to the local repo
        local_repo_dir = sobject.get_local_repo_dir()

        # get the media path
        fla_link, fla = my._get_file_info(sobject, my.flash_snapshot, file_type=file_type)
        # use the full name
        import os
        if not fla_link:
            return "alert('Flash file location undetermined. Its snapshots may have all been retired.')"
        

        pat = re.compile(r'(.jpg|.tga|.bmp|.png|.tif|.mov|.aif)$', re.IGNORECASE)
        if pat.search(fla):
            my.importable = True
        
        if not my.importable and file_type==my.TYPE_1:
            new_fla_link, new_fla = my._get_file_info(sobject, my.flash_snapshot, file_type=my.TYPE_2)
            if pat.search(new_fla):
                my.importable = True
                fla_link, fla = new_fla_link, new_fla

        fla = os.path.basename(fla_link)
        to_path = "%s/%s" % (local_repo_dir,fla)
        if not my.importable:
             return "pyflash.download('%s','%s','%s','%s')" \
                % ( fla_link, to_path, code, my.load_msg_id)
        search_type = my.sobject.get_search_type_obj().get_base_key()
        template_name = search_type.replace("/", "-")
        sandbox_path  =  my.sobject.get_sandbox_dir()

        # get the template paths and if a template does not exist, use the 
        # failsafe default
        tmpl_fla_link, tmpl_fla = super(FlashLoad, my)._get_file_info(my.get_template())
        if not tmpl_fla_link:
            tmpl_fla_link, tmpl_fla = my.get_default_template("flash-asset_default.fla")

        web = WebContainer.get_web()
        local_dir = web.get_local_dir() + "/download"
        tmpl_to_path = "%s/%s" % (local_dir,tmpl_fla)

        

        return "pyflash.import('%s','%s','%s','%s','%s',"  \
            "'%s','%s')" \
            % ( fla_link, to_path, code, sandbox_path,   \
            tmpl_fla_link, tmpl_to_path, my.load_msg_id) 
            
    def get_stage_script(my):
        ''' this imports the icon_main file, but may not be desirable due to its file size'''
        return my.get_script(file_type=my.TYPE_1)
    
    def _get_file_info(my, sobject, snapshot=None, file_type='main'):
        ''' return the web url and the file name with media sobject'''
        web_dir = None
        if not sobject:
            return None, None


        if not snapshot:
	    key = sobject.get_search_key()
            # the latest snapshot
            snapshot = Snapshot.get_latest_by_sobject(sobject)
            
        if snapshot:
            fla = snapshot.get_name_by_type(file_type)
            fla_file_name = snapshot.get_file_name_by_type(file_type)
            web_dir = sobject.get_remote_web_dir()
            fla_link = "%s/%s" % (web_dir, fla_file_name)
            return fla_link, fla
        else:
            return None, None

    def is_importable(my):
        return my.importable == True




