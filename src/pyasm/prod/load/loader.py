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

__all__ = ["LoaderException", "LoaderCmd", 'MayaFileLoaderCmd',
'MayaAssetLoaderCmd', 'MayaInstanceLoaderCmd', 'MayaAnimLoaderCmd',
'MayaAnimExportLoaderCmd', 'FlashAssetLoaderCmd','TemplateLoaderCmd',
'MayaGroupLoaderCmd', 'MayaShotLoaderCmd', 'MayaAssetUpdaterCmd',
'MayaAnimUpdaterCmd', 'MayaGroupUpdaterCmd', 'MayaShotUpdaterCmd', 
'CreateSetNodeCmd']

from pyasm.common import *
from pyasm.search import *
from pyasm.command import Command
from pyasm.biz import *
from pyasm.checkin import *
from pyasm.prod.biz import *


import os, re


class LoaderException(Exception):
    pass


class LoaderCmd(Command):
    '''This defines that base loader class, which will load
    an instance of an asset in to a session.  These classes will
    essentiall take a high level XML snapshot from the database and
    transform it into a low level xml command language which a
    SessionBuilder class will handle'''


    def __init__(my):

        # the input snapshot and xml
        my.snapshot = None
        my.snapshot_xml = None

        # the final xml file
        my.execute_xml = None
        my.is_top_loader_flag = False

        # the instance passed from a parent loader.
        my.instance = None
        my.instance_name = ""

        # loader options
        my.options = {}

        # use the default one
        my.loader_context = None


        # determine whether this loader must check for uniqueness first
        my.is_unique = False


    def get_execute_xml(my):
        return my.execute_xml


    def set_snapshot(my, snapshot):
        my.snapshot = snapshot
        my.snapshot_xml = snapshot.get_xml_value("snapshot")

    def set_snapshot_xml(my, snapshot_xml):
        my.snapshot_xml = Xml()
        my.snapshot_xml.read_string(snapshot_xml)


    def get_context(my):
        return my.loader_context.get_context()


    def get_option(my, name):
        return my.loader_context.get_option(name)


    def get_instance(my, instance):
        return my.instance

    def set_instance(my, instance):
        my.instance = instance
        my.instance_name = instance.get_name()


    def set_unique(my):
        my.is_unique = True



    def check(my):
        return True

    def get_description(my):
        return "LoaderCmd"


    def set_loader_context(my, loader_context):
        my.loader_context = loader_context

    def get_loader_context(my):
        return my.loader_context



    def add_warning(my, msg, label=""):
        '''add a warning to the execute xml'''
        print msg
        root = my.execute_xml.get_root_node()

        warning_node = my.execute_xml.create_element("warning")
        Xml.set_attribute(warning_node, "label", label)
        Xml.set_attribute(warning_node, "msg", msg)
        Xml.append_child(root, warning_node)


    def _create_file_info(my, node, snapshot):
        assert snapshot

        file_code = Xml.get_attribute(node,"file_code")

        file = File.get_by_code(file_code)
        if file == None:
            print("File SObject [%s] from snapshot [%s] does not exist" % (file_code, snapshot.get_code()))
            #raise LoaderException("File SObject [%s] from snapshot [%s] does not exist" % (file_code, snapshot.get_code()))
            return None, None

        # create the file node
        file_node = my.execute_xml.create_element("file")


        # get the repo
        repo = snapshot.get_repo(snapshot)
        from pyasm.checkin import PerforceRepo
        if isinstance(repo, PerforceRepo):
            conn_type = "perforce"
        else:
            conn_type = my.get_option("connection")

        file_type = Xml.get_attribute(node, "type")
        
        # server side nfs
        if conn_type == "server_fs":
            dir = snapshot.get_lib_dir(file_type=file_type)
        # or web (http://)
        elif conn_type == "http":
            dir = snapshot.get_remote_web_dir(file_type=file_type)
        # or client nfs
        elif conn_type == "file system":
            dir = snapshot.get_client_lib_dir(file_type=file_type)
        # check out through perforce on a local sync
        elif conn_type == "perforce":

            # use the p4 workspace of the client
            dir = snapshot.get_relative_dir(file_type=file_type)

            # set the version
            Xml.set_attribute(file_node, "version", snapshot.get_value("version"))

        else:
            dir = snapshot.get_remote_web_dir(file_type=file_type)


        Xml.set_attribute(file_node, "connection", conn_type)

        # build up the file node
        filename = file.get_full_file_name()

        # handle the type of link
        link = my.get_option("link")
        if link == "current":
            filename = re.sub("_v\d+_(r\d+_)?", "_CURRENT_", filename)
            Xml.set_attribute(file_node, "link", link)

        url = "%s/%s" % (dir,filename)
        Xml.set_attribute(file_node, "url", url)


        # establish the "to" path
        if url.startswith("http://"):
            local_repo_dir = snapshot.get_local_repo_dir(file_type=file_type)
            Xml.set_attribute(file_node, "to", local_repo_dir)
            # set the asset directory
            naming = Project.get_dir_naming()
            asset_dir = naming.get_base_dir("local")[0]
            Xml.set_attribute(file_node, "tactic_asset_dir", asset_dir)
        # for non http connections
        else:
            naming = Project.get_dir_naming()
            asset_dir = naming.get_base_dir("client_repo")[0]
            Xml.set_attribute(file_node, "tactic_asset_dir", asset_dir)


        # establish the sandbox path
        sandbox_dir = snapshot.get_sandbox_dir(file_type=file_type)
        Xml.set_attribute(file_node, "sandbox_dir", sandbox_dir)



        # send over the checksum
        md5_checksum = file.get_value("md5")
        if md5_checksum:
            Xml.set_attribute(file_node, "md5", md5_checksum)

        return file_node, file




    def execute(my):

        # get the current execute parser.  Note this assume that there
        # can only be one at a time.
        key = "LoaderCmd:top_loader"
        top_loader = Container.get(key)
        if top_loader == None:
            my.execute_xml = Xml()
            my.execute_xml.create_doc("execute")
            top_loader = my
            my.is_top_loader_flag = True
            Container.put(key, top_loader)
        else:
            my.execute_xml = top_loader.execute_xml

        # decipher the XML
        my.handle_xml(my.snapshot_xml)

        # clean up the execute xml
        if top_loader == my:

            print "*"*20
            my.execute_xml.dump()
            print "*"*20

            Container.remove(key)


    def handle_xml(my, xml):
        raise LoaderException("Must override handle_xml() function")



    def is_top_loader(my):
        '''determine whether this loader is the top loader'''
        return my.is_top_loader_flag



class MayaFileLoaderCmd(LoaderCmd):
    '''Simply loads in a file'''

    def handle_xml(my, xml):

        root = my.execute_xml.get_root_node()

        ref_file_node = xml.get_node("snapshot/file")
        file_node, file = my._create_file_info(ref_file_node,my.snapshot)
        if file_node is None:
            return
        Xml.append_child(root, file_node)
        
        instantiation = my.get_option("instantiation") 
        if instantiation == 'reference':
            import_node = my.execute_xml.create_element("reference")
        elif instantiation == 'import':
            import_node = my.execute_xml.create_element("import")
            proj_setting = ProdSetting.get_value_by_key('loader_use_namespace')
            config_setting = Config.get_value('load', 'loader_use_namespace')
            if proj_setting in ['true','false']:
                my.loader_context.set_option("use_namespace", proj_setting)
            elif config_setting in ['true','false']:
                my.loader_context.set_option("use_namespace", config_setting)

        elif instantiation == 'import_media':
            import_node = my.execute_xml.create_element("import_media")
        else:
            import_node = my.execute_xml.create_element("open")
        
        Xml.append_child(root, import_node)
        Xml.set_attribute(import_node, "name", my.snapshot.get_sobject().get_code())
        Xml.set_attribute(import_node, "node_name", my.snapshot.get_sobject().get_code())
        Xml.set_attribute(import_node, "namespace", my.snapshot.get_sobject().get_code())
        Xml.set_attribute(import_node, "asset_code", my.snapshot.get_sobject().get_code())
        Xml.set_attribute(import_node, "project_code", Project.get_project_code())




class MayaAssetLoaderCmd(LoaderCmd):
    '''Implementation of the loader for assets.  Assets are loaded as
    imports (not references) so that they can be worked on as assets'''

    def handle_xml(my, xml):
        is_file_system = my.get_option("connection") == "file system"
        # get any sub references first
        if not is_file_system:
            sub_nodes = xml.get_nodes("snapshot//ref")
            for sub_node in sub_nodes:

                latest = False
                # get the dependent snapshot, but lock the version to that
                # which was at checkin time.  The update is manual because
                # of the high level of complex dependency which must be done
                # manually - eg: uv - model relationship
                context = Xml.get_attribute(sub_node,"context")
                ref_snapshot = my.loader_context.get_snapshot( \
                    sub_node, context, latest)
                
                my.handle_ref_snapshot(ref_snapshot)
        
        inst_mode = 'reference'
        if my.get_option("instantiation") == "import":
            inst_mode = 'import'
            proj_setting = ProdSetting.get_value_by_key('loader_use_namespace')
            config_setting = Config.get_value('load', 'loader_use_namespace')
            if proj_setting in ['true','false']:
                my.loader_context.set_option("use_namespace", proj_setting)
            elif config_setting in ['true','false']:
                my.loader_context.set_option("use_namespace", config_setting)
        elif my.get_option("instantiation") == "open":
            inst_mode = 'open'
        elif my.get_option("instantiation") == "import_media":
            inst_mode = 'import_media'
        
        use_namespace = True
        if my.get_option("use_namespace") == "false" or inst_mode == 'open':
            use_namespace = False


        # get the node and handle it
        for node_type in ['maya', 'houdini', 'xsi', 'obj', 'collada', '.fla', 'file', 'main']:
            app_nodes = xml.get_nodes("snapshot/file[@type='%s']" % node_type)
            for app_node in app_nodes:

                my.handle_app_file(app_node, instantiation=inst_mode, is_unique=my.is_unique, use_namespace=use_namespace)
        #if not is_file_system:
        my.handle_all_textures(xml, use_namespace)

        my.handle_all_cache(xml, use_namespace)


    def handle_ref_snapshot(my, snapshot):
        if not snapshot:
            return

        # handle the files in this snpashot
        xml = snapshot.get_xml_value("snapshot")

        # handle the refs in this snpashot
        ref_nodes = xml.get_nodes("snapshot/ref")
        #if ProdSetting.get_value_by_key('reference_dependency') == 'current':
        #    latest = True
         
        for ref_node in ref_nodes:

            search_type = Xml.get_attribute(ref_node,"search_type")
            search_id = Xml.get_attribute(ref_node,"search_id")
            context = Xml.get_attribute(ref_node,"context")
            #if ref_dependency_mode == 'current':
            #    version = 0
            #else:
            version = Xml.get_attribute(ref_node,"version")

            # get the snapshot
            ref_snapshot = Snapshot.get_by_version(search_type,search_id,\
                        context, version)

            my.handle_ref_snapshot(ref_snapshot)

        # handle file nodes
        file_nodes = xml.get_nodes("snapshot/file")
        for file_node in file_nodes:
            if Xml.get_attribute(file_node, 'type') in ['web','icon']:
                continue
            file_node, file = my._create_file_info(file_node,snapshot)
            if file_node is None:
                return

            root = my.execute_xml.get_root_node()
            Xml.append_child(root, file_node)

    def get_asset_code(my, sobject):
        asset_code = ''
        if sobject.has_value("asset_code"):
            asset_code = sobject.get_value("asset_code")
        else:
            asset_code = sobject.get_code()

        return asset_code

    def handle_app_file(my, node, instantiation='reference', is_unique=True,  use_namespace=True):

        root = my.execute_xml.get_root_node()

        file_node, file = my._create_file_info(node,my.snapshot)
        if file_node is None:
            return


        my.execute_xml.append_child(root, file_node)

        # use the open flag
        if instantiation == 'open':
            import_node = my.execute_xml.create_element("open")

        # add the import node
        elif instantiation == 'import':
            import_node = my.execute_xml.create_element("import")
        elif instantiation == 'import_media':
            import_node = my.execute_xml.create_element("import_media")
        else:
            import_node = my.execute_xml.create_element("reference")

        # HACK: put in an overriding replace mode in here for now
        if my.get_option("load_mode") == "replace":
            import_node = my.execute_xml.create_element("replace")
            Xml.set_attribute(import_node, "append_attr", "true")
            replacee = my.get_option("replacee")
            if replacee:
                Xml.set_attribute(import_node, "replacee",  replacee)

        sobject = file.get_sobject()

        # get the instance if one is set
        if my.instance_name:
            Xml.set_attribute(import_node, "instance", my.instance_name )

        # use ProdNodeNaming
        naming = Project.get_naming("node")

        if my.instance:
            naming.set_sobject(my.instance)
        else:
            naming.set_sobject(sobject)

        naming.set_snapshot(my.snapshot)
        namespace = naming.get_value()
        namespace = namespace.replace("/", "_")
        

        Xml.set_attribute(import_node, "namespace", namespace)
        
        # this only applies to 'import' mode
        if instantiation == 'import':
            if use_namespace:
                Xml.set_attribute(import_node, "use_namespace", "true")
            else:
                Xml.set_attribute(import_node, "use_namespace", "false")


        # add the asset_code
        asset_code = my.get_asset_code(sobject)

        Xml.set_attribute(import_node, "asset_code", asset_code)


        # add the node_name if available.  The node name is stored in
        # the database so that it will match the reference within a file.
        # (it cannot be procedurally built)
        xml = my.snapshot_xml
        node = xml.get_node('snapshot/file')
        node_name = Xml.get_attribute(node, 'node_name')
        if node_name:
            Xml.set_attribute(import_node, "node_name", node_name)

        # set whether the instance must be unique
        if is_unique:
            Xml.set_attribute(import_node, "unique", "true")
        else:
            Xml.set_attribute(import_node, "unique", "false")
           
        Xml.append_child(root, import_node)

        # add info about this snapshot
        my._add_info(my.snapshot)



    def _add_attr(my, name, value, type=""):
        root = my.execute_xml.get_root_node()
        attr_node = my.execute_xml.create_element("add_attr")
        Xml.set_attribute(attr_node, "attr", name)
        Xml.set_attribute(attr_node, "value", value)
        if type != "":
            Xml.set_attribute(attr_node, "type", type)

        Xml.append_child(root, attr_node)

    def _set_node_attr(my, name, attr, value, node_name=None):
        root = my.execute_xml.get_root_node()
        attr_node = my.execute_xml.create_element("set_node_attr")
        if node_name:
            Xml.set_attribute(attr_node, "node", node_name)
        Xml.set_attribute(attr_node, "name", name)
        Xml.set_attribute(attr_node, "attr", attr)
        Xml.set_attribute(attr_node, "value", value)
        Xml.append_child(root, attr_node)

    def _add_current_node(my, asset_code, namespace=''):
        ''' a node that specifies the builder what the current node is 
            NOTE: Don't put : as the default here. MayaNodeNaming will take care of that'''
        root = my.execute_xml.get_root_node()
        attr_node = my.execute_xml.create_element("current_node")
        Xml.set_attribute(attr_node, "asset_code", asset_code)
        Xml.set_attribute(attr_node, "namespace", namespace)
        Xml.append_child(root, attr_node)

    def _add_node(my, node_name, type):
        root = my.execute_xml.get_root_node()
        attr_node = my.execute_xml.create_element("add_node")
        Xml.set_attribute(attr_node, "name", node_name)
        Xml.set_attribute(attr_node, "type", type)
        Xml.append_child(root, attr_node)



    def _add_to_set(my, set_name, instance_name=None):
        root = my.execute_xml.get_root_node()
        attr_node = my.execute_xml.create_element("add_to_set")
        Xml.set_attribute(attr_node, "set_name", set_name)

        if instance_name:
            Xml.set_attribute(attr_node, "instance", instance_name)

        Xml.append_child(root, attr_node)


        
    def _add_info(my, snapshot):
        # add info attributes
        root = my.execute_xml.get_root_node()
        snapshot_code = snapshot.get_code()
        context = snapshot.get_value("context")
        version = snapshot.get_value("version")
        revision = snapshot.get_value("revision", no_exception=True)
        type = snapshot.get_value("snapshot_type")
        if type == "anim_export":
            type = "anim"
        element_name = '%s_snapshot' % type
        sobject = snapshot.get_sobject()

        asset_code = my.get_asset_code(sobject)
        # tacticNodeData
        my._set_node_attr(element_name, "code", snapshot_code)
        my._set_node_attr(element_name, "context", context)
        my._set_node_attr(element_name, "version", version)
        if revision:
            my._set_node_attr(element_name, "revision", revision)

        my._set_node_attr(element_name, "asset_code", asset_code )
        if my.instance_name:
            my._set_node_attr(element_name, "instance", my.instance_name )

        my._set_node_attr(element_name, "project_code", Project.get_project_code())

    def handle_all_textures(my, xml, use_namespace):

        # determine which textures to load
        textures_option = my.get_option("textures")
        texture_nodes = []

        dependency_option = my.get_option("dependency")
        connection_option = my.get_option("connection")

        # handle all of the references the textures

        texture_nodes = xml.get_nodes("snapshot/ref[@type='texture']")
        for texture_node in texture_nodes:
            # get the snapshot
            search_type = Xml.get_attribute(texture_node, "search_type")
            search_id = Xml.get_attribute(texture_node, "search_id")
            context = Xml.get_attribute(texture_node, "context")
    
            if dependency_option == "latest":
                snapshot = Snapshot.get_latest( \
                    search_type, search_id, context )
            elif dependency_option == "current":
                snapshot = Snapshot.get_current( \
                    search_type, search_id, context )
            else:
                # as_checked_in means do nothing.. also avoid any reference edits in Maya. If it's file system mode, continue. http mode needs to download it
                if connection_option == 'file system':
                    continue

                version = Xml.get_attribute(texture_node, "version")
                snapshot = Snapshot.get_by_version( \
                    search_type, search_id, context, version )

            if not snapshot:
                continue
            texture_xml = snapshot.get_xml_value("snapshot")

            file_node = None
            if textures_option == "none":
                # TODO: provide a "no textures" support
                raise LoaderException("No support for no textures yet")
            elif textures_option == "low":
                file_node = texture_xml.get_node("snapshot/file[@type='web']")
            elif textures_option == "proxy":
                file_node = texture_xml.get_node("snapshot/file[@type='web']")
            else:
                file_node = texture_xml.get_node("snapshot/file[@type='main']")

            # HACK: Backwards compatibility: put the node name in here
            # so handle_texture works as before
            node_name = Xml.get_attribute(texture_node, "node")
            attr_name = Xml.get_attribute(texture_node, "attr")
            Xml.set_attribute(file_node, "node", node_name)
            Xml.set_attribute(file_node, "attr", attr_name)

            my._handle_texture(file_node, snapshot, use_namespace)



        # handle direct file references for the textures

        if textures_option == "none":
            # clear all texture node attributes
            rm_texture_nodes = xml.get_nodes("snapshot/file[@type='texture']")
            for node in rm_texture_nodes:
                my.handle_clear_texture_attr(node)
                return
        elif textures_option == "low":
            texture_nodes = xml.get_nodes("snapshot/file[@type='texture|lowres']")
        elif my.get_context() == "proxy":
            texture_nodes = xml.get_nodes("snapshot/file[@type='texture|lowres']")
        else:
            texture_nodes = xml.get_nodes("snapshot/file[@type='texture']")


        # handle all of the textures
        for texture_node in texture_nodes:
            my._handle_texture(texture_node, my.snapshot)



    def _handle_texture(my, node, snapshot, use_namespace ):

        root = my.execute_xml.get_root_node()

        # get and add file node
        file_node, file = my._create_file_info(node,snapshot)
        if file_node is None:
            return
        
        Xml.append_child(root, file_node)
        
     
        node_name = Xml.get_attribute(node, "node")
        attr_name = Xml.get_attribute(node, "attr")
        file_range = Xml.get_attribute(node, "file_range")
        if file_range == 'None':
            file_range =''

        if attr_name in ['', 'None']:
            # backwards compatibility for Maya
            attr_name = 'ftn'

        # get the path where the texture originates from
        url = Xml.get_attribute(file_node, "url")
        
        # for web connection, marshal to the local path
        if my.get_option("connection") == "http":
            # put in the local scenes path
            local_repo_dir = snapshot.get_local_repo_dir()
            # Commented out for now.. This tries to set a relative path. but Maya would only 
            # accept it if the project is set to this location where the relative path 
            # actually exists
            #app_local_repo_dir = my.snapshot.get_local_repo_dir()
            #relative_dir = Common.relative_dir(app_local_repo_dir, local_repo_dir)
            texture_path = "%s/%s" % (local_repo_dir, os.path.basename(url))
        # for file connections, map to the repository
        elif my.get_option("connection") == "server_fs":
            fs_texture_dir = snapshot.get_lib_dir()
            texture_path = "%s/%s" % (fs_texture_dir, os.path.basename(url))

        elif my.get_option("connection") == "file system":
            fs_texture_dir = snapshot.get_client_lib_dir()
            texture_path = "%s/%s" % (fs_texture_dir, os.path.basename(url))
        else:
            local_repo_dir = snapshot.get_local_repo_dir()
            texture_path = "%s/%s" % (local_repo_dir, os.path.basename(url))

        # reset the file attribute to point to this texture
        set_attr_node = my.execute_xml.create_element("add_attr")
        Xml.set_attribute(set_attr_node, "node", node_name)
        Xml.set_attribute(set_attr_node, "attr", attr_name)
        Xml.set_attribute(set_attr_node, "value", texture_path)
        Xml.set_attribute(set_attr_node, "type", "string")
        snapshot_type = my.snapshot.get_value("snapshot_type")
        Xml.set_attribute(set_attr_node, "snapshot_type", snapshot_type)
        Xml.set_attribute(set_attr_node, "file_range", file_range)

        is_xsi = my.snapshot.get_name_by_type('xsi')
        is_hou = my.snapshot.get_name_by_type('houdini')
        if is_xsi or is_hou or not use_namespace:
            Xml.set_attribute(set_attr_node, "use_namespace", "false")
        Xml.append_child(root, set_attr_node)




    def handle_clear_texture_attr(my, node):
        root = my.execute_xml.get_root_node()

        node_name = Xml.get_attribute(node, "node")
        attr_name = Xml.get_attribute(node, "attr")

        set_attr_node = my.execute_xml.create_element("add_attr")
        Xml.set_attribute(set_attr_node, "node", node_name)
        Xml.set_attribute(set_attr_node, "attr", attr_name)
        Xml.set_attribute(set_attr_node, "value", "")
        snapshot_type = my.snapshot.get_value("snapshot_type")
        Xml.set_attribute(set_attr_node, "snapshot_type", snapshot_type)
        Xml.append_child(root, set_attr_node)


    def handle_all_cache(my, xml, use_namespace):
        '''handle all of the references to the cache'''
        cache_nodes = xml.get_nodes("snapshot/ref[@type='cache']")
        for cache_node in cache_nodes:
            # get the snapshot
            search_type = Xml.get_attribute(cache_node, "search_type")
            search_id = Xml.get_attribute(cache_node, "search_id")
            context = Xml.get_attribute(cache_node, "context")
    
            version = Xml.get_attribute(cache_node, "version")
            snapshot = Snapshot.get_by_version( \
                    search_type, search_id, context, version )

            if not snapshot:
                continue
            
            cache_xml = snapshot.get_xml_value("snapshot")

            file_node = cache_xml.get_node("snapshot/file[@type='geo']")

            # HACK: Backwards compatibility: put the node name in here
            # so handle_texture works as before
            node_name = Xml.get_attribute(cache_node, "node")
            attr_name = Xml.get_attribute(cache_node, "attr")
            Xml.set_attribute(file_node, "node", node_name)
            Xml.set_attribute(file_node, "attr", attr_name)

            my._handle_cache(file_node, snapshot, use_namespace)


    def _handle_cache(my, node, snapshot, use_namespace ):
        '''handle each cache node here'''
        root = my.execute_xml.get_root_node()

        # get and add file node
        file_node, file = my._create_file_info(node,snapshot)
        if file_node is None:
            return
        Xml.append_child(root, file_node)

        node_name = Xml.get_attribute(node, "node")
        attr_name = Xml.get_attribute(node, "attr")
        file_range = Xml.get_attribute(node, "file_range")
        if file_range == 'None':
            file_range =''
        if attr_name in ['', 'None']:
            # backward compatibility for Maya
            attr_name = 'cacheName'

        # get the path where the texture originates from
        url = Xml.get_attribute(file_node, "url")
        
        # for web connection, marshal to the local path
        if my.get_option("connection") == "http":
            # put in the local scenes path
            local_repo_dir = snapshot.get_local_repo_dir()
            # Commented out for now.. This tries to set a relative path. but Maya would only 
            # accept it if the project is set to this location where the relative path 
            # actually exists
            #app_local_repo_dir = my.snapshot.get_local_repo_dir()
            #relative_dir = Common.relative_dir(app_local_repo_dir, local_repo_dir)
            cache_path = "%s/%s" % (local_repo_dir, os.path.basename(url))
        # for file connections, map to the repository
        elif my.get_option("connection") == "server_fs":
            fs_texture_dir = snapshot.get_lib_dir()
            cache_path = "%s/%s" % (fs_texture_dir, os.path.basename(url))

        elif my.get_option("connection") == "file system":
            fs_texture_dir = snapshot.get_client_lib_dir()
            cache_path = "%s/%s" % (fs_texture_dir, os.path.basename(url))
        else:
            local_repo_dir = snapshot.get_local_repo_dir()
            cache_path = "%s/%s" % (local_repo_dir, os.path.basename(url))
        is_maya = my.snapshot.get_name_by_type('maya')

        cache_leaf = cache_path
        cache_dir = ''
        if is_maya:
            cache_path, ext = os.path.splitext(cache_path)
            cache_dir, cache_leaf = os.path.split(cache_path)
        
        # set the base directory to cache_dir for maya, otherwise it would not enable a 
        # cache path pointing to somewhere outside the base directory data\cache\

        set_attr_node = my.execute_xml.create_element("add_attr")
        Xml.set_attribute(set_attr_node, "node", node_name)
        Xml.set_attribute(set_attr_node, "attr", "cachePath")
        Xml.set_attribute(set_attr_node, "value", cache_dir)
        Xml.set_attribute(set_attr_node, "type", "string")
        if not use_namespace:
            Xml.set_attribute(set_attr_node, "use_namespace", "false")
        Xml.append_child(root, set_attr_node)

        
        # reset the file attribute to point to this cache
 
        set_attr_node = my.execute_xml.create_element("add_attr")
        Xml.set_attribute(set_attr_node, "node", node_name)
        Xml.set_attribute(set_attr_node, "attr", attr_name)
        Xml.set_attribute(set_attr_node, "value", cache_leaf)
        Xml.set_attribute(set_attr_node, "type", "string")
        snapshot_type = my.snapshot.get_value("snapshot_type")
        Xml.set_attribute(set_attr_node, "snapshot_type", snapshot_type)
        Xml.set_attribute(set_attr_node, "file_range", file_range)

        #is_xsi = my.snapshot.get_name_by_type('xsi')
        if not use_namespace:
            Xml.set_attribute(set_attr_node, "use_namespace", "false")
        Xml.append_child(root, set_attr_node)
      

    def handle_mel(my, mel_node):
        root = my.execute_xml.get_root_node()
        child = Xml.get_first_child(mel_node)
        cmd = Xml.get_node_value(child)

        new_mel_node = my.execute_xml.create_text_element('mel',cmd)
        Xml.append_child(root, new_mel_node)



    def handle_standard_tags(my, xml):
        '''handles all of the standard tags found'''

        # handle any maya nodes
        maya_nodes = xml.get_nodes("snapshot/file[@type='maya']")
        for maya_node in maya_nodes:
            my.handle_app_file(maya_node, instantiation = 'reference')

        # allow the ability to add arbitrary mel commands
        mel_nodes = xml.get_nodes("snapshot/mel")
        for mel_node in mel_nodes:
            my.handle_mel(mel_node)

        # handle any textures
        my.handle_all_textures(xml)
 




class MayaInstanceLoaderCmd(MayaAssetLoaderCmd):
    '''Implementation of the loader for instances.  Instances are loaded
    as references (as opposed in import).'''

    def handle_xml(my, xml):

        # get any sub references first
        sub_nodes = xml.get_nodes("snapshot/file/ref")
        for sub_node in sub_nodes:
            ref_snapshot = my.loader_context.get_snapshot(node)

            ref_xml = ref_snapshot.get_xml_value("snapshot")
            ref_file_node = ref_xml.get_node("snapshot/file")
            file_node, file = my._create_file_info(ref_file_node,ref_snapshot)

            root = my.execute_xml.get_root_node()
            Xml.append_child(root, file_node)

        # get the maya node and handle it
        maya_node = xml.get_node("snapshot/file[@type='maya']")
        my.handle_app_file(maya_node, instantiation == 'reference')
        my.handle_all_textures(xml)



class MayaAnimExportLoaderCmd(MayaAssetLoaderCmd):
    '''loads in animation that was exported using MayaExport'''

    def handle_xml(my, xml):

        my.loader_context.set_option("has_instance", "false")
        #my.loader_context.set_option("instantiation", "import")
        my.loader_context.set_option("use_namespace", "false")
        #my.loader_context.set_option("is_unique", "true")
        my.set_unique()

        super(MayaAnimExportLoaderCmd,my).handle_xml(xml)




class MayaAnimLoaderCmd(MayaInstanceLoaderCmd):
    '''loads in animation takes of instances'''

    def handle_xml(my, xml):

        # first get all of the references
        ref_nodes = xml.get_nodes("snapshot/ref")
        anim_node = xml.get_node("snapshot/file[@type='anim']")

        for ref_node in ref_nodes:
            ref_instance_name = Xml.get_attribute(ref_node, "instance")
            context = Xml.get_attribute(ref_node, "context")

            # get the snapshot for this reference
            ref_snapshot = my.loader_context.get_snapshot(ref_node, context)
            if ref_snapshot == None:
                msg = "Skipping [%s]" %  ref_instance_name
                my.add_warning(msg, ref_instance_name)
                continue

            # anim loaders always load the reference with specified context
            # in the ref node
            loader = my.loader_context.get_loader(ref_snapshot, context)
            if loader == None:
                continue

            shot = my.loader_context.get_shot(shot)
            instance = ShotInstance.get_by_shot(shot, ref_instance_name)
            if not instance:
                print('WARNING: Asset Instance [%s] not found in shot [%s]'%(ref_instance_name, shot.get_code()))
                continue
            loader.set_instance(instance)

            # all instances are unique
            loader.set_unique()

            loader.execute()

            # handle anim
            anim_node = xml.get_node("snapshot/file[@type='anim']")
            if anim_node is not None:
                my.handle_anim(anim_node, ref_instance_name)


            # add data about this snapshot
            my._add_info(my.snapshot)

        my.handle_standard_tags(xml)



    def handle_anim(my, node, instance_name):
        root = my.execute_xml.get_root_node()

        # get and add file node
        file_node, file = my._create_file_info(node,my.snapshot)
        Xml.append_child(root, file_node) 
        anim_node = my.execute_xml.create_element("anim")
        Xml.set_attribute(anim_node, "instance", instance_name)
        Xml.append_child(root, anim_node)



class MayaGroupLoaderCmd(MayaAnimLoaderCmd):
    '''This snapshot will contain many reference to other snapshot and
    a single file that positions everything'''


    def handle_xml(my, xml):

        # get all of the references and the anim node
        ref_nodes = xml.get_nodes("snapshot/ref")
        anim_node = xml.get_node("snapshot/file[@type='anim']")
        sobject = my.snapshot.get_sobject()
        
        if not my.instance_name:
            my.instance_name = sobject.get_value("name")


        for ref_node in ref_nodes:
            ref_instance_name = Xml.get_attribute(ref_node,"instance")

            # backwards compatibility: for when sets contained full Maya
            # namespaces
            if ref_instance_name.find(":") != -1:
                msg = "WARNING: snapshot '%s' has Maya namespaces in it" % \
                    my.snapshot.get_code()
                my.add_warning(msg, my.snapshot.get_code())
                ref_instance_name, tmp = ref_instance_name.split(":", 1)


            # if this instance is culled, then skip loading this
            if my.loader_context.is_instance_culled(ref_instance_name):
                print "Culling [%s]" % ref_instance_name
                continue

            context = my.loader_context.get_context()

            # Get the snapshot for this reference, using the group's context.
            # Loading a group's within a context means that references
            # below will inherit this context
            ref_snapshot = my.loader_context.get_snapshot(ref_node, context, recurse=True)


            if not ref_snapshot:
                msg = "Skipping [%s]: No snapshot found" %  ref_instance_name
                my.add_warning(msg, ref_instance_name)
                continue

            # group loaders always load references under the context of the
            # group, not the reference.  The reference context is ignored
            loader = my.loader_context.get_loader(ref_snapshot, context)
            if loader == None:
                msg = "Skipping [%s]: No loader found" %  ref_instance_name
                my.add_warning(msg, ref_instance_name)
                continue
            # FIXME: using backdoor here
            loader.instance_name = ref_instance_name
            loader.execute()


            # handle anim for this group only if there is no animation
            # set by loader
            has_anim = isinstance( loader, MayaAnimLoaderCmd )
            if my.instance_name != "cull" and not has_anim and anim_node:
                my.handle_anim(anim_node, ref_instance_name)

            # put a references to this group
            my._add_info(my.snapshot)

            #my._add_to_set(my.instance_name, ref_instance_name)
            # ref_instance_name should not be passed thru, use current node
            # name instead
            my._add_to_set(my.instance_name)


        # handle any maya nodes
        maya_nodes = xml.get_nodes("snapshot/file[@type='maya']")
        for maya_node in maya_nodes:
            # this is for now meant for non-tactic nodes
            # references requires namespace so we support import for now
            my.handle_app_file(maya_node, instantiation = 'import', is_unique=False)
            my._add_selection_to_set(my.instance_name)
            
        # allow the ability to add arbitrary mel commands
        mel_nodes = xml.get_nodes("snapshot/mel")
        for mel_node in mel_nodes:
            my.handle_mel(mel_node)



        # handle any textures
        my.handle_all_textures(xml)


        # add the information to the set
        my._set_node_attr("set_snapshot", "code", my.snapshot.get_code(), my.instance_name )
        my._set_node_attr("set_snapshot", "context", my.snapshot.get_value('context'), my.instance_name )
        my._set_node_attr("set_snapshot", "version", my.snapshot.get_version(), my.instance_name )
        my._set_node_attr("set_snapshot", "asset_code", sobject.get_code(), my.instance_name )
        my._set_node_attr("set_snapshot", "project_code", Project.get_project_code(), my.instance_name )

    def handle_app_file(my, node, instantiation='reference', is_unique=True, use_namespace=False):
        ''' assuming these are non-tactic nodes that accompany a set'''
        root = my.execute_xml.get_root_node()

        file_node, file = my._create_file_info(node,my.snapshot)
        Xml.append_child(root, file_node)
        
        if instantiation == 'import':
            import_node = my.execute_xml.create_element("import")
        else:
            import_node = my.execute_xml.create_element("reference")
         
        Xml.set_attribute(import_node, "set", my.instance_name )
     
        # set whether the instance must be unique
        if is_unique:
            Xml.set_attribute(import_node, "unique", "true" )
        else:
            Xml.set_attribute(import_node, "unique", "false" )
            
        Xml.append_child(root, import_node)

    def _add_selection_to_set(my, set_name):
        root = my.execute_xml.get_root_node()
        
        mel_cmd = "sets -add %s `selectedNodes`" %set_name
        attr_node = my.execute_xml.create_text_element("mel", mel_cmd)
        
        Xml.append_child(root, attr_node) 
        
class MayaShotLoaderCmd(MayaAssetLoaderCmd):


    def handle_app_file(my, node, instantiation='reference', is_unique=True,\
            has_instance=True, use_namespace=False):

        root = my.execute_xml.get_root_node()

        file_node, file = my._create_file_info(node,my.snapshot)
        Xml.append_child(root, file_node)
        
        if instantiation == 'open':
            import_node = my.execute_xml.create_element("open")
        elif instantiation == 'reference':
            import_node = my.execute_xml.create_element("reference")
        else:
            import_node = my.execute_xml.create_element("import")  
            # hardcoding the default for import
            Xml.set_attribute(import_node, "use_namespace", "false" )
    
        # HACK: put in an overriding replace mode in here for now
        if my.get_option("load_mode") == "replace":
            import_node = my.execute_xml.create_element("replace")
            Xml.set_attribute(import_node, "append_attr", "true")

        Xml.append_child(root, import_node)
        Xml.set_attribute(import_node, "unique", "true")

        sobject = file.get_sobject()
        # get the instance, just for completeness of the tacticNodeData
        if my.instance_name == "":
            my.instance_name = sobject.get_name()
            

        # use ProdNodeNaming
        naming = Project.get_naming("node")
        naming.set_sobject(sobject)
        naming.set_snapshot(my.snapshot)
        namespace = naming.get_value()


        asset_code = sobject.get_code()
        Xml.set_attribute(import_node, "asset_code", asset_code)
        Xml.set_attribute(import_node, "shot", "true")

        if not instantiation == 'open':
            # NOTE: even if namespace is specified. import mode will ignore namespace by default
            Xml.set_attribute(import_node, "namespace", namespace)

       
        if instantiation == 'import':
            # this is important when import mode is chosen since current node will become
            # randomly as one of the top nodes of the imported shot
            my._add_current_node(asset_code)

        my._add_to_set(asset_code)
        # add data about this snapshot
        my._add_info(my.snapshot)

       
class FlashAssetLoaderCmd(MayaAssetLoaderCmd):
    pass

class TemplateLoaderCmd(LoaderCmd):
    def __init__(my):
        my.file_path = ''
        super(TemplateLoaderCmd, my).__init__()

    def handle_xml(my, xml):

        root = my.execute_xml.get_root_node()

        ref_file_node = xml.get_node("snapshot/file")
        file_node = None
        if my.snapshot:
            file_node, file = my._create_file_info(ref_file_node,my.snapshot)
        else:
            file_node = my.get_file_node_from_path()
        Xml.append_child(root, file_node)
        import_node = my.execute_xml.create_element("open")
        Xml.append_child(root, import_node)
        
        Xml.set_attribute(import_node, "asset_code", my.snapshot.get_sobject().get_code())
   
    def get_file_node_from_path(my):
         # server side nfs
       
        url = my.file_path

        # build up the file node
        file_node = my.execute_xml.create_element("file")
        Xml.set_attribute(file_node, "url", url)

        # establish the "to" path for non http connections
        if url.startswith("http://"):
            sandbox_dir = Config.get_value("checkin","win32_sandbox_dir")
            Xml.set_attribute(file_node, "to", sandbox_dir)

        # establish the sandbox path
        #sandbox_dir = snapshot.get_sandbox_dir()
        #Xml.set_attribute(file_node, "sandbox_dir", sandbox_dir)
        return file_node

# Updater starts here 

class MayaAssetUpdaterCmd(MayaAssetLoaderCmd):
    '''Implementation of the node info updater for assets.'''

    def __init__(my):
        my.asset_code = ''
        # my.instance is not really useful in Updater
        my.instance_name = ''
        my.namespace = ''
        super(MayaAssetUpdaterCmd, my).__init__()
        
    def set_asset_code(my, asset_code):
        my.asset_code = asset_code

    def set_namespace(my, namespace):
        my.namespace = namespace


    def handle_xml(my, xml):
        node_types = ['maya','houdini']
        for node_type in node_types:
            app_nodes = xml.get_nodes("snapshot/file[@type='%s']" % node_type)
            for app_node in app_nodes:
                my._add_current_node(my.asset_code, my.namespace)
                # add info attributes for every app file
                my._add_info(my.snapshot)

    def _add_info(my, snapshot):
        # add info attributes
        snapshot_code = snapshot.get_code()
        snapshot_type = snapshot.get_value("snapshot_type")

        context = snapshot.get_value("context")
        version = snapshot.get_value("version")
        element_name = '%s_snapshot' % snapshot_type
        sobject = snapshot.get_sobject()

        # tacticNodeData
        # node name is required
        my._set_node_attr(element_name, "code", snapshot_code)
        my._set_node_attr(element_name, "context", context)
        my._set_node_attr(element_name, "version", version)
        my._set_node_attr(element_name, "asset_code", sobject.get_code())
        my._set_node_attr(element_name, "project_code", Project.get_project_code())



class MayaShotUpdaterCmd(MayaAssetUpdaterCmd):
    
    def handle_xml(my, xml):
        
        # add info attributes
        snapshot_code = my.snapshot.get_code()
        context = my.snapshot.get_value("context")
        version = my.snapshot.get_value("version")
        element_name = '%s_snapshot' % my.snapshot.get_value("snapshot_type")
        sobject = my.snapshot.get_sobject()

        # commented out just like MayaShotLoaderCmd
        #my._add_to_set(my.namespace)

        # tacticNodeData
        # select the node first i.e. a shot or shot_set which are both objectSet
        my._add_current_node(my.asset_code, my.namespace)
        my._set_node_attr(element_name, "code", snapshot_code)
        my._set_node_attr(element_name, "context", context)
        my._set_node_attr(element_name, "version", version )
        my._set_node_attr(element_name, "asset_code", sobject.get_code())
        my._set_node_attr(element_name, "project_code", Project.get_project_code()) 



class MayaAnimUpdaterCmd(MayaAssetUpdaterCmd):
    '''loads in animation takes of instances'''

    def handle_xml(my, xml):

        # first get all of the references
        ref_nodes = xml.get_nodes("snapshot/ref")
        anim_node = xml.get_node("snapshot/file[@type='anim']")

        for ref_node in ref_nodes:
            ref_instance_name = Xml.get_attribute(ref_node, "instance")
            context = Xml.get_attribute(ref_node, "context")

            # get the snapshot for this reference
            ref_snapshot = my.loader_context.get_snapshot(ref_node, context)
            if ref_snapshot == None:
                msg = "Skipping [%s]" % ref_instance_name
                my.add_warning(msg, ref_instance_name)
                continue

            # anim updaters always update the reference with specified context
            # in the ref node
            updater = my.loader_context.get_updater(ref_snapshot, my.asset_code, \
                my.namespace, context)
            if not updater:
                continue
            #updater.set_instance(ref_instance_name)
            updater.execute()

            # specify current node
            my._add_current_node(my.asset_code, my.namespace)
            # add data about this snapshot
            my._add_info(my.snapshot)


class MayaGroupUpdaterCmd(MayaAssetUpdaterCmd):
    '''This snapshot will contain many reference to other snapshot and
    a single file that positions everything'''


    def handle_xml(my, xml):

        # get all of the references and the anim node
        ref_nodes = xml.get_nodes("snapshot/ref")
        anim_node = xml.get_node("snapshot/file[@type='anim']")
        sobject = my.snapshot.get_sobject()
        
        if my.namespace == "":
            my.namespace = sobject.get_value("name")

        for ref_node in ref_nodes:
            ref_instance_name = Xml.get_attribute(ref_node,"instance")


            # backwards compatibility: for when sets contained full Maya
            # namespaces
            if ref_instance_name.find(":") != -1:
                print "WARNING: snapshot '%s' has Maya namespaces in it" % \
                    my.snapshot.get_code()
                ref_instance_name, tmp = ref_instance_name.split(":", 1)


            # if this instance is culled, then skip loading this
            if my.loader_context.is_instance_culled(ref_instance_name):
                print "Culling [%s]" % ref_instance_name
                continue

            context = my.loader_context.get_context()

            # Get the snapshot for this reference, using the group's context.
            # Loading a group's within a context means that references
            # below will inherit this context
            ref_snapshot = my.loader_context.get_snapshot(ref_node, context)
            if ref_snapshot == None:
                msg = "Skipping [%s]: No snapshot found" %  ref_instance_name
                my.add_warning(msg, ref_instance_name)
                continue

            # group loaders always load references under the context of the
            # group, not the reference.  The reference context is ignored
            asset = Search.get_by_id(ref_snapshot.get_value('search_type'), \
                ref_snapshot.get_value('search_id'))

            updater = my.loader_context.get_updater(ref_snapshot, asset.get_code(), \
                ref_instance_name, context)
            if not updater:
                continue
            #updater.set_instance(ref_instance_name)
            updater.execute()

            # add data about this snapshot
            my._add_info(my.snapshot)



        my._add_current_node(my.asset_code, my.namespace)
        # add the information to the set
        
        my._set_node_attr("set_snapshot", "code", my.snapshot.get_code() )
        my._set_node_attr("set_snapshot", "context", my.snapshot.get_value('context') )
        my._set_node_attr("set_snapshot", "version", my.snapshot.get_version() )
        my._set_node_attr("set_snapshot", "asset_code", sobject.get_code() )
        my._set_node_attr("set_snapshot", "instance", sobject.get_code() )



class CreateSetNodeCmd(MayaAssetLoaderCmd):
    '''Implementation of the node info updater for assets.'''

    def __init__(my):
        my.asset_code = ''
        my.instance_name = ''
        my.selected_list = []
        super(CreateSetNodeCmd, my).__init__()
        
    def set_asset_code(my, asset_code):
        my.asset_code = asset_code
   
    def set_instance(my, instance_name):
        my.instance_name = instance_name

    def set_contents(my, selected_list):
        my.selected_list = selected_list

    def execute(my):

        # get the current execute parser.  Note this assume that there
        # can only be one at a time.
        # is this key OK?
        key = "LoaderCmd:top_loader"
        top_loader = Container.get(key)
        if top_loader == None:
            my.execute_xml = Xml()
            my.execute_xml.create_doc("execute")
            top_loader = my
            my.is_top_loader_flag = True
            Container.put(key, top_loader)
        else:
            my.execute_xml = top_loader.execute_xml

        my.construct()    
        # clean up the execute xml
        if top_loader == my:

            print "*"*20
            my.execute_xml.dump()
            print "*"*20

            Container.remove(key)
            
    def construct(my):
        my._add_current_node(my.asset_code, my.instance_name)
        # add a set node
        element_name = "add_to_set"
        for selected in my.selected_list:
            my._add_to_set(my.instance_name, selected)

            
   
