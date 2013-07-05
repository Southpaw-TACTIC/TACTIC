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


__all__ = ['PluginCreator', 'PluginInstaller', 'PluginUninstaller', 'PluginSObjectAdderCmd']

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


        my.plugin_dir = my.kwargs.get("plugin_dir")
        my.base_dir = my.kwargs.get("base_dir")
        my.manifest = my.kwargs.get("manifest")
        my.code = my.kwargs.get("code")
        my.version = my.kwargs.get("version")

        # get the plugin sobject (this is DEPRECATED)
        if my.search_key:
            plugin = SearchKey.get_by_search_key(my.search_key)
            my.manifest = plugin.get_value("manifest")

        elif my.manifest:
            pass

        elif upload_file_name:
            # The path is moved to the plugin dir, if this process is taking
            # "local" file (such as one uploaded)
            upload_dir = Environment.get_upload_dir()
            upload_path = "%s/%s" % (upload_dir, upload_file_name)

            plugin_base_dir = Environment.get_plugin_dir()
            shutil.move(upload_path, plugin_base_dir)

            zip_path = "%s/%s" % (plugin_base_dir, upload_file_name)

            zip_util = ZipUtil()
            
            code = my.kwargs.get("code")
            assert code
            manifest_path = "%s/%s/manifest.xml" % (plugin_base_dir, code)

            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()


        # NOTE: this is not relevant for Creator
        elif zip_path:
            # unzip the file in to the tmp_dir or plugin_dir (for install)
            zip_util = ZipUtil()

            tmp_dir = Environment.get_tmp_dir()
            zip_util.extract(zip_path, base_dir=tmp_dir)

            # FIXME: is the code really necessary? or can it be inferred?
            code = my.kwargs.get("code")
            assert(code)
            my.base_dir = tmp_dir
            manifest_path = "%s/%s/manifest.xml" % (tmp_dir, code)

            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()

        elif my.plugin_dir:
            code = my.kwargs.get("code")
            manifest_path = "%s/manifest.xml" % (my.plugin_dir)
            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()


        # NOTE: is this even useful?
        elif my.base_dir:
            code = my.kwargs.get("code")
            manifest_path = "%s/%s/manifest.xml" % (my.base_dir, code)
            f = open(manifest_path, 'r')
            my.manifest = f.read()
            f.close()


        elif my.code:
            search = Search("config/plugin")
            search.add_filter("code", my.code)
            plugin = search.get_sobject()
            my.manifest = plugin.get_value("manifest")


        else:
            raise Exception("No plugin found")

            code = my.kwargs.get("code")
            if code:
                my.manifest = "<manifest code='%s'/>" % code
            else:
                raise TacticException("Cannot find code for plugin")

        my.xml = Xml()
        my.xml.read_string(my.manifest)

        if not my.code:
            my.code = my.xml.get_value("manifest/@code")
        if not my.code:
            my.code = my.xml.get_value("manifest/data/code")
        assert my.code

        if not my.base_dir:
            my.base_dir = Environment.get_plugin_dir()

        # set the base directory for this particular plugin
        if not my.plugin_dir:
            if my.version:
                my.plugin_base_dir = "%s/%s-%s" % (my.base_dir, my.code, my.version)
            else:
                my.plugin_base_dir = "%s/%s" % (my.base_dir, my.code)
        else:
            my.plugin_base_dir = my.plugin_dir




class PluginCreator(PluginBase):
    '''Class to create a plugin from an existing project'''

    def get_zip_path(my):
        return my.zip_path


    def execute(my):

        force = my.kwargs.get("force")

        # ensure that plugin dir is empty
        if os.path.exists(my.plugin_base_dir):
            if force in ['true', True]:
                shutil.rmtree(my.plugin_base_dir)
            else:
                raise Exception("Plugin is already located at [%s]" % my.plugin_base_dir)

        os.makedirs(my.plugin_base_dir)


        # get the plugin sobject
        # DEPRECATED
        my.plugin = my.kwargs.get("plugin")
        if not my.plugin:
            if my.search_key:
                my.plugin = Search.get_by_search_key(my.search_key)


        if not my.plugin:
            # build the information from the manifest

            code = my.kwargs.get("code")
            if not code:
                code = my.xml.get_value("manifest/@code")

            version = my.kwargs.get("version")
            if not version:
                version = my.xml.get_value("manifest/@version")

            my.plugin = SearchType.create("sthpw/virtual")
            if version:
                my.plugin.set_value("version", version)
            my.plugin.set_value("code", code)
        else:
            version = my.plugin.get_value("version")
            code = my.plugin.get_value("code")


        nodes = my.xml.get_nodes("manifest/*")


        # handle all of the nodes in the manifest
        has_info = False
        for node in nodes:
            name = my.xml.get_node_name(node)
            if name == 'sobject':
                my.handle_sobject(node)
            elif name == 'search_type':
                my.handle_search_type(node)



        # make sure there is a data node and handle it
        data_node = my.xml.get_node("manifest/data")
        if data_node is None:
            root_node = my.xml.get_root_node()
            data_node = my.xml.create_element("data")
            my.xml.append_child(root_node, data_node)

        my.handle_data(data_node)
            
 



        manifest_path = "%s/manifest.xml" % (my.plugin_base_dir)
        file = codecs.getwriter('utf8')(open(manifest_path, 'wb'))
        file.write(my.xml.to_string())
        file.close()

        # FIXME: leaving this out for now
        #my.handle_snapshots()



        # zip up the contents
        import zipfile
        #version = "0.1"
        if version:
            zip_path = "%s/%s-%s.zip" % (my.base_dir, my.code, version)
        else:
            zip_path = "%s/%s.zip" % (my.base_dir, my.code)

        from pyasm.common import ZipUtil
        ZipUtil.zip_dir(my.plugin_base_dir, zip_path)

        #f = codecs.open(zip_path, 'w')
        #zip = zipfile.ZipFile(f, 'w', compression=zipfile.ZIP_DEFLATED)
        #my.zip_dir(zip, my.plugin_base_dir, "asset", rel_dir='')

        my.zip_path = zip_path



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


    


    def handle_sobject(my, node):
        
        search_type = my.xml.get_attribute(node, "search_type")
        expr = my.xml.get_attribute(node, "expression")
        code = my.xml.get_attribute(node, "code")
        include_id = my.xml.get_attribute(node, "include_id")
        if include_id in [True, 'true']:
            include_id = True
        else:
            include_id = False


        ignore_columns = Xml.get_attribute(node, "ignore_columns")
        if ignore_columns:
            ignore_columns = ignore_columns.split(",")
        else:
            ignore_columns = []




        if expr:
            sobjects = Search.eval(expr)

        elif search_type:
            search = Search(search_type)
            search.set_show_retired(True)
            if code:
                search.add_filter("code", code)

            search.add_order_by("id")
            sobjects = search.get_sobjects()
        else:
            sobjects = []

        if not sobjects:
            print "Skipping as no sobjects found for [%s]" %search_type
            return



        # FIXME: if there are no sobjects, then no file is created because
        # no path can be extracted.

        path = my.xml.get_attribute(node, "path")
        if not path:
            if not search_type:
                search_type = sobjects[0].get_base_search_type()
            path = "%s.spt" % search_type.replace("/","_")

        path = "%s/%s" % (my.plugin_base_dir, path)

        print "Writing: ", path
        fmode = 'w'
        if os.path.exists(path):
            fmode = 'a'
        if not sobjects:
            # write out an empty file
            #f = open(path, 'w')
            f = codecs.open(path, fmode, 'utf-8')
            f.close()
            return

        dumper = TableDataDumper()
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        if search_type == 'config/widget_config':
            dumper.set_ignore_columns(['code'])
        dumper.set_include_id(include_id)
        dumper.set_ignore_columns(ignore_columns)
        dumper.set_sobjects(sobjects)
        dumper.dump_tactic_inserts(path, mode='sobject')

        print "\t....dumped [%s] entries" % (len(sobjects))



    def handle_search_type(my, node):
        search_type = my.xml.get_attribute(node, "code")
        if not search_type:
            raise TacticException("No code found for search type in manifest")

        path = my.xml.get_attribute(node, "path")
        if not path:
            path = "%s.spt" % search_type.replace("/", "_")

        path = "%s/%s" % (my.plugin_base_dir, path)

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
        else:
            ignore_columns = []


        # dump out the table definition
        dumper = TableSchemaDumper(search_type)
        dumper.set_delimiter("#-- Start Entry --#", "#-- End Entry --#")
        dumper.set_ignore_columns(ignore_columns)
        dumper.dump_to_tactic(path, mode='sobject')


    def handle_snapshots(my):


        path = "__snapshot_files.spt"
        path = "%s/%s" % (my.plugin_base_dir, path)
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

        new_dir = "%s/files" % (my.plugin_base_dir)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        for snapshot in snapshots:
            paths = snapshot.get_all_lib_paths(mode="lib")
            for path in paths:
                file_name = os.path.basename(path)
                new_path = "%s/%s" % (new_dir, file_name)

                shutil.copy(path, new_path)





class PluginInstaller(PluginBase):

    def execute(my):

        if not os.path.exists(my.plugin_base_dir):
            # check the install dir to see if the plugin exists in TACTIC
            install_dir = Environment.get_install_dir()
            my.plugin_base_dir = "%s/src/install/%s" % (install_dir, my.code)


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
            plugin.set_value("version", version)
            plugin.set_value("manifest", my.manifest)

            plugin_base_dir = Environment.get_plugin_dir()
            if my.plugin_dir.startswith(plugin_base_dir):
                rel_dir = my.plugin_dir.replace(plugin_base_dir, "")
                rel_dir = rel_dir.lstrip("/")
                plugin.set_value("rel_dir", rel_dir)

            plugin.commit()

        my.import_manifest(nodes)



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

                path = "%s/%s" % (my.plugin_base_dir, path)
                print "Reading search_type: ", path

                # NOTE: priviledged knowledge of the order or return values
                jobs = my.import_data(path, commit=True)
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
                        print 'Search Type [%s] is already registered' % search_type_chk.get_value("search_type")
                    else:
                        search_type_obj.commit()
                except SearchException, e:
                    if e.__str__().find('not registered') != -1:
                        search_type_obj.commit()

                # check if table exists 
                has_table = False
                if has_table:
                    print 'Table [%s] already exists'
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

                path = "%s/%s" % (my.plugin_base_dir, path)
                if path in paths_read:
                    continue

                unique = my.xml.get_attribute(node, "unique")
                if unique == 'true':
                    unique = True
                else:
                    unique = False

                
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


            elif node_name == 'python':
                module = my.xml.get_attribute(node, 'module')

                # look for a folder with the module name
                plugin_base_dir = Environment.get_plugin_dir()




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





    def import_data(my, path, commit=True, unique=False):
        if not os.path.exists(path):
            print "WARNING: path [%s] does not exist" % path
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
                statement_str = "\n".join([x.strip("\n") for x in statement])

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
                        search = Search( sobject.get_base_search_type() )
                        column = 'code'
                        #if sobject.get_base_search_type() == 'sthpw/login_group':
                        #    column = 'login_group'
                        code = sobject.get_value(column)
                        search.add_filter(column, code)
                        unique_sobject = search.get_sobject()
                        
                        if unique_sobject:
                            sobject.set_value("id", unique_sobject.get_id() )

                        if sobject == None:
                            continue

                    try:
                        if commit:
                            sobject.commit(triggers=False)
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

        print "\t... added [%s] entries" % count
        return jobs




class PluginUninstaller(PluginBase):
    # NOTE: this is still a work in progress.  It will remove entries added
    # by the plugin, but it is not clear that this is what we want to do.

    def execute(my):

        # uninstall the plugin
        nodes = my.xml.get_nodes("manifest/*")
        nodes.reverse()

        for node in nodes:
            node_name = my.xml.get_node_name(node)
            if node_name == 'search_type':
                my.remove_search_type(node)
            elif node_name == 'sobject':
                my.remove_sobjects(node)

        # deregister the plugin
        plugin = Search.eval("@SOBJECT(config/plugin['code','%s'])" % my.code, single=True)
        if not plugin:
            return

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
            table_drop = DropTable(search_type)
            try:
                table_drop.commit()
                # FIXME: need to log the undo for this
            except Exception, e:
                print "Error: ", e.message

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
        if search_type.startswith("prod/") or search_type.startswith("sthpw/"):
            print "WARNING: A plugin cannot deregister a search type from the 'sthpw' or 'prod' namespace'"
        else:
            search = Search("sthpw/search_object")
            search.add_filter("search_type", search_type)
            search_type_sobj = search.get_sobject()
            if search_type_sobj:
                search_type_sobj.delete()




    def remove_sobjects(my, node):
        expr = my.xml.get_attribute(node, "expression")
        search_type = my.xml.get_attribute(node, "search_type")
        code = my.xml.get_attribute(node, "code")

        if expr:
            sobjects = Search.eval(expr)

        elif search_type:
            search = Search(search_type)
            search.set_show_retired(True)
            if code:
                search.add_filter("code", code)

            search.add_order_by("id")
            sobjects = search.get_sobjects()
        else:
            sobjects = []

        # TODO: Possible check: a plugin can only delete sobjects that it
        # created? This gets pretty tricky to track.
        for sobject in sobjects:
            sobject.delete()

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




