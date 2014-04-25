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


__all__ = ["ConfigException", "Config"]

import os

from base import *
from container import *
from common import *

class TacticException(Exception):
    pass


# prefer lxml
try:
    import lxml.etree as etree
    from lxml_wrapper import *
except Exception, e:
    print "WARNING: ", e
    from xml_wrapper import *


class ConfigException(Exception):
    pass

    
class Config(Base):
    '''provides access to sitewide configuation files'''

    CONFIG_KEY = "Config:data"

    def get_value(cls, module_name, key, no_exception=True, default="", use_cache=True, sub_key=None):
        '''get configuration file value'''

        data = Container.get(Config.CONFIG_KEY)
        if data == None:
            data = {}
            Container.put(Config.CONFIG_KEY, data)

        KEY = "%s:%s" % (module_name, key)
        if sub_key:
            KEY = "%s:%s:%s" % (module_name, key, sub_key)
        value = data.get(KEY)

        if not use_cache or value == None:
            xml_data = Config.get_xml_data()

            version = xml_data.get_value("config/@version")
            if not version:
                xpath = "config/%s/@%s" % (module_name, key)
                value = xml_data.get_value(xpath)
            else:
                xpath = "config/%s/%s" % (module_name, key)
                value = xml_data.get_value(xpath)

            value = Common.expand_env(value)

            if not value and default:
                value = default

            if not no_exception and value == "":
                raise ConfigException("config value [%s/%s] is empty or does not exist" % ( module_name, key) )

            value = value.strip()
            if sub_key:
                sub_value = eval(value)
                sub_value = sub_value.get(sub_key)
                value = sub_value

            data[KEY] = value

        return value

    get_value = classmethod(get_value)

    def get_dict_value(cls, module_name, key, no_exception=True, default="", use_cache=True):
        value = cls.get_value(module_name, key, no_exception, default, use_cache)
        if value:
            try:
                value = jsonloads(value)
            except ValueError, e:
                value = {
                    'default': value.strip()
                }
        else:
            value = {}
        return value
    get_dict_value = classmethod(get_dict_value)



    def reload_config():
        Container.put(Config.CONFIG_KEY, {})
        xml_data = Config.get_xml_data()
    reload_config = staticmethod(reload_config)




    def get_section_values(section_name):
        xml_data = Config.get_xml_data()
        xpath = "config/%s" % section_name
        node = xml_data.get_node(xpath)

        version = xml_data.get_value("config/@version")
        if not version:
            attributes = Xml.get_attributes(node)
        else:
            attributes = Xml.get_node_values_of_children(node)

        return attributes
    get_section_values = staticmethod(get_section_values)



    def set_value(module_name, key, value, no_exception=True, create=True):
        xml_data = Config.get_xml_data()

        node = xml_data.get_node("config/%s/%s" % (module_name, key))
        # the node has to already exist
        if node is None:
            if not no_exception:
                raise ConfigException("No node for module [%s] with key [%s] in TACTIC config file" % (module_name, key))
            # else auto create
            elif create:
                parent_node = xml_data.get_node("config/%s" % (module_name))
                if parent_node is None:
                    parent_node = xml_data.create_element(module_name)
                    root_node = xml_data.get_root_node()
                    Xml.append_child(root_node,parent_node)

                node = xml_data.create_element(key)
                Xml.append_child(parent_node, node)
            else:
                return

        xml_data.set_node_value(node, jsondumps(value))

        data = Container.get(Config.CONFIG_KEY)
        if data == None:
            data = {}
            Container.put(Config.CONFIG_KEY, data)

        KEY = "%s:%s" % (module_name, key)
        #if sub_key:
        #    KEY = "%s:%s:%s" % (module_name, key, sub_key)
        data[KEY] = jsondumps(value)
 



    set_value = staticmethod(set_value)


    def remove(module_name, key):
        xml_data = Config.get_xml_data()
        node = xml_data.get_node("config/%s/%s" % (module_name, key))
        if node is None:
            return
        parent = Xml.get_parent(node)
        Xml.remove_child(parent, node)
    remove = staticmethod(remove)
 

    def get_xml_data(use_cache=True):
        '''read the main framwork configuration file'''
        config_path = Config.get_config_path()
        #print "config: ", config_path

        xml_data = Xml()

        if not os.path.exists(config_path):
            config = "<config/>"
            xml_data.read_string(config)
        else:
            xml_data.read_file(config_path, cache=use_cache)

        return xml_data

        # parse only once
        #XML_KEY = "Config:xml_data"
        #xml_data = Container.get(Config.XML_KEY)
        #if xml_data == None:
        #    config_path = Config.get_config_path()
        #    xml_data = Xml()
        #    xml_data.read_file(config_path)
        #    Container.put(Config.XML_KEY, xml_data)
        #return xml_data

    get_xml_data = staticmethod(get_xml_data)


    def get_default_config_path():
        # use the default
        from environment import Environment
        install_dir = Environment.get_install_dir()
        if os.name == 'nt':
            filename = "standalone_win32-conf.xml"
        else:
            filename = "standalone_linux-conf.xml"

        path = "%s/src/install/config/%s" % (install_dir, filename)
        return path
    get_default_config_path = staticmethod(get_default_config_path)


    def get_config_dir(cls):
        '''the priority goes from 
           TACTIC_CONFIG_PATH > TACTIC_DATA_DIR > TACTIC_SITE_DIR (depreceated)'''
        dirname = None
        path = os.environ.get("TACTIC_CONFIG_PATH")
        if path:
            dirname = path.replace("\\", "/")
            dirname = os.path.dirname(path)

	if not dirname:
	    dirname = os.environ.get("TACTIC_DATA_DIR")
	    if dirname:
                dirname = "%s/config" % dirname

        # DEPRECATED
        if not dirname:
            dirname = os.environ.get("TACTIC_SITE_DIR")
            dirname = "%s/config" % dirname

        return dirname

    get_config_dir = classmethod(get_config_dir)


    def set_tmp_config():
        config_path = Config.get_default_config_path()
        os.environ["TACTIC_TMP_CONFIG_PATH"] = config_path

        # The only reason to set the tmp config is because there is something
        # wrong with the database connection
        from environment import Environment
        data_dir = Environment.get_data_dir()
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        if data_dir:
            f = open("%s/first_run" % data_dir, 'w')
            f.write("\n")
            f.close()

    set_tmp_config = staticmethod(set_tmp_config)

    def unset_tmp_config():
        from environment import Environment
        try:
            os.environ.pop("TACTIC_TMP_CONFIG_PATH")
        except:
            pass
    unset_tmp_config = staticmethod(unset_tmp_config)



    def get_config_path(cls, no_exception=True):
        '''get the path for configuration file for the framework'''

        path = os.environ.get("TACTIC_TMP_CONFIG_PATH")
        if not path:
            path = os.environ.get("TACTIC_CONFIG_PATH")

        if path:
            path = path.replace("\\", "/")

	if not path:
	    path = os.environ.get("TACTIC_DATA_DIR")
	    if path:
                path = "%s/config/tactic-conf.xml" % path

                #if os.name == 'nt':
                #    path = "%s/config/tactic_win32-conf.xml" % path
                #else:
                #    path = "%s/config/tactic_linux-conf.xml" % path

	
	if not path:
            path = cls.get_default_config_path()


        if no_exception == False and not os.path.exists(path):
	    raise TacticException("Config path [%s] does not exist" % path)
	

        return path

    get_config_path = classmethod(get_config_path)



    def save_config():
        '''save the config in memory to file'''

        xml_data = Config.get_xml_data()
        path = Config.get_config_path()
        xml_string = xml_data.to_string()
        
        f = open(path, 'w')
        f.write( xml_string )
        f.close()
        
    save_config = staticmethod(save_config)


