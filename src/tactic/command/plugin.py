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


__all__ = ['PluginBase', 'PluginCreator', 'PluginUploader', 'PluginInstaller', 'PluginUninstaller', 'PluginReloader', 'PluginSObjectAdderCmd', 'PluginTools']

import tacticenv

from pyasm.common import Xml, Config, TacticException, Environment, jsonloads, ZipUtil, Common
from pyasm.biz import Project, Schema
from pyasm.security import Sudo
from pyasm.search import Search, SearchType, TableSchemaDumper, TableDataDumper, DbContainer, Insert, DropTable, CreateTable, CreateView, SearchKey, TableUndo, SqlException, SearchException
from pyasm.web import WebContainer
from pyasm.command import Command, DatabaseAction

import os, codecs, shutil, datetime, sys, functools

IS_Pv3 = sys.version_info[0] > 2





class PluginBase(Command):

    UNIQUE_DICT = {
                'config/widget_config': ['view','search_type','category','widget_type','login'],
                'config/naming':  ['search_type','context','checkin_type','snapshot_type','condition','latest_versionless','current_versionless','manual_version'],
                'config/custom_script':  ['folder','title'],
                'config/url': ['url']
        }

    def __init__(self, **kwargs):
        super(PluginBase,self).__init__(**kwargs)

        # plugin sobject (Not really used anymore?)
        self.search_key = self.kwargs.get("search_key")

        zip_path = self.kwargs.get("zip_path")
        upload_file_name = self.kwargs.get("upload_file_name")

        self.base_dir = self.kwargs.get("base_dir")

        self.plugin_dir = self.kwargs.get("plugin_dir")
        self.manifest = self.kwargs.get("manifest")
        self.code = self.kwargs.get("code")
        self.version = self.kwargs.get("version")

        relative_dir = self.kwargs.get("relative_dir")

        self.verbose = self.kwargs.get("verbose") not in [False, 'false']
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
            self.plugin_dir, ext = os.path.splitext(zip_path)

            # mv from temp
            if self.plugin_dir != unzip_dir:
                if os.path.exists(self.plugin_dir):
                    shutil.rmtree(self.plugin_dir)
                shutil.move(unzip_dir, self.plugin_dir)

            manifest_path = "%s/manifest.xml" % self.plugin_dir
            f = open(manifest_path, 'r')
            self.manifest = f.read()
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

            self.plugin_dir = "%s/%s" % (plugin_base_dir, basename)
            self.plugin_dir = self.plugin_dir[:-4]
            manifest_path = "%s/manifest.xml" % (self.plugin_dir)

            if os.path.exists(manifest_path):
                f = open(manifest_path, 'r')
                self.manifest = f.read()
                f.close()
            else:
                # when uploading, this will likely not be needed
                self.manifest = "<manifest/>"
                return



        elif relative_dir:
            plugin_base_dir = Environment.get_plugin_dir()
            self.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
            manifest_path = "%s/manifest.xml" % self.plugin_dir
            if not os.path.exists(manifest_path):
                plugin_base_dir = Environment.get_builtin_plugin_dir()
                self.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
                manifest_path = "%s/manifest.xml" % self.plugin_dir


            f = open(manifest_path, 'r')
            self.manifest = f.read()
            f.close()

        elif self.plugin_dir:
            manifest_path = "%s/manifest.xml" % (self.plugin_dir)

            f = open(manifest_path, 'r')
            self.manifest = f.read()
            f.close()


        # get the plugin sobject
        elif self.search_key:
            plugin = SearchKey.get_by_search_key(self.search_key)
            self.manifest = plugin.get_value("manifest")
            self.code = plugin.get_code()
            self.version = plugin.get_value("version")


        elif self.manifest:
            # everything is extracted from the manifest later
            pass


        elif self.code:
            search = Search("config/plugin")
            search.add_filter("code", self.code)
            plugin = search.get_sobject()
            # In case there is extra plugins folder which is the case when the user
            # is developing.
            relative_dir = plugin.get_value("rel_dir")
            if not relative_dir:
                relative_dir = plugin.get_value("code")

            if self.code.startswith("TACTIC"):
                plugin_base_dir = Environment.get_builtin_plugin_dir()
            else:
                plugin_base_dir = Environment.get_plugin_dir()

            self.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)

            # TODO: fix the ZipUtil.zip_dir()
            manifest_path = "%s/manifest.xml" % self.plugin_dir
            if not os.path.exists(manifest_path):
                plugin_base_dir = Environment.get_builtin_plugin_dir()
                self.plugin_dir = "%s/%s" % (plugin_base_dir, relative_dir)
                manifest_path = "%s/manifest.xml" % self.plugin_dir

            if os.path.exists(manifest_path):
                f = open(manifest_path, 'r')
                self.manifest = f.read()
                f.close()
            else:
                # this condition happens likely for a versioned installed plugin from a zip file
                # where it starts with an extra folder "plugins" and the rel_dir has not been recorded properly
                self.manifest = plugin.get_value("manifest")

            self.code = plugin.get_code()
            self.version = plugin.get_value("version")

        else:
            raise Exception("No plugin found")


        # assertions
        assert self.manifest


        # read the xml
        self.xml = Xml()
        self.xml.read_string(self.manifest)


        # if code is passed in, then use that.
        if not self.code:
            self.code = self.xml.get_value("manifest/data/code")
            # old implementation
            if not self.code:
                self.code = self.xml.get_value("manifest/@code")
        if not self.version:
            self.version = self.xml.get_value("manifest/data/version")

        assert self.code


        if not self.base_dir:
            if self.code.startswith("TACTIC"):
                self.base_dir = Environment.get_builtin_plugin_dir()
            else:
                self.base_dir = Environment.get_plugin_dir()

        # set the base directory for this particular plugin
        if not self.plugin_dir:
            if self.version:
                self.plugin_dir = "%s/%s-%s" % (self.base_dir, self.code, self.version)
            else:
                self.plugin_dir = "%s/%s" % (self.base_dir, self.code)



    def get_sobjects_by_node(self, node):
        # get the sobjects
        search_type = self.xml.get_attribute(node, "search_type")
        expr = self.xml.get_attribute(node, "expression")
        code = self.xml.get_attribute(node, "code")

        try:
            search_type_sobj = SearchType.get(search_type)
        except SearchException as e:
            return []


        if expr:
            sudo = Sudo()
            try:
                sobjects = Search.eval(expr)
            finally:
                sudo.exit()


            # order by id
            def sort_sobjects(a, b):
                a_id = a.get_code()
                b_id = b.get_code()

                if a_id > b_id:
                    return 1
                elif a_id == b_id:
                    return 0
                else:
                    return -1

            #sobjects.sort(sort_sobjects)
            sobjects = sorted(sobjects,key=functools.cmp_to_key(sort_sobjects))


        elif search_type:
            try:
                search = Search(search_type)
            except SearchException as e:
                return []


            search.set_show_retired(True)
            if code:
                search.add_filter("code", code)


            # have some specific attributes for specific search types
            # can use wildcards like % and *
            if search_type_sobj.get_base_key() == 'config/widget_config':
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



    def get_path_from_node(self, node):
        path = self.xml.get_attribute(node, "path")
        if not path:
            search_type = Xml.get_attribute(node, "search_type")
            if search_type:
                search_type_obj = SearchType.get(search_type)
                search_type = search_type_obj.get_base_key()
                path = "%s.spt" % search_type.replace("/","_")

        if path:
            path = "%s/%s" % (self.plugin_dir, path)

        return path





class PluginCreator(PluginBase):
    '''Class to create a plugin from an existing project'''

    def get_zip_path(self):
        return self.zip_path


    def execute(self):

        force = self.kwargs.get("force")
        clean = self.kwargs.get("clean")
        if clean in [False, 'false']:
            clean = False

        # ensure that plugin dir is empty
        if os.path.exists(self.plugin_dir):
            if clean:
                if force in ['true', True]:
                    shutil.rmtree(self.plugin_dir)
                else:
                    raise Exception("Plugin is already located at [%s]" % self.plugin_dir)


        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)


        # build the information from the manifest

        code = self.kwargs.get("code")
        if not code:
            code = self.xml.get_value("manifest/@code")

        version = self.kwargs.get("version")
        if not version:
            version = self.xml.get_value("manifest/@version")

        nodes = self.xml.get_nodes("manifest/*")


        # clean out all of the files
        self.delete_files(nodes)


        has_info = False
        sobjects = []

        # handle all of the nodes in the manifest
        for i, node in enumerate(nodes):
            name = self.xml.get_node_name(node)
            if name == 'sobject':
                dumped_sobjects = self.dump_sobject(node)
                if not dumped_sobjects:
                    dumped_sobjects = []
                sobjects.extend(dumped_sobjects)
            elif name == 'search_type':
                self.handle_search_type(node)
            elif name == 'include':
                self.handle_include(node)
            elif name == 'python':
                self.handle_python(node)
            elif name == 'plugin':
                self.handle_plugin(node)



        # make sure there is a data node and handle it
        data_node = self.xml.get_node("manifest/data")
        if data_node is None:
            root_node = self.xml.get_root_node()
            data_node = self.xml.create_element("data")
            child = self.xml.get_first_child(root_node)
            if child is None:
                self.xml.append_child(root_node, data_node)
            else:
                self.xml.insert_before(data_node, child)

        self.handle_data(data_node)





        manifest_path = "%s/manifest.xml" % (self.plugin_dir)
        file = codecs.getwriter('utf8')(open(manifest_path, 'wb'))
        file.write(self.xml.to_string())
        file.close()

        # FIXME: leaving this out for now
        #self.handle_snapshots()

        dist_dir = self.kwargs.get("dist_dir")
        if not dist_dir:
            dist_dir = Environment.get_dist_dir()

        # get the basename of the code
        basecode = os.path.basename(self.code)

        # zip up the contents
        import zipfile
        if version:
            zip_path = "%s/%s-%s.zip" % (dist_dir, basecode, version)
        else:
            zip_path = "%s/%s.zip" % (dist_dir, basecode)

        print("Zipping up plugin file [%s]" % zip_path)
        print("    from [%s]" % self.plugin_dir)
        from pyasm.common import ZipUtil
        ignore_dirs = ['.svn']

        # ignore file
        #ignore_path = "%s/.ignore" % (self.plugin_dir)

        parts = self.code.split("/")
        root_dir = "%s/%s" % (self.base_dir, parts[0])
        if len(parts) >= 2:
            include_dirs = ["/".join(parts[1:])]
        else:
            include_dirs = None

        ZipUtil.zip_dir(root_dir, zip_path, ignore_dirs=ignore_dirs, include_dirs=include_dirs)
        print("... done")

        #f = codecs.open(zip_path, 'w')
        #zip = zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_DEFLATED)
        #self.zip_dir(zip, self.plugin_dir, "asset", rel_dir='')

        self.zip_path = zip_path

        # encrypt the file
        """
        print("encrypting!!!!", zip_path)
        self.enc_path = "%s.enc" % zip_path
        from pyasm.common import EncryptUtil
        ticket = "OMG"
        encrypt = EncryptUtil(ticket)
        encrypt.encrypt_file(zip_path)
        """


        # register the plugin into the current project
        if self.kwargs.get("register") in [True, 'true']:

            # first check if a plugin with this code already exists
            plugin = Search.get_by_code("config/plugin", self.code)
            if plugin:
                raise TacticException("Plugin [%s] already existed in the project." % self.code)
            # create a new one
            plugin = SearchType.create("config/plugin")
            plugin.set_value("code", self.code)

            # update the information
            if version:
                plugin.set_value("version", version)

            # NOTE: not sure if this is desirable
            plugin.set_value("manifest", self.manifest)

            if self.plugin_dir.startswith(self.base_dir):
                rel_dir = self.plugin_dir.replace(self.base_dir, "")
                rel_dir = rel_dir.lstrip("/")
                plugin.set_value("rel_dir", rel_dir)

            plugin.commit()

            # record all of the sobject exported
            if plugin.get_value("type", no_exception=True) == "config":
                for sobject in sobjects:
                    plugin_content = SearchType.create("config/plugin_content")
                    plugin_content.set_value("search_type", sobject.get_search_type())
                    plugin_content.set_value("search_code", sobject.get_code())
                    plugin_content.set_value("plugin_code", self.code)
                    plugin_content.commit()



    def delete_files(self, nodes):

        # clean out all of the files
        for node in nodes:
            name = self.xml.get_node_name(node)

            if name == "include":
                path = self.xml.get_attribute(node, "path")
                if not path:
                    print("WARNING: No path found for search type in manifest")
                    continue

                path = "%s/%s" % (self.plugin_dir, path)

                if path.endswith(".py"):
                    from tactic.command import PythonCmd
                    cmd = PythonCmd(file_path=path)
                    manifest = cmd.execute()
                    if manifest:
                        xml = Xml()
                        xml.read_string(manifest)
                        include_nodes = xml.get_nodes("manifest/*")

                        self.delete_files(include_nodes)
            elif name == "python":
                # don't delete python node file
                pass
            else:
                path = self.get_path_from_node(node)
                if path and os.path.exists(path):
                    print("Deleting: ", path)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.unlink(path)



    def handle_data(self, node):

        for name in ['code', 'title', 'version', 'description']:
            value = self.kwargs.get(name)
            if value:
                children = self.xml.get_children(node)
                old_node = None
                for child_node in children:
                    child_name = self.xml.get_node_name(child_node)
                    if child_name == name:
                        old_node = child_node

                value_node = self.xml.create_element(name)
                self.xml.set_node_value(value_node, value)
                if old_node is None:
                    self.xml.append_child(node, value_node)
                else:
                    self.xml.replace_child(node, old_node, value_node)


    def handle_plugin(self, node):

        code = self.xml.get_attribute(node, "code")
        print("WARNING: Cannot export plugin [%s] through tag <plugin>" % code)
        return

        # read the manifest
        manifest_path = "%s/%s" % (self.plugin_dir, code)
        if not os.path.exists(manifest_path):
            pass
        kwargs = {
        }
        creator = PluginCreator(**kwargs)





    def zip_dir(self, zip, base_dir, plugin, rel_dir=''):

        plugin = os.path.basename(base_dir)

        if rel_dir:
            dir = '%s/%s' % (base_dir, rel_dir)
        else:
            dir = base_dir

        filenames = os.listdir(dir)

        for filename in filenames:
            path = "%s/%s" % (dir, filename)
            print(path)
            if os.path.isdir(path):
                print(" ... directory!")
            if os.path.isdir(path):
                if rel_dir:
                    self.zip_dir(zip, base_dir, plugin, "%s/%s" % (rel_dir,filename))
                else:
                    self.zip_dir(zip, base_dir, plugin, filename)
                continue


            filename = str(filename)
            path = str(path)
            if rel_dir:
                zip.write(path, str("%s/%s/%s" % (plugin, rel_dir, filename)))
            else:
                zip.write(path, str("%s/%s" % (plugin,filename)))





    def dump_sobject(self, node):
        '''dump sobject entries in plugin creation'''
        project = Project.get()
        project_code = project.get_value("code")

        search_type = self.xml.get_attribute(node, "search_type")
        replace_variable = self.xml.get_attribute(node, "replace_variable")
        include_id = self.xml.get_attribute(node, "include_id")
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

        self._validate_ignore_columns(node, search_type, ignore_columns)

        # FIXME:
        # it is possible that the manifest defines sobjects on search types
        # that don't exist.  This is because it uses the manifest of
        # the new pipeline and not the original ...
        sobjects = self.get_sobjects_by_node(node)
        if not sobjects:
            #print("Skipping as no sobjects found for [%s]" %search_type)
            return []



        # If there are no sobjects, then no file is created because
        # no path can be extracted.

        path = self.get_path_from_node(node)

        #print("Writing: ", path)
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

        if replace_variable =="true":
            if search_type == "sthpw/pipeline":
                #regex is looking for a word bfore "/"
                regex = r'^\w+\/'
                dumper.set_replace_token("$PROJECT/", "code", regex)
            elif search_type == "config/process":
                regex = r'^\w+\/'
                dumper.set_replace_token("$PROJECT/", "pipeline_code", regex)


        relative_dir_column = Xml.get_attribute(node, "relative_dir_column")

        dumper.dump_tactic_inserts(path, mode='sobject', relative_dir_column=relative_dir_column)

        print("\t....dumped [%s] entries" % (len(sobjects)))

        return sobjects


    def _validate_ignore_columns(self, node, search_type, ignore_columns):
        '''validate only if unique is set to true'''
        is_unique = self.xml.get_attribute(node, "unique") == 'true'
        if not is_unique:
            return True
        # defaults to ['code']
        restricted_cols = self.UNIQUE_DICT.get(search_type, ['code'])
        for col in restricted_cols:
            if col in ignore_columns:
                raise TacticException("You have '%s' set in ignore_columns and unique='true' set for [%s]. You need to remove this from ignore_columns to enable the unique feature." %(col, search_type))

    def handle_search_type(self, node):

        search_type = self.xml.get_attribute(node, "code")
        if not search_type:
            raise TacticException("No code found for search type in manifest")

        path = self.xml.get_attribute(node, "path")

        if not path:
            path = "%s.spt" % search_type.replace("/", "_")

        path = "%s/%s" % (self.plugin_dir, path)

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



    def handle_include(self, node):
        path = self.xml.get_attribute(node, "path")
        if not path:
            raise TacticException("No path found for include in manifest")

        path = "%s/%s" % (self.plugin_dir, path)

        if path.endswith(".py"):
            from tactic.command import PythonCmd
            cmd = PythonCmd(file_path=path)
            manifest = cmd.execute()

        if not manifest:
            print("No manifest discovered in [%s]" %path)
            return

        xml = Xml()
        xml.read_string(manifest)
        nodes = xml.get_nodes("manifest/*")

        sobjects = []
        for i, node in enumerate(nodes):
            name = self.xml.get_node_name(node)
            if name == 'sobject':
                dumped_sobjects = self.dump_sobject(node)
                if not dumped_sobjects:
                    dumped_sobjects = []
                sobjects.extend(dumped_sobjects)
            elif name == 'search_type':
                self.handle_search_type(node)
            elif name == 'include':
                self.handle_include(node)


    def handle_python(self, node):
        path = self.xml.get_attribute(node, "path")
        if not path:
            raise TacticException("No path found for python in manifest")

        if not path.endswith('.py'):
            raise TacticException("Path should have the .py extension for python in manifest")

        path = "%s/%s" % (self.plugin_dir, path)
        if not os.path.exists(path):
            raise TacticException("Path [%s] does not exist." %path)



    def handle_snapshots(self):


        path = "__snapshot_files.spt"
        path = "%s/%s" % (self.plugin_dir, path)
        print("Writing: ", path)
        # write out an empty file
        #f = open(path, 'w')

        fmode = 'w'
        if os.path.exists(path):
            fmode = 'a'
        f = codecs.open(path, fmode, 'utf-8')
        f.close()


        # get all of the latest snapshots for this plugin
        search = Search("sthpw/snapshot")
        search.add_parent_filter(self.plugin)
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

        new_dir = "%s/files" % (self.plugin_dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        for snapshot in snapshots:
            paths = snapshot.get_all_lib_paths(mode="lib")
            for path in paths:
                file_name = os.path.basename(path)
                new_path = "%s/%s" % (new_dir, file_name)

                shutil.copy(path, new_path)



class PluginUploader(PluginBase):
    def execute(self):
        pass



class PluginInstaller(PluginBase):

    def execute(self):

        # install the plugin
        mode = self.kwargs.get("mode")
        if not mode:
            mode = 'install'

        # register mode actually reads the manifest.
        if mode == 'install':
            nodes = self.xml.get_nodes("manifest/*")
        else:
            # DEPRECATED
            # dynamically create the plugin node in the manifest
            plugin_node = self.xml.create_element("sobject")
            self.xml.set_attribute(plugin_node, "path", "config_plugin.spt")
            nodes = []
            nodes.insert(0, plugin_node)

        # register the plugin.
        register = self.kwargs.get("register")
        code = None
        plugin = None
        if register in ['true', True]:
            node = self.xml.get_node("manifest/data")
            data = self.xml.get_node_values_of_children(node)

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
                if code:
                    plugin.set_value("code", code)


            # update the information
            if version:
                plugin.set_value("version", version)

            # NOTE: is this really needed?
            plugin.set_value("manifest", self.manifest)

            if self.plugin_dir.startswith(self.base_dir):
                rel_dir = self.plugin_dir.replace(self.base_dir, "")
                rel_dir = rel_dir.lstrip("/")
                plugin.set_value("rel_dir", rel_dir)

            plugin.commit()

        self.plugin = plugin



        self.import_manifest(nodes)

        # Users see Activate in the UI
        label = mode
        if mode == 'install':
            label = 'activate'

        if code:
            self.add_description('%s plugin [%s]' % (label.capitalize(), code))



    def import_manifest(self, nodes):

        tools = PluginTools(**self.kwargs)

        paths_read = []

        for node in nodes:

            node_name = self.xml.get_node_name(node)
            if node_name == "plugin":

                plugin_code = self.xml.get_attribute(node, 'code')
                mode = self.xml.get_attribute(node, 'mode')

                if mode == "absolute":
                    plugin_base_dir = Environment.get_plugin_dir()
                    plugin_dir = "%s/%s" % (plugin_base_dir, plugin_code)
                else:
                    plugin_dir = "%s/%s" % (self.plugin_dir, plugin_code)

                print("Installing plugin: ", plugin_dir)
                installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True)
                installer.execute()



            elif node_name == 'search_type':
                search_type = self.xml.get_attribute(node, 'code')

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

                path = self.xml.get_attribute(node, "path")
                if not path:
                    path = "%s.spt" % search_type.replace("/", "_")

                path = "%s/%s" % (self.plugin_dir, path)

                if path in paths_read:
                    continue

                if self.verbose:
                    print("Reading search_type: ", path)

                # NOTE: priviledged knowledge of the order or return values
                jobs = tools.import_data(path, commit=True)

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
                        if self.verbose:
                            print('WARNING: Search Type [%s] is already registered' % search_type_chk.get_value("search_type"))
                    else:
                        search_type_obj.commit()
                except SearchException as e:
                    if e.__str__().find('not registered') != -1:
                        search_type_obj.commit()

                # check if table exists
                has_table = False
                if has_table:
                    if self.verbose:
                        print('WARNING: Table [%s] already exists')
                elif table:
                    #print(table.get_statement())
                    if table:
                        database = table.get_database()
                        table_name = table.get_table()

                        TableUndo.log(search_type, database, table_name)


                # import the backup data back
                backup_dir = "%s/backup" % self.plugin_dir
                backup_path = "%s/%s.spt" % (backup_dir, search_type.replace("/", "_"))
                tools_backup = PluginTools(plugin_dir=self.plugin_dir, verbose=self.verbose)
                tools_backup.import_data(backup_path)

                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)


            elif node_name == 'sobject':
                path = self.xml.get_attribute(node, "path")
                search_type = self.xml.get_attribute(node, "search_type")
                seq_max = self.xml.get_attribute(node, "seq_max") or 0
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

                path = "%s/%s" % (self.plugin_dir, path)
                if path in paths_read:
                    continue

                unique = self.xml.get_attribute(node, "unique")
                if unique == 'true':
                    unique = True
                else:
                    unique = False

                if self.verbose:
                    print("Reading: ", path)


                ignore_columns = Xml.get_attribute(node, "ignore_columns")
                if ignore_columns:
                    ignore_columns = ignore_columns.split(",")
                    ignore_columns = [x.strip() for x in ignore_columns]
                else:
                    ignore_columns = []


                # jobs doesn't matter for sobject node
                jobs = tools.import_data(path, unique=unique, ignore_columns=ignore_columns)

                # reset it in case it needs to execute a PYTHON tag right after
                Schema.get(reset_cache=True)
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

                path = self.xml.get_attribute(node, "path")

                path = "%s/%s" % (self.plugin_dir, path)

                from tactic.command import PythonCmd
                cmd = PythonCmd(file_path=path)
                manifest = cmd.execute()

                if manifest:
                    xml = Xml()
                    xml.read_string(manifest)
                    nodes = xml.get_nodes("manifest/*")

                    self.import_manifest(nodes)

            elif node_name == 'python':

                path = self.xml.get_attribute(node, "path")
                path = "%s/%s" % (self.plugin_dir, path)

                # just run the python script
                from tactic.command import PythonCmd
                cmd = PythonCmd(file_path=path)
                cmd.execute()


        ''' TODO: do we store the transaction here???
        try:
            from pyasm.search import Transaction
            transaction = Transaction.get()
            transaction_str = transaction.xml.to_string()
            self.plugin.set_value("transaction", transaction_str)
            self.plugin.commit()
        except Exception as e:
            print("Error: ", e.message)
        '''

class PluginReloader(PluginBase):

    def execute(self):
    	print("Uninstalling plugin: ", self.plugin_dir)
    	uninstaller = PluginUninstaller(plugin_dir=self.plugin_dir, verbose=False)
    	uninstaller.execute()

    	print("Installing plugin: ", self.plugin_dir)
    	installer = PluginInstaller(plugin_dir=self.plugin_dir, verbose=False, register=True)
    	installer.execute()


class PluginUninstaller(PluginBase):

    def execute(self):
        # uninstall the plugin
        nodes = self.xml.get_nodes("manifest/*")

        nodes.reverse()

        self.handle_nodes(nodes)

        self.add_description('Remove plugin [%s]' %self.code)

    def handle_nodes(self, nodes):
        tools = PluginTools(plugin_dir=self.plugin_dir, verbose=self.verbose)

        for node in nodes:
            node_name = self.xml.get_node_name(node)
            if node_name == 'search_type':
                #self.remove_search_type(node)
                tools._remove_search_type(node)
            elif node_name == 'sobject':
                self.remove_sobjects(node)
            elif node_name == 'include':
                self.handle_include(node)
            elif node_name == 'python':
                self.handle_python(node)
            elif node_name == 'plugin':
                self.handle_plugin(node)


        # remove plugin contents
        search = Search("config/plugin_content")
        search.add_filter("plugin_code", self.code)
        plugin_contents = search.get_sobjects()
        for plugin_content in plugin_contents:
            plugin_content.delete()



        # deregister the plugin
        plugin = Search.eval("@SOBJECT(config/plugin['code','%s'])" % self.code, single=True)
        if plugin:
            plugin.delete()



    def handle_plugin(self, node):

        plugin_code = self.xml.get_attribute(node, 'code')
        print("Uninstalling plugin [%s]: " % plugin_code)
        plugin_dir = "%s/%s" % (self.plugin_dir, plugin_code)

        uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
        uninstaller.execute()



    def remove_sobjects(self, node):

        sobjects = self.get_sobjects_by_node(node)
        if not sobjects:
            #print("Skipping as no sobjects found for: ", node)
            return

        # delete all the sobjects present in the plugin
        for sobject in sobjects:
            try:
                sobject.delete()
            except Exception as e:
                print("WARNING: could not delete [%s] due to error [%s]" % (sobject.get_search_key(), e))


    def handle_include(self, node):
        path = self.xml.get_attribute(node, "path")
        if not path:
            raise TacticException("No path found for search type in manifest")

        path = "%s/%s" % (self.plugin_dir, path)

        if path.endswith(".py"):
            from tactic.command import PythonCmd
            cmd = PythonCmd(file_path=path)
            manifest = cmd.execute()

        if not manifest:
            return

        xml = Xml()
        xml.read_string(manifest)
        nodes = xml.get_nodes("manifest/*")
        nodes.reverse()

        self.handle_nodes(nodes)


    def handle_python(self, node):
        '''during uninstall, handle the python undo_path'''
        path = self.xml.get_attribute(node, "undo_path")

        # if no path, then nothing to undo
        if not path:
            print("No undo_path defined for this python node")
            return

        if not path.endswith('.py'):
            raise TacticException("Path should have the .py extension for python in manifest")

        path = "%s/%s" % (self.plugin_dir, path)
        if not os.path.exists(path):
            raise TacticException("Undo Path [%s] does not exist python in manifest" %path)
        if path.endswith(".py"):
            from tactic.command import PythonCmd
            cmd = PythonCmd(file_path=path)
            cmd.execute()









class PluginTools(PluginBase):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.xml = kwargs.get("xml")

        self.plugin_dir = kwargs.get("plugin_dir")
        if not self.plugin_dir:
            self.plugin_dir = "."

        self.verbose = self.kwargs.get("verbose") not in [False, 'false']

        self.plugin = kwargs.get("plugin")


    #
    # Simple wrapper methods
    #

    def dump_sobject(self, search_type, path):
        xml = Xml()
        xml.read_string( '''<sobject path="%s" search_type="%s"/>''' % (path, search_type))
        self.xml = xml
        node = Xml.get_node(xml, "sobject")
        return self._dump_sobject(node)


    def dump_search_type(self, search_type, path):
        xml = Xml()
        xml.read_string( '''<search_type path="%s" code="%s"/>''' % (path, search_type))
        self.xml = xml
        node = Xml.get_node(xml, "search_type")
        return self._dump_search_type(node)




    def remove_search_type(self, search_type):
        xml = Xml()
        xml.read_string( '''<search_type code="%s"/>''' % search_type)
        self.xml = xml
        node = Xml.get_node(xml, "search_type")
        return self._remove_search_type(node)





    #
    # Node tools
    #

    def _dump_sobject(self, node):

        project = Project.get()
        project_code = project.get_value("code")

        search_type = self.xml.get_attribute(node, "search_type")
        replace_variable = self.xml.get_attribute(node, "replace_variable")
        include_id = self.xml.get_attribute(node, "include_id")
        ignore_columns = self.xml.get_attribute(node, "ignore_columns")


        if include_id in [True, 'true']:
            include_id = True
        else:
            include_id = False


        if ignore_columns:
            ignore_columns = ignore_columns.split(",")
            ignore_columns = [x.strip() for x in ignore_columns]
        else:
            ignore_columns = []

        # FIXME:
        # it is possible that the manifest defines sobjects on search types
        # that don't exist.  This is because it uses the manifest of
        # the new pipeline and not the original ...
        sobjects = self.get_sobjects_by_node(node)
        if not sobjects:
            #print("Skipping as no sobjects found for [%s]" %search_type)
            return []



        # If there are no sobjects, then no file is created because
        # no path can be extracted.

        path = self.get_path_from_node(node)

        #print("Writing: ", path)
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
        dumper.set_skip_invalid_column()
        dumper.set_sobjects(sobjects)

        if replace_variable =="true":
            if search_type == "sthpw/pipeline":
                #regex is looking for a word bfore "/"
                regex = r'^\w+\/'
                dumper.set_replace_token("$PROJECT/", "code", regex)
            elif search_type == "config/process":
                regex = r'^\w+\/'
                dumper.set_replace_token("$PROJECT/", "pipeline_code", regex)

        dumper.dump_tactic_inserts(path, mode='sobject')

        print("\t....dumped [%s] entries" % (len(sobjects)))

        return sobjects



    def _dump_search_type(self, node):

        search_type = Xml.get_attribute(node, "code")
        if not search_type:
            raise TacticException("No code found for search type in manifest")

        path = Xml.get_attribute(node, "path")

        if not path:
            path = "%s.spt" % search_type.replace("/", "_")

        path = "%s/%s" % (self.plugin_dir, path)

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





    def _remove_search_type(self, node):
        search_type = Xml.get_attribute(node, 'code')

        # get sobject entry
        search = Search("sthpw/search_object")
        search.add_filter("search_type", search_type)
        search_type_sobj = search.get_sobject()

        if not search_type_sobj:
            print("WARNING: Search type [%s] does not exist" % search_type)
            return


        # dump the table data into backup folder
        backup_path = "backup/%s.spt" % search_type.replace("/", "_")
        full_backup_path = "%s/%s" % (self.plugin_dir, backup_path)

        if os.path.exists(full_backup_path):
            os.unlink(full_backup_path)

        tools = PluginTools(plugin_dir=self.plugin_dir)
        tools.dump_sobject(search_type, backup_path)

        # get the table and remove it
        from pyasm.search import DropTable
        try:
            table_drop = DropTable(search_type)
            table_drop.commit()
            # NOTE: do we need to log the undo for this?
        except Exception as e:
            print("Error: ", e)


        # NOTE: it is not clear that unloading a plugin should delete
        # the search type ... this search type (at present) can be
        # shared amongst multiple projects and this will break it
        return

        """
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
            print("WARNING: A plugin cannot deregister a search type from the 'sthpw' or 'config' namespace'")
        else:

            search = Search("sthpw/search_object")
            search.add_filter("search_type", search_type)
            search_type_sobj = search.get_sobject()
            if search_type_sobj:
                search_type_sobj.delete()
        """




    def import_sobject(self, node):

        tools = PluginTools(**self.kwargs)

        paths_read = []

        path = self.xml.get_attribute(node, "path")
        search_type = self.xml.get_attribute(node, "search_type")
        seq_max = self.xml.get_attribute(node, "seq_max")

        ignore_columns = Xml.get_attribute(node, "ignore_columns")
        if ignore_columns:
            ignore_columns = ignore_columns.split(",")
            ignore_columns = [x.strip() for x in ignore_columns]
        else:
            ignore_columns = []

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

        path = "%s/%s" % (self.plugin_dir, path)
        if path in paths_read:
            return

        unique = self.xml.get_attribute(node, "unique")
        if unique == 'true':
            unique = True
        else:
            unique = False

        if self.verbose:
            print("Reading: ", path)
        # jobs doesn't matter for sobject node
        jobs = tools.import_data(path, unique=unique, ignore_columns=ignore_columns)

        # reset it in case it needs to execute a PYTHON tag right after
        Schema.get(reset_cache=True)
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
        return path



    def get_unique_sobject(self, sobject):
        '''get unique sobject in the existing table when installing plugin'''
        base_st = sobject.get_base_search_type()
        cols = self.UNIQUE_DICT.get(base_st, ['code'])

        search = Search( sobject.get_base_search_type(), sudo=True )
        has_filter = False
        for col in cols:
            value = sobject.get_value(col)
            if value:
                search.add_filter(col, value)
                has_filter = True
            else:
                search.add_filter(col, None)

        # ensure there is some filtering before getting sobject
        if has_filter:
            unique_sobject = search.get_sobject()
        else:
            unique_sobject = None
        return unique_sobject




    def import_data(self, path, commit=True, unique=False, ignore_columns=[]):

        if not os.path.exists(path):
            # This is printed too often in harmless situations
            #print("WARNING: path [%s] does not exist" % path)
            return []


        if os.path.isdir(path):
            f = []

            for root, dirnames, basenames in os.walk(path):

                for basename in basenames:
                    subpath = "%s/%s" % (root, basename)
                    try:
                        if Common.IS_Pv3:
                            subf = open(subpath, 'r')
                        else:
                            subf = codecs.getreader('utf8')(open(subpath, 'r'))
                        f.extend(subf.readlines())
                        subf.close()
                        f.append("\n")
                    except Exception as e:
                        print("WARNING: ", e)
                        print("File [%s]" % subpath)
                        raise
        else:
            #f = codecs.open(path, 'r', 'utf-8')
            if IS_Pv3:
                f = open(path, 'r')
            else:
                f = codecs.getreader('utf8')(open(path, 'r'))




        statement = []
        count = 1

        insert = None
        table = None
        sobject = None

        jobs = []

        filter_line_handler = self.kwargs.get('filter_line_handler')
        filter_sobject_handler = self.kwargs.get('filter_sobject_handler')

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
                statement.insert(0, "from pyasm.search import SearchType, CreateTable, Search, CreateView")
                statement_str = "\n".join([x.rstrip("\r\n") for x in statement])

                try:
                    gc = {}
                    lc = {}
                    exec(statement_str, gc, lc)
                    insert = lc.get("insert")
                    table = lc.get("table")
                except SqlException as e:
                    print("ERROR (SQLException): ", e)
                except Exception as e:
                    print("ERROR: ", e)
                    print("\n")
                    print(statement_str)
                    print("\n")
                    raise
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



                    # if the search type is in sthpw namespace, then change
                    # the project code to the current project
                    base_search_type = sobject.get_base_search_type()

                    if base_search_type.startswith("config/"):
                        project = Project.get()
                        project_code = project.get_value("code")
                        if base_search_type == "config/process":
                            if "$PROJECT" in sobject.get('pipeline_code'):
                                old_code = sobject.get('pipeline_code')
                                new_code = old_code.replace("$PROJECT",project_code,1)
                                sobject.set_value('pipeline_code',new_code)

                            else:
                                old_pipeline_code = sobject.get("pipeline_code")
                                if old_pipeline_code.find("/") != -1:
                                    parts = old_pipeline_code.split("/", 1)
                                    new_pipeline_code = "%s/%s" % (project_code,parts[1]);
                                    sobject.set_value('pipeline_code',new_pipeline_code)



                    if base_search_type.startswith("sthpw/"):

                        project = Project.get()
                        project_code = project.get_value("code")

                        if SearchType.column_exists(sobject, "project_code"):
                            old_project_code = sobject.get_value("project_code")
                            if "project_code" not in ignore_columns:
                                sobject.set_value("project_code", project_code)
                            else:
                                sobject.set_value("project_code", "__TEMPLATE__")

                        else:
                            old_project_code = None

                        if base_search_type == "sthpw/schema":
                            # if a schema is already defined, the delete
                            # the current one.  This is not necessary
                            # if unique flag is on
                            if not unique:
                                search = Search("sthpw/schema")
                                search.add_filter("code", project_code)
                                old_schema = search.get_sobject()
                                if old_schema:
                                    old_schema.delete()

                            sobject.set_value("code", project_code)


                        if base_search_type == "sthpw/pipeline":

                            if "$PROJECT" in sobject.get('code'):
                                # Not really used
                                old_code = sobject.get('code')
                                new_code = old_code.replace("$PROJECT",project_code,1)
                                search = Search("sthpw/pipeline")
                                search.add_filter("code", new_code)
                                exists = search.get_sobject()
                                if not exists:
                                    sobject.set_value('code',new_code)
                                    unique = True

                            else:
                                # This is probably easier to maintain
                                old_code = sobject.get('code')
                                if old_code.find("/") != -1:
                                    parts = old_code.split("/", 1)
                                    new_code =  "%s/%s" % (project.get_code(), parts[1])

                                    search = Search("sthpw/pipeline")
                                    search.add_filter("code", new_code)
                                    exists = search.get_sobject()
                                    if not exists:
                                        sobject.set_value('code',new_code)
                                        unique = True


                        if base_search_type == "sthpw/login_group":
                            if old_project_code:
                                login_group = sobject.get_value("login_group")
                                delimiter = None
                                if login_group.startswith("%s_" % old_project_code):
                                    delimiter = "_"
                                elif login_group.startswith("%s/" % old_project_code):
                                    delimiter = "/"

                                if delimiter:
                                    login_group = login_group[len(old_project_code)+1:]
                                    login_group = "%s%s%s" % (project_code, delimiter, login_group)

                                    sobject.set_value("code", login_group)
                                    sobject.set_value("login_group", login_group)


                            # convert all of xml to this project
                            xml = sobject.get_xml_value("access_rules")
                            nodes = Xml.get_nodes(xml, "rules/rule")
                            for node in nodes:
                                test = xml.get_attribute(node, "project")
                                if test:
                                    xml.set_attribute(node, "project", project_code)

                            sobject.set_value("access_rules", xml.to_string())




                    if unique:
                        unique_sobject = self.get_unique_sobject(sobject)
                        if unique_sobject:
                            sobject.set_value("id", unique_sobject.get_id() )

                        if sobject == None:
                            continue



                    sudo = Sudo()
                    try:
                        if commit:
                            try:
                                sobject.commit(triggers=False)
                            except UnicodeDecodeError as e:
                                raise
                            except Exception as e:
                                print("WARNING: could not commit [%s] due to error [%s]" % (sobject.get_search_key(), e))
                                continue


                            chunk = 100
                            if self.verbose and count and count % chunk == 0:
                                print("\t... handled entry [%s]" % count)


                            if self.plugin and self.plugin.get_value("type", no_exception=True) == "config":
                                plugin_content = SearchType.create("config/plugin_content")
                                plugin_content.set_value("search_type", sobject.get_search_type())
                                plugin_content.set_value("search_code", sobject.get_code())
                                plugin_content.set_value("plugin_code", self.plugin.get_code())
                                plugin_content.commit()

                    except UnicodeDecodeError as e:
                        print("Skipping due to unicode decode error: [%s]" % statement_str)
                        continue

                    finally:
                        sudo.exit()


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

        if not isinstance(f, list):
            f.close()

        if self.verbose:
            print("\t... added [%s] entries" % count)
        return jobs













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
    def execute(self):
        plugin = self.sobject

        web = WebContainer.get_web()
        value = web.get_form_value( self.get_input_name() )
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




