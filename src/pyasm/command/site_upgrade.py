from tactic.command import PluginUninstaller, PluginInstaller
from pyasm.common import Xml, Environment
from pyasm.command import Command
from pyasm.search import Sql
from copy import copy
from pyasm.biz import Project
from pyasm.security import Sudo, Site
from pyasm.search import Search
import datetime
import os


__all__ = ['SiteUpgradeCmd']


class SiteUpgradeCmd(Command):
    
    def execute(self):
        '''Update the Plugins and Database of this project'''
        sudo = Sudo()

        project_code = self.kwargs.get("project_code")
        site = self.kwargs.get("site")
        tmp_dir = Environment.get_tmp_dir()
        upgrade_status = "%s/upgrade/upgrade_%s_%s.txt" % (tmp_dir, site, project_code)

        Site.set_site(site)

        search = Search('config/plugin')
        plugin_sobjects = search.get_sobjects()

        project_sobject = Search.eval("@SOBJECT(sthpw/project['code', '%s'])" % project_code)
        project_version = project_sobject[0].get_value("last_version_update")
        newest_version = Environment.get_release_version()

        if newest_version[0] == 'v':
            newest_version = newest_version[1: len(newest_version)]
        
        if project_version:
            if project_version != newest_version:
                f = open(upgrade_status, "w")
                f.write("start")
                f.close()

                os.system("python /spt/tactic/TACTIC/src/bin/upgrade_db.py -y -f -p %s -s %s" % (project_code, site))

        for plugin_sobject in plugin_sobjects:
            code = plugin_sobject.get_value("code")
            version = plugin_sobject.get_value("version")
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
                    f = open(upgrade_status, "w")
                    f.write("start")
                    f.close()
                    print("Uninstalling plugin: ", plugin_dir)
                    uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
                    uninstaller.execute()
                    
                    print("Installing plugin: ", plugin_dir)
                    installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
                    installer.execute()

                    log_f = open(log_path, 'a')
                    log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
                    log_f.close()
                elif version != latest_version:
                    f = open(upgrade_status, "w")
                    f.write("start")
                    f.close()
                    print("Uninstalling plugin: ", plugin_dir)
                    uninstaller = PluginUninstaller(plugin_dir=plugin_dir, verbose=False)
                    uninstaller.execute()

                    print("Installing plugin: ", plugin_dir)
                    installer = PluginInstaller(plugin_dir=plugin_dir, verbose=False, register=True, version=latest_version)
                    installer.execute()

                    log_f = open(log_path, 'a')
                    log_f.write("Plugin Updated to version %s: %s\n" % (latest_version, datetime.datetime.now()))
                    log_f.close()
        
        f = open(upgrade_status, "w")
        f.write("end")
        f.close()
        
        sudo.exit()