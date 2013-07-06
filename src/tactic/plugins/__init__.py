############################################################
#
#    Copyright (c) 2012, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#


import tacticenv
import sys

from pyasm.common import Environment

import os

__all__ = ['import_plugin']


GC = globals()
LC = locals()


plugins = None

def init():
    from pyasm.search import Search
    search = Search("config/plugin")
    sobjects = search.get_sobjects()
    global plugins
    if plugins != None:
        return

    plugins = {}

    for sobject in sobjects:
        code = sobject.get_code()
        plugins[code] = sobject

    for sobject in sobjects:
        code = sobject.get_code()
        import_plugin(code)



def import_plugin(plugin, version=None, gc=None, lc=None):

    if not gc:
        gc = GC
    if not lc:
        lc = LC

    global plugins
    plugin_sobj = plugins.get(plugin)

    if not version:
        if plugin_sobj:
            version = plugin_sobj.get_value("version")


    plugin_dir = Environment.get_plugin_dir()
    if version:
        plugin_path = "%s/%s-%s" % (plugin_dir, plugin, version)
        module = "%s-%s" % (plugin, version)
    else:
        plugin_path = "%s/%s" % (plugin_dir, plugin)
        module = plugin

    if os.path.exists(plugin_path):
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
    else:
        install_dir = Environment.get_install_dir()
        plugin_path = "%s/src/tactic/plugins/%s" % (install_dir, plugin)
        if os.path.exists(plugin_path):
            if plugin_path not in sys.path:
                sys.path.insert(0, plugin_path)
        else:
            return


    module = module.replace(".", "_")
    module = module.replace("-", "_")

    if not os.path.exists("%s/%s" % (plugin_path, module)):
        return

    exec("import %s as %s" % (module, plugin), gc, lc)
    sys.path.remove(plugin_path)

    module = eval(plugin)
    if not module:
        print "WARNING: module [%s] could not be loaded" % module

    return module


init()

