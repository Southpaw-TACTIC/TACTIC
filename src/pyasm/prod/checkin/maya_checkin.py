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

__all__ = ['MayaCheckin', 'MayaAssetCheckin', 'MayaGroupCheckin', 'MayaAnimCheckin', 'MayaAnimExportCheckin', 'MayaSObjectCheckin','MayaSetCreateCmd', 'ShotCheckin', 'TextureCheckin']

import os, shutil, re

from pyasm.common import *
from pyasm.checkin import *
from pyasm.biz import *
from pyasm.command import CommandException, Command
from pyasm.search import SearchType, Search, SObject
from pyasm.application.maya import *
from pyasm.application.xsi import *
from pyasm.prod.biz import *

class MayaCheckin(FileCheckin):

    def __init__(self, sobject):
        BaseCheckin.__init__(self, sobject)
        self.process = ''
        self.context = "publish"
        self.column = "snapshot"
        self.instance = sobject.get_code()
        # default is asset
        self.snapshot_type = "asset"

        self.file_types = []
        
        self.options = {}

        # extras
        self.checkin_type = 'strict' 
        
        self.level_type = None
        self.level_id = None
        self.source_paths = []
        self.mode = None
        self.use_handoff_dir = False
        self.server_dir = ''
        # TODO: super FileCheckin above and avoid redefining FileCheckin instance variables
        self.md5s = []

        self.dir_naming = None
        self.file_naming = None
 

    def set_option(self, key, value):
        self.options[key] = value

    def get_option(self, key):
        value = self.options.get(key)
        if not value:
            return ""
        else:
            return value

    def set_instance(self, instance):
        self.instance = instance


    def set_description(self, description):
        self.description = description

    def set_process(self, process):
        self.process = process
        # FIXME: need to add this for now.  At present, dependency process
        # notifying uses process_name.
        self.process_name = process

    def set_context(self, context):
        self.context = context

    def set_use_handoff(self, use_handoff):
        self.use_handoff_dir = use_handoff

    def set_snapshot_type(self, snapshot_type):
        self.snapshot_type = snapshot_type
        

    def get_snapshot_type(self):
        '''this sets the snapshot type that will be put into the snapshot'''
        return self.snapshot_type


    def execute(self):
        
        # look for the presence of an error file.  If it is there,
        # then bail.  This means that the client side failed for some reason
        error_path = "%s/error.txt" % self.get_upload_dir()
        if os.path.exists(error_path):
            file = open(error_path,"r")
            lines = file.read()
            if lines:
                if lines.find('bad local file header') > -1:
                    lines = 'Restart your 3D App. New TACTIC version is detected. %s' %lines
            file.close()
            os.unlink(error_path)
            raise ClientTacticException(lines)

        else:
            super(MayaCheckin,self).execute()

    def get_description(self):
        return "Checked in %s, context: %s" % \
            (self.sobject.get_code(), self.context)



    def _read_ref_file(self):
        '''read the reference file containing extra node information'''
      
        server_dir = self.get_upload_dir() 
        xml = Xml()

        filename = File.get_filesystem_name( self.instance )

        xml.read_file( "%s/%s-ref.xml" % (server_dir,filename) )
        return xml

    def get_handoff_dir(self):
        '''get handoff dir through the ref file attr'''
        xml = self._read_ref_file()
        handoff_dir = xml.get_value("session/ref/@handoff_dir")
        if not handoff_dir:
            raise CheckinException("Handoff dir not recorded at the [code]-ref.xml [%s]"%self.get_upload_dir())
        from pyasm.web import WebContainer 
        web = WebContainer.get_web()
        handoff_dir = handoff_dir.replace('\\','/')
        
        ticket = handoff_dir.split('/')[-1]
        server_dir = web.get_server_handoff_dir(ticket)
        return server_dir

    def get_server_dir(self):
        if self.server_dir:
            return self.server_dir
        if self.use_handoff_dir:
            server_dir = self.get_handoff_dir()
        else:
            server_dir = self.get_upload_dir()
        self.server_dir = server_dir
        return server_dir

    def _add_file_info(self, xml, paths):
        '''get the file path info from ref.xml and add to self.file_info'''
        self.file_info = {}

        # get the uploaded file (assume there is only one file)
        orig_path = xml.get_value("session/ref/@path")
        node_name = xml.get_value("session/ref/@node_name")
        if not orig_path:
           orig_path = xml.get_value("session/file/@path")

        if not orig_path:
            return 

        basename = os.path.basename(orig_path)
        basename = File.get_filesystem_name(basename)
        action = "upload"
        server_dir = self.get_server_dir()
        if self.use_handoff_dir:
            action = "hand off"
        
        path = "%s/%s" % (server_dir, basename)
        
        if not os.path.exists(path):
            raise CheckinException("Failed to %s file on checkin '%s'" % (action, orig_path))

        base, ext = os.path.splitext(path)
        filename = os.path.basename(path)
        paths.append(path)
        self.file_info[filename] = {}

        # FIXME: hard coded relationships
        if ext == ".ma" or ext == ".mb":
            self.file_info[filename]["type"] = "maya"
        elif ext == ".hip" or ext == ".otl":
            self.file_info[filename]["type"] = "houdini"
        elif ext == ".dae":
            self.file_info[filename]["type"] = "collada"
        elif ext == ".scn" or ext == ".xsi" or ext == '.emdl':
            self.file_info[filename]["type"] = "xsi"
        elif ext == ".obj":
            self.file_info[filename]["type"] = "obj"
        else:
            raise CheckinException("File '%s' has unsupported extension" % \
                filename )

        self.file_info[filename]["node_name"] = node_name






class MayaAssetCheckin(MayaCheckin):
    '''checks in a maya asset_node.'''
    def __init__(self, sobject):
        super(MayaAssetCheckin,self).__init__(sobject)

        self.file_paths = []

        # a number of texrure variables that must be used throughout the
        # process
        self.texture_mode = "reference"
        self.texture_codes = []
        self.texture_nodes = []
        self.texture_names = []
        self.texture_snapshots = []
        self.textures = []

        self.snapshot_type = "asset"
 
    def get_title(self):
        return "Asset Checkin"

    def set_texture_mode(self, mode):
        assert mode in ['reference','embed','ignore']
        self.texture_mode = mode

    
    def create_files(self):

        paths = []
   
        # look in the info file
        xml = self._read_ref_file()
        self._add_file_info(xml, paths)
        self.source_paths = paths[:]

        # set md5 if found
        main_md5 = xml.get_value("session/ref/@md5")
        if not main_md5:
            main_md5 = None
        self.md5s = [main_md5]
        return paths

    def count_duplicates(self, input_list):
        unique_set = set(item for item in input_list)
        return [(item, input_list.count(item)) for item in unique_set]


    def handle_geo_files(self, builder):
        # read reference file and get all of the geo nodes
        xml = self._read_ref_file()
        geo_nodes = xml.get_nodes("session/*/file[@type='geo']")

        # if there are no geo nodes get out
        if not geo_nodes:
            return

       
        upload_dir = self.get_server_dir()

        #self.geo_cache_paths = []
        #self.orig_geo_cache_paths = []
        #self.all_geo_cache_paths = []
        types = []

	    # these dicts organize cache path and prevents duplicated check-ins
        node_cache_dict = {}
        node_dup_dict = {}
        geo_cache_path_dict = {}
        geo_snapshot_dict = {}
        
        # check for unique path name but duplicated file name
        validate_paths = []
        validate_file_names = []
        for node in geo_nodes:
            
            path = Xml.get_attribute(node, "path")
            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )
            validate_paths.append(path)
            validate_file_names.append(filename)

        path_output = self.count_duplicates(validate_paths)
        filename_output = self.count_duplicates(validate_file_names)

        for idx, output in enumerate(filename_output):
            name, count = output
            if count > 1:
                path_name, path_count = path_output[idx]
                if count != path_count:
                    raise TacticException('Some cache paths share the same cache file name [%s]. Please ensure they are unique during creation.'%name)  
 
        for node in geo_nodes:
            
            path = Xml.get_attribute(node, "path")
            
          
            type = Xml.get_attribute(node, "type")
            attr = Xml.get_attribute(node, "attr")
            node_name = Xml.get_attribute(node, "node")

            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )

            # find the local path of the uploaded/handoff file 
            path = "%s/%s" % (upload_dir,filename)
            path_list = node_cache_dict.get(node_name)
            if not path_list:
                path_list = []
                node_cache_dict[node_name] = path_list
            path_list.append(path)
            
            # keep track of duplicates
            if path not in geo_cache_path_dict.keys():
                geo_cache_path_dict[path] = node_name
            else:
                # duplicates found, store it in node_dup_dict
                node_dup_dict[node_name] = geo_cache_path_dict.get(path)



        for node_name, value in node_cache_dict.items():
            path_list = value
            # if there is only 1 cache file, simplify it and just call the context 'cache'
            if len(node_cache_dict) == 1:
	        cache_context = "cache"
            else:
                cache_context = "cache/%s" %node_name
         
            # collect types, reject more than 1 geo in a path_list 
            # since that's cache per frame which needs FileGroupCheckin to support

            types = []
            geo_count = 0
            for path in path_list:
                if path.endswith(".xml"):
                    types.append("xml")
                else:
                    types.append("geo")
                    geo_count += 1
                if geo_count > 1:
                    raise TacticException('Please generate single cache file for the whole time frame. One file per frame caching is not yet supported.') 
        
            dup_node = node_dup_dict.get(node_name)
            if not dup_node:
                
                checkin = FileCheckin(self.sobject, path_list, types, context=cache_context)
                checkin.execute()
                geo_snapshot = checkin.get_snapshot()
                geo_snapshot_dict[node_name] = geo_snapshot
            else:
                # get the geo snaposhot of the stored node_name
                geo_snapshot = geo_snapshot_dict.get(dup_node)

            #dir = geo_snapshot.get_lib_dir(file_type="geo")
            #filenames = geo_snapshot.get_names_by_type("geo")
            #for filename in filenames:
            #    self.geo_cache_paths.append("%s/%s" % (dir, filename))

            geo_node = builder.add_ref_by_snapshot(geo_snapshot)
            Xml.set_attribute(geo_node, "type", "cache")
            Xml.set_attribute(geo_node, "node", node_name)

    def _get_file_info_dict(self, parent_code, nodes):
        '''NEW UPDATED METHOD: get a dictionary of file_path : (texture_code, node_name) list'''
        info = {}
           
        for i, node in enumerate(nodes):
            path = Xml.get_attribute(node, "path")
            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )

            attr = Xml.get_attribute(node, "attr")
            node_name = Xml.get_attribute(node, "node")
            
            
            full_node_name = ''
            # for xsi:
            if attr == "SourceFileName":
                # xsi uses the full_node_name for description
                full_node_name = node_name
                tmp = node_name.split(".")
                try:
                    front_part = tmp[2:4]
                    front_part.append(tmp[-1]) 
                    
                    node_name = '_'.join(front_part)
                except IndexError:
                    raise TacticException('Expecting a node name in the form of'\
                        'node_name.mesh_name.Material.shading.file_node. Received [%s]' %node_name)
            else:
                # if there is a namespace, the split and take the last part
                # (for maya)
                node_name = node_name.split(":")[-1]

                # split this and take the last one in this path
                # (for Houdini paths)
                node_name = node_name.split("/")[-1]

            # shorten the texture code for maya ftn attributes or xsi ImageClips
            if not attr or attr in ["ftn" , "SourceFileName"]:
                texture_code = "%s-%s" % (parent_code, node_name)
            else:
                texture_code = "%s-%s-%s" % (parent_code, node_name, attr)
            
            # remove / in subcontext if any
            texture_code = texture_code.replace("/", "-")

            # keep this in sequence for use in add_dependecies
            self.texture_codes.append(texture_code)
           
            #local_path = "%s/%s" % (server_dir,filename)
            #sub_info = info.get(local_path)
            #new_md5 = File.get_md5(local_path)
            # texture codes part is not used any more
            info_list = info.get(filename.lower())
            if info_list:
                info_list.append((texture_code, node_name))
            else:
                info[filename.lower()] = [(texture_code, node_name)]
                
        return info


    def add_dependencies(self, snapshot_xml):
        '''look into maya session and create the files'''
        # build the snapshot
        tt = Xml()
        tt.read_string(snapshot_xml)
        builder = SnapshotBuilder(tt)
      
        # read reference file
        xml = self._read_ref_file()

        # handle the geo files
        self.handle_geo_files(builder)


        # get the sobject_code and the context
        sobject_code = self.sobject.get_code()
        context = self.context
        base_search_type = self.sobject.get_base_search_type()

        # self.server_dir has been obtained earlier
        server_dir = self.get_server_dir()


        #--------------------------
        # handle layers
        #self.layer_nodes = xml.get_nodes("session/*/layer[@type='render']")
        if base_search_type == "prod/shot":
            layer_nodes = xml.get_nodes("session/*/layer")

            # get all of the layers for this sobject
            cur_layers = self.sobject.get_all_layers()
            cur_layer_names = [x.get_value("name") for x in cur_layers]

            for layer_node in layer_nodes:
                # see if these layers exist
                layer_name = Xml.get_attribute(layer_node, "name")
                if layer_name not in cur_layer_names:
                    Layer.create(layer_name, sobject_code)





        #-------------------------
        # handle textures

        # keep a list of textures that have already been checked in in this
        # transaction for a particular texture_code
        checked_textures = {}

        # get the dependent textures and process
        if self.texture_mode == 'ignore':
            self.texture_nodes = []
        else:
            self.texture_nodes = xml.get_nodes("session/*/file[@type='texture']")

        if self.get_option('texture_search_type'):
            texture_search_type = self.get_option('texture_search_type')
            texture_search_type_obj = SearchType.create(texture_search_type)
            texture_cls = texture_search_type_obj.__class__
            # have to set the SEARCH_TYPE for hte custom class
            texture_cls.SEARCH_TYPE = texture_search_type
            
        elif base_search_type == 'prod/shot':
            texture_cls = ShotTexture
        elif base_search_type == 'prod/shot_instance':
            texture_cls = ShotTexture
        else:
            texture_cls = Texture


        # get a dict of filename.lower() : texture code , node_name list
        tex_dict = self._get_file_info_dict(sobject_code, self.texture_nodes)
      
        for i, node in enumerate(self.texture_nodes):
            # initialize file_code
            file_code = ''
            path = Xml.get_attribute(node, "path")
            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )

            texture_code = self.texture_codes[i]
            
            # this "code" is applicable for new checkin_asset
            file_code = Xml.get_attribute(node, "code")

            md5 = Xml.get_attribute(node, "md5")
            node_name = Xml.get_attribute(node, "node")

            # use lowercase since windows user's path can have varied cases
            # which refer to the same path
            info_list = tex_dict.get(filename.lower())
            
            # remapped to already checked in file so that it can be reused
            # check to see if there is already a corresponding texture

            # find the local path of the uploaded file 
            local_path = "%s/%s" % (server_dir,filename)

            texture = None
            # find an existing texture sobject if it exists during this Checkin process
            # clear the cache first
            texture_cls.clear_cache()
            for info_item in info_list:
                info_texture_code, info_node_name = info_item
                texture = texture_cls.get(info_texture_code, sobject_code)
                if texture:
                    break

            # applicable for Maya
            # texture could be created or not created depending on the order of the texture node list
            # so do not check if texture is created here
            if not file_code and checked_textures.get(local_path.lower()):
                file_code = checked_textures.get(local_path.lower())
                # the find existing texture sobject logic above should find one regardless
                # TODO: remove this logic below
                # in some rare case in Maya with Layered Shader, there is no texture for this texture code yet
                if not texture:
                    # inquire about the file's parent
                    file = File.get_by_code(file_code)
                    texture = Search.get_by_id(file.get_value('search_type'), file.get_value('search_id')) 
                    if isinstance(texture, ShotTexture):
                        parent_code_column = 'shot_code'
                    elif isinstance(texture, Texture):
                        parent_code_column = 'asset_code'
                    else:
                        parent_code_column = 'asset_code'

                    if texture.get_value(parent_code_column, no_exception=True) != self.sobject.get_code():
                        raise CheckinException("Cannot locate the texture sobject for this texture [%s]" %local_path)
            

            # use file_code if available
            if file_code:
                file_object = File.get_by_code(file_code)
            else:
                # look up the file name in the database. NOTE: This is error prone
                file_object = File.get_by_filename(filename)
            
            if file_object:
            
                snapshot_code = file_object.get_value("snapshot_code")
                if snapshot_code == "":
                    raise CheckinException("file object '%s' does not have a snapshot_code" % file_object.get_code())


                texture_snapshot = Snapshot.get_by_code(snapshot_code)
                if not texture_snapshot:
                    raise CheckinException("Snapshot code '%s' does not exist in the database" % snapshot_code)


                texture = texture_snapshot.get_sobject()

                texture_name = file_object.get_full_file_name()

                # store the necessary info about this texture
                self.texture_names.append(texture_name)
                self.textures.append(texture)
                self.texture_snapshots.append(texture_snapshot)

                continue

            # for XSI or Houdini, it should not get to this point as it assume upload_dir here

            

            # if no corresponding texture object is found, then create one
            if not texture:
                category = "texture"
                (texture_basename, ext) = os.path.splitext( os.path.basename(filename) )
                description = '%s-%s' % ( texture_basename, node_name )
                texture = texture_cls.create(self.sobject, texture_code, 
                    category, description, sobject_context=context )
            
            # check in a new version of the texture file
            icon_creator = IconCreator(local_path)
            icon_creator.set_texture_mode()
            icon_creator.create_icons()

            web_path = icon_creator.get_web_path()
            icon_path = icon_creator.get_icon_path()

            # checkin all of the texture maps
            if web_path:
                file_paths = [local_path, web_path, icon_path]
                file_types = ['main','web','icon']
                md5_list = [md5, None, None]
            else:
                file_paths = [local_path]
                file_types = ['main']
                md5_list = [md5]

            # checkin this file into the texture
            # default to creation context, and use the current snapshot's
            # context if found
            texture_context = "publish"

            texture_snapshot = Snapshot.get_current_by_sobject(texture)
            
            if texture_snapshot:
                texture_context = texture_snapshot.get_context()
            checkin = FileCheckin(texture, file_paths, file_types, \
               snapshot_type="texture", context=texture_context, md5s=md5_list) 
            
            checkin.execute()


            texture_snapshot = checkin.get_snapshot()
            texture_xml = texture_snapshot.get_xml_value("snapshot")


            # update both the texture and the snapshot
            texture_snapshot.set_value("snapshot", texture_xml.to_string() )
            texture_snapshot.commit()
            texture.set_value("snapshot", texture_xml.to_string() )
            texture.commit()

            # get the main file
            file_name = texture_snapshot.get_name_by_type("main")
            file_code = texture_snapshot.get_file_code_by_type("main")
            # store the file_code which is unique
            checked_textures[local_path.lower()] = file_code

            # store the texture snapshots
            self.texture_names.append(file_name)
            self.textures.append(texture)
            self.texture_snapshots.append(texture_snapshot)


 
        # handle all of the textures
        for i in range(0, len(self.texture_nodes) ):

            texture_node = self.texture_nodes[i]
            texture = self.textures[i]
            texture_snapshot = self.texture_snapshots[i]

            path = Xml.get_attribute(texture_node, "path")
            node = Xml.get_attribute(texture_node, "node")
            attr = Xml.get_attribute(texture_node, "attr")

            # find the local path of the uploaded file
            file_name = os.path.basename(path)


            # check to see if there is a corresponding texture
            base, ext = os.path.splitext(file_name)
            #texture_code, context = base.split("_")
            context = texture_snapshot.get_context()

            # if there is an associated texture
            #search_type = texture.get_search_type()
            #search_id = texture.get_id()


            version = texture_snapshot.get_value("version")
            ref_node = builder.add_ref(texture, context, version)

            Xml.set_attribute(ref_node, "type", "texture")
            Xml.set_attribute(ref_node, "node", node)
            Xml.set_attribute(ref_node, "attr", attr)


        # commit it to the snapshot
        self.snapshot.set_value("snapshot", builder.to_string())       
        self.snapshot.commit()



    def create_snapshot(self, file_objects):

        # build the snapshot
        builder = SnapshotBuilder()
        if self.process:
            builder.add_root_attr('process', self.process)

        # add in all of the file references
        for i in range(0, len(file_objects)):
            file_object = file_objects[i]

            file_name = file_object.get_file_name()
            if self.file_info.has_key(file_name):
                file_info = self.file_info[file_name]
            else:
                full_file_name = file_object.get_full_file_name()
                file_info = self.file_info[full_file_name]

            node = builder.add_file( file_object, file_info )

            # get the namespace for this node
            top_node_name = file_info["node_name"]
            parts = top_node_name.split(":")
            namespace = parts[0]


            # handle embedded references
            xml = self._read_ref_file()

            # FIXME: handle input references (use asset_snapshot_code for now)
            snapshot_code = xml.get_value("session/ref/@asset_snapshot_code")
            if snapshot_code:
                builder.add_ref_by_snapshot_code(snapshot_code, type='input_ref')


            # handle sub references
            sub_refs = xml.get_nodes("session/ref/ref")
            for sub_ref in sub_refs:
                #snapshot_code = Xml.get_attribute(sub_ref, "asset_snapshot_code")
                # use filename instead ... it is more reliable at the moment
                # FIXME: the snapshot code should be more reliable.
                # We ae using file code, because the assumption that "asset_snapshot_code" is the sub_ref is false.  This should be ref_snapshot.  This needs to be reworked completely.  The reason that it is this way is that the tactic node needed to be able to store 2 or 3 sets of information: ie animation information which may node be a file.
                # FIXME: and this should be scoped by project
                path = Xml.get_attribute(sub_ref, "path")
                path = path.replace("\\", "/")
                filename = os.path.basename(path)
                file_obj = File.get_by_filename(filename)

                if file_obj:
                    pass
                elif self.get_option("unknown_ref") == "ignore":
                    continue
                else:
                    raise CheckinException("File '%s' not recognized by Tactic. You can check the Ignore Unknown references option to suppress this error." % path)

                snapshot_code = file_obj.get_value("snapshot_code")
                snapshot = Snapshot.get_by_code(snapshot_code)
                
                instance = Xml.get_attribute(sub_ref, "instance")

                node_name = Xml.get_attribute(sub_ref, "node_name")
                # strip the top namespace
                # NOTE: this is highly maya specific.  Not necessary in
                # other packages
                if node_name.startswith("%s:" % namespace):
                    node_name = node_name.replace("%s:" % namespace, "")


                if not snapshot:
                    print "Warning: instance '%s' has no snapshot '%s'" % \
                        (instance, snapshot_code)
                    continue

                builder.add_ref_by_snapshot(snapshot, instance, parent=node, node_name=node_name)


        return builder.to_string()






    def preprocess_files(self, paths):
        '''Process the maya file so that all of the files exist.
        This makes the files self-consistent and usable without the
        asset management system'''

        # find all of the textures and their replacements
        xml = self._read_ref_file()
        tmp_path = xml.get_value("session/ref/@path")

        # only process maya files
        basename, ext = os.path.splitext(tmp_path)
        if ext != ".ma" and ext != ".xsi":
            return

        old_texture_paths = \
            xml.get_values("session/*/file[@type='texture']/@path")

        new_texture_paths = self.texture_names

        # find the instance to be replaced
        instance = xml.get_value("session/ref/@instance")
        # process the maya file
        path = paths[0]
        parser = None

        # parse and process the maya file
        if path.endswith(".ma"):
            parser = MayaParser(path)
            parser.read_only_flag = False

            reference_filter = MayaReferenceReplaceFilter(self.snapshot)
            if self.get_option("unknown_ref") == "ignore":
                reference_filter.set_ignore_unknown_ref(True)
            parser.add_filter(reference_filter)

            remove_namespace = self.get_option("remove_namespace")
            if remove_namespace != "false" and instance != "":
                namespace_filter = MayaRemoveNamespaceFilter(instance)
                parser.add_filter(namespace_filter)

            
        
            texture_filter = MayaTextureReplaceFilter(self.snapshot, self.texture_snapshots, old_texture_paths, new_texture_paths)
            parser.add_filter(texture_filter)

        elif path.endswith(".xsi"):
            parser = XSIParser(path)
            parser.read_only_flag = False

            texture_filter = XSITextureReplaceFilter(self.snapshot, self.texture_snapshots, old_texture_paths, new_texture_paths)
            parser.add_filter(texture_filter)


        if not parser:
            raise CheckinException('File [%s] does not end with .xsi or .ma'%path)
        parser.parse()

        return




class MayaTextureReplaceFilter(MayaParserFilter):

    def __init__(self, snapshot, texture_snapshots, old_texture_paths, new_texture_paths):
        self.parser = None
        self.cache_file_node = False

        self.snapshot = snapshot
        self.texture_snapshots = texture_snapshots
        self.old_texture_paths = old_texture_paths
        self.new_texture_paths = new_texture_paths


    def process(self, line):
        # replace any paths with the new paths of the checked in textures
        if line.find('setAttr ".ftn"') != -1 or line.find('setAttr ".imn"') != -1:
            for i in range(0, len(self.old_texture_paths) ):

                if line.find(self.old_texture_paths[i]) == -1:
                    continue

                if len(self.new_texture_paths) < i+1:
                    Environment.add_warning("missing texture paths", "%s" % self.new_texture_paths)
                    continue

                # find the relative directory between the maya file
                # and textures
                maya_dir = self.snapshot.get_lib_dir()
                if self.texture_snapshots:
                    textures_dir = self.texture_snapshots[i].get_lib_dir()
                    relative_dir = Common.relative_dir(maya_dir,textures_dir)
                else:
                    relative_dir = "."

                line = line.replace(self.old_texture_paths[i],"%s/%s" % ( relative_dir, self.new_texture_paths[i]) )
                break

            return line



class XSITextureReplaceFilter(XSIParserFilter):

    def __init__(self, snapshot, texture_snapshots, old_texture_paths, new_texture_paths):
        self.parser = None
        self.cache_file_node = False

        self.snapshot = snapshot
        self.texture_snapshots = texture_snapshots
        self.old_texture_paths = old_texture_paths
        self.new_texture_paths = new_texture_paths


    def process(self, line):

        current_node = self.parser.current_node
        if not current_node:
            return

        current_node_type = self.parser.current_node_type
        if current_node_type not in ['XSI_Image']:
            return


        # replace any paths with the new paths of the checked in textures
        for i in range(0, len(self.old_texture_paths) ):

            if line.find(self.old_texture_paths[i]) == -1:
                continue

            if len(self.new_texture_paths) < i+1:
                Environment.add_warning("missing texture paths", "%s" % self.new_texture_paths)
                continue

            # find the relative directory between the xsi file
            # and textures
            xsi_dir = self.snapshot.get_lib_dir()
            if self.texture_snapshots:
                textures_dir = self.texture_snapshots[i].get_lib_dir()
                relative_dir = Common.relative_dir(xsi_dir,textures_dir)
            else:
                relative_dir = "."

            line = line.replace(self.old_texture_paths[i],"%s/%s" % ( relative_dir, self.new_texture_paths[i]) )
            break

        return line






class MayaRemoveNamespaceFilter(MayaParserFilter):

    def __init__(self, instance):
        self.parser = None
        self.cache_file_node = False

        self.instance = instance

    def process(self, line):
        try:
            line = line.replace('"%s:' % self.instance, '"')
            line = line.replace('|%s:' % self.instance, '|')
            return line
        except Exception, e:
            raise TacticException(line + " - " + e.__str__())







class MayaGroupCheckin(MayaCheckin):
    '''checkin for groups.  This assumes all necessary files are in the
    upload dir'''

    def get_title(self):
        return "Set Checkin Command"

    def get_snapshot_type(self):
        return "set"


    def create_files(self):
        paths = []

        # look in the info file
        xml = self._read_ref_file()
        
        self._add_file_info(xml, paths)
        dir = self.get_server_dir()
        path = "%s/%s.anim" % (dir,self.sobject.get_code())
        paths.append(path)

        return paths



    def create_snapshot(self, file_objects):

        builder = SnapshotBuilder()
        if self.process:
            builder.add_root_attr('process', self.process)

        # add in the reference to the sobject
        xml = self._read_ref_file()

        for node in xml.get_nodes("session/ref"):

            # get the snapshot_code
            snapshot_code = Xml.get_attribute(node, "asset_snapshot_code")
            snapshot = Snapshot.get_by_code(snapshot_code)

            instance = Xml.get_attribute(node, "instance")

            # if snapshot is none, then the snapshot created in session
            # is no longer valid (because of undo).  In this case,
            # just ignore (this is a rare occurance anyway)
            if snapshot == None:
                raise CommandException("Snapshot '%s' on instance '%s' does not exist" % (snapshot_code,instance) )

            # get the info from the snapshot
            search_type = snapshot.get_value("search_type")
            search_id = snapshot.get_value("search_id")
            version = snapshot.get_value("version")
            context = snapshot.get_value("context")

            # If the context is "proxy" then checkin with the latest
            # NOTE: this is up for debate.  It is uncertain whether a set
            # checked in with proxies should record the proxies that were
            # in session at the time of the checkin
            # or record the latest of the "publish" at the time of the checkin.
            # It is not clear whether or not the proxy version will ever
            # be useful, unless it is used at a deeper level (ie it actaully
            # gets rendered.)  For now, just use the latest publish.
            if context == "proxy":

                proxy_snapshot = snapshot

                context = "publish"
                snapshot = Snapshot.get_latest(search_type, search_id, context)

                # if it doesn't exist, use the model
                if not snapshot:
                    snapshot = Snapshot.get_latest(search_type,search_id,"model")

                # if that doesn't exist, then use the proxy
                if snapshot == None:
                    snapshot = proxy_snapshot


                # get the update version for this snapshot
                version = snapshot.get_value("version")
                context = snapshot.get_value("context")


            # get the search type
            search_type_obj = SearchType.get(search_type)
            search = Search(search_type_obj)

            search.add_id_filter(search_id)
            sobject = search.get_sobject()

            builder.add_ref(sobject, context, version, instance)

        for i in range(0, len(file_objects)):
            filename = file_objects[i].get_file_name()
            (base, ext) = os.path.splitext(filename)
            type = "main"
            if ext == ".anim":
                type = "anim"
            elif ext == ".ma":
                type = "maya"
            elif ext == ".hip":
                type = "houdini"

            builder.add_file( file_objects[i], {"type": type} )


        return builder.to_string()





class MayaAnimCheckin(MayaGroupCheckin):
    '''checks in a maya interface (animation).  This is functionally identical
    to the group checkin except that the sobject is an instance instead
    of an asset'''
    def __init__(self, set):
        super(MayaAnimCheckin,self).__init__(set)
        
        # set some default values
        self.context = "layout"


    def get_title(self):
        return "Anim Checkin Command"
    
    def get_snapshot_type(self):
        return "anim"


    def create_files(self):
        '''look into maya session and create the files'''
        paths = []
        dir = self.get_upload_dir()

        instance_name = self.sobject.get_value("name")

        filename = File.get_filesystem_name( instance_name )
        paths.append("%s/%s.anim" % (dir, filename))

        
        return paths




class MayaAnimExportCheckin(MayaAssetCheckin):
    '''checks in a maya interface (animation).  This is functionally identical
    to the group checkin except that the sobject is an instance instead
    of an asset'''
    def __init__(self, set):
        super(MayaAnimExportCheckin,self).__init__(set)

        # set some default values
        self.context = "layout"


    def get_title(self):
        return "Anim Export Checkin Command"

    def get_snapshot_type(self):
        return "anim_export"


    def create_files(self):
        '''look into maya session and create the files'''
        paths = []

        # look in the info file
        xml = self._read_ref_file()
        self._add_file_info(xml, paths)

        return paths






class MayaSObjectCheckin(MayaGroupCheckin):
    '''checks in a maya interface (animation).  This is functionally identical
    to the group checkin except that the sobject is an instance instead
    of an asset'''
    def __init__(self, set):
        super(MayaSObjectCheckin,self).__init__(set)
        
        # set some default values
        self.context = "lighting"

    def get_title(self):
        return "Sobject Checkin Command"

    def get_snapshot_type(self):
        return "set"


    def _read_ref_file(self):
        '''read the reference file containing extra node information'''
        dir = self.get_upload_dir()
        xml = Xml()
        key = self.sobject.get_search_key()

        # make this filename good for the file system
        filename = File.get_filesystem_name(key)
        xml.read_file( "%s/%s-ref.xml" % (dir,filename) )
        return xml



    def create_files(self):
        '''layers have no files associated with them'''
        paths = []
        return paths



class MayaSetCreateCmd(Command):
    ''' Creates a set asset in the asset table '''
    def __init__(self):
        super(MayaSetCreateCmd, self).__init__()
        self.code = None
   
    def get_title(self):
        return "Set Creation"
    
    def set_set_name(self, set_name):
        self.set_name = set_name
        
    def set_cat_name(self, cat_name):
        self.cat_name = cat_name
        
    def check(self):

        if not self.cat_name:
            raise UserException("You need to select a Category first! They are defined\
                    in the Asset Libraries Tab")
        
        if re.compile('^\d+.*|.*\s+.*').match(self.set_name):
            raise UserException("Section name cannot start with a numeric or contain spaces!")
            return False

        if Asset.get_by_name(self.set_name):
            raise UserException("Section name [%s] has been taken" % self.set_name)
            return False

        if not self.cat_name:
            return False

        return True
       
    def get_asset_code(self):
        return self.code
    
    def execute(self):
      
        self.description = "Created set section"

        asset = Asset.create_with_autocode(self.set_name, self.cat_name,\
                self.description, asset_type="section")

        self.code = asset.get_code()
        self.description = "%s [%s]" % (self.description, self.code)

        return self.code, self.set_name    
    

class ShotCheckin(MayaAssetCheckin):


    def __init__(self, sobject):
        super(ShotCheckin,self).__init__(sobject)

    def check(self):
        return True


    def _read_ref_file(self):
        '''read the reference file containing extra node information'''
        dir = self.get_upload_dir()
        xml = Xml()
        filename = "shot_%s" % self.sobject.get_code()
        xml.read_file( "%s/%s-ref.xml" % (dir,filename) )
        return xml

    def get_snapshot_type(self):
        return "shot"



    def preprocess_files(self, paths):
        '''Warning: copied from maya_checkin.py'''

        path = paths[0]

        if not path.endswith(".ma"):
            return

        parser = MayaParser(path)
        parser.read_only_flag = False

        reference_filter = MayaReferenceReplaceFilter(self.snapshot)
        if self.get_option("unknown_ref") == "ignore":
            reference_filter.set_ignore_unknown_ref(True)
        parser.add_filter(reference_filter)

        # FIXME: parser doesn't even have geo cache logic yet!
        #geo_cache_filter = MayaFileGeoCacheFilter()
        #parser.add_filter(geo_cache_filter)

        parser.parse()



class MayaReferenceReplaceFilter(MayaParserFilter):

    def __init__(self, snapshot):
        self.parser = None
        self.snapshot = snapshot
        self.cache_file_node = False
        self.ignore_unknown_ref = False

        # 3 modes: environment, absolute and relative
        self.reference_mode = "environment"


    def set_ignore_unknown_ref(self, flag):
        self.ignore_unknown_ref = flag

    def process(self, line):

        # change reference paths to relative paths
        if line.startswith("file") and line.find("-rfn") != -1:
            # extract the id from the file
            # FIXME: this is a painful regular expression.  It is VERY
            # tenuous
            #p = re.compile(r'RN\d?" "(.*\.ma)"')
            p = re.compile(r'"(.*?)"')
            m = p.findall(line)
            if not m:
                raise CommandException("Can't find path in reference line: ", line )

            orig_path = m[len(m)-1]

            # get the reference file path
            ref_file_code = File.extract_file_code(orig_path)

            # file names are unique
            file_name = os.path.basename(orig_path)
            ref_file = File.get_by_filename(file_name)

            # if the ref file exists, then replace it with the one in
            # the repository
            if ref_file:

                # get the reference file path
                ref_lib_path = ref_file.get_lib_path()

                # get the ref snapshot directory and find the relative path
                # to this directory
                if self.reference_mode == "relative":
                    this_lib_dir = self.snapshot.get_lib_dir()
                    filename = os.path.basename(ref_lib_path)
                    ref_dir = os.path.dirname(ref_lib_path)
                    relative_path = Common.relative_dir(this_lib_dir, ref_dir)
                    # replace the paths
                    line = line.replace(orig_path, \
                        "%s/%s" % (relative_path,filename))

                elif self.reference_mode == "absolute":
                    pass

                # TEST: try it relatative to a base directory
                # Since there is no way to save unresolved reference paths, we
                # may not be able to use relative paths. In its place, we use
                # an envrionment variable.
                elif self.reference_mode == "environment":
                    asset_dir = Environment.get_asset_dir()

                    # check if app_base_asset_dir exists
                    app_asset_base_dir = Config.get_value("checkin", "app_asset_base_dir")

                    replacer = "$TACTIC_ASSET_DIR"
                    if app_asset_base_dir:
                        replacer = app_asset_base_dir
                    ref_env_path = ref_lib_path.replace(asset_dir, replacer)
                    line = line.replace(orig_path, ref_env_path)
                return line

            else:
                msg = "Reference file [%s] does not exist in the database" % orig_path
                if self.ignore_unknown_ref:
                    Environment.add_warning("Unknown References", msg)
                else:
                    raise CommandException(msg)




class MayaFileGeoCacheFilter(MayaParserFilter):

    def __init__(self):
        self.parser = None
        self.cache_file_node = False

    def process(self, line):
        if line.startswith('createNode cacheFile'):
            self.cache_file_node = True
            return
        elif line.startswith('createNode'):
            self.cache_file_node = False
            return

        elif self.cache_file_node and line.startswith('setAttr ".cp"'):
            p = re.compile(r'"([\w|/|:|\\]*)";$')
            groups = p.findall(line)
            if groups:
                geo_cache_paths = self.parser.geo_cache_paths
                geo_cache_dir = os.path.dirname(geo_cache_paths[0])
                    
                this_lib_dir = self.parser.snapshot.get_lib_dir()
                relative_dir = Common.relative_dir(this_lib_dir, geo_cache_dir)

                line = line.replace(groups[0], relative_dir)
                return line

        elif self.cache_file_node and line.startswith('setAttr ".cn"'):
            p = re.compile(r'"([\w|/|:|\\]*)";$')
            groups = p.findall(line)
            if groups:
                geo_cache_paths = self.parser.geo_cache_paths
                orig_geo_cache_paths = self.parser.orig_geo_cache_paths

                assert len(geo_cache_paths) == len(orig_geo_cache_paths)

                # find the index in the original
                current_geo_cache_name = groups[0]
                index = 0
                for orig_geo_cache_path in orig_geo_cache_paths:
                    orig_geo_cache_name = os.path.basename(orig_geo_cache_path)
                    orig_geo_cache_name,ext = os.path.splitext(orig_geo_cache_name)
                    if orig_geo_cache_name == current_geo_cache_name:
                        geo_cache_name = os.path.basename(geo_cache_paths[index])
                        geo_cache_name, ext = os.path.splitext(geo_cache_name)
                        line = line.replace(current_geo_cache_name, geo_cache_name)
                        return line

                    index += 1

                raise Exception("No match found for line '%s'" % line)




class TextureCheckin(Command):
    '''handles all of the texture checkins'''

    def __init__(self, parent, context="publish", paths=[], file_ranges=[], node_names=[], attrs=[], use_handoff_dir=False, md5s=[]):
        
        self.parent = parent

        # the various parameters that are needed to do a proper checkin
        self.node_names = node_names
        # filter the paths for \
        self.paths = []
        for path in paths:
            path = path.replace("\\", "/")
            self.paths.append(path)

        self.file_ranges = file_ranges
        self.attrs = attrs

        self.context = context

        self.options = {}
        # stored texture information
        self.texture_names = []
        self.textures = []
        self.texture_snapshots = []
        # TODO assert number of texture_names, nodes_names, path are the same
        self.use_handoff_dir = use_handoff_dir
        if md5s:
            assert len(md5s) == len(paths)
        else:
            # Checkin may not provide md5s, make a None list
            md5s = [ None for x in xrange(len(paths))]
        self.md5s = md5s
        super(TextureCheckin, self).__init__()


    def get_title(self):
        return "Texture Checkin"

    def check(self):
        return True

    def get_texture_paths(self):
        paths = []
        for snapshot in self.texture_snapshots:
            path = snapshot.get_env_path_by_type("main")
            paths.append(path)
    
        return paths


            
    def get_texture_md5(self):
        files = []
        for snapshot in self.texture_snapshots:
            #path = snapshot.get_lib_path_by_type("main")
            #paths.append(path)
            file_code = snapshot.get_file_code_by_type("main")
            file = File.get_by_code(file_code)
            files.append(file.get_value("md5") )
    
        return files
         
          
    def get_file_codes(self):
        '''get file codes of the main type corresponding to new texture file objects'''
        file_codes = []
        for snapshot in self.texture_snapshots:
            file_code = snapshot.get_file_code_by_type("main")
            file_codes.append(file_code)
    
        return file_codes
    
    def set_option(self, key, value):
        self.options[key] = value

    def get_option(self, key):
        value = self.options.get(key)
        if not value:
            return ""
        else:
            return value

    """
    ## NOT USED ##
    def get_md5_info(self, new_path, file_info_dict, parent_code, texture_cls):
        '''return a dict of info like is_match, file sobject, and snapshot codes'''
        info = {}
        
        # always check for file_group first so it will get reused especially
        # in cases where original file name is kept
        # NOTE: file group or single, when a reuse occurs, it is tied to the existing texture sobject
        texture_code_list = file_info_dict.get(new_path).get('texture_codes')
        new_md5 = file_info_dict.get(new_path).get('md5')

        for idx, texture_code in enumerate(texture_code_list):
            texture_sobj = texture_cls.get(texture_code, parent_code)
            if not new_md5 and File.is_file_group(new_path):
                info['is_file_group'] = True
            if not texture_sobj:
                info['is_match'] = False
                continue
            snapshots = Snapshot.get_by_sobject(texture_sobj)

            snapshot_codes = SObject.get_values(snapshots, 'code')
            info['snapshot_codes'] = snapshot_codes

            if not snapshots:
                info['is_match'] = False
                continue
            
            file_codes = []
            for snapshot in snapshots:
                file_code = snapshot.get_file_code_by_type("main")

                file_codes.append(file_code)

            files = Search.get_by_code('sthpw/file', file_codes)
            for file in files:
                last_md5 =file.get_value("md5")
                if last_md5 == new_md5:
                    info['is_match'] = True

                    info['file_sobj'] = file
                    if idx==2:
                        "FOUND IT", file.get_code(), texture_code
                    return info
                else:
                    info['is_match'] = False 
                    
        
        return info
    
    """

    ### NOT USED ###
    def get_info_from_xml(self, xml):
        '''not sure if this will be used.  It is mainly kept here to keep the
        code around'''

        # get the dependent textures and process
        if self.texture_mode == 'ignore':
            self.texture_nodes = []
        else:
            self.texture_nodes = xml.get_nodes("session/*/file[@type='texture']")

        for node in self.texture_nodes:
            self.path = Xml.get_attribute(node, "path")
            self.attr = Xml.get_attribute(node, "attr")
            self.node_name = Xml.get_attribute(node, "node")

            # ????
            self.execute()




    def execute(self):
        #-------------------------
        # handle textures

        # keep a list of textures that have already been checked in in this
        # transaction. {original_filename: file_object} 
        # This is different from the same variable in MayaAssetCheckin
        checked_textures = {}

        base_search_type = self.parent.get_base_search_type()
        if self.get_option('texture_search_type'):
            texture_search_type = self.get_option('texture_search_type')
            texture_cls = SearchType.create(texture_search_type)
        elif base_search_type == 'prod/shot':
            texture_cls = ShotTexture
        elif base_search_type == 'prod/shot_instance':
            texture_cls = ShotTexture
        else:
            texture_cls = Texture

        parent_code = self.parent.get_code()

        #file_info_dict = self.get_file_info_dict(parent_code, self.paths, self.attrs, self.node_names)

        for i, path in enumerate(self.paths):
            if not self.attrs:
                attr = None
            else:
                attr = self.attrs[i]
            node_name = self.node_names[i]
            full_node_name = ''
            # for xsi:
            if attr == "SourceFileName":
                # xsi uses the full_node_name for description
                full_node_name = node_name
                tmp = node_name.split(".")
                try:
                    front_part = tmp[2:4]
                    front_part.append(tmp[-1]) 
                    
                    node_name = '_'.join(front_part)
                except IndexError:
                    raise TacticException('Expecting a node name in the form of'\
                        'node_name.mesh_name.Material.shading.file_node. Received [%s]' %node_name)
                # clear the attr to shorten the texture code
                #attr = ''
            else:
                # if there is a namespace, the split and take the last part
                # (for maya)
                node_name = node_name.split(":")[-1]

                # split this and take the last one in this path
                # (for Houdini paths)
                node_name = node_name.split("/")[-1]

            # shorten the texture code for ftn attributes
            if not attr or attr in ["ftn" , "SourceFileName"]:
                texture_code = "%s-%s" % (parent_code, node_name)
            else:
                texture_code = "%s-%s-%s" % (parent_code, node_name, attr)
            
            # remove subcontext /
            texture_code = texture_code.replace("/", "-")
            
            if self.use_handoff_dir:
                
                from pyasm.web import WebContainer 
                web = WebContainer.get_web()
                temp_path = path.replace('\\','/')
                dir = os.path.dirname(temp_path)
                
                ticket = dir.split('/')[-1]
                server_dir = web.get_server_handoff_dir(ticket)
            else:
                server_dir = FileCheckin.get_upload_dir()

            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )
            (texture_basename, ext) = os.path.splitext( os.path.basename(filename) )
            # find the local path of the uploaded file 
            local_path = "%s/%s" % (server_dir,filename)

            # remapped to already checked in file for the same texture code so that it can be reused
            # it's unlikely it will be reused since we scope by texture code also
            is_remapped = False
            texture = texture_cls.get(texture_code, parent_code)
            
            remapped_file_obj = checked_textures.get(local_path.lower())
            info = {}
            if remapped_file_obj:
                is_remapped = True
            
            is_old_file = False
            if is_remapped:
                is_old_file = True
                info['file_sobj'] = remapped_file_obj

            # look up the file name in the database, so no duplicate checkin
            if is_old_file:
                file_object = info.get('file_sobj')
                snapshot_code = file_object.get_value("snapshot_code")
                if snapshot_code == "":
                    raise CheckinException("file code '%s' does not have a snapshot_code" % file_code)


                texture_snapshot = Snapshot.get_by_code(snapshot_code)
                if not texture_snapshot:
                    raise CheckinException("Snapshot code '%s' does not exist in the database" % snapshot_code)


                texture = texture_snapshot.get_sobject()

                texture_name = file_object.get_full_file_name()

                # store the necessary info about this texture
                self.texture_names.append(texture_name)
                self.textures.append(texture)
                self.texture_snapshots.append(texture_snapshot)

                continue


           
            # if no corresponding texture object is found, then create one
            if not texture:
                category = "texture"
                # applicable for xsi
                if full_node_name:
                    node_name = full_node_name
                description = '%s %s' % ( texture_basename, node_name )

                texture = texture_cls.create(self.parent, texture_code, 
                    category, description, sobject_context=self.context )


            
            file_range = self.file_ranges[i]
            if file_range:
                file_range = FileRange.get(file_range)
           
            # generate icon for now
            web_path, icon_path = self.process_icon(local_path, file_range)
            # checkin all of the texture maps
            if web_path:
                file_paths = [local_path, web_path, icon_path]
                file_types = ['main','web','icon']
                md5s = [self.md5s[i], None, None]
            else:
                file_paths = [local_path]
                file_types = ['main']
                md5s = [self.md5s[i]]
            """
            # if skipping icon generation completely
            file_paths = [local_path]
            file_types = ['main']
            md5s = [self.md5s[i]]
            """

            if file_range:
                # checkin this file group into the texture
                checkin = FileGroupCheckin(texture, file_paths, file_types, \
                    file_range, context='publish', snapshot_type="texture_sequence", \
                    description="Texture File Group")

            else:
                # checkin this file into the texture
                checkin = FileCheckin(texture, file_paths, file_types, \
                    snapshot_type="texture", md5s=md5s)
            checkin.execute()

            

            texture_snapshot = checkin.get_snapshot()
            texture_file_objs = checkin.get_file_objects()
            texture_xml = texture_snapshot.get_xml_value("snapshot")


            # update both the texture and the snapshot (TODO: the fisrt part seems unnecessary)
            texture_snapshot.set_value("snapshot", texture_xml.to_string() )
            texture_snapshot.commit(triggers=False)
            texture.set_value("snapshot", texture_xml.to_string() )
            texture.commit(triggers=False)

            # get the main file
            file_name = texture_snapshot.get_name_by_type("main")
            file_code = texture_snapshot.get_file_code_by_type("main")

            main_file_obj = self._get_file_object(file_code, texture_file_objs)
            if not main_file_obj:
                raise CheckinException('Main file object not found for code [%s]'%file_code)
            # store the file object here to minimize db activity
            checked_textures[local_path.lower()] = main_file_obj

            # store the texture snapshots
            self.texture_names.append(file_name)
            self.textures.append(texture)
            self.texture_snapshots.append(texture_snapshot)

            
        self.description = "Checked in textures to [%s]" % parent_code
        

    def _get_file_object(self, file_code, file_objects):
        '''get the proper file object matching the file_code'''
        for file_obj in file_objects:
            if file_code == file_obj.get_code():
                return file_obj

        return None


    def process_icon(self, local_path, file_range=None):
        '''process icon and return web_path, icon_path as tuple'''
        # take the first one for file range
        if file_range:
            expanded = FileGroup.expand_paths(local_path, file_range)
            local_path = expanded[0] 
        icon_creator = IconCreator(local_path)
        icon_creator.set_texture_mode()
        icon_creator.create_icons()

        web_path = icon_creator.get_web_path()
        icon_path = icon_creator.get_icon_path()
        return web_path, icon_path

    """
    def get_file_info_dict(self, parent_code, paths, attrs, node_names):
        '''get a dictionary of file_path : texture_code_list, md5'''
        info = {}
        for i, path in enumerate(paths):
            if not attrs:
                attr = None
            else:
                attr = attrs[i]
            node_name = node_names[i]
            full_node_name = ''
            # for xsi:
            if attr == "SourceFileName":
                # xsi uses the full_node_name for description
                full_node_name = node_name
                tmp = node_name.split(".")
                try:
                    front_part = tmp[2:4]
                    front_part.append(tmp[-1]) 
                    
                    node_name = '_'.join(front_part)
                except IndexError:
                    raise TacticException('Expecting a node name in the form of'\
                        'node_name.mesh_name.Material.shading.file_node. Received [%s]' %node_name)
                # clear the attr to shorten the texture code
                attr = ''
            else:
                # if there is a namespace, the split and take the last part
                # (for maya)
                node_name = node_name.split(":")[-1]

                # split this and take the last one in this path
                # (for Houdini paths)
                node_name = node_name.split("/")[-1]

            # shorten the texture code for ftn attributes
            if not attr or attr == "ftn":
                texture_code = "%s-%s" % (parent_code, node_name)
            else:
                texture_code = "%s-%s-%s" % (parent_code, node_name, attr)
            
            # remove subcontext /
            texture_code = texture_code.replace("/", "-")

            # and make it filesystem friendly
            filename = os.path.basename(path)
            filename = File.get_filesystem_name( filename )

            if self.use_handoff_dir:
                from pyasm.web import WebContainer 
                web = WebContainer.get_web()
                temp_path = path.replace('\\','/')
                dir = os.path.dirname(temp_path)
                
                ticket = dir.split('/')[-1]
                server_dir = web.get_server_handoff_dir(ticket)
            else:
                server_dir = FileCheckin.get_upload_dir()
            local_path = "%s/%s" % (server_dir,filename)
            sub_info = info.get(local_path)
            new_md5 = File.get_md5(local_path)
            # texture codes part is not used any more
            if not sub_info:
                info[local_path] = {'texture_codes': [texture_code], 'md5': new_md5}
            else:
                sub_info.get('texture_codes').append(texture_code)
        return info
    """
