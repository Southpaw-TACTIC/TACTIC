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

__all__ = ['SessionBuilder']

import os, sys
from xml.dom.minidom import parseString

from base_app_info import *
from app_environment import AppEnvironment
from application import AppException

class SessionBuilder(object):
    '''builds a session from an execute xml document'''

    def __init__(self):
        self.env = AppEnvironment.get()
        self.app = self.env.get_app()

        self.node_data = {}
        self.load_mode = ''


    def get_tmpdir(self):
        return self.env.get_tmpdir()

    def get_sandbox_dir(self):
        return self.env.get_sandbox_dir()



    def import_file(self, node_name, path, instantiation='import'):
        raise Exception("Implement import_file")


    def import_anim(self, instance, path, created_node=""):
        raise Exception("Implement import_anim")

    def load_file(self, path, node_name):
        self.app.load(path)

    def check_existence(self, tactic_node_name):
        ''' check if this node exist '''
        if not self.app.node_exists(tactic_node_name):
            info = BaseAppInfo.get()
            info.report_warning('opened node name missing', \
                '[%s] cannot be found in the scene, which could '\
                'cause invalid TacticNodeData.\n' %tactic_node_name)

    def handle_mel(self, cmd_str):
        cmds = cmd_str.split("\n")
        for cmd in cmds:
            if cmd == "":
                continue
            self.app.mel(cmd)


    def publish_file(self, asset_code, node_name):
        raise Exception("Implement publish_file")


    def set_attr(self, node_name, node, current_node_name):
        '''set attribute for the current app'''
        attr = node.getAttribute("attr")
        value = node.getAttribute("value")
        attr_type = node.getAttribute("type")
        self.app.set_attr(node_name,attr,value,attr_type)

    def execute(self, xml):
        '''executes a series of commands as dictated execute xml string'''

        info = BaseAppInfo.get()
        dom = parseString(xml)
        root = dom.documentElement
        nodes = root.childNodes

        # initialize applicaton object
        self.app.set_verbose()

        current_path = None
        current_node_name = None
        current_node_naming = None
        append_attr = False

        for node in nodes:
            node_name = node.nodeName

            if node_name == "file":
                url = node.getAttribute("url")
                to = node.getAttribute("to")
                md5_checksum = node.getAttribute("md5")
                connection = node.getAttribute("connection")

                # set the tactic asset directory
                tactic_asset_dir = node.getAttribute("tactic_asset_dir")
                if tactic_asset_dir:
                    tactic_asset_dir = str(tactic_asset_dir)
                    os.putenv("TACTIC_ASSET_DIR", tactic_asset_dir)
                    #os.environ["TACTIC_ASSET_DIR"] = tactic_asset_dir
                    if os.name =='nt' and not os.getenv("TACTIC_ASSET_DIR"):
                        Common.set_sys_env('TACTIC_ASSET_DIR', tactic_asset_dir)  

                # if the file is from the web, then download
                if url.startswith("http://"):
                    current_path = self.env.download(url, to, md5_checksum)
                elif connection == "perforce":

                    version = node.getAttribute("version")

                    from pyasm.application.perforce import Perforce
                    perforce = Perforce()
                    root = perforce.get_root()
                    url = "%s%s" % (root, url)
                    if version:
                        ret_val = perforce.sync("%s#%s" % (url,version))
                    else:
                        ret_val = perforce.sync(url)

                    current_path = url

                else:
                    current_path = url

                # set the sandbox directory
                sandbox_dir = node.getAttribute("sandbox_dir")


                self.env.set_sandbox_dir(sandbox_dir)

            elif node_name == "reference":
                namespace = node.getAttribute('namespace')
                instance = node.getAttribute("instance")
                asset_code = node.getAttribute("asset_code")
                set = node.getAttribute("set")
                tactic_node_name = node.getAttribute("node_name")
                if not tactic_node_name:
                    tactic_node_name = asset_code
        
                # build up the expected node name
                if set:
                    node_name = set
                else:
                    node_naming = self.app.get_node_naming()
                    node_naming.set_asset_code(asset_code)
                    node_naming.set_namespace(namespace)
                    node_name = node_naming.build_node_name()

                # NOTE: this only works in some situations
                unique = node.getAttribute("unique")
                if unique == "true" and self.app.node_exists(node_name):
                    info.report_warning(node_name, \
                        "WARNING: Node [%s] already exists, skipping" % node_name, type='urgent')
                    current_node_naming = None
                    current_node_name = None
                    continue

                # remember the real node naming
                current_node_name = self.import_file(node_name, current_path, 'reference')
                

                # check if tactic_node_name with namespace exists, if so, make it current
                # NOTE: THIS IS HIGHLY MAYA SPECIFIC, comment it out
                '''
                tactic_node_name = '%s:%s' %(namespace, tactic_node_name)

                if self.app.node_exists(tactic_node_name):
                    current_node_name = tactic_node_name
                '''
                current_node_naming = self.app.get_node_naming(current_node_name)
                # tracks the state of this loading
                self.load_mode = "reference"

            elif node_name == "replace":
                '''replace instance with the current file'''

                namespace = node.getAttribute("namespace")
                asset_code = node.getAttribute("asset_code")
                set = node.getAttribute("set")
                replacee = node.getAttribute('replacee')
                if node.getAttribute('append_attr'):
                    append_attr = True

                # build up the expected node name
                if set:
                    node_name = set
                elif replacee:
                    node_name = replacee
                else:
                    node_naming = self.app.get_node_naming()
                    node_naming.set_asset_code(asset_code)
                    node_naming.set_namespace(namespace)
                    node_name = node_naming.build_node_name()

                if not self.app.node_exists(node_name):
                    raise TacticException("Error: node [%s] does not exist in session" % node_name)

                # remember the real node naming
                rtn_path = self.app.replace_reference(node_name, current_path)
                if rtn_path != current_path:
                    info.report_warning('Update failed', \
                        '[%s] failed to load and replace reference.\n' %current_path)
                current_node_name = node_name
                current_node_naming = self.app.get_node_naming(current_node_name)


            elif node_name == "import" or node_name == "import_media":
                instantiation_mode = node_name

                namespace = node.getAttribute('namespace')
                instance = node.getAttribute("instance")
                asset_code = node.getAttribute("asset_code")
                set = node.getAttribute("set")
                is_shot = node.getAttribute("shot") == 'true'
                use_namespace = node.getAttribute("use_namespace")
                tactic_node_name = node.getAttribute("node_name")
                if not tactic_node_name:
                    tactic_node_name = asset_code
    
                # build up the expected node name
                if set:
                    node_name = set
                elif is_shot:
                    node_name = asset_code
                else:
                    node_naming = self.app.get_node_naming()
                    node_naming.set_asset_code(asset_code)
                    node_naming.set_namespace(namespace)
                    node_name = node_naming.build_node_name()

                
                unique = node.getAttribute("unique")
                if unique == "true" and self.app.node_exists(node_name):
                    info.report_warning(node_name, 'Node [%s] already exists, skipping.' %node_name, type='urgent')
                    #print "WARNING: node '%s' already exists" % node_name

                    current_node_naming = None
                    node_name = None
                    continue

                if use_namespace == "true":
                    use_namespace = True
                    # This causes double namespace, comment it out for now
                    #tactic_node_name = '%s:%s' %(namespace, tactic_node_name)
                else:
                    use_namespace = False

                # import the file
                current_node_name = self.import_file(node_name, current_path, \
                    instantiation_mode, use_namespace=use_namespace)
               
                # on very first checkin which uses plain asset code, this is not true
                if self.app.node_exists(tactic_node_name):
                    current_node_name = tactic_node_name


                self.app.message("current node name: %s" % current_node_name)

                # remember the real node naming
                current_node_naming = self.app.get_node_naming(current_node_name)

            elif node_name == "open":
                tactic_node_name = node.getAttribute("node_name") 
                asset_code = node.getAttribute("asset_code")
                self.load_file(current_path, asset_code)
                
                if tactic_node_name:
                    node_naming = self.app.get_node_naming()
                    node_naming.set_node_name(tactic_node_name)
                   
                else:
                    #namespace = node.getAttribute("namespace")
                    node_naming = self.app.get_node_naming()
                    node_naming.set_asset_code(asset_code)
                    # open mode has no namespace
                    #node_naming.set_namespace(namespace)
                    tactic_node_name = node_naming.build_node_name() 

                # set the user environment
                sandbox_dir = self.get_sandbox_dir()
                basename = os.path.basename(current_path)
                self.app.set_user_environment(sandbox_dir, basename)
        
                self.check_existence(tactic_node_name)

                
                # remember the real node naming
                current_node_name = tactic_node_name
                current_node_naming = node_naming

            elif node_name == "anim":
                # always put the animation on the current instance.  If there
                # is no current instance, then it must be specified
                orig_instance = node.getAttribute("instance")
                asset_code = current_node_naming.get_asset_code()

                node_naming = self.app.get_node_naming()
                node_naming.set_instance(orig_instance)
                node_naming.set_asset_code(asset_code)
                node_name = node_naming.build_node_name()


                self.import_anim(node_name, current_path, current_node_name)

            elif node_name == "add_attr":
                node_name = node.getAttribute("node")
                snap_type = node.getAttribute("snapshot_type")
                use_namespace =  node.getAttribute("use_namespace")
                if node_name == "":
                    node_name = current_node_name
                elif node_name == "{top_node}":
                    node_name = current_node_name
                elif use_namespace == "false":
                    pass
                # shot snapshot uses the node_name as is with namespace probably
                elif snap_type == 'shot' and self.load_mode != "reference":
                    pass
                else:
                    # build the full node name
                    instance = ''
                    if current_node_naming:
                        instance = current_node_naming.get_instance()
                    node_naming = self.app.get_node_naming()
                    node_naming.set_instance(instance)
                    node_naming.set_asset_code(node_name)

                    node_name = node_naming.get_node_name()

                attr = node.getAttribute("attr")
                value = node.getAttribute("value")
                attr_type = node.getAttribute("type")
                try:
                    self.app.add_attr(node_name,attr,attr_type)
                    self.set_attr(node_name, node, current_node_name)
                except AppException, e:
                    info.report_warning('MEL Script Error', str(e))
                    continue

            elif node_name == "current_node":
                asset_code = node.getAttribute("asset_code")
                namespace = node.getAttribute("namespace")
                
                node_naming = self.app.get_node_naming()
                node_naming.set_namespace(namespace)
                node_naming.set_asset_code(asset_code)

                # if the current node is a set-type node, this
                # current node_name is not really used, a node attribute
                # will be specified instead for <set_node_attr/>
                current_node_name = node_naming.get_node_name()

            elif node_name == "set_node_attr":
                node_name = node.getAttribute("node")
                if node_name == "":
                    node_name = current_node_name
                if not node_name:
                    continue
                if self.node_data.has_key(node_name):
                    node_data = self.node_data[node_name]
                else:
                    node_data = self.app.get_node_data(node_name)
                    # clears it for the first time if it is not in append_attr mode
                    # in case the user added some junk data in it
                    if not append_attr:
                        node_data.clear()
                    self.node_data[node_name] = node_data
                name = node.getAttribute("name")
                attr = node.getAttribute("attr")
                value = node.getAttribute("value")

                try:
                    node_data.set_attr(name,attr,value)
                    node_data.commit()
                except AppException, e:
                    info.report_warning('MEL Script Set TacticNodedata Error', str(e))
                    continue

            elif node_name == "add_node":

                name = node.getAttribute("name")
                type = node.getAttribute("type")

                self.app.add_node(type, name)


            elif node_name == "add_to_set":
                set_name = node.getAttribute("set_name")
                set_item = node.getAttribute("instance")

                node_name = current_node_name
                # use set_item if it is defined
                if set_item:
                    node_name = set_item
                self.app.create_set(set_name)
                if node_name:
                    self.app.add_to_set(set_name, node_name)
           
 
            elif node_name == "mel":
                child = node.firstChild
                cmd = child.nodeValue
                self.handle_mel(cmd)

            elif node_name == "save":
                self.app.save_file()

            elif node_name == "warning":
                info = BaseAppInfo.get()
                label = current_node_name
                warning_label = node.getAttribute("label")
                if warning_label:
                    label = warning_label
                info.report_warning(label, '%s\n' %node.getAttribute("msg"))

            # checkin/publish function
            elif node_name == "publish":
                code = node.getAttribute("asset_code")
                node_name = node.getAttribute("node")
                self.publish_file(code, node_name)

