###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['PluginBase', 'PluginCreator', 'PluginUploader', 'PluginInstaller', 'PluginUninstaller', 'PluginSObjectAdderCmd']

import tacticenv

from pyasm.common import Xml, Config, TacticException, Environment, jsonloads, ZipUtil
from pyasm.biz import Project, Schema
from pyasm.search import Search, SearchType, TableSchemaDumper, TableDataDumper, DbContainer, Insert, DropTable, CreateTable, SearchKey, TableUndo, SqlException, SearchException
from pyasm.web import WebContainer
from pyasm.command import Command, DatabaseAction

import os, codecs, shutil, datetime

class PluginBase(Command):

    def __init__(my, **kwargs):
        super(PluginBase,my).__init__(**kwargs)

        # plugin sobject (Not really used anymore?)
        my.search_key = my.kwargs.get("search_key")

        zip_path = my.kwargs.get("zip_path")
        upload_file_name = my.kwargs.get("upload_file_name")

        my.base_dir = my.kwargs.get("base_dir")

        my.plugin_dir = my.kwargs.get("plugin_dir")
        my.manifest = my.kwargs.get("manifest")
        my.code = my.kwargs.get("code")
        my.version = my.kwargs.get("version")

        relative_dir = my.kwargs.get("relative_dir")

        my.verbose = my.kwargs.get("verbose") not in [False, 'false']
        # at the end of this, the following variables are needed in order to
        # define the plugin
        #
        #   version: the version of the plugin
        #   plugin_dir: the directory where the plugin definition is located
        #   manifest: the description of what is in the plugin

        if zip_path:

            # assume the zip path is the same as the basename
            basename = os.path.basename(zip_path)
            basename, ext = os.path.splitext(basename)
            assert ext == '.zip'

            tmp_dir = Environment.get_tmp_dir()

            unzip_dir = "%s/%s" % (tmp_dir, basename)
            if os.path.exists(unzip_dir):
               shutil.rmtree(unzip_dir)


            # unzip the file in to the tmp_dir or plugin_dir (for install)
            zip_util = ZipUtil()
            zip_util.extract(zip_path, base_dir=tmp_dir)


            # assume zip path
            my.plugin_dir, ext = os.path.splitext(zip_path)

            # mv from temp
            if my.plugin_dir != unzip_dir:
                if os.path.exists(my.plugin_dir):
                    shutil.rmtree(my.plugin_dir)
                shutil.move(unzip_dir, my.plugin_dir)

            manifest_path = "%s/manifest.xml" % my.plugin_dir
            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()


        elif upload_file_name:
            # The path is moved to the plugin dir, if this process is taking
            # "local" file (such as one uploaded)
            upload_dir = Environment.get_upload_dir()
            upload_path = "%s/%s" % (upload_dir, upload_file_name)
            plugin_base_dir = Environment.get_plugin_dir()
            dist_dir = Environment.get_dist_dir()
            if not os.path.exists(dist_dir):
                os.makedirs(dist_dir)

            basename = os.path.basename(upload_path)
            #if os.path.exists("%s/%s" % (plugin_base_dir, basename)):
            #    os.unlink("%s/%s" % (plugin_base_dir, basename) )
            #shutil.move(upload_path, plugin_base_dir)


            # copy to dist folder
            if os.path.exists("%s/%s" % (dist_dir, basename)):
                os.unlink("%s/%s" % (dist_dir, basename) )
            shutil.move(upload_path, dist_dir)

            zip_path = "%s/%s" % (dist_dir, upload_file_name)

            zip_util = ZipUtil()
            zip_util.extract(zip_path, base_dir=plugin_base_dir)

            my.plugin_dir = "%s/%s" % (plugin_base_dir, basename)
            my.plugin_dir = my.plugin_dir[:-4]
            manifest_path = "%s/manifest.xml" % (my.plugin_dir)

            if os.path.exists(manifest_path):
                f = open(manifest_path, 'r')
                my.manifest = f.read()
                f.close()
            else:
                # when uploading, this will likely not be needed
                my.manifest = "<manifest/>"
                return



        elif relative_dir:
            plugin_base_dir = Environment.get_plugin_dir()
            my.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
            manifest_path = "%s/manifest.xml" % my.plugin_dir
            if not os.path.exists(manifest_path):
                plugin_base_dir = Environment.get_builtin_plugin_dir()
                my.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
                manifest_path = "%s/manifest.xml" % my.plugin_dir

            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()

        elif my.plugin_dir:
            manifest_path = "%s/manifest.xml" % (my.plugin_dir)

            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()


        # get the plugin sobject
        elif my.search_key:
            plugin = SearchKey.get_by_search_key(my.search_key)
            my.manifest = plugin.get_value("manifest")
            my.code = plugin.get_code()
            my.version = plugin.get_value("version")


        elif my.manifest:
            # everything is extracted from the manifest later
            pass


        elif my.code:
            search = Search("config/plugin")
            search.add_filter("code", my.code)
            plugin = search.get_sobject()
            # In case there is extra plugins folder which is the case when the user 
            # is developing. 
            relative_dir = plugin.get_value("rel_dir")
             
            plugin_base_dir = Environment.get_plugin_dir()
            my.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
            
            # TODO: fix the ZipUtil.zip_dir()
            manifest_path = "%s/manifest.xml" % my.plugin_dir
            if not os.path.exists(manifest_path):
                plugin_base_dir = Environment.get_builtin_plugin_dir()
                my.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
                manifest_path = "%s/manifest.xml" % my.plugin_dir
                
            if os.path.exists(manifest_path):
                f = open(manifest_path, 'r')
                my.manifest = f.read()
                f.close()
            else:
                # this condition happens likely for a versioned installed plugin from a zip file
                # where it starts with an extra folder "plugins" and the rel_dir has not been recorded properly
                my.manifest = plugin.get_value("manifest") 
            
            my.code = plugin.get_code()
            my.version = plugin.get_value("version")

        else:
            raise Exception("No plugin found")


        # assertions
        assert my.manifest


        # read the xml
        my.xml = Xml()
        my.xml.read_string(my.manifest)


        # if code is passed in, then use that.
        if not my.code:
            my.code = my.xml.get_value("manifest/data/code")
            # old implementation
            if not my.code:
                my.code = my.xml.get_value("manifest/@code")
        if not my.version:
            my.version = my.xml.get_value("manifest/data/version")

        assert my.code


        if not my.base_dir:
            if my.code.startswith("TACTIC"):
                my.base_dir = Environment.get_builtin_plugin_dir()
            else:
                my.base_dir = Environment.get_plugin_dir()

        # set the base directory for this particular plugin
        if not my.plugin_dir:
            if my.version:
                my.plugin_dir = "%s/%s-%s" % (my.base_dir, my.code, my.version)
            else:
                my.plugin_dir = "%s/%s" % (my.base_dir, my.code)



    def get_sobjects_by_node(my, node):
        # get the sobjects        
        search_type = my.xml.get_attribute(node, "search_type")
        expr = my.xml.get_attribute(node, "expression")
        code = my.xml.get_attribute(node, "code")


        if expr:
            sobjects = Search.eval(expr)

        elif search_type:
            search = Search(search_type)
            search.set_show_retired(True)
            if code:
                search.add_filter("code", code)


            # have some specific attributes for specific search types
            # can use wildcards like % and *
            if search_type == 'config/widget_config':
                view = Xml.get_attribute(node, "view")
                if view:
                    ignore_columns = 'id,code'
                    Xml.set_attribute(node, "ignore_columns", ignore_columns)

                    if view.find("%") != -1 or view.find("*") != -1:
                        view = view.replace("*", "%")
                        view = view.replace("/", ".")
                        search.add_filter("view", view, op="like")
                    else:
                        search.add_filter("view", view)

            elif search_type == 'config/url':
                url = Xml.get_attribute(node, "url")
                if url:
                    ignore_columns = 'id,code'
                    Xml.set_attribute(node, "ignore_columns", ignore_columns)
                    if url.find("%") != -1:
                        search.add_filter("url", url, op="like")
                    else:
                        search.add_filter("url", url)
 


            search.add_order_by("id")
            sobjects = search.get_sobjects()
        else:
            sobjects = []


        return sobjects




 

class PluginCreator(PluginBase):
    '''Class to create a plugin from an existing project'''

    def get_zip_path(my):
        return my.zip_path


    def execute(my):

        force = my.kwargs.get("force")
        clean = my.kwargs.get("clean")
        if clean in [False, 'false']:
            clean = False

        # ensure that plugin dir is empty
        if os.path.exists(my.plugin_dir):
            if clean:
                if force in ['true', True]:
                    shutil.rmtree(my.plugin_dir)
                else:
                    raise Exception("Plugin is already located at [%s]" % my.plugin_dir)
       
        
        if not os.path.exists(my.plugin_dir):
            os.makedirs(my.plugin_dir)


        # build the information from the manifest

        code = my.kwargs.get("code")
        if not code:
            code = my.xml.get_value("manifest/@code")

        version = my.kwargs.get("version")
        if not version:
            version = my.xml.get_value("manifest/@version")

        nodes = my.xml.get_nodes("manifest/*")


        # clean out all of the files
        my.delete_files(nodes)


        has_info = False
        sobjects = []

        # handle all of the nodes in the manifest
        for i, node in enumerate(nodes):
            name = my.xml.get_node_name(node)
            if name == 'sobject':
                dumped_sobjects = my.handle_sobject(node)
                if not dumped_sobjects:
                    dumped_sobjects = []
                sobjects.extend(dumped_sobjects)
            elif name == 'search_type':
                my.handle_search_type(node)
            elif name == 'include':
                my.handle_include(node)


        # make sure there is a data node and handle it
        data_node = my.xml.get_node("manifest/data")
        if data_node is None:
            root_node = my.xml.get_root_node()
            data_node = my.xml.create_element("data")
            child = my.xml.get_first_child(root_node)
            if child is None:
                my.xml.append_child(root_node, data_node)
            else:
                my.xml.insert_before(data_node, child)

        my.handle_data(data_node)
            
 



        manifest_path = "%s/manifest.xml" % (my.plugin_dir)
        file = codecs.getwriter('utf8')(open(manifest_path, 'wb'))
        file.write(my.xml.to_string())
        file.close()

        # FIXME: leaving this out for now
        #my.handle_snapshots()

        dist_dir = my.kwargs.get("dist_dir")
        if not dist_dir:
            dist_dir = Environment.get_dist_dir()

        # get the basename of the code
        basecode = os.path.basename(my.code)

        # zip up the contents
        import zipfile
        if version:
            zip_path = "%s/%s-%s.zip" % (dist_dir, basecode, version)
        else:
            zip_path = "%s/%s.zip" % (dist_dir, basecode)

        print "Zipping up plugin file [%s]" % zip_path
        print "    from [%s]" % my.plugin_dir
        from pyasm.common import ZipUtil
        ignore_dirs = ['.svn']

        # ignore file
        #ignore_path = "%s/.ignore" % (my.plugin_dir)

        parts = my.code.split("/")
        root_dir = "%s/%s" % (my.base_dir, parts[0])
        if len(parts) >= 2:
            include_dirs = ["/".join(parts[1:])]
        else:
            include_dirs = None

        ZipUtil.zip_dir(root_dir, zip_path, ignore_dirs=ignore_dirs, include_dirs=include_dirs)
        print "... done"

        #f = codecs.open(zip_path, 'w')
        #zip = zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_DEFLATED)
        #my.zip_dir(zip, my.plugin_dir, "asset", rel_dir='')

        my.zip_path = zip_path

        # encrypt the file
        """
        print "encrypting!!!!", zip_path
        my.enc_path = "%s.enc" % zip_path
        from pyasm.common import EncryptUtil
        ticket = "OMG"
        encrypt = EncryptUtil(ticket)
        encrypt.encrypt_file(zip_path)
        """


        # register the plugin into the current project
        if my.kwargs.get("register") in [True, 'true']:

            # first check if a plugin with this code already exists
            plugin = Search.get_by_code("config/plugin", my.code)
            if plugin:
                raise TacticException("Plugin [%s] already existed in the project." % my.code)
            # create a new one
            plugin = SearchType.create("config/plugin")
            plugin.set_value("code", my.code)
           
            # update the information
            if version:
                plugin.set_value("version", version)

            # NOTE: not sure if this is desirable
            plugin.set_value("manifest", my.manifest)

            if my.plugin_dir.startswith(my.base_dir):
                rel_dir = my.plugin_dir.replace(my.base_dir, "")
                rel_dir = rel_dir.lstrip("/")
                plugin.set_value("rel_dir", rel_dir)

            plugin.commit()

        # TODO: consider updating the manifest if plugin sobject exists

        # record all of the sobject exported
        for sobject in sobjects:                    
            plugin_content = SearchType.create("config/plugin_content")
            plugin_content.set_value("search_type", sobject.get_search_type())
            plugin_content.set_value("search_code", sobject.get_code())
            plugin_content.set_value("plugin_code", my.code)
            plugin_content.commit()



    def delete_files(my, nodes):

        # clean out all of the files
        for node in nodes:
            name = my.xml.get_node_name(node)

            if name == "include":
                path = my.xml.get_attribute(node, "path")
                if not path:
                    print("WARNING: No path found for search type in manifest")
                    continue

                path = "%s/%s" % (my.plugin_dir, path)

                if path.endswith(".py"):
                    from tactic.command import PythonCmd
                    cmd = PythonCmd(file_path=path)
                    manifest = cmd.execute()

                    xml = Xml()
                    xml.read_string(manifest)
                    include_nodes = xml.get_nodes("manifest/*")

                    my.delete_files(include_nodes)

            else:
                path = my.get_path_from_node(node)
                if path and os.path.exists(path):
                    print "Deleting: ", path
                    os.unlink(path)



    def handle_data(my, node):

        for name in ['code', 'title', 'version', 'description']:
            value = my.kwargs.get(name)
            if value:
                children = my.xml.get_children(node)
                old_node = None
                for child_node in children:
                    child_name = my.xml.get_node_name(child_node)
                    if child_name == name:
                        old_node = child_node

                value_node = my.xml.create_element(name)
                my.xml.set_node_value(value_node, value)
                if old_node is None:
                    my.xml.append_child(node, value_node)
                else:
                    my.xml.replace_child(node, old_node, value_node)
            
 


    def zip_dir(my, zip, base_dir, plugin, rel_dir=''):

        plugin = os.path.basename(base_dir)

        if rel_dir:
            dir = '%s/%s' % (base_dir, rel_dir)
        else:
            dir = base_dir
        
        filenames = os.listdir(dir)

        for filename in filenames:
            path = "%s/%s" % (dir, filename)
            print path
            if os.path.isdir(path):
                print " ... directory!"
            if os.path.isdir(path):
                if rel_dir:
                    my.zip_dir(zip, base_dir, plugin, "%s/%s" % (rel_dir,filename))
                else:
                    my.zip_dir(zip, base_dir, plugin, filename)
                continue


            filename = str(filename)
            path = str(path)
            if rel_dir:
                zip.write(path, str("%s/%s/%s" % (plugin, rel_dir, filename)))
            else:
                zip.write(path, str("%s/%s" % (plugin,filename)))


    

    def get_path_from_node(my, node):
        path = my.xml.get_attribute(node, "path")
        if not path:
            search_type = my.xml.get_attribute(node, "search_type")
            if search_type:
                search_type_obj = SearchType.get(search_type)
                search_type = search_type_obj.get_base_key()
                path = "%s.spt" % search_type.replace("/","_")

        if path:
            path = "%s/%s" % (my.plugin_dir, path)

        return path



    def handle_sobject(my, node):
        search_type = my.xml.get_attribute(node, "search_type")

        include_id = my.xml.get_attribute(node, "include_id")
        if include_id in [True, 'true']:
            include_id = True
        else:
            include_id = False


        ignore_columns = Xml.get_attribute(node, "ignore_columns")
        if ignore_columns:
            ignore_columns = ignore_columns.split(",")
            ignore_columns = [x.strip() for x in ignore_columns]
        else:
            ignore_columns = []


        sobjects = my.get_sobjects_by_node(node)
        if not sobjects:
            print "Skipping as no sobjects found for [%s]" %search_type
            return []



        # If there are no sobjects, then no file is created because
        # no path can be extracted.

        path = my.get_path_from_node(node)

        print "Writing: ", path
        fmode = 'w'
        if os.path.exists(path):
            fmode = 'a'
        if not sobjects:
            # write out an empty file
            #f = open(path, 'w')
            f = codecs.open(path, fmode, 'utf-8')
            f.close()
            return []

        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        if search_type == 'config/widget_config':
            dumper.set_ignore_columns(['code'])
        dumper.set_include_id(include_id)
        dumper.set_ignore_columns(ignore_columns)
        dumper.set_sobjects(sobjects)
        dumper.dump_tactic_inserts(path, mode='sobject')

        print "\t....dumped [%s] entries" % (len(sobjects))

        return sobjects



    def handle_search_type(my, node):
        search_type = my.xml.get_attribute(node, "code")
        if not search_type:
            raise TacticException("No code found for search type in manifest")

        path = my.xml.get_attribute(node, "path")
        if not path:
            path = "%s.spt" % search_type.replace("/", "_")

        path = "%s/%s" % (my.plugin_dir, path)

        if os.path.exists(path):
            os.unlink(path)

        # dump out search type registration
        search = Search("sthpw/search_object")
        search.add_filter("search_type", search_type)
        sobject = search.get_sobject()
        if not sobject:
            raise TacticException("Search type [%s] does not exist" % search_type)

        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_include_id(False)
        dumper.set_sobjects([sobject])
        dumper.dump_tactic_inserts(path, mode='sobject')


        ignore_columns = Xml.get_attribute(node, "ignore_columns")
        if ignore_columns:
            ignore_columns = ignore_columns.split(",")
            ignore_columns = [x.strip() for x in ignore_columns]
        else:
            ignore_columns = []


        # dump out the table definition
        dumper = TableSchemaDumper(search_type)
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_ignore_columns(ignore_columns)
        dumper.dump_to_tactic(path, mode='sobject')



    def handle_include(my, node):
        path = my.xml.get_attribute(node, "path")
        if not path:
            raise TacticException("No path found for search type in manifest")

        path = "%s/%s" % (my.plugin_dir, path)

        if path.endswith(".py"):
            from tactic.command import PythonCmd
            cmd = PythonCmd(file_path=path)
            manifest = cmd.execute()

        xml = Xml()
        xml.read_string(manifest)
        nodes = xml.get_nodes("manifest/*")

        sobjects = []
        for i, node in enumerate(nodes):
            name = my.xml.get_node_name(node)
            if name == 'sobject':
                dumped_sobjects = my.handle_sobject(node)
                if not dumped_sobjects:
                    dumped_sobjects = []
                sobjects.extend(dumped_sobjects)
            elif name == 'search_type':
                my.handle_search_type(node)
            elif name == 'include':
                my.handle_include(node)








    def handle_snapshots(my):


        path = "__snapshot_files.spt"
        path = "%s/%s" % (my.plugin_dir, path)
        print "Writing: ", path
        # write out an empty file
        #f = open(path, 'w')

        fmode = 'w'
        if os.path.exists(path):
            fmode = 'a'
        f = codecs.open(path, fmode, 'utf-8')
        f.close()


        # get all of the latest snapshots for this plugin
        search = Search("sthpw/snapshot")
        search.add_parent_filter(my.plugin)
        search.add_filter("is_latest", True)
        snapshots = search.get_sobjects()

        if not snapshots:
            return

        # dump out these snapshots
        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_include_id(False)
        dumper.set_sobjects(snapshots)
        dumper.dump_tactic_inserts(path, mode='sobject')

        # get all of the files for all of the snapshots and copy the director
        # structure


        # get all of the latest snapshots for this plugin
        search = Search("sthpw/file")
        search.add_relationship_filters(snapshots)
        files = search.get_sobjects()

        # dump out these snapshots
        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_include_id(False)
        dumper.set_sobjects(files)
        dumper.dump_tactic_inserts(path, mode='sobject')

        new_dir = "%s/files" % (my.plugin_dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        for snapshot in snapshots:
            paths = snapshot.get_all_lib_paths(mode="lib")
            for path in paths:
                file_name = os.path.basename(path)
                new_path = "%s/%s" % (new_dir, file_name)

                shutil.copy(path, new_path)



class PluginUploader(PluginBase):
    def execute(my):
        pass



class PluginInstaller(PluginBase):

    def execute(my):

        # install the plugin
        mode = my.kwargs.get("mode")
        if not mode:
            mode = 'install'

        # register mode actually reads the manifest.
        if mode == 'install':
            nodes = my.xml.get_nodes("manifest/*")
        else:
            # DEPRECATED
            # dynamically create the plugin node in the manifest
            plugin_node = my.xml.create_element("sobject")
            my.xml.set_attribute(plugin_node, "path", "config_plugin.spt")
            nodes = []
            nodes.insert(0, plugin_node)

        # register the plugin.
        register = my.kwargs.get("register")
        code = None
        plugin = None
        if register in ['true', True]:
            node = my.xml.get_node("manifest/data")
            data = my.xml.get_node_values_of_children(node)

            code = data.get("code")
            version = data.get("version")

            # first check if a plugin with this code already exists
            plugin = Search.get_by_code("config/plugin", code)
            if plugin:
                # uninstall the plugin???
                pass
            else:
                # create a new one
                plugin = SearchType.create("config/plugin")
                plugin.set_value("code", code)

           
            # update the information
            if version:
                plugin.set_value("version", version)

            # NOTE: is this really needed?
            plugin.set_value("manifest", my.manifest)

            if my.plugin_dir.startswith(my.base_dir):
                rel_dir = my.plugin_dir.replace(my.base_dir, "")
                rel_dir = rel_dir.lstrip("/")
                plugin.set_value("rel_dir", rel_dir)

            plugin.commit()

        my.plugin = plugin



        my.import_manifest(nodes)

        # Users see Activate in the UI
        label = mode
        if mode == 'install':
            label = 'activate'

        if code:
            my.add_description('%s plugin [%s]' % (label.capitalize(), code))



    def import_manifest(my, nodes):
        paths_read = []

        for node in nodes:

            node_name = my.xml.get_node_name(node)
            if node_name == 'search_type':
                search_type = my.xml.get_attribute(node, 'code')

                # implicitly add the entry to the schema table.
                # Reset the cache every time to ensure that any updates to
                # the scehma are reflected here.
                schema = Schema.get(reset_cache=True)
                xml = schema.get_xml()
                schema_node = xml.get_node("schema/search_type[@name='%s']" % search_type)
                parent = xml.get_node("schema")
                if schema_node == None:
                    schema_node = xml.create_element("search_type")
                    xml.set_attribute(schema_node, "name", search_type)

                    #parent = xml.get_parent(node)
                    xml.append_child(parent, schema_node)
                    schema.set_value('schema', xml.to_string() )
                    schema.commit()

                    # TODO: connections?

                path = my.xml.get_attribute(node, "path")
                if not path:
                    path = "%s.spt" % search_type.replace("/", "_")

                path = "%s/%s" % (my.plugin_dir, path)

                if path in paths_read:
                    continue

                if my.verbose:
                    print "Reading search_type: ", path

                # NOTE: priviledged knowledge of the order or return values
                jobs = my.import_data(path, commit=True)

                paths_read.append(path)

                if not jobs:
                    continue

                search_type_obj = jobs[0]

                if len(jobs) == 1:
                    # only the search type was defined
                    table = None
                else:
                    table = jobs[1]


                try:
                    # check to see if the search type already exists
                    search_type_chk = SearchType.get(search_type)
                    if search_type_chk:
                        if my.verbose:
                            print 'WARNING: Search Type [%s] is already registered' % search_type_chk.get_value("search_type")
                    else:
                        search_type_obj.commit()
                except SearchException, e:
                    if e.__str__().find('not registered') != -1:
                        search_type_obj.commit()

                # check if table exists 
                has_table = False
                if has_table:
                    if my.verbose:
                        print 'WARNING: Table [%s] already exists'
                elif table:
                    #print table.get_statement()
                    if table:
                        database = table.get_database()
                        table_name = table.get_table()

                        TableUndo.log(search_type, database, table_name)




            elif node_name == 'sobject':
                path = my.xml.get_attribute(node, "path")
                search_type = my.xml.get_attribute(node, "search_type")
                seq_max = my.xml.get_attribute(node, "seq_max")
                try:
                    if seq_max:
                        seq_max = int(seq_max)
                except ValueError:
                    seq_max = 0

                if not path:
                    if search_type:
                        path = "%s.spt" % search_type.replace("/","_")
                if not path:
                    raise TacticException("No path specified")

                path = "%s/%s" % (my.plugin_dir, path)
                if path in paths_read:
                    continue

                unique = my.xml.get_attribute(node, "unique")
                if unique == 'true':
                    unique = True
                else:
                    unique = False

                if my.verbose: 
                    print "Reading: ", path
                # jobs doesn't matter for sobject node
                jobs = my.import_data(path, unique=unique)

                # compare sequence 
                st_obj = SearchType.get(search_type)
                SearchType.sequence_nextval(search_type)
                cur_seq_id = SearchType.sequence_currval(search_type)

                sql = DbContainer.get("sthpw")
                if seq_max > 0 and seq_max > cur_seq_id:
                    # TODO: SQL Server - Reseed the sequences instead of passing.
                    if sql.get_database_type() == 'SQLServer':
                        pass
                    else:
                        SearchType.sequence_setval(search_type, seq_max)
                else:
                    cur_seq_id -= 1
                    # TODO: SQL Server - Reseed the sequences instead of passing.
                    if sql.get_database_type() == 'SQLServer':
                        pass
                    else:
                        # this is a db requirement
                        if cur_seq_id > 0:
                            SearchType.sequence_setval(search_type, cur_seq_id)


                
                paths_read.append(path)


            elif node_name == 'include':

                path = my.xml.get_attribute(node, "path")

                path = "%s/%s" % (my.plugin_dir, path)

                from tactic.command import PythonCmd
                cmd = PythonCmd(file_path=path)
                manifest = cmd.execute()

                xml = Xml()
                xml.read_string(manifest)
                nodes = xml.get_nodes("manifest/*")

                my.import_manifest(nodes)





        ''' TODO: do we store the transaction here???
        try:
            from pyasm.search import Transaction
            transaction = Transaction.get()
            transaction_str = transaction.xml.to_string()
            my.plugin.set_value("transaction", transaction_str)
            my.plugin.commit()
        except Exception, e:
            print "Error: ", e.message
        '''


    def get_unique_sobject(my, sobject):
        '''get unique sobject in the existing table when installing plugin'''
        base_st = sobject.get_base_search_type()
        if base_st == 'config/widget_config':
            cols = ['view','search_type','category','widget_type']
        elif base_st == 'config/naming':
            cols = ['search_type','context','checkin_type','snapshot_type','condition','latest_versionless','current_versionless','manual_version']
        elif base_st == 'config/url':
            cols = ['url']
        else:
            cols = ['code']

        search = Search( sobject.get_base_search_type() )
        for col in cols:
            value = sobject.get_value(col)
            if value:
                search.add_filter(col, value)   
        unique_sobject = search.get_sobject()
        return unique_sobject


    def import_data(my, path, commit=True, unique=False):
        if not os.path.exists(path):
            # This is printed too often in harmless situations
            #print "WARNING: path [%s] does not exist" % path
            return []

        #f = codecs.open(path, 'r', 'utf-8')
        f = codecs.getreader('utf8')(open(path, 'r'))
        statement = []
        count = 0

        insert = None
        table = None
        sobject = None

        jobs = []

        filter_line_handler = my.kwargs.get('filter_line_handler')
        filter_sobject_handler = my.kwargs.get('filter_sobject_handler')

        for line in f:

            # FIXME: this SQLServer specific
            #if line.startswith("insert.set_value('Version'"):
            #    #line = "insert.set_value('Version', '')"
            #    continue


            if filter_line_handler:
                line = filter_line_handler(path, line)
                if line == None:
                    continue


            if line.startswith("#-- Start Entry --#"):
                statement = []
            elif line.startswith("#-- End Entry --#"):
                if not statement:
                    continue
                # strip out a line feeds and add proper new lines
                #statement_str = "\n".join([x.strip("\n") for x in statement])
                statement_str = "\n".join([x.rstrip("\r\n") for x in statement])

                try:
                    exec(statement_str)
                except SqlException, e:
                    print "ERROR (SQLException): ", e
                except Exception, e:
                    print "ERROR: ", e
                    print
                    print statement_str
                    print
                    #raise
                    continue


                sobject = insert

                if sobject:
                    jobs.append(sobject)

                    stype_id  = 0
                    if sobject.get_base_search_type() =='sthpw/search_object':
                        stype_id = Search.eval("@GET(sthpw/search_object['search_type', '%s'].id)" %sobject.get_value('search_type'), single=True)

                    else:
                        # if there is an id, then set the sobject to be insert
                        sobject_id = sobject.get_id()
                        if sobject_id and sobject_id != -1:
                            sobject.set_force_insert(True)


                    # if unique, then check to see if it already exists.
                    # Same idea with stype_exists
                    # if so, take the id to turn this from an insert to an
                    # update operation writing over existing data
                    if stype_id:
                        sobject.set_value("id", stype_id)


                    if filter_sobject_handler:
                        sobject = filter_sobject_handler(sobject)
                    
                    if unique:
                        unique_sobject = my.get_unique_sobject(sobject)
                        
                        if unique_sobject:
                            sobject.set_value("id", unique_sobject.get_id() )

                        if sobject == None:
                            continue


                    # if the search type is in sthpw namespace, then change
                    # the project code to the current project
                    base_search_type = sobject.get_base_search_type()
                    if base_search_type.startswith("sthpw/"):
                        project = Project.get()
                        project_code = project.get_value("code")
                        if SearchType.column_exists(sobject.get_search_type(), "project_code"):
                            sobject.set_value("project_code", project_code)

                        if base_search_type == "sthpw/schema":
                            sobject.set_value("code", project_code)


                    try:
                        if commit:
                            sobject.commit(triggers=False)

                            if my.plugin: 
                                plugin_content = SearchType.create("config/plugin_content")
                                plugin_content.set_value("search_type", sobject.get_search_type())
                                plugin_content.set_value("search_code", sobject.get_code())
                                plugin_content.set_value("plugin_code", my.plugin.get_code())
                                plugin_content.commit()

                    except UnicodeDecodeError, e:
                        print "Skipping due to unicode decode error: [%s]" % statement_str
                        continue


                if table:
                    jobs.append(table)
                    if commit:
                        table.commit()
                elif sobject == None:
                    # this is meant for saying the table is None for a search type creation
                    jobs.append(None)

                count += 1
                table = None
                insert = None
                sobject = None
            else:
                statement.append(line)
        f.close()

        if my.verbose:
            print "\t... added [%s] entries" % count
        return jobs




class PluginUninstaller(PluginBase):
    # NOTE: this is still a work in progress.  It will remove entries added
    # by the plugin, but it is not clear that this is what we want to do.

    def execute(my):

        # uninstall the plugin
        nodes = my.xml.get_nodes("manifest/*")

        nodes.reverse()

        my.handle_nodes(nodes)
        
        my.add_description('Remove plugin [%s]' %my.code)
        
    def handle_nodes(my, nodes):

        for node in nodes:
            node_name = my.xml.get_node_name(node)
            if node_name == 'search_type':
                my.remove_search_type(node)
            elif node_name == 'sobject':
                my.remove_sobjects(node)
            elif node_name == 'include':
                my.handle_include(node)


        # remove contents
        search = Search("config/plugin_content")
        search.add_filter("plugin_code", my.code)
        plugin_contents = search.get_sobjects()
        for plugin_content in plugin_contents:
            plugin_content.delete()



        # deregister the plugin
        plugin = Search.eval("@SOBJECT(config/plugin['code','%s'])" % my.code, single=True)
        if plugin:
            plugin.delete()


    def remove_search_type(my, node):
        search_type = my.xml.get_attribute(node, 'code')

        # get sobject entry
        search = Search("sthpw/search_object")
        search.add_filter("search_type", search_type)
        search_type_sobj = search.get_sobject()

        if not search_type_sobj:
            print "WARNING: Search type [%s] does not exist" % search_type
        else:
            # dump the table first ???

            # get the table and remove it ???
            from pyasm.search import DropTable
            try:
                table_drop = DropTable(search_type)
                table_drop.commit()
                # NOTE: do we need to log the undo for this?
            except Exception, e:
                print "Error: ", e.message


        # NOTE: it is not clear that unloading a plugin should delete
        # the search type ... this search type (at present) can be
        # shared amongst multiple projects and this will break it
        return

        # remove entry from schema
        schema = Schema.get()
        xml = schema.get_xml()
        node = xml.get_node("schema/search_type[@name='%s']" % search_type)
        if node != None:
            parent = xml.get_parent(node)
            xml.remove_child(parent, node)
            schema.set_value('schema', xml.to_string() )
            schema.commit()

        # remove search type entry
        if search_type.startswith("config/") or search_type.startswith("sthpw/"):
            print "WARNING: A plugin cannot deregister a search type from the 'sthpw' or 'config' namespace'"
        else:

            search = Search("sthpw/search_object")
            search.add_filter("search_type", search_type)
            search_type_sobj = search.get_sobject()
            if search_type_sobj:
                search_type_sobj.delete()




    def remove_sobjects(my, node):

        sobjects = my.get_sobjects_by_node(node)
        if not sobjects:
            print "Skipping as no sobjects found for: ", node
            return

        # delete all the sobjects present in the plugin
        for sobject in sobjects:
            sobject.delete()


    def handle_include(my, node):
        path = my.xml.get_attribute(node, "path")
        if not path:
            raise TacticException("No path found for search type in manifest")

        path = "%s/%s" % (my.plugin_dir, path)

        if path.endswith(".py"):
            from tactic.command import PythonCmd
            cmd = PythonCmd(file_path=path)
            manifest = cmd.execute()

        xml = Xml()
        xml.read_string(manifest)
        nodes = xml.get_nodes("manifest/*")
        nodes.reverse()

        my.handle_nodes(nodes)

 



# How to define a plugin??
def main(mode):
    manifest = '''
    <manifest code='test_plugin' version='1'>
    <!--
    <search_type code="prod/asset" path="search_type.spt"/>
    -->
    <sobject expr="@SOBJECT(config/custom_script['code','5CG'])" path="file.spt"/>
    <sobject expr="@SOBJECT(config/widget_config['code','35CG'])" path="file2.spt"/>
    </manifest>
    '''


    if mode == 'create':
        plugin = PluginCreator(manifest=manifest)
    elif mode == 'install':
        plugin = PluginInstaller(manifest=manifest)
    elif mode == 'uninstall':
        plugin = PluginUninstaller(manifest=manifest)

    Command.execute_cmd(plugin)




class PluginSObjectAdderCmd(DatabaseAction):
    '''Used when drop sobjects into the plugin drop zone'''
    def execute(my):
        plugin = my.sobject

        web = WebContainer.get_web()
        value = web.get_form_value( my.get_input_name() )
        if not value:
            return
        src_search_keys = jsonloads(value)


        manifest = plugin.get_xml_value("manifest")

        top_node = manifest.get_node("manifest")

        for search_key in src_search_keys:
            sobject = SearchKey.get_by_search_key(search_key)

            node = manifest.create_element("sobject")

            # For now, a plugin must contain project specfic entries
            search_type = sobject.get_base_search_type()
            code = sobject.get_value("code")
            manifest.set_attribute(node, "search_type", search_type)
            manifest.set_attribute(node, "code", code)

            #search_key = SearchKey.get_by_sobject(sobject)
            #manifest.set_attribute(node, "search_key", search_key)

            manifest.append_child(top_node, node)

        plugin.set_value("manifest", manifest.to_string() )
        plugin.commit()


if __name__ == '__main__':
    from pyasm.security import Batch
    Batch(project_code='japan')

    mode = 'install'
    main(mode)




