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

__all__ = ["RenderException", "FlashLayerRenderCmd"]

from pyasm.command import *
from pyasm.search import *
from pyasm.checkin import SnapshotBuilder, SnapshotCheckin, FileCheckin, FileGroupCheckin
from pyasm.biz import Snapshot, Template, IconCreator, FileGroup, FileException
from biz import FlashLayer
from flash_render_context import *
from pyasm.common import Config, Environment
from pyasm.prod.biz import Render

import os, shutil, re, sys, time

class RenderException(Exception):
    pass


class FlashLayerRenderCmd(Command):
          
    FLASH_LAYER_TYPE = '.fla' 
    
    def __init__(my):
        super(FlashLayerRenderCmd, my).__init__()
        my.sobject = None 
    
    def set_project(my, project):
        my.project = project

    def set_search_keys(my, search_keys):
        my.search_keys = search_keys

    def set_cam_search_key(my, search_key):
        my.cam_search_key = search_key

    def set_context_name(my, context_name):
        my.render_context_name = context_name
        
    def set_render_context(my, context):
        my.render_context = context
        
    def get_title(my):
        return "Flash Layer Render"

    def execute(my):
        SearchType.set_project(my.project)
        
        # multiple layers can get rendered
        for search_key in my.search_keys:
            f = file('%s/temp/render_exec.jsfl' % Environment.get_tmp_dir(), 'w')
            render_command = my.get_render_command(search_key, my.cam_search_key)
            f.write(render_command)
            f.write(my.get_render_log_command())
            
            f.close()
       
            os.startfile( "\"%s\"" %f.name)
            
            my.remove_file(my.get_render_log_path())

            # check if the render is done
            sys.stdout.write("\nRendering")
            while not os.path.isfile(my.get_render_log_path()):
                sys.stdout.write('. ')
                time.sleep(2)
            print
            
            f = file(my.get_render_log_path(), 'a')
            now = time.localtime(time.time())
            f.write(' at %s' %time.asctime(now))
            f.close()
            
            #my.convert_images()
            print("Checking in Render. . .")
            my.checkin_render()

    def get_render_log_command(my):
        '''generate render log, mainly to signal a layer render is finished'''
        render_dir = my.render_context.get_render_dir()
        render_log = my.render_context.get_render_log()
        function = 'write_render_log'
        
        server = Config.get_value("install", "install_dir")
        jsfl_path = 'file:///%s/src/context/JSFL/load.jsfl' % server 
        cmd = "fl.runScript( '%s', '%s', '%s', '%s')\n" \
                % (jsfl_path, function, render_dir, render_log)
        return cmd

    def get_render_command(my, search_key, cam_search_key):
        '''render in a separate process'''
        '''NOTE: Highly specific to Flash render'''
        fla_clone_path, fla_sobj, fla_snap = my._get_layer_info(search_key)
            
        cam_clone_path, cam_sobj, cam_snap = my._get_layer_info(cam_search_key)
        cam_layer_name = ''
        if cam_sobj:
            cam_layer_name = cam_sobj.get_value('name')
            
        #search_type, search_id = search_key.split('|')
        #fla_snap = Snapshot.get_latest(search_type, search_id)
        function = 'render_layer'

        render_context = eval( '%s(fla_sobj)'% my.render_context_name)  
        render_context.set_snapshot(fla_snap)
        my.set_render_context(render_context)
        
        # directories will get auto-created before rendering 
        render_dir = my.render_context.get_render_dir()
        file_format = my.render_context.get_file_format()

        server = Config.get_value("install", "install_dir")

        # TODO: Merge this back in to work with layer concept.
        #jsfl_path = 'file:///%s/src/context/JSFL/load.jsfl' % server 
        #preprocess_jsfl_path = 'file:///%s/src/context/JSFL/preprocess.jsfl' % server 
        #cmd = "fl.runScript( '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')\n" \
        #        % (jsfl_path, function, preprocess_jsfl_path, fla_clone_path, \
        #        fla_sobj.get_value('name'),\
        #        cam_clone_path, cam_layer_name, render_dir, file_format)


        jsfl_path = 'file:///%s/src/context/JSFL/load2.jsfl' % server 
        cmd = "fl.runScript( '%s', '%s', '%s', '%s', '%s')\n" \
                % (jsfl_path, "load_asset", fla_clone_path, "", fla_sobj.get_name() )
        jsfl_path = 'file:///%s/src/context/JSFL/render.jsfl' % server 
        cmd += "fl.runScript( '%s', '%s', '%s', '%s', '%s')\n" \
                % (jsfl_path, "render_layer", fla_sobj.get_name(), file_format, render_dir )


        return cmd


    def _get_layer_info(my, search_key):
        ''' clone the source and return the clone path and layer name '''
        try:
            search_type, search_id = search_key.split('|')
        except Exception, e:
            print "WARNING: invalid or empty search key. ", e
            return None, None, None
        
        fla_sobj = Search.get_by_search_key(search_key) 
        fla_snap = Snapshot.get_latest(search_type, search_id) 
        if not fla_snap:
            parent = fla_sobj.get_parent("prod/shot")
            fla_snap = Snapshot.get_latest_by_sobject(parent)
            if not fla_snap:
                raise CommandException("Nothing to render for %s" % search_key)

        fla_path = fla_snap.get_lib_path_by_type(my.FLASH_LAYER_TYPE)

        fla_dir, fla_basename = os.path.split(fla_path)
        fla_clone_path =  '%s/download/%s'  %(\
            Environment.get_tmp_dir(), fla_basename)
                    
        shutil.copy2(fla_path, fla_clone_path)
        
        return fla_clone_path, fla_sobj, fla_snap


    def checkin_render(my):

        render_dir = my.render_context.get_render_dir()
        # check the expected images
   
        org_pat, final_pat = my.render_context.get_render_file_naming()
        #TODO: move frame range into render context

        filenames = os.listdir(render_dir)
        pat = re.compile(org_pat)

        # attach the sobject and snapshot to the render
        snapshot = my.render_context.get_snapshot()
        sobject = my.render_context.get_sobject()

        # for auto-increment, use -1 for version number
        file_range = my.render_context.get_frame_range()
        
        render = Render.create(sobject, snapshot, '<session/>', \
            file_range.get_key(), -1)
        my.description += "Flash render [%s] in %s\n" \
            %(sobject.get_description(), my.render_context.get_name())
        my.sobject = sobject
        
        # checkin the render
        file_format = my.render_context.get_file_format()
        if file_format =='png':
           my._check_in_png( snapshot, sobject, render, pat, final_pat, render_dir, filenames)
        elif file_format =='swf':
           my._check_in_swf( snapshot, sobject, render, pat, final_pat, render_dir, filenames) 
                
        
    def _check_in_swf(my, snapshot, sobject, render, pat, final_pat, render_dir, filenames):
        final_path = icon_path = ''
        for name in filenames:
            if pat.match(name):
                final_name = pat.sub(final_pat, name)
                shutil.move(render_dir + "/" + name, render_dir \
                    + "/" + final_name)
                src_path = "%s/%s" % (render_dir, final_name) 
                if final_name.endswith('.png'):
                    icon_creator = IconCreator(src_path)
                    icon_creator.create_icons()
                    icon_path = icon_creator.get_icon_path()
                elif final_name.endswith('.swf'):
                    final_path = src_path
        types = ["main"]
        paths = [final_path]
        
        if icon_path:
            paths.append(icon_path)
            types.append('icon')
        checkin = FileCheckin(render, paths, types, context="render", column="images")
        checkin.execute()

    def _check_in_png(my, snapshot, sobject, render, pat, final_pat, render_dir, filenames):
        icon_path = final_path = ''
        icon_creator = None

        file_range = my.render_context.get_frame_range()
        
        for name in filenames:
            if pat.match(name):
                final_name = pat.sub(final_pat, name)
                shutil.move(render_dir + "/" + name, render_dir + "/" + final_name)
                final_path = "%s/%s" % (render_dir, final_name)
                icon_creator = IconCreator(final_path)
                icon_creator.create_icons()
        if icon_creator:
            icon_path = icon_creator.get_icon_path()
        gen_icon_path = re.sub("(.*_icon\.)(\d{4})(\.png)", r"\1####\3", icon_path) 
        gen_final_path = re.sub("(.*\.)(\d{4})(\.png)", r"\1####\3", final_path)  
        types = ["main", "icon"]
        paths = [gen_final_path, gen_icon_path]
        
        # check that all the files exist
        try:
            for path in paths:
                FileGroup.check_paths(path, file_range)    
        except FileException, e:
            print( "The frame range of layer [%s] probably\
                does not match the shot's frame range [%s]. %s" \
                %(sobject.get_value('name'), file_range.get_key(), e))
           
            # FIXME: this is a little redundant, but it works
            count = 0
            file_paths = FileGroup.expand_paths(paths[0], file_range)
            for file_path in file_paths:
                if not os.path.exists(file_path):
                    break
                count += 1
            file_range.frame_end = count

            
        # check in the render
        checkin = FileGroupCheckin(render, paths, types, file_range,\
            context="render", column="images")
        checkin.execute()
        
    def get_render_log_path(my):
        render_dir = my.render_context.get_render_dir()
        render_log = my.render_context.get_render_log()
        return '%s/%s' % (render_dir, render_log)
    
    def remove_file(my, file_path):
        try:
            os.unlink(file_path)
        except OSError, e:
            if e.errno != 2:
                raise e





