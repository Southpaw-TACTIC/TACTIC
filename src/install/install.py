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

__all__ = ['Install']

import os, shutil, sys
import subprocess
import re
import os.path

PYTHON_EXE = 'python'

class InstallException(Exception):
    pass

class Install:

    def run_sql(my, sql):
        from pyasm.search import DatabaseImpl, DbContainer
        db = DbContainer.get("sthpw")
        db.do_update(sql)

    

    def check_db_program(my):
        try:
            print
            print "Verifying the database is installed. The default is no password if you have followed the instructions to not require a password. If you see it asking for 'Password for user postgres', you should close this window and make the database not require a password first (refer to our install documentation) and resume the installation."
            print

            # Determine database type.
            # Run command query and exit.
            print '\nDatabase type is: ', my.database_type
            print '(if this is not the database type desired,'
            print 'hit Ctrl+C to cancel and see the types available with \'python install.py -h\' )'
            if my.database_type == 'PostgresSQL':
                program = subprocess.Popen(['psql', '-U',  'postgres', '-p', my.port_num, '-c', "\q"], shell=True, stdout = subprocess.PIPE , stderr = subprocess.PIPE, stdin=sys.stdin)
            elif my.database_type == 'SQLServer':
                program = subprocess.Popen(['sqlcmd', '-U',  'tactic', '-P', 'south123paw', '-Q', "quit"], shell=True, stdout = subprocess.PIPE , stderr = subprocess.PIPE, stdin=sys.stdin)
                        
            elif my.database_type == 'Oracle':
                raise InstallException('Integration with Oracle SQL shell command has not been implemented yet.')
            else:
                raise InstallException('Database type must be: PostgresSQL or SQLServer.  Please try again.')
            

            lines = program.stderr.readlines()
            line = '\n'.join(lines)
            if os.name =='nt' and line.find('is not recognized') != -1:
                if my.database_type == 'PostgresSQL':
                    raise InstallException('Please put psql.exe for Postgres in your PATH environment variable. When you are finished, run install.py again.')
                elif my.database_type == 'SQLServer':
                    raise InstallException('Please put sqlcmd.exe for SQLServer in your PATH environment variable. When you are finished, run install.py again.')
                else:
                    raise InstallException('Please put the SQL command shell for the database in your PATH environment variable. When you are finished, run install.py again.')
          
	except KeyboardInterrupt, e:
            print "Exiting..."
            sys.exit(0)

    def check_db_exists(my, project_code):
        # create the sthpw database

        if my.database_type == 'SQLServer':
            # TODO: Implement drop database option for SQL Server.
            return

        if os.name == 'nt':
            if my.database_type == 'SQLServer':
                # Print out an error and exit
                # if the sthpw already exists.
                args = 'sqlcmd -U tactic -P south123paw -Q \" \
                    DECLARE @db_id int; \
                    SET @db_id = db_id(\'%s\'); \
                    IF @db_id IS NOT NULL \
                        print \'Database already exists\'\
                    \"' % project_code
                program = subprocess.Popen(args, shell=True, \
                    stdout = subprocess.PIPE , stderr = subprocess.PIPE, stdin=sys.stdin)
                lines = program.stdout.readlines()
                line = '\n'.join(lines)
                if line.find('Database already exists') != -1:
                    print "\nError: Database '%s' already exists. Please drop the database '%s' and re-run install again." %(project_code, project_code)
                    print "Exiting..."
                    sys.exit(0)
            else:
                args = ['psql','-U', 'postgres',  '-p', my.port_num, '-c', "\c %s;\q"%project_code]

        else:
            args = 'psql -U postgres -p %s -c  "\c %s;\q"'%(my.port_num, project_code)
        program = subprocess.Popen(args, shell=True, \
            stdout = subprocess.PIPE , stderr = subprocess.PIPE, stdin=sys.stdin)
        lines = program.stdout.readlines()
        line = '\n'.join(lines)
        
        if line.find('connected to database') != -1:
            print "Database '%s' already exists. Do you want to drop the database '%s' and continue?, If you choose 'y', It will be backed up to the current directory.  (y/n)" %(project_code, project_code)
            print
            answer = raw_input("(n) -> " )
            if answer in ['y','Y']:
                # can't read from config file at this point, just make these default assumptions
                db_host = 'localhost'
                db_user = 'postgres'
                backup_name = 'sthpw_backup.sql'
                current_dir = my.get_current_dir()
                
                backup_cmd = 'pg_dump -h %s -U %s -p %s --clean sthpw > %s/%s ' % (db_host, db_user, my.port_num, current_dir, backup_name)
                os.system(backup_cmd)
                my.backup_msg =  "Database 'sthpw' is backed up to [%s/%s]" %(current_dir, backup_name)
                if my.backup_msg:
                    print
                    print my.backup_msg


                os.system('dropdb -U postgres -p %s sthpw'%my.port_num)
                my.check_db_exists('sthpw')
            else:
                raise InstallException("Database '%s' already exists. You can back it up first and then run the install again." % project_code)


   
    def update_tactic_configs(my):
        #tactic_conf_path = '%s/config/%s' %(my.tactic_site_dir, my.tactic_conf)
        tactic_conf_path = '%s/config/tactic-conf.xml' %(my.tactic_data_dir)
        f = open(tactic_conf_path, 'r')
        new_lines = []
        data_keyword = ''

        if os.name == 'nt':
            keyword = 'C:/Program Files/Southpaw'
            data_keyword = 'C:/ProgramData/Southpaw'
        else:
            keyword = '/home/apache'
        for line in f:
            if line.find(keyword) != -1:
                 line = line.replace(keyword, my.tactic_base_dir)
            elif line.find(data_keyword) != -1 and os.name == 'nt':
                 line = line.replace(data_keyword, my.tactic_data_base_dir)

            new_lines.append(line)
        f.close()
    
        f = open(tactic_conf_path, 'w')
        for line in new_lines:
            f.write(line)
        f.close()

        # apache conf extension
        new_lines = []
        apache_conf_path = '%s/config/%s' %(my.tactic_data_dir, my.apache_conf)
        my.apache_conf_path = apache_conf_path
        f = open(apache_conf_path, 'r')
        new_lines = []
        for line in f:
            if line.find(keyword) != -1:
                 line = line.replace(keyword, my.tactic_base_dir)
            elif line.find(data_keyword) != -1 and os.name == 'nt':
                 line = line.replace(data_keyword, my.tactic_data_base_dir)

            new_lines.append(line)
        f.close()
    
        f = open(apache_conf_path, 'w')
        for line in new_lines:
            f.write(line)
        f.close()


    def create_temp_directory(my):
        from pyasm.common import Environment 
        my.tmp_dir = Environment.get_tmp_dir()
        print "Creating TACTIC temp directories: ", my.tmp_dir
        if not os.path.exists(my.tmp_dir):
            os.makedirs(my.tmp_dir)

    def change_directory_ownership(my):
        if os.name != 'nt':
            print "Changing directory ownership of temp and data directories"
            # set the owner of tmp_dir and site_dir
            os.system('chown -R %s \"%s\"'\
                %(my.tactic_apache_user, my.tmp_dir))

            os.system('chown -R %s \"%s\"'\
                %(my.tactic_apache_user, my.tactic_site_dir))

            os.system('chown -R %s \"%s\"'\
                %(my.tactic_apache_user, my.tactic_data_dir))

            os.system('chown -R %s \"%s/assets\"'\
                %(my.tactic_apache_user, my.tactic_base_dir))

            os.system('chown -R %s \"%s\"'\
                %(my.tactic_apache_user, my.tactic_src_dir))

    def install_win32_service(my):
        if os.name == 'nt':
            print "Installing win32 service."
            # install the windows service
            current_dir = my.get_current_dir()
            service_path = '"%s/src/install/service/win32_service.py" install'%current_dir
            os.system(PYTHON_EXE + ' %s' %service_path)


    def execute(my, install_db=True, install_defaults=False, database_type='PostgresSQL', port_num='5432'):
        my.tactic_base_dir = None
        my.tactic_data_base_dir = None
        my.tactic_install_dir = None
        my.tmp_dir = None
        my.tactic_site_dir = None
        my.tactic_apache_user = 'apache'
        my.apache_conf_path = None
        my.database_type = database_type
        my.port_num = port_num

        my.backup_msg = None
        my.non_default_install = False
        project_code = "sthpw"
        project_type = "sthpw"

        my.print_header()

        # verification
        try:
            if install_db:
                my.check_db_program()

            	my.check_db_exists(project_code)
            # install the necessary files to python directory
            my.install_to_python(install_defaults)
        
        except InstallException, e:
            print "Error: %s" %e.__str__()
            print
            print "Exiting..."
            print
            sys.exit(2)

        my.update_tactic_configs()

        # check modules
        try:
            import tacticenv
        except ImportError:
            print 'Error: Failed to "import tacticenv"'
            return
        my.check_modules(install_db)

        # create the asset_dir
        from pyasm.common import Environment
        asset_dir = Environment.get_asset_dir()
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)



        # check that the main directories exists
        install_dir = os.getenv("TACTIC_INSTALL_DIR")
        data_dir = os.getenv("TACTIC_DATA_DIR")
        if not os.path.exists(install_dir):
            print "Environment variable TACTIC_INSTALL_DIR '%s' does not exist" % install_dir
            return
        if not os.path.exists(data_dir):
            print "Environment variable TACTIC_DATA_DIR '%s' does not exist" % data_dir
            return

        my.create_temp_directory()

        my.change_directory_ownership()

        my.install_win32_service()


        if install_db == False:
            print "TACTIC setup successful.  Next, the TACTIC database needs to be configured."
            return

        # dynamically load modules now that we know where they are
        from pyasm.search import DatabaseImpl, DbContainer

        # create the sthpw database
        database = DatabaseImpl.get()

     

        # check if database exists
        print "Creating database '%s' ..." % project_code
        print

        db_exists = False
        from pyasm.search import DatabaseException
        try:
            if database.database_exists(project_code):
                print "... already exists. Please remove first"
                raise InstallException("Database '%s' already exists" % project_code)
                db_exists = True
        except DatabaseException, e:
            pass
            
        if not db_exists:
            # create the database
            database.create_database(project_code)

        # import the default schema
        database.import_schema(project_code, project_type)

        # import the default data
        database.import_default_data(project_code, project_type)

        # add the default user (admin)
        my.run_sql('''
      
        --add in admin group
INSERT INTO login_group (login_group, description)
VALUES ('admin', 'Site Administration');

        --add in admin user, default password 'tactic'
INSERT INTO "login" ("login", "password", "upn", first_name, last_name)
VALUES ('admin', '39195b0707436a7ecb92565bf3411ab1', 'admin', 'Admin', '');

        --add the admin user to the admin group
INSERT INTO login_in_group ("login", login_group) VALUES ('admin', 'admin');
        ''')


        # add in the necessary triggers for email notification
        my.run_sql('''
        --register notification
INSERT INTO notification (code, description, "type", search_type, event)
VALUES ('asset_attr_change', 'Attribute Changes For Assets', 'email', 'prod/asset', 'update|prod/asset');
INSERT INTO notification (code, description, "type", search_type, event)
VALUES ('shot_attr_change', 'Attribute Changes For Shots', 'email', 'prod/shot', 'update|prod/shot');
        ''')

       
        print "Upgrading the database schema in quiet mode..."
        print

        from pyasm.search.upgrade import Upgrade
        from pyasm.security import Batch


         
        Batch()
        version = my.get_version()
        version.replace('.', '_')
        upgrade = Upgrade(version, is_forced=True, project_code=None, quiet=True)
        upgrade.execute()
        #print os.system('python \"%s/src/bin/upgrade_db.py\" -f -q -y'%install_dir)

        print
        print
        print "*** Installation of TACTIC completed at [%s] ***" %my.tactic_base_dir
        print
        print
        #if my.backup_msg:
        #    print my.backup_msg

        if os.name != 'nt':
            print "Next, please install the Apache Web Server and then copy the Apache config extension [%s] to the Apache web server config area. e.g. /etc/httpd/conf.d/"%my.apache_conf_path

        else:
            print "Next, please install the Apache Web Server and then copy the Apache config extension [%s] to the Apache web server config area. e.g. C:/Program Files/Apache Software Foundation/Apache2.2/conf/"%my.apache_conf_path
    
        print
        print "Depending on the OS, you may need to add the following line to the main config file [httpd.conf] shipped with Apache as well:"


        print
        if os.name == 'nt':
            print "Include conf/tactic_win32.conf"
        else:
            print "Include conf.d/*.conf"
        print

    def print_header(my):
        print
        print
        print "*"*20
        print "Tactic Installation"
        print "*"*20
        print


    def get_user(my):
        import getpass
        user = getpass.getuser()
        return user

    def get_version(my):
        cur_path = os.path.abspath(__file__)
        cur_path, file = os.path.split(cur_path)

        if os.name == "nt":
            parts = cur_path.split('\\')
        else:
            parts = cur_path.split('/')
        parts = parts[:-2]
            
        current_dir = '/'.join(parts)
        f = open('%s/VERSION' %current_dir,'r')
        version = f.readline()
        f.close()
        return version

    def in_directory(my, file, directory):
        #make both absolute    
        directory = os.path.realpath(directory)
        file = os.path.realpath(file)
        #return true, if the common prefix of both is equal to directory
        #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
        return os.path.commonprefix([file, directory]) == directory
    
    def check_web_server_user(my, name):
        import pwd
        try:
            pw = pwd.getpwnam(name)
            uid = pw.pw_uid
        except KeyError:
            return False
        return uid
      
    def get_default_web_server_user(my):
        user = 'apache'
        try:
            f = open('/etc/passwd', 'r')
            for line in f:
                if line.startswith('apache'):
                    user = 'apache'
                    break
                if line.startswith('www-data'):
                    user = 'www-data'
                    break
                if line.startswith('wwwrun'):
                    user = 'wwwrun'
                    break
        except:
            user = 'apache'

        return user


    def get_current_dir(my):
        ''' get the current tactic src root where install.py is launched from'''
        cur_path = os.path.abspath(__file__)
        cur_path, file = os.path.split(cur_path)

        if os.name == "nt":
                parts = cur_path.split('\\')
        else:
                parts = cur_path.split('/')
        parts = parts[:-2]
            
        current_dir = '/'.join(parts)
        return current_dir

    def install_to_python(my, install_defaults=False):
        # install the files into python site-packages directory
        version_info = sys.version_info
        from distutils.sysconfig import get_python_lib
        python_site_packages_dir = get_python_lib()

        # use old method of it is not found
        if not python_site_packages_dir:

            if os.name == 'nt':
                python_site_packages_dir = "C:/Python%s%s/Lib/site-packages" % \
                (version_info[0], version_info[1])
            elif os.name == 'mac':
                python_site_packages_dir = "/Library/Python/%s.%s/site-packages" % \
                (version_info[0], version_info[1])

                # look at an alternative location
                if not os.path.exists(python_site_packages_dir):
                    python_site_packages_dir = "/Library/Frameworks/Python.framework/Versions/%s.%s/lib/python%s.%s/site-packages" % (version_info[0], version_info[1], version_info[0], version_info[1])

            else:
                python_site_packages_dir = "/usr/lib/python%s.%s/site-packages" % \
                (version_info[0], version_info[1])

            linux_version_path = '/etc/issue'
            linux_os = 'CentOS'
            if os.name == 'posix' and os.path.exists(linux_version_path):
                f = open(linux_version_path, 'r')
                content = ' '.join(f.readlines())
                f.close()
                if 'CentOS' in content:
                    linux_os = 'CentOS'
                elif 'Fedora' in content:
                    linux_os = 'Fedora'
                elif 'Debian' in content:
                    linux_os = 'Debian'



        if not os.path.exists(python_site_packages_dir) and os.name =='posix':
            if linux_os == 'CentOS':
                # CentOS stores the python site packages under /usr/local/lib, not /usr/lib
                python_site_packages_dir = "/usr/local/lib/python%s.%s/site-packages" % \
                    (version_info[0], version_info[1])
            elif linux_os == 'Debian':
                python_site_packages_dir = "/usr/lib/python%s.%s/dist-packages" % \
                    (version_info[0], version_info[1])


        if not os.path.exists(python_site_packages_dir):
            raise Exception("Could not find python site-packages location [%s]" % python_site_packages_dir)


        python_install_dir = "%s/tacticenv" % python_site_packages_dir
        if not os.path.exists(python_install_dir):
            os.makedirs(python_install_dir)


        current_dir = my.get_current_dir()
        # copy the data files
        files = ["__init__.py", "tactic_paths.py"]
        for file in files:
            shutil.copy("%s/src/install/data/%s" %(current_dir, file), "%s/%s" % (python_install_dir,file))

        default_data_dir = ''
        tactic_data_base_dir = ''
        # set defaults according to os
        if os.name == "nt":
            default_base_dir = "C:/Program Files/Southpaw"
            default_data_dir = "C:/ProgramData/Southpaw"
        else:
            default_base_dir = "/home/apache"


        
        # set tactic install dir
        if not install_defaults:
            print
            print "Please enter the base path of the Tactic installation:"
            print
            tactic_base_dir = raw_input("(%s) -> " % default_base_dir)
            if not tactic_base_dir:
                tactic_base_dir = default_base_dir
            print
    
            # only for windows
            if os.name == 'nt': 
                tactic_data_base_dir = default_data_dir

        else:
            tactic_base_dir = default_base_dir
            tactic_data_base_dir = default_data_dir

        tactic_base_dir = tactic_base_dir.replace("\\", "/")
        tactic_base_dir = tactic_base_dir.rstrip('/')

        tactic_data_base_dir = tactic_data_base_dir.replace("\\", "/")
        tactic_data_base_dir = tactic_data_base_dir.rstrip('/')

        if tactic_base_dir != default_base_dir:
            my.non_default_install = True
           

        version = my.get_version()
        my.tactic_base_dir = tactic_base_dir
        my.tactic_src_dir = '%s/tactic_src_%s'%(tactic_base_dir, version)
        my.tactic_install_dir = '%s/tactic'%tactic_base_dir

        my.tactic_site_dir = '%s/projects' %tactic_base_dir
    

        # set apache user for Linux
        if os.name != 'nt':
            default_apache_user = my.get_default_web_server_user()
            if not install_defaults:
                print
                print "Please enter the user Apache Web Server is run under:"
                print
                tactic_apache_user = raw_input("(%s) -> " % default_apache_user)
                if not tactic_apache_user:
                    tactic_apache_user = default_apache_user
                print 
	    else:
                tactic_apache_user = default_apache_user

            my.tactic_apache_user = tactic_apache_user
            user_id  =  my.check_web_server_user(tactic_apache_user) 
            if user_id == False:
                print "User [%s] does not exist in the system. Exiting..." %tactic_apache_user
                print
                sys.exit(2)


        my.tactic_data_dir = '%s/tactic_data' %my.tactic_base_dir
        if os.name == 'nt':
            my.tactic_data_dir = '%s/Tactic' %tactic_data_base_dir
            my.tactic_data_base_dir = tactic_data_base_dir


        # copy the files to the python directory
        f = open("%s/tactic_paths.py" % python_install_dir, "a")
        f.write("\n")
        f.write("TACTIC_INSTALL_DIR='%s'\n" % my.tactic_install_dir)
        #f.write("TACTIC_SITE_DIR='%s'\n" % my.tactic_site_dir)
        f.write("TACTIC_SITE_DIR=''\n")
        f.write("TACTIC_DATA_DIR='%s'\n" % my.tactic_data_dir)
        f.write("\n")
        f.close()

        try:
            if not os.path.exists(my.tactic_site_dir):
                os.makedirs(my.tactic_site_dir)
            if not os.path.exists(my.tactic_data_dir):
                os.makedirs(my.tactic_data_dir)
        except OSError, e:
            if e.__str__().find('Access is denied') != -1:

                print "Permission error to create directories"
                if os.name =='nt':
                    print "Try to run your cmd.exe as Administrator by Shift+right clicking on the Cmd.exe icon."
                raise InstallException(e)

        # set the tactic user
        # Disabling until this actuall has meaning
        """
        if not os.name == "nt":
            default_tactic_user = "apache"
            default_tactic_group = "apache"
            print
            print "Please enter TACTIC user:"
            print
            my.tactic_user = raw_input("(%s) -> " % default_tactic_user)
            if not my.tactic_user:
                my.tactic_user = default_install_dir
            my.tactic_group = my.tactic_user
       



        # copy all of the files from the template to the sites directory
        for root, dirs, files in os.walk("template"):
            root = root.replace("\\","/")

            # ignore ".svn"
            if root.find("/.svn") != -1:
                continue

            # create root directory
            old = root
            new = old.replace("template", my.tactic_site_dir)
            dirname = os.path.dirname(new)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # go through each and copy
            for file in files:
                # ignore compiled python files
                if file.endswith(".pyc") or file.startswith('.'):
                    continue

                old = "%s/%s" % (root, file)
                new = old.replace("template", my.tactic_site_dir)

                dirname = os.path.dirname(new)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)

                shutil.copyfile(old, new)
                # FIXME: this does not work ... need uid and gid
                #if not os.name == "nt":
                #    os.chown(new,my.tactic_user,my.tactic_group)


        """
        

        my.tactic_license = 'tactic-license.xml'
        if os.name != 'nt':
            my.apache_conf = 'tactic.conf'
            my.tactic_conf = 'tactic_linux-conf.xml'
        else:
            my.apache_conf = 'tactic_win32.conf'
            my.tactic_conf = 'tactic_win32-conf.xml'






        try:
            src = '%s/src/install/apache/%s' %(current_dir, my.apache_conf)
            dst_dir= '%s/config' % my.tactic_data_dir
            dst = '%s/config/%s' %(my.tactic_data_dir, my.apache_conf)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            shutil.copyfile(src, dst)

            src = '%s/src/install/template/config/%s' %(current_dir, my.tactic_conf)
            dst = '%s/config/tactic-conf.xml' %(my.tactic_data_dir)
            shutil.copyfile(src, dst)
           
            # Copy the TACTIC EPL license over to the tactic_data/config directory
            src = '%s/src/install/template/config/%s' %(current_dir, my.tactic_license)
            dst = '%s/config/%s' %(my.tactic_data_dir, my.tactic_license)
            shutil.copyfile(src, dst)
           
            # copy default project templates
            src = '%s/src/install/start/templates' %current_dir
            dst =  '%s/templates' %my.tactic_data_dir
            if not os.path.exists(dst):
                shutil.copytree(src, dst)

        except OSError, e:
            raise InstallException(e)
        except IOError, e:
            raise InstallException(e)

        if os.name != 'nt':
            src_dir = my.tactic_src_dir
        else:
            src_dir = my.tactic_install_dir






        # prevent copying to itself
        #print "SRC_DIR ", src_dir
        #print "CUR ", current_dir
        if my.in_directory(src_dir, current_dir):
            raise InstallException("The install directory can't be inside the current directory.")

        if src_dir != current_dir:

            if os.path.exists(src_dir):
                print
                output = raw_input("Custom install directory [%s] already exists. It will be removed and copied over. Continue? (y/n) -> "%src_dir)
                if output.lower() not in ['yes', 'y']:
                    print "Installation has been stopped."
                    sys.exit(2)
                else:
                    try:
                        shutil.rmtree(src_dir)
                    except OSError, e:
                        print
                        print "Errors in removing directories."
                        raise InstallException(e)

            print
            print "Copying files to the install directory... It may take several minutes."
            shutil.copytree(current_dir, src_dir)

        sys.path.append("%s/src"%src_dir)


        # create symlink
        if os.name != 'nt':
            if os.path.islink(my.tactic_install_dir):
                os.unlink(my.tactic_install_dir)

            if not os.path.exists(my.tactic_install_dir):
                print
                print "Creating a symlink at [%s]..." % my.tactic_install_dir
                os.symlink(my.tactic_src_dir, my.tactic_install_dir)
            



    def check_modules(my, install_db):
        print
        print "Verifying Python modules are properly installed..." 
        print

        try:
            import Crypto
        except ImportError:
            print "ERROR: Cannot import Crypto python module.  Please Install."
            print
            raise
 

        try:
           #import Image
           from PIL import Image 
        except ImportError:
            print "ERROR: Cannot import Python Imaging Library. Please Install."
            print
            raise
            
        #try:
        #    from Ft.Xml.XPath import Evaluate
        #except ImportError:
        #    print "ERROR: Cannot import Python 4Suite Xml module.  Please Install."
        #    print
        #    raise
        try:
            from lxml import etree
        except ImportError:
            print "ERROR: Cannot import lxml.  Please Install."
            print
            raise
 

 
        try:
            from pyasm.search import Sql
        except ImportError:
            try:
                import pyodbc
            except ImportError:
                print "ERROR: Cannot import Python Database module (pgdb or pyscopg2 or pyodbc).  Please install."
                print
                raise

        try:
            # Python 2.6 ships with json
            import json
        except ImportError:
            try:
                import simplejson
            except ImportError:
                print "ERROR: Cannot import simplejson module.  Please Install."
                print
                raise
        if os.name == 'nt':
            try:
                import win32serviceutil
            except ImportError:
                print "ERROR: Cannot import Python Database module (win32serviceutil).  Please Install py-win32."
                print
                raise





if __name__ == '__main__':
    from optparse import OptionParser
    install_defaults = False
    parser = OptionParser()

    parser.add_option("-i", "--install_db", action="store", help="Install Database Schema (default true)", dest="install_db")
    parser.add_option("-d", "--defaults",  action="store_true", help="Accept default answers" ,dest="install_defaults")
    parser.add_option("-t", "--type", help="Specify database type: SQLServer or PostgresSQL (default PostgresSQL)", dest="database_type")
    parser.add_option("-p", "--port", help="Specify database port to install in. Default is 5432", dest="port_num", default="5432")
    opts, args = parser.parse_args()
    install_db = opts.install_db
    install_defaults = opts.install_defaults
    database_type = opts.database_type
    port_num = opts.port_num
    if not install_defaults:
        install_defaults = False
    else:
        install_defaults = True

    if not install_db:
        install_db = True
    elif install_db == "false" or install_db == "False":
        install_db = False
        print
        print "  (Database Schema: You have indicated not to install the database schema.)"
    else:
        install_db = True

    if not database_type:
        database_type = 'PostgresSQL'

    install = Install()
    install.execute(install_db=install_db,install_defaults=install_defaults,database_type=database_type, port_num=port_num )
    





