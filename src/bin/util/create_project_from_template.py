
import tacticenv

import os
import sys
import re
import subprocess

import getopt

from pyasm.common import Config
from pyasm.security import Batch
from pyasm.biz import Project

from pyasm.search import SObjectFactory, SearchType, Search, TableDataDumper, Sql, DbContainer, Insert
from pyasm.command import Command


def run_sys_cmd( sys_cmd, do_print=True ):

    print
    print "> Running system command: %s" % sys_cmd
    print

    #[ input, output ] = os.popen4(sys_cmd)
    bufsize = 0
    p = subprocess.Popen(sys_cmd, shell=True, bufsize=bufsize,
          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
          stderr=subprocess.STDOUT, close_fds=True)
    (input, output) = (p.stdin, p.stdout)


    result = output.read()

    if do_print:
        print
        print result
        print

    return result


def tactic_create_new_sobj( search_type, key_value_pairs ):

    item = SearchType.create( search_type )
    has_items  = False
    for k,v in key_value_pairs.items():
        # skip inserting code for widget_config
        if search_type.endswith('widget_config') and k == 'code':
            continue
        item.set_value( k, v )
        has_items = True
    if has_items:
        item.commit(triggers=False)


def do_search(search_type, filters, order_by="id asc"):
    search = Search( search_type )
    for f in filters:
        search.add_filter( f[0], f[1] )

    search.add_order_by( order_by )
    item_list = search.get_sobjects()
    return item_list




class GatherTemplateProjectDetailsCmd(Command):

    def set_project(my, project_code):
        my.project_code = project_code


    def get_gathered_info(my):
        return my.info


    def gather_from_sthpw(my):

        my.info[ 'sthpw/schema' ] = do_search( 'sthpw/schema', [ ['code', my.project_code] ] )

        my.info[ 'sthpw/search_object' ] = do_search( 'sthpw/search_object', [ ['database', my.project_code] ] )

        my.info[ 'sthpw/project' ] = do_search( 'sthpw/project', [ ['code', my.project_code] ] )

        my.info[ 'sthpw/trigger' ] = do_search( 'sthpw/trigger', [ ['project_code', my.project_code] ] )


        my.info[ 'sthpw/pipeline' ] = do_search( 'sthpw/pipeline', [ ['project_code', my.project_code] ] )


    def gather_from_template_project(my):

        config_tables = [
                'custom_property',
                'custom_script',
                'naming',
                'prod_setting',
                'widget_config',
                'spt_client_trigger',
                'spt_plugin',
                'spt_process',
                'spt_trigger',
                'spt_url',
        ]

        for t in config_tables:
            # search_type = '%s/%s' % (my.project_code, t)
            search_type = '%s/%s' % ("config", t.replace("spt_", ""))
            try:
                my.info[ search_type ] = do_search( search_type, [] )
            except:
                bits = t.split('_')
                new_bits = []
                for b in bits:
                    new_bits.append( b.capitalize() )
                label = ' '.join( new_bits )

                values = {
                    "search_type": search_type,
                    "namespace": "config",
                    "description": label,
                    "database": "{project}",
                    "table_name": t,
                    "class_name": "pyasm.search.SObject",
                    "title": label,
                    "schema": "public",
                }

                print
                print ( "WARNING: did not find '%s' entry in the 'sthpw/search_object' table ... creating %s" %
                        (search_type, "entry for it now ...") )
                print

                tactic_create_new_sobj( 'sthpw/search_object', values )

        # add the asset_type table for prod type project
        project = Project.get_by_code(my.project_code)
        project_type = project.get_base_type()
        if project_type == 'prod':
            print "ADDING asset_type", do_search('prod/asset_type', [])
            my.info['prod/asset_type'] = do_search('prod/asset_type', [] )
            
    def execute(my):

        my.info = {}

        my.gather_from_sthpw()
        my.gather_from_template_project()
        #print "PRINT INFO ", my.info.keys()
        return my.info


class CloneTemplateProjectCmd(Command):

    def set_template_project_info( my, info, template_project, new_project, template_initials, new_title,
                                   widget_config_convert_flag, custom_script_convert_flag , db_host):

        my.info = info

        my.new_project = new_project
        my.new_title = new_title

        my.template_project = template_project
        my.template_initials = template_initials

        my.widget_config_convert_flag = widget_config_convert_flag
        my.custom_script_convert_flag = custom_script_convert_flag
        my.db_host = db_host
        my.db_user = Config.get_value('database', 'user')

    def copy_config(my, search_type, sobj_list):

        # 'custom_property',
        # 'custom_script',
        # 'naming',
        # 'prod_setting',
        # 'widget_config',

        field_ignore_list = [ 'id', 'timestamp' ]
        field_convert_list = []
        field_convert_list_upper = []

        new_search_type = search_type.replace( my.template_project, my.new_project )

        if search_type.endswith('custom_property'):
            field_convert_list = [ 'search_type' ]
            field_convert_list_upper = []

        elif search_type.endswith('custom_script'):
            field_convert_list = []
            if my.custom_script_convert_flag:
                field_convert_list.extend( [ 'folder', 'script' ] )
            field_convert_list_upper = []

        elif search_type.endswith('naming'):
            # no need to convert search_type
            field_convert_list = []
            field_convert_list_upper = [ 'code' ]

        elif search_type.endswith('prod_setting'):
            field_convert_list = []
            field_convert_list_upper = []

        elif search_type.endswith('widget_config'):
            #field_convert_list = [ 'search_type' ]
            field_convert_list = [ ]
            if my.widget_config_convert_flag:
                field_convert_list.append( 'config' )
            field_convert_list_upper = ['code']

        for sobj in sobj_list:
            new_data = {}
            for k,v in sobj.data.items():
                if k not in field_ignore_list:
                    new_val = v
                    if new_val:

                        if k in field_convert_list:
                            new_val = re.sub( r"\b%s\b" % my.template_project, my.new_project, v )
                        elif k in field_convert_list_upper:
                            if my.template_initials:
                                new_val = re.sub( r"%s" % my.template_initials.upper(), my.new_project.upper(), v )
                            else:
                                new_val = re.sub( r"%s" % my.template_project.upper(), my.new_project.upper(), v )

                        new_data[ k ] = new_val

            tactic_create_new_sobj( new_search_type, new_data )


    def adjust_sthpw(my, search_type, sobj_list):

        # 'schema',
        # 'search_objectj',
        # 'project',

        field_ignore_list = [ 'id', 'timestamp' ]
        field_convert_list = []
        field_convert_list_upper = []

        if search_type.endswith('schema'):
            field_convert_list = [ 'code' ]
            field_convert_list_upper = []

        elif search_type.endswith('search_object'):
            #field_convert_list = [ 'search_type', 'namespace', 'database' ]
            field_convert_list =  []
            field_convert_list_upper = []

        elif search_type.endswith('project'):
            field_convert_list = [ 'code' ]
            field_convert_list_upper = []

        elif search_type.endswith('trigger'):
            field_convert_list = [ 'project_code', 'script_path', 'event' ]
            field_convert_list_upper = []

        elif search_type.endswith('pipeline'):
            field_convert_list = [ 'project_code', 'code' ]
            field_convert_list_upper = []

      

        for sobj in sobj_list:
            new_data = {}
            for k,v in sobj.data.items():
                if k not in field_ignore_list:
                    new_val = v
                    if new_val:
                        if k in field_convert_list:
                            new_val = re.sub( r"\b%s\b" % my.template_project, my.new_project, v )
                        elif k in field_convert_list_upper:
                            if my.template_initials:
                                new_val = re.sub( r"%s" % my.template_initials.upper(), my.new_project.upper(), v )
                            else:
                                new_val = re.sub( r"%s" % my.template_project.upper(), my.new_project.upper(), v )
                        
                        if search_type == 'sthpw/project' and k == 'title':
                            if my.new_title:
                                new_val = "%s" % (my.new_title)
                            else:
                                new_val = "%s (%s)" % (new_val, sobj.get_id())

                        new_data[ k ] = new_val

            # TODO: add check here first! (see if the entry is already in sthpw DB)
            if search_type.endswith( 'search_object' ):
                check_exists_list = do_search( search_type, [ ['search_type', new_data.get('search_type')] ] )
            elif search_type.endswith( 'trigger' ):
                check_exists_list = do_search( search_type, [
                            ['project_code', my.new_project],
                            ['event', new_data.get('event')],
                            ['script_path', new_data.get('script_path')]
                    ] )
            else:
                # all these ones have a 'code' column to compare ...
                check_exists_list = do_search( search_type, [ ['code', new_data.get('code')] ] )

            if not check_exists_list:
                tactic_create_new_sobj( search_type, new_data )


    def execute(my):

        # find a tmp path dump to
        dir = Config.get_value("install", "tmp_dir")
        path = "%s/%s--schema.sql" % (dir, my.template_project)

        # First ... create new DB ...
        print
        print "> Creating DB for new project '%s' ..." % my.new_project
        sys_cmd = '''createdb -h %s -U %s %s -E UTF8;''' % (my.db_host, my.db_user, my.new_project)
        run_sys_cmd( sys_cmd )

        # Second ... dump schema for existing project ...
        print
        print "> Dumping schema of template project '%s' ..." % my.template_project
        sys_cmd = 'pg_dump -h %s -U %s --clean --schema-only %s > %s' % (my.db_host, my.db_user, my.template_project, path)
                                              
        run_sys_cmd( sys_cmd )
      

        # Third ... load the template schema into the newly created DB ...
        print
        print "> Loading template DB schema into new project '%s' ..." % my.new_project
        sys_cmd = 'psql -h %s -U %s -f %s %s' % (my.db_host, my.db_user, path, my.new_project)
        run_sys_cmd( sys_cmd )

        # Then ...
        print
        print "> Copying necessary data from template project into new project copy ..."

        sort_dict = {}

        st_list = my.info.keys()
        for idx, st in enumerate(st_list):
            sort_dict[st] = idx

        sort_dict['sthpw/project'] = -10
        sort_dict['sthpw/schema'] = -9
        sort_dict['sthpw/search_object'] = -8
        sort_dict['sthpw/pipeline'] = -7
        sort_dict['sthpw/trigger'] = -6

        st_list = sorted(st_list, key=sort_dict.__getitem__)
        Batch( project_code='sthpw' )

        for st in st_list:
            if st.startswith("sthpw/"):
                print
                print "    >> now copying sthpw search_type '%s' entries from template project to new project ..." % st
                my.adjust_sthpw( st, my.info.get(st) )

        Batch( project_code=my.new_project )

        for st in st_list:
            if st.startswith("config/") or st.startswith("prod/"):
                print
                print "    >> now copying project search_type '%s' entries from template project to new project ..." % st
                my.copy_config( st, my.info.get(st) )

        print
        print


def usage():

    script = os.path.basename( sys.argv[0] )

    print
    print "  Usage: %s -s <source_project> -n <new_project> [ <optional_args> ]" % script
    print
    print
    print "      REQUIRED arguments"
    print "      ------------------"
    print
    print "         -s <source_project> | --source-project <source_project>"
    print "             ... where <source_project> is the project code of the source project"
    print
    print "         -n <new_project> | --new-project <new_project>"
    print "             ... where <new_project> is the project code of the new project to create"
    print
    print
    print "      OPTIONAL arguments"
    print "      ------------------"
    print
    print "         -i <initials_source> | --initials-source <initials_source>"
    print "             ... where <initials_source> is the short initials code of the source project"
    print
    print "         -t <title_new> | --title-new <title_new>"
    print "             ... where <title_new> is the title label for the new project to create"
    print
    print "         -w | --widget-config-convert"
    print "             ... flag to do a search and replace of source project code in widget_config"
    print "             config column XML ... have to be careful with this one ... works if source"
    print "             project code is NOT like a real word or key word that could be in the config"
    print "             XML for some other purpose (i.e. not as a project code identifier)."
    print
    print "             By default, the script will leave the copy over the widget_config 'config'"
    print "             column values as is."
    print
    print "         -c | --custom-script-convert"
    print "             ... flag to do a search and replace of source project code in custom_script"
    print "             'folder' and 'script' column values ... have to be careful with this one ... works if source"
    print "             project code is NOT like a real word or key word that could be in the folder"
    print "             or script values for some other purpose (i.e. not as a project code identifier,"
    print "             like a using a project code that is the same as a python or JavaScript keyword)."
    print
    print "             By default, the script will leave the copy over the custom_script 'folder'"
    print "             and 'script' column values as is."
    print
    print
    print "         -o <IP> | --host <IP>"
    print "             ... flag to specify the IP address of the database host"


if __name__ == '__main__':


    template_project = None
    template_initials = None

    new_project = None
    new_title = None

    widget_config_convert_flag = False
    custom_script_convert_flag = False
    if Config.get_value('database','server'):
        db_host =  Config.get_value('database','server')
    else:
        db_host = 'localhost'
    
    # setup arguements passed to getopt
    try:
        opts, args = getopt.getopt( sys.argv[1:],
                                    "hwcs:n:i:t:o:",
                                    [
                                        "help", "widget-config-convert", "custom-script-convert",
                                        "source-project=", "new-project=", "initials-source=", "title-new=","host="
                                    ])
    except getopt.error:
        usage()
        sys.exit(1)

    #--------------------------------------
    # set arguments
    #--------------------------------------
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-s", "--source-project"):
            template_project = arg
        elif opt in ("-n", "--new-project"):
            new_project = arg
        elif opt in ("-i", "--initials-source"):
            template_initials = arg
        elif opt in ("-t", "--title-new"):
            new_title = arg
        elif opt in ("-w", "--widget-config-convert"):
            widget_config_convert_flag = True
        elif opt in ("-c", "--custom-script-convert"):
            custom_script_convert_flag = True
        elif opt in ("-o", "--host"):
            db_host = arg

    if not template_project or not new_project:
        usage()
        print
        print "*** NO template/source project code set or NO new project code provided ... aborting script!"
        print
        sys.exit(0)


    Batch(project_code=template_project)

    cmd = GatherTemplateProjectDetailsCmd()
    cmd.set_project( template_project )

    # Command.execute_cmd(cmd)  # use this so that a transaction log entry gets generated
    info = cmd.execute()

    '''
    for k,v in info.items():
        print
        print
        print '"%s" = %s' % (k,v)
    '''

    #sys_cmd = 'psql -h %s -U postgres -c "ALTER TABLE pipeline ALTER COLUMN project_code TYPE character varying (1024);" sthpw' %db_host
    #run_sys_cmd( sys_cmd )


    '''
    Batch(project_code=new_project)
    curr_project_code = Project.get_database_name()
    if new_db_name != new_project:
        print
        print "ERROR: current project DB (%s) does not match new project code of (%s)" % (new_db_name, new_proj)
        print "       ... aborting cloning of project template!"
        print

    else:
    '''

    cmd2 = CloneTemplateProjectCmd()
    cmd2.set_template_project_info( info, template_project, new_project, template_initials, new_title,
                                    widget_config_convert_flag, custom_script_convert_flag, db_host )

    cmd2.execute()

    print
    print "[DONE]"
    print





