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

__all__ = ['XSIImpl']


from xsi import XSI, XSIEnvironment, XSINodeNaming
from xsi_parser import XSIParser, XSIParserTextureFilter
from pyasm.application.common import AppException, Common
import re,os
import sys

# library of XSI constants
try:
    from win32com.client import constants as c
except ImportError:
    #print("Warning: xsi.py requires model [win32com.client]")
    pass



class XSIImpl(object):
    '''class which holds the specifics for an example XSI implementation.
    '''
    def __init__(self):
        self.env = XSIEnvironment.get()
        self.app = XSI.get()


    def dump_interface(self, node_name):
        '''Dump animation from an node '''
        # export the selected node
        file_path = "%s/%s.tmp.cmd" % (self.env.get_tmpdir(),node_name)
        self.app.export_anim(file_path, node_name)
        return file_path

    def get_save_dir(self):
        dir = self.app.get_save_dir()
        return dir

    def start_progress(self, title, visible, step):
        bar = ProgressBar(self.app, title, visible, step)
        return bar

    def get_snapshot_code(self, node_name, snapshot_type):
        '''This function gets the snapshot_code that was used to load this
        asset'''
        node_data = self.app.get_node_data(node_name)
        snapshot_code = node_data.get_attr("%s_snapshot" % snapshot_type,"code")
        return snapshot_code


    def get_snapshot_attr(self, node_name, snapshot_type, attr):
        '''This function gets the snapshot_code that was used to load this
        asset'''
        node_data = self.app.get_node_data(node_name)
        snapshot_code = node_data.get_attr("%s_snapshot" % snapshot_type, attr)
        return snapshot_code


    def get_textures_from_instance(self, node_name):
        '''extracts external file path references from a maya file'''
        '''NOTE: this is not currently used because there is no simple
        way in Maya to determine which file node belongs to which assets'''

        texture_nodes = []
        texture_paths = []
        
        return texture_nodes, texture_paths

    

    def get_textures_from_path(self, path):
        # find all of the textures in the extracted file
        # can only do this with dotXSI files
        if path.endswith(".dotXSI"):

            current_node = None

            texture_nodes = []
            texture_paths = []
            texture_attrs = []

            # parse the xsi file
            parser = XSIParser(path)
            parser.set_app(self.app)
            filter = XSIParserTextureFilter()
            parser.add_filter( filter )
            parser.parse()

            texture_nodes, texture_paths, texture_attrs = filter.get_textures()

            return texture_nodes, texture_paths, texture_attrs
        else:
            return [],[],[]

    def get_texture_code(self, parent_code, node_name):
        '''TODO: remove this. Not needed. get a derived texture code. This corresponds to logic in TextureCheckin'''
        tmp = node_name.split(".")
        try:
            front_part = tmp[2:4]
            front_part.append(tmp[-1]) 
            
            node_name = '_'.join(front_part)
        except IndexError:
            raise AppException('Expecting a node name in the form of'\
                'node_name.mesh_name.Material.shading.file_node. Received [%s]' %node_name)
        texture_code = "%s-%s" % (parent_code, node_name)
        return texture_code

    def get_textures_from_session(self, node_name):
        texture_nodes = []
        texture_paths = []
        texture_attrs = []

        self.app.xsi.LogMessage("get_textures_from_session")

        root = self.app.xsi.ActiveProject.ActiveScene.Root

        node = root.FindChild(node_name)
        # skip if it is not a Model node
        if not node or node.Type != '#model':
            return [], [], []

        self.app.xsi.LogMessage("node: [%s]" % node)
        try:
            fs = node.ExternalFiles
            tex_node_dict = self._get_texture_node_dict(node_name)
            for f in fs:
                if not f:
                    continue
                path = f.ResolvedPath
                if self.is_file_group(path):
                    group_exists = True
                    file_path = self.get_tactic_file_group_path(path)
                    file_range = self.get_file_range(path)
                    file_group = Common.expand_paths(file_path, file_range)
                    for item in file_group:
                        if not os.path.exists(item):
                            self.app.message("WARNING: one of the file groups does not exist")
                            group_exists = False
                            break
                    if not group_exists:
                        continue
                #TODO: add a self.impl.path_exists()
                else:
                    if not os.path.exists(path):
                        continue
                #self.app.xsi.LogMessage("f.PATH " + path)
                owner = f.Owners[0]

                if not path:
                    self.app.message("WARNING: external file for node [%s] is empty" % node_name)
                    continue

                # check if this is a reference. if so, ignore
                if owner.LockType == c.siLockTypeRefModel:
                    continue

                # if FileType is not Pictures, skip
                if f.FileType != "Pictures":
                    continue

                #to check if a path has either 'ght'(to check if lightmap name exists) since we want to ignore this file
                #along with 
                #pat = re.compile('(.*ght.*\.map)|(.*\.(fgmap|phmap|htm))$',re.IGNORECASE)
                #if pat.match(path):
                #    continue
                
                # texture node contains the mesh node in the model node
                texture_node_list = tex_node_dict.get(path)
                if not texture_node_list:
                    self.app.message('WARNING: [%s] does not have a corresponding node'%path) 
                    continue
                for texture_node in texture_node_list:
                    # texture node should be unique
                    if texture_node not in texture_nodes:
                        texture_nodes.append(texture_node)
                        texture_paths.append(path)
                        texture_attrs.append('SourceFileName')

        except AppException, e:
            self.app.xsi.LogMessage("WARNING: %s" % e.__str__())
        return texture_nodes, texture_paths, texture_attrs


    def _get_texture_node_dict(self, node_name):
        '''get the texture node dict and add prefix(asset_code) to the texture first
            if nececssary'''
        root = self.app.xsi.ActiveProject.ActiveScene.Root
        # extract asset_code
        naming = XSINodeNaming(node_name)
        asset_code = naming.get_asset_code()
        node = root.FindChild(node_name)
        info = {}
        children = node.FindChildren('','', ['Mesh Geometries','Clusters'], True)
        image_attr = "AllImageClips"
        if self.app.xsi.Version() < "7":
            image_attr = "ImageClips"
        clip_dict = {} 
        for i in children:
            clips = eval('i.Material.%s' % image_attr)
            
            for clip in clips:
                if self._is_light_map(clip):
                    continue
                if self._is_clip_referenced(clip):
                    continue
                clip_name = str(clip.Name)
                
                # add prefix if it does not exist
                if not clip_name.startswith(asset_code):
                    clip_name = '%s_%s' %(asset_code, clip_name) 
                    clip.Name = clip_name
                path = clip.Parameters('SourceFileName').Value
                clip_dict[clip_name] = clip.FullName, path
            

            #listing clusters for each mesh along with their material
            for j in i.ActivePrimitive.Geometry.Clusters:
                if (j.type=="poly"):
                    clips = eval('j.Material.%s' % image_attr)
                    nested_clips=filter(lambda nest:\
                        nest.Type=='ImageClip', j.Material.NestedObjects)
                    all_clips = []
                    all_clips.extend(clips)
                    if nested_clips:
                        all_clips.extend(nested_clips)
                    for clip in all_clips:
                        if self._is_light_map(clip):
                            continue
                        if self._is_clip_referenced(clip):
                            continue
                        clip_name = str(clip.Name)
                        # add prefix if it does not exist
                        if not clip_name.startswith(asset_code):
                            clip_name = '%s_%s' %(asset_code, clip_name) 
                            clip.Name = clip_name
                        path = clip.Parameters('SourceFileName').Value
                        clip_dict[clip_name] = clip.FullName, path
                
        for key, value in clip_dict.items():
            full_name, path = value
            current_list = info.get(path)
            if current_list:
                current_list.append(full_name)
            else:
                info[path] = [full_name]
        ''' # this only works if the Shader name is Material
        import win32com.client
        o = win32com.client.Dispatch( "XSI.Collection" )
        o.Items = '%s.*.Material, %s.*.*.cls.*.Material' %(node_name, node_name) 
        o.Unique = True
        LogMessage( o.Count )
        for i in o:
            clips = i.ImageClips
            for clip in clips:
                path = clip.Parameters('SourceFileName').Value
                info[path] = clip.FullName
           
        '''

        return info
                
    def _is_light_map(self, clip):
        if clip.Type == "WritableImageSource":
            return True
        else:
            return False

    def _is_clip_referenced(self, clip):
        '''returns True if a clip is referenced'''
        owners = clip.Owners
        if len(owners) < 2:
            return False

        if not owners[1] or owners[1].Name =='TransientObjectContainer':
            return False
        lock_type = None
        for owner in [owners[1], owners[0]]:
            if hasattr(owner, 'LockType'):
                lock_type = owner.LockType
                break
        if lock_type and lock_type == c.siLockTypeRefModel:
            return True
        else:
            return False
         
    def get_global_texture_dirs(self):
        return []

    def get_geo_paths(self):
        return []

    def set_user_environment(self, sandbox_dir, basename):
       
        progress = self.start_progress('Setting Project', True, 1)
        dirs = sandbox_dir.split("/")
        # TODO: this is weird code, it should have been truncated in the server side
        if dirs[-1] in ["Scenes", 'scenes']:
            dirs = dirs[:-1]
            project_dir = "/".join(dirs)
        else:
            project_dir = sandbox_dir

        self.app.set_project(project_dir)
        progress.increment()
        progress.stop()
      
    # File group functions
    def is_file_group(self, path):
        xsi_pat = re.compile('\[\d+\.\.\d+(;\d+)?\]')
        if xsi_pat.search(path):
            return True
        return False

    def get_file_range(self, path):
        start = 0
        end = 0
        by = 1
        xsi_pat = re.compile('.*\[(\d+\.\.\d+(;\d+)?)\].*')
        m = xsi_pat.match(path)
        groups = m.groups()
        info_range = groups[0]
        pad = 3
        if ';' in info_range:
            info_range, pad = info_range.split(';')
        start, end = info_range.split('..',1)
            
        return '%s-%s/%s' %(start, end, by)


    def get_tactic_file_group_path(self, path):
        '''get TACTIC compatible notation ####.jpg given app's path'''
        new_str = path
        def replace_str(m):
            groups = m.groups()
            info_range = groups[0]
            info_range = info_range[1:len(info_range)-1]
            pad = 3
            if ';' in info_range:
                info_range, pad = info_range.split(';')
            start, end = info_range.split('..',1)
            return '#'*int(pad)
        
       
        xsi_pat = re.compile('(\[\d+\.\.\d+(;\d+)?\])')
        new_str = xsi_pat.sub(replace_str, path)  

        return new_str

    def get_app_file_group_path(self, file_name, file_range):
        '''get the group path notation specific for the application'''
        pat = re.compile('\.(#+)\.')
        m = pat.search(file_name)
        new_str = file_name
        if m:
            group = m.groups()[0]
            frame_start, frame_end, frame_by = Common.get_file_range(file_range)
            replace_str = '.[%s..%s;%s].'%(frame_start, frame_end, len(group))
            
            new_str = pat.sub(replace_str, file_name)
        return new_str

class ProgressBar(object):
    ''' A progress bar used in XSI '''
    def __init__(self, app, title, visible, max): 
        ''' @params
            progress_bar- XSI's progress bar in the XSIUIToolkit module
            title- title
            visible- visibility
            step- number of steps in this process '''
        self.bar = app.toolkit.ProgressBar
        self.interactive = app.xsi.Interactive
        if max <= 0:
            max = 1
        self.bar.Maximum = max
        """
        if step > 0:
            self.bar.Step = int(100 / step)
        else:
            self.bar.Step = 100
        """
        self.bar.Step = 1
        self.bar.Caption = title
        self.bar.Visible = visible
        self.bar.CancelEnabled = False
        
    def increment(self):
        if not self.interactive:
            sys.stdout.write('.')
            return
        if self.bar.Value < self.bar.Maximum:
            self.bar.Increment()

    def set_message(self, message):
        if not self.interactive:
            print message
            return
        self.bar.Caption = message

    def stop(self):
        if not self.interactive:
            return
        self.bar.Visible = False


