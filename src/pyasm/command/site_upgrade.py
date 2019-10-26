from tactic.command import PluginUninstaller, PluginInstaller
from pyasm.common import Xml, Environment
from pyasm.command import Command
from copy import copy
from pyasm.biz import Project
from pyasm.security import Sudo
import datetime


__all__ = ['SiteUpgradeCmd']


class SiteUpgradeCmd(Command):
    
    def execute(self):
        '''Update the Plugins and Database of this project'''
        sudo = Sudo()
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(self.kwargs)
        project_code = self.kwargs.get("project_code")
        site = self.kwargs.get("site")
        is_upgrade = self.kwargs.get("is_upgrade") or [None]

        Project.set_project('sthpw')
        db_resource = Project.get().get_project_db_resource()
        db = Sql(db_resource)
    
        update_sql = "select last_version_update from project where code = '%s';" % project_code
        project_version = db.do_query(update_sql)
        newest_version = Environment.get_release_version()

        if newest_version[0] == 'v':
            newest_version = newest_version[1: len(newest_version)]
        
        if project_version:
            if project_version != newest_version:
                os.system("python /spt/tactic/TACTIC/src/bin/upgrade_db.py -y -f -p %s -s %s" % (project_code, site))

        Project.set_project(project_code)
        project_db_resource = Project.get().get_project_db_resource()
        project_db = Sql(project_db_resource)
        plugin_sql = 'select code, version from spt_plugin'
        plugins = copy(project_db.do_query(plugin_sql))
        
        for code, version in plugins:
            if "stypes" in code:
                continue
            plugin_dir = '%s/%s' % (Environment.get_plugin_dir(), code)
            manifest_path = "%s/manifest.xml" % plugin_dir
            log_path = "%s/upgrade_log.txt" % plugin_dir
            if not os.path.exists(plugin_dir):
                manifest_path = "/spt/Southpaw/consulting/%s/manifest.xml" % code
                log_path = "/spt/Southpaw/consulting/%s/upgrade_log.txt" % code
            
            if os.path.exists(manifest_path):
                f = open(manifest_path, 'r')
                manifest = f.read()
                f.close()

                xml = Xml()
                xml.read_string(manifest)
                latest_version = xml.get_value("manifest/data/version") or None
                if not latest_version:
                    continue
                elif not version:
                    print("Uninstalling plugin: ", plugin_dir)
                    uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
                    uninstaller.execute()
                    
                    print("Installing plugin: ", plugin_dir)
                    installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
                    installer.execute()

                    log_f = open(log_path, 'a')
                    log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
                    log_f.close()
                    is_upgrade[0] = True
                elif version != latest_version:
                    print("Uninstalling plugin: ", plugin_dir)
                    uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
                    uninstaller.execute()

                    print("Installing plugin: ", plugin_dir)
                    installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
                    installer.execute()

                    log_f = open(log_path, 'a')
                    log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
                    log_f.close()
                    is_upgrade[0] = True
        sudo.exit()