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

import cStringIO, os, re, shutil, sys, urllib
from xml.dom.minidom import parseString, parse
from xml.dom.minidom import getDOMImplementation

from common import *
#import tactic_load


from pyasm.application.common import *


class Checkin(object):
    # class that creates the necessary files for checkin and uploads them
    # to a server

    def __init__(self):

        self.env = AppEnvironment.get()

        self.info = TacticInfo.get()
        self.impl = self.info.get_app_implementation()

        self.app = self.env.get_app()
        self.app.set_namespace()

        self.texture_paths = []
        self.texture_nodes = []
        self.texture_attrs = []
        self.texture_file_codes = []
        self.texture_md5_list = []

        self.geo_info = []

        # DEPRECATED
        self.houdini_refs = []

        self.generated_paths = []
        self.upload_paths = []

        self.options = {}
        self.handlers = {}
        self.handoff_dir = ''
       
        
        #self.clean_up()

    def clean_up(self):
        ticket = self.env.get_ticket()
        project_code = self.env.get_project_code()

        # clear the upload dir first
        from pyasm.application.common.interpreter.tactic_client_lib import * 
        client_server = TacticServerStub(setup=False)
        server_name = self.env.get_server()
        client_server.set_server(server_name)
        client_server.set_project(project_code)
        client_server.set_ticket(ticket)
        client_server.clear_upload_dir()

    def set_options(self, options_str):
        exprs = options_str.split("|")
        for expr in exprs:
            name, value = expr.split("=")
            self.options[name] = value
        
    def set_option(self, name, value):
        self.options[name] = value

    def get_option(self, name):
        if self.options.has_key(name):
            return self.options[name]
        else:
            return ""

    def set_handlers(self, handlers_str):
        exprs = handlers_str.split("|")
        for expr in exprs:
            name, value = expr.split("=")
            self.handlers[name] = value

    def get_handler(self, name):
        if self.handlers.has_key(name):
            return self.handlers[name]
        else:
            return ""



    def add_path(self, path):
        self.generated_paths.append(path)

    def upload_files(self):
        upload_paths = Common.get_unique_list(self.generated_paths)
        for path in upload_paths:
            self.env.upload(path)

        for path in self.upload_paths:
            self.env.upload(path)
            # remove upload files
            #os.unlink(path)

        

    def handoff_files(self):
        dir = self.handoff_dir
        for path in self.generated_paths:
            file_name = os.path.basename(path)
            file_name = Common.get_filesystem_name(file_name)
            new_file_path = '%s/%s' %(dir, file_name)
            print "copying to: ", new_file_path
            shutil.copy(path, new_file_path)

        for path in self.upload_paths:
            self.env.upload(path)

    def dump_nodes(self, asset_code, node_list):
        ''' exports non-tactic nodes'''
        for node_name in node_list:
            self._check_existence(node_name)

        
        path = self._export_node(node_list,  preserve_ref=False)
        # dump out the reference file
        return self.dump_file(asset_code, path, append=True)
      

    def dump_node(self, node_name, instance=None):
        '''exports a node and everything under it'''
        namespace = self._check_existence(node_name)
        
        # NOTE: Even an asset does not really have an instance, we must set
        # it using the asset_name in checkin_asset, since the server checkin 
        # callback uses that to locate the description and ref.xml file
        
        if not instance:
            instance = namespace

        # create the node data attribute if it doesn't exist
        node_data = self.app.get_node_data(node_name)
        node_data.create()
       
        use_filename = True
        if  self.get_option('use_filename')=='false':
            use_filename = False
        self._export_node(node_name, use_filename=use_filename)

        # dump out the reference file
        return self.dump_ref(instance, [node_name])


    def _check_existence(self, node_name):
        # use naming to extract info
        naming = self.app.get_node_naming(node_name)
        namespace = naming.get_namespace()
        asset_code = naming.get_asset_code()

        # check whether node is in session
        is_present = self.app.node_exists(node_name)
        if not is_present:
            msg = "Error: Node '%s' is not in the session" % node_name
            raise TacticException(msg)
            
        return namespace


    def _export_node(self, node_name, preserve_ref=True, use_filename=True):

        # NOTE: node_name can be a list ... should make this clearer

        file_type = self.get_option("file_type")
        context = self.get_option('context')
        instance = self.get_option('instance')
        filename = ''


        export_method = self.get_option("export_method")
        handler_cls = self.get_handler("checkin/create")
        if export_method == "Pipeline" and handler_cls:
            handler = AppEnvironment.create_from_class_path(handler_cls)
            input = {'node_name': node_name}
            handler.set_input(input)
            handler.execute()
            path = handler.get_output_value("path")
        elif export_method == "Save":
            # get the last saved file name and use it by default
            old_path = self.app.get_file_path()
            if use_filename and old_path:
                filename = os.path.basename(old_path)
                path = self.app.save("%s/%s" % (self.info.get_save_dir(), filename) )
            else:
                path = self.app.save_node(node_name, self.env.get_tmpdir(), type=file_type )
        else:
            old_path = self.app.get_file_path()
            if use_filename:
                filename = os.path.basename(old_path)
            
            path = self.app.export_node(node_name, context, self.env.get_tmpdir(), \
                type=file_type, preserve_ref=preserve_ref, filename=filename,\
                instance=instance)

        # now that the file is exported, allow an handler to process the file
        handler_cls = self.get_handler("checkin/process")
        if handler_cls:
            handler = AppEnvironment.create_from_class_path(handler_cls)
            handler.set_input({"path" : path})
            handler.execute()


        self.generated_paths.append(path)


        # handle the dependencies in the old manner
        if self.app.APPNAME == "maya":
            md5_list = []
            dependent_paths = self.handle_dependencies(path, node_name)
            for dependent_path in dependent_paths:
                self.generated_paths.append(dependent_path)
                md5_list.append(Common.get_md5(dependent_path))
            self.texture_md5_list = md5_list 
        return path



    def handle_dependencies(self, path="", node_name=None):
        '''record all the dependencies for a given session/app file'''

        dependent_paths = []
        if self.get_option('handle_texture_dependency')=='false':
            return dependent_paths

        # now that the file is exported, allow an handler to process the file
        handler_cls = self.get_handler("checkin/dependency")
        if handler_cls:
            handler = AppEnvironment.create_from_class_path(handler_cls)
            input = {"path":path, "node_name": node_name}
            handler.set_input(input)
            handler.execute()



        # find all of the textures in the extracted file
        if self.app.APPNAME == "maya":
            
            if path.endswith(".ma"):
                # handle the textures
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_path(path)
                # remember all of the geo paths
                self.geo_info = self.impl.get_geo_from_session(node_name)
                for info in self.geo_info:
                    geo_path = info[1]
                    dependent_paths.append(geo_path)
            else:
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_session(node_name)

        elif self.app.APPNAME == "houdini":
            self.texture_nodes, self.texture_paths, self.texture_attrs = \
                self.app.get_textures_from_session(node_name)

        elif self.app.APPNAME == "xsi":
            if path.endswith(".xsi"):
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.impl.get_textures_from_path(path)
            elif path.endswith(".emdl"):
                self.texture_nodes, self.texture_paths, self.texture_attrs = \
                    self.app.get_textures_from_session(node_name)


        # add all of the texture paths
        for texture_path in self.texture_paths:
            # FIXME: all of the texture paths are uploaded!!!, even if
            # they are identical
            dependent_paths.append(texture_path)

        return dependent_paths



    def read_file(self, file_path):
        try:
            file_path = file_path.replace("\\", "/")
            doc = parse(file_path)
            return doc
        except Exception, e:
            print "Error in xml file: ", file_path
            raise Exception(e)

       
    def dump_file(self, instance, ref_path, append=False):
        '''dumps a file node in the ...ref.xml'''
        # get all of the selected nodes
        # This matches File.get_filesystem_name(instance)
        filename = instance.replace("/", "__")
        filename = filename.replace("|", "__")
        filename = filename.replace(":", "__")
        filename = filename.replace("?", "__")
        filename = filename.replace("=", "__")
        path = "%s/%s-ref.xml" % (self.env.get_tmpdir(), filename)
        # dump info to send to the server
        impl = getDOMImplementation()
        doc = None
        if append:
            doc = self.read_file(path)
        else:
            doc = impl.createDocument(None, "session", None)
        root = doc.documentElement

        
        # create the top node reference
        top_node = doc.createElement("file")

        # add in a path
        top_node.setAttribute("path", ref_path)
        root.appendChild(top_node)

        
        file = open(path, 'w')
        file.write( doc.toprettyxml() )
        file.close()

        # return the xml file path
        return path


    def dump_ref(self, instance, node_names, append=False):
        '''dumps all of the references in the group'''
        # get all of the selected nodes
        # This matches File.get_search_key(key)
        file_name = Common.get_filesystem_name(instance)
        path = "%s/%s-ref.xml" % (self.env.get_tmpdir(), file_name)

        # dump info to send to the server
        impl = getDOMImplementation()
        doc = None
        if append:
            doc = self.read_file(path)
        else:
            doc = impl.createDocument(None, "session", None)
        root = doc.documentElement

        for node_name in node_names:
            
            # create the top node reference
            top_node = doc.createElement("ref")

            if node_name:

                node_naming = self.app.get_node_naming(node_name)
                instance = node_naming.get_instance()

                asset_snapshot_code = self.impl.get_snapshot_code(node_name,"asset")
                anim_snapshot_code = self.impl.get_snapshot_code(node_name,"anim")

                # add these assertions because if these are None, pretty print
                # fails and it is difficult to find out where the error occured
                assert asset_snapshot_code != None
                assert anim_snapshot_code != None
                assert instance != None
                assert node_name != None
                top_node.setAttribute("asset_snapshot_code", asset_snapshot_code)
                top_node.setAttribute("anim_snapshot_code", anim_snapshot_code)
                top_node.setAttribute("instance", instance)
                top_node.setAttribute("node_name", node_name)

            # add in a path
            if self.generated_paths:
                assert self.generated_paths[0] != None
                top_node.setAttribute("path", self.generated_paths[0])
                top_node.setAttribute("handoff_dir", self.handoff_dir)
                # only generate for xsi as maya file may change on parsing
                if self.app.name == 'xsi':
                    top_node_md5 = Common.get_md5(self.generated_paths[0])
                    top_node.setAttribute("md5", top_node_md5)
            # add this top node
            root.appendChild(top_node)


            # get all of the tactic sub references.
            sub_refs = self.app.get_reference_nodes(node_name)
            for sub_ref in sub_refs:

                node_naming2 = self.app.get_node_naming(sub_ref)
                instance2 = node_naming2.get_instance()

                sub_path = self.app.get_reference_path(sub_ref)
                # remove maya's weird {#} at the end
                sub_path = re.sub('{\d+}','', sub_path)
                sub_asset_snapshot_code = self.impl.get_snapshot_code(sub_ref,"asset")
                sub_anim_snapshot_code = self.impl.get_snapshot_code(sub_ref,"anim")
                sub_node = doc.createElement("ref")
                sub_node.setAttribute("asset_snapshot_code", sub_asset_snapshot_code)
                sub_node.setAttribute("anim_snapshot_code", sub_anim_snapshot_code)
                sub_node.setAttribute("instance", instance2)
                sub_node.setAttribute("path", sub_path)

                sub_node.setAttribute("node_name", sub_ref)
                top_node.appendChild(sub_node)


            # add in all of the textures
            texture_nodes = self.texture_nodes
            texture_paths = self.texture_paths
            texture_attrs = self.texture_attrs
            texture_file_codes = self.texture_file_codes
            texture_md5_list = self.texture_md5_list

            use_namespace = self.get_option('use_namespace')

            for i in range(0, len(texture_paths)):
                file_node = doc.createElement("file")
                file_node.setAttribute("type", "texture")

                # eliminate the namespace
                if use_namespace:
                    texture_node = texture_nodes[i]
                elif texture_nodes[i].find(":") != -1:
                    parts = texture_nodes[i].split(":")
                    texture_node = parts[-1]
                else:
                    texture_node = texture_nodes[i]
                    
                file_node.setAttribute("node", texture_node)
                file_node.setAttribute("attr", texture_attrs[i])

                file_node.setAttribute("path", texture_paths[i])
                try:
                    texture_file_code = texture_file_codes[i]
                except IndexError:
                    texture_file_code = ''

                
                file_node.setAttribute("code", texture_file_code)
                # md5_list could be empty
                if texture_md5_list:
                    md5 = texture_md5_list[i]
                    if md5:
                        file_node.setAttribute("md5", md5) 

                top_node.appendChild(file_node)


            # add in the geo caches
            for info in self.geo_info:
                geo_node, geo_path = info
                file_node = doc.createElement("file")
                file_node.setAttribute("type", "geo")
                file_node.setAttribute("path", geo_path)
                file_node.setAttribute("node", geo_node)
                top_node.appendChild(file_node)



            # record the layers
            if self.app.APPNAME == "maya":
                layers = self.app.get_all_layers()
                for layer in layers:
                    file_node = doc.createElement("layer")
                    file_node.setAttribute("name", layer)
                    top_node.appendChild(file_node)



            """
            # Houdini references
            # FIXME: I don't think this is necessary anymore.
            for info in self.houdini_refs:
                houdini_node = info[0]
                houdini_attr = info[1]
                houdini_path = info[2]

                file_node = doc.createElement("file")
                file_node.setAttribute("type", "texture")
                file_node.setAttribute("path", houdini_path)

                # TODO: this is the full node with the instance name.  This
                # should not have this hardcoded
                file_node.setAttribute("node", houdini_node)
                file_node.setAttribute("attr", houdini_attr)

                top_node.appendChild(file_node)
            """
                


        file = open(path, 'w')
        file.write( doc.toprettyxml(encoding='utf-8'))
        file.close()

        #self.generated_paths.append(path)
        # only this ref xml is uploaded
        self.upload_paths.append(path)
        return path




    def dump_group(self, group_name, group_asset_code):

        nodes = []
        if self.get_option("selected") == "false":
            '''nodes = self.app.get_top_nodes()
            if not nodes:
                msg = "No assets in session"
                raise TacticException(msg)
            '''
            nodes = self.app.get_nodes_in_set(group_name)
        
        else:
            # get all of the selected nodes
            nodes = self.app.get_selected_top_nodes()
            if not nodes:
                msg = "No assets selected"
                raise TacticException(msg)
        
        non_tactic_nodes = []
        tactic_nodes = []
        for node_name in nodes:
            # dump the arbitrary nodes included in a set if any
            if not self.app.is_tactic_node(node_name):
                non_tactic_nodes.append(node_name)
            else:
                tactic_nodes.append(node_name)
        
        # dump out the reference file
        self.dump_ref(group_asset_code, tactic_nodes)
        
        # dump out the animation for each interface
        first = True
        path = None
       

        for node_name in tactic_nodes:
            path = self._dump_interface(group_asset_code, node_name, first)
            first = False

        if non_tactic_nodes:
            self.dump_nodes(group_asset_code, non_tactic_nodes)

        return path



    def _dump_interface(self, basename, node_name, create=True):
        '''dump the animation: use animImport, but tag it with comments
        so that multiple imports can be stored in the same file and 
        accessed non-linearly'''

        node_naming = self.app.get_node_naming(node_name)
        instance = node_naming.get_instance()

        # dump the animation file
        node_anim_path = self.impl.dump_interface(node_name)

       
        #base, ext = os.path.splitext(node_anim_path)
        ext = ".anim"

        out_anim_file = "%s/%s%s" % (self.env.get_tmpdir(),basename,ext)
        src_files = {}
        src_files[node_anim_path] = 'ANIM'

        if self.app.APPNAME == "maya":
            # dump the static file for Maya
            node_static_path = self.impl.dump_interface(node_name, mode='static')
            src_files[node_static_path] = 'STATIC'
            
        # copy into the master file
        for src_file, src_file_type in src_files.items():
            file = open(src_file, "r")
            if create == True:
                file2 = open(out_anim_file, "w")
                create = False
                # remember the created file
                self.upload_paths.append(out_anim_file)
                
            else:
                file2 = open(out_anim_file, "a")

            if self.app.APPNAME == "houdini":
                file2.write("#------------------\n")
                file2.write("#START_%s=%s\n" % (src_file_type, instance))
                file2.write("#------------------\n")
            else:
                file2.write("//------------------\n")
                file2.write("//START_%s=%s\n" % (src_file_type, instance))
                file2.write("//------------------\n")


            file2.write("\n")
            for line in file.readlines():
                # comment out the opadd for houdini
                if self.app.APPNAME == "houdini" and line.startswith("opadd -n"):
                    line = "#%s" % line
                file2.write(line)

            if self.app.APPNAME == "houdini":
                file2.write("#------------------\n")
                file2.write("#END_%s=%s\n" % (src_file_type, instance))
                file2.write("#------------------\n\n")
            else:
                file2.write("//------------------\n")
                file2.write("//END_%s=%s\n" % (src_file_type, instance))
                file2.write("//------------------\n\n")


        file2.close()
        file.close


        return out_anim_file


    def dump_anim(self, node_name):
        '''dump out the animation of a node'''

        node_naming = self.app.get_node_naming(node_name)
        instance_name = node_naming.get_instance()

        # dump out the reference file
        self.dump_ref(instance_name, [node_name])

        # dump out the animation for each interface
        out_file = self._dump_interface(instance_name, node_name, True)
        return out_file





# API commands
def checkin_asset_old(namespace, asset_code, instance, options=None, handlers=None):
    env = AppEnvironment.get()
    ticket = env.get_ticket()
    
    checkin = Checkin()
    naming = checkin.app.get_node_naming()
    naming.set_namespace(namespace)
    naming.set_asset_code(asset_code)
    node_name = naming.get_node_name()
    if options:
        checkin.set_options(options)
        if checkin.get_option('clean_up') == 'true':
            checkin.clean_up()
    if handlers:
        checkin.set_handlers(handlers)
    
    
    export_method = checkin.get_option("export_method")
    handler_cls = checkin.get_handler("checkin/pre_export")
    if handler_cls:
        handler = AppEnvironment.create_from_class_path(handler_cls)
        input = {'node_name': node_name}
        handler.set_input(input)
        handler.execute() 

    current_path = checkin.app.get_file_path()
    checkin.handoff_dir = get_handoff_dir(ticket, env) 

    checkin.dump_node(node_name, instance)

    # rename back to the original path
    checkin.app.rename(current_path)

    use_handoff_dir = checkin.get_option("use_handoff_dir") == 'true'
    if use_handoff_dir:
        checkin.handoff_files()
    else:
        checkin.upload_files()


#def checkin_binary_asset(namespace, asset, instance, options=None):
def checkin_asset(namespace, asset_code, instance, options=None, handlers=None):
    '''try checkin in an asset with a binary file format ... this checkin
    mode requires the application for inspection of the dependent assets'''

    # 1) dump out the ref and checkin all files with placeholder main file
    # 2) get all the checked in filenames back
    # 3) copy all the dependent paths to the local repo with the new names (if they don't already exist)
    # 4) change all of the paths in session
    # 5) dump out the node with the new paths
    # 6) replace the main file in the repo
    # 7) switch to paths in local repo
    
    # HACK: maya only supports ascii files because of textures
    # get some info
    env = AppEnvironment.get()
    app = env.get_app()
    
    if app.APPNAME == "maya":
        return checkin_asset_old(namespace, asset_code, instance, options, handlers)

    ticket = env.get_ticket()
    server = env.get_xmlrpc_server()
    project_code = env.get_project_code()
    
    checkin = Checkin()

    naming = checkin.app.get_node_naming()
    naming.set_namespace(namespace)
    naming.set_asset_code(asset_code)
    node_name = naming.get_node_name()

    if options:
        checkin.set_options(options)
        if checkin.get_option('clean_up') == 'true':
            checkin.clean_up()
    if handlers:
        checkin.set_handlers(handlers)

    
    
    # replace local references with lib_path in case loaded thru http mode
    swap_ref_path(ticket, env, checkin.app)
        
    # find the dependent files and upload them
    file_type = checkin.get_option("file_type")
    use_handoff_dir = checkin.get_option("use_handoff_dir") == 'true'

    mode = checkin.get_option("texture_match")
    dependency = Dependency(node_name, file_type)
    handle_texture = checkin.get_option('handle_texture_dependency') =='true'
    # check if we want to handle textures
    if handle_texture:
        dependency.execute()
    
    filtered_texture_paths, filtered_texture_nodes, filtered_texture_attrs, filtered_md5s = [], [], [], []
    repo_texture_paths, repo_texture_nodes, repo_texture_attrs, repo_file_ranges, repo_file_codes = [], [], [], [], []

    # these original attrs are used at the end, do not alter them
    texture_paths, texture_nodes, texture_attrs = dependency.get_texture_info()
    # check for existence:
    progress = checkin.impl.start_progress('Verifications...', True, 1 + len(texture_paths))
    if checkin.app.is_reference(node_name):
        checkin.info.report_error(' [%s] is a reference ' %node_name)
    else:
        progress.increment()

    
    for path in texture_paths:
        progress.increment()
        # skip checking for file group
        if checkin.impl.is_file_group(path):
            continue
        if not os.path.exists(path):
            checkin.info.report_error('Path [%s] does not exist' %path)
            progress.stop()
            return
    progress.stop() 
   
    """
    use_handoff_dir = False
    if app.name == 'xsi':
        use_handoff_dir = True
    """
    md5_list = []
    if handle_texture:
        if mode == 'md5':
            title = 'Analyzing file md5...'
        else:
            title = 'Analyzing file name...'
        progress = checkin.impl.start_progress(title, True, len(texture_paths))
        # need md5 for both modes
        for tex_path in texture_paths:
            md5_list.append(Common.get_md5(tex_path))
            progress.increment() 
    checkin.texture_md5_list = md5_list 

    if use_handoff_dir:
        
        from pyasm.application.common.interpreter.tactic_client_lib import * 
        client_server = TacticServerStub(setup=False)
        project_code = env.get_project_code()
        server_name = env.get_server()
        client_server.set_server(server_name)
        client_server.set_project(project_code)
        client_server.set_ticket(ticket)
        try:
            client_server.start("Transferring Textures")
            dir = client_server.get_handoff_dir()
            checkin.handoff_dir = dir
            # check for already checked in texture and determine what to copy over
            #texture_codes = [checkin.impl.get_texture_code(asset_code, x) for x in texture_nodes]
            
                #md5_list = [ None for x in xrange(len(texture_paths))]
            
            # use forward path to avoid auto escaping
            
            forward_texture_paths = [ x.replace('\\','/') for x in texture_paths]
           
            file_group_dict = get_file_group_dict(checkin, forward_texture_paths)
            md5_info = client_server.get_md5_info(md5_list, forward_texture_paths, asset_code, 'Texture', file_group_dict, project_code, mode)
            for idx, texture_path in enumerate(texture_paths):
                #texture_code = texture_codes[idx]

                # key contains tex code and path
                key = forward_texture_paths[idx]
                # the path has to correspond to the corresponding texture code list
                sub_info = md5_info.get(key)
                is_match = False
                if sub_info:
                    is_match = sub_info.get('is_match')

                if not is_match:
                    filtered_texture_paths.append(texture_path)
                    filtered_texture_nodes.append(texture_nodes[idx])
                    filtered_texture_attrs.append(texture_attrs[idx])
                    filtered_md5s.append(md5_list[idx])
                else:
                    repo_path = md5_info.get(key).get('repo_path')

                    repo_file_code = md5_info.get(key).get('repo_file_code')
                    repo_texture_paths.append(repo_path)
                    repo_file_codes.append(repo_file_code)
                    repo_texture_nodes.append(texture_nodes[idx])
                    repo_texture_attrs.append(texture_attrs[idx])

                    # should check the original path here 
                    if checkin.impl.is_file_group(texture_path):
                        file_range = md5_info.get(key).get('repo_file_range')
                        repo_file_ranges.append(file_range)
                    else:
                        repo_file_ranges.append(None)   

            progress.stop()       
            
            handoff_texture_paths, file_ranges = copy_file(checkin, filtered_texture_paths, dir)
            app.message("[%s] Textures to be checked in: " %len(filtered_texture_paths))
            for idx, path in enumerate(filtered_texture_paths):
                app.message("%s. (%s)-(%s)" % ( (idx+1), path, filtered_texture_nodes[idx]))
        except:
            client_server.abort()
            raise
        else:
            # do not finish() here as the CheckinCbk is run right after
            if checkin.get_option('use_batch')=='true':
                pass
            else:
                client_server.finish()
    else:
        progress = checkin.impl.start_progress('Texture Uploading', True, len(texture_paths))
        for path in texture_paths:
            progress.increment()
            env.upload(path)
        progress.stop()
        # there is no handoff here really
        handoff_texture_paths = texture_paths
        filtered_texture_nodes = texture_nodes
        filtered_texture_attrs = texture_attrs
        file_ranges = [None for x in xrange(len(texture_paths))]
   
    # just check in external references, which are checked in separately
    new_paths, file_code_list = server.checkin_textures(ticket, project_code, asset_code, handoff_texture_paths, file_ranges, filtered_texture_nodes, filtered_texture_attrs, use_handoff_dir, filtered_md5s)


    # combine the list together 
    checkin.texture_paths = new_paths + repo_texture_paths
    checkin.texture_nodes = filtered_texture_nodes + repo_texture_nodes
    checkin.texture_attrs = filtered_texture_attrs + repo_texture_attrs
    checkin.texture_file_codes = file_code_list + repo_file_codes
    whole_file_ranges = file_ranges + repo_file_ranges

    # remap the paths according to app
    for i, texture_node in enumerate(checkin.texture_nodes):
        texture_attr = checkin.texture_attrs[i]
        new_path = checkin.texture_paths[i]
        file_range = whole_file_ranges[i]
        if Common.is_file_group(new_path):
            new_path = checkin.impl.get_app_file_group_path(new_path, file_range)
        try:
            app.set_attr(texture_node, texture_attr, new_path, "string")
        except AppException, e:
            checkin.info.report_warning('Failed Attribute Setting', str(e))
            continue

    # provide callback for users to do whatever they wish to the maya file
    ClientTrigger.call("pre_asset_export")
 
    # dump node with all of the dependencies
    try:
        current_path = checkin.app.get_file_path()
        app_path = checkin.dump_node(node_name, instance)
        if use_handoff_dir:
            checkin.handoff_files()
        else:
            checkin.upload_files()
        #Trigger.call("postdump")

    finally:
        # set this back even if something goes wrong
        checkin.app.rename(current_path)

        # move the attributes back to what they were before the dump
        # TODO: this should be an option
        for i, texture_node in enumerate(texture_nodes):
            texture_attr = texture_attrs[i]
            old_path = texture_paths[i]
            try:
                app.set_attr(texture_node, texture_attr, old_path, "string")
            except AppException, e:
                checkin.info.report_warning('Failed Attribute Setting', str(e))
                continue

def swap_ref_path(ticket, env, app):
    if app.name != 'xsi':
        return
    ref_nodes = app.get_reference_nodes()
    for ref_node in ref_nodes:
        node_data= app.get_node_data(ref_node)
        snap_code = node_data.get_attr('asset_snapshot', 'code')
        from pyasm.application.common.interpreter.tactic_client_lib import * 
        client_server = TacticServerStub(setup=False)
        client_server.set_ticket(ticket)
        project = env.get_project_code()
        server_name = env.get_server()
        client_server.set_server(server_name)
        client_server.set_project(project)
        lib_path = ''
        client_server.start("Retrieving Lib Path")
        try:
            if not snap_code:
                continue
            lib_path = client_server.get_path_from_snapshot(snap_code, file_type=app.APPNAME)
        except:
            client_server.abort()
            raise
        else:
            client_server.finish()
            app.message("Replacing path for [" + ref_node + "] with " + lib_path)
            app.update_reference(ref_node, lib_path, top_reference=True)

def get_file_group_dict(checkin, file_paths):
    '''get a dictionary of <original file path>: tactic_file_path, file_range. It also determines an implicitly
       stated range for certain 3d apps'''
    file_range = ''
    file_group_dict = {} 
       
    flex_range = checkin.app.has_flex_range()
    for file_path in file_paths:
        file_range = ''
        if checkin.impl.is_file_group(file_path):
            file_range = checkin.impl.get_file_range(file_path)
            #file_ranges.append(file_range)
            tactic_file_path = checkin.impl.get_tactic_file_group_path(file_path)
            file_group = Common.expand_paths(tactic_file_path, file_range)

            new_file_range = Common.get_file_range(file_range)
            is_start_set = False
            start_frame = new_file_range[0]
            end_frame = new_file_range[1]

            for idx, path in enumerate(file_group):
                if flex_range:
                    # determine the implicit flexible range
                    if os.path.exists(path):
                        pat = re.compile('.*\.(\d+)\..*')
                        m = pat.match(path)
                        num = int(m.groups()[0])
                        if not is_start_set and num >= new_file_range[0]:
                            start_frame = num
                            is_start_set = True
                        end_frame = num
    
                    else:
                        continue
                
            if flex_range:
                file_range = '%s-%s/%s'%(start_frame, end_frame, new_file_range[2])
                    
            file_group_dict[file_path] = tactic_file_path, file_range
        
        
    return file_group_dict


def copy_file(checkin, file_paths, new_dir):
    '''copy file to the handoff dir'''
    new_file_paths = []
    file_ranges = []
    if not file_paths:
        return new_file_paths, file_ranges
    progress = checkin.impl.start_progress('Texture Copying', True, len(file_paths))
        
    file_group_dict = get_file_group_dict(checkin, file_paths) 
    for file_path in file_paths:
        progress.increment()

        if checkin.impl.is_file_group(file_path):
            #file_range = checkin.impl.get_file_range(file_path)
            file_range = file_group_dict.get(file_path)[1]
            file_path = checkin.impl.get_tactic_file_group_path(file_path)
            file_group = Common.expand_paths(file_path, file_range)

            new_file_name = os.path.basename(file_path)
            new_file_pat = '%s/%s' %(new_dir, new_file_name)
            new_file_paths.append(new_file_pat) 

            for idx, path in enumerate(file_group):
                file_name = os.path.basename(path)
                file_name = Common.get_filesystem_name(file_name)
                new_file_path = '%s/%s' %(new_dir, file_name)
                shutil.copy(path, new_file_path)

            file_ranges.append(file_range)
            continue
        else:
            file_ranges.append(None)
        
        # singles copying
        file_name = os.path.basename(file_path)
        progress.set_message("Copying ['%s'] " %file_path)

        file_name = Common.get_filesystem_name(file_name)
        new_file_path = '%s/%s' %(new_dir, file_name)
        
        shutil.copy(file_path, new_file_path)
        checkin.app.message("Copying to [%s]" %new_file_path)
        new_file_paths.append(new_file_path)
    progress.stop()
    return new_file_paths, file_ranges




def checkin_anim(namespace, asset_code, instance, options=None):
    checkin = Checkin()

    naming = checkin.app.get_node_naming()
    naming.set_namespace(namespace)
    naming.set_asset_code(asset_code)
    node_name = naming.get_node_name()
    
    if options:
        checkin.set_options(options)


    # test for export mode
    #if checkin.get_option("export") == "export":
    use_handoff_dir = checkin.get_option("use_handoff_dir") == 'true'
    if use_handoff_dir:
        env = AppEnvironment.get()
        ticket = env.get_ticket()
        checkin.handoff_dir = get_handoff_dir(ticket, env) 
    if 1:
        # setting instance as an option for wider usage
        checkin.set_option('instance', instance)
        checkin.dump_node(node_name, instance)
        if use_handoff_dir:
            checkin.handoff_files()
        else:
            checkin.upload_files()
        return

    # NOTE: code ends here for now

    if namespace == "cull":
        checkin.set_option("selected", "true")
        # FIXME: I think it needs node_name instead of namespace here
        checkin.dump_group(namespace, asset_code)
    else:
        checkin.dump_anim(node_name, instance)

    checkin.dump_node(node_name, instance)

    checkin.upload_files()





def checkin_set(instance_name, asset_code, options=None):
    checkin = Checkin()

    # checkin everything in session
    checkin.set_option("selected", "false")
    checkin.dump_group(instance_name, asset_code)
    checkin.upload_files()



def checkin_layer(node_name):
    checkin = Checkin()

    # get all of the selected nodes
    from pyasm.application.maya import Maya
    selected = Maya.get().get_selected_top_nodes()
    if not selected:
        msg = "No assets selected"
        raise TacticException(msg)

    # dump out the reference file
    checkin.dump_ref(node_name, selected)
    checkin.upload_files()


def get_handoff_dir(ticket, env):
    project = env.get_project_code()
    
    from pyasm.application.common.interpreter.tactic_client_lib import * 
    client_server = TacticServerStub(setup=False)
    client_server.set_project(project)
    client_server.set_ticket(ticket)
    server_name = env.get_server()
    client_server.set_server(server_name)
    client_server.start("Get Handoff Dir")
    handoff_dir = ''
    try:
        handoff_dir = client_server.get_handoff_dir()
    except:
        print "Get handoff dir failed"
        client_server.abort()
        raise
    else:
        client_server.finish()

    return handoff_dir

def checkin_shot(shot_code, context, options='', handlers=None):

    checkin = Checkin()
    env = AppEnvironment.get()

    dir = env.get_tmpdir()
    ticket = env.get_ticket()
    server = env.get_xmlrpc_server()

    # set the option to save
    options = '%s|export_method=Save' %options
    checkin.set_options(options)
    if checkin.get_option('clean_up') == 'true':
        checkin.clean_up()
    if handlers:
        checkin.set_handlers(handlers)
    tactic_node_name = "%s" % shot_code
    # HACK: highly maya specific
    if not checkin.app.node_exists(tactic_node_name):
        if checkin.app.APPNAME == "maya":
            checkin.app.mel("sets -em -n %s" % tactic_node_name )
        elif checkin.app.APPNAME == "xsi":
            checkin.app.xsi.ActiveProject.ActiveScene.Root.AddNull(tactic_node_name)
        # houdini checks for bundle existence separately
        elif checkin.app.APPNAME == "houdini":
            checkin.app.hscript('opcf /obj; opadd -n null "%s"' %tactic_node_name)

    current_path = checkin.app.get_file_path()

    # this should be the same as the one used in checkin_shot_set()
    name = "shot_%s" % shot_code

    use_filename=True
    if checkin.get_option('use_filename') == 'false':
        use_filename=False
   
    # replace local references with lib_path in case loaded thru http mode
    swap_ref_path(ticket, env, checkin.app)

    handler_cls = checkin.get_handler("checkin/pre_export")
    if handler_cls:
        handler = AppEnvironment.create_from_class_path(handler_cls)
        handler.execute() 
    path = checkin._export_node(name, use_filename=use_filename)

    checkin.set_option('use_namespace', True)

    checkin.handoff_dir = get_handoff_dir(ticket, env) 

    # HACK: use None to represent entire session
    checkin.dump_ref(name, [None])

    checkin.app.rename(current_path)

   
    
    use_handoff_dir = checkin.get_option("use_handoff_dir") == 'true'
    if use_handoff_dir:
        checkin.handoff_files()
    else:
        checkin.upload_files()

def checkin_shot_set(shot_code, set_name, process, context, checkin_as,\
        currency, unknown_ref, desc, use_filename, options):

    checkin = Checkin()
    info = checkin.info
    dir = info.get_tmpdir()

    ticket = info.get_ticket()
    server = info.get_xmlrpc_server()
    project_code = info.get_project_code()
  
    # export all the set_members, but without the top set node
    set_members = checkin.app.get_nodes_in_set(set_name)
    if shot_code not in set_members:
        # clear selection first to prevent addition of anything to this set
        checkin.app.select_none()
        checkin.app.create_set(shot_code)
        # add to set
        checkin.app.add_to_set(set_name, shot_code)
        set_members.append(shot_code)
        

    if use_filename =='true': use_filename = True
    else: use_filename = False

    checkin._export_node(set_members, use_filename=use_filename)
    checkin.set_options(options)
    if checkin.get_option('clean_up') == 'true':
        checkin.clean_up()

    # this should be the same as the one used in checkin_shot()
    ref_name = "shot_%s" %shot_code
    checkin.set_option('use_namespace', True)
    checkin.handoff_dir = get_handoff_dir(ticket, env) 

    checkin.dump_ref(ref_name, [set_name])

    use_handoff_dir = checkin.get_option("use_handoff_dir") == 'true'
    if use_handoff_dir:
        checkin.handoff_files()
    else:
        checkin.upload_files()

    # publish to db
    snapshot_code = server.checkin_shot_set(ticket, project_code, shot_code, process, \
        context, checkin_as, currency, unknown_ref, desc)

    # update tacticNodeInfo
    load.update(snapshot_code, '', set_name, context) 

