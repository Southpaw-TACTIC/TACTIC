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

__all__ = ['HoudiniException', 'Houdini', 'HoudiniNodeNaming', 'hscript']


import sys, types, re, os

from pyasm.application.common import *

from houdini_environment import *
from houdini_socket import *

class HoudiniException(AppException):
    pass


class HoudiniNodeNaming(object):
    def __init__(self, node_name=None):
        # chr001_joe_black
        self.node_name = node_name
        self.namespace = ''
        
        if node_name:
            if self.node_name.find("__") != -1:
                self.has_namespace_flag = True
                self.asset_code, self.namespace = node_name.split("__",1)
            else:
                self.has_namespace_flag = False
                self.asset_code = self.namespace = node_name

    def get_asset_code(self):
        return self.asset_code

    def set_asset_code(self, asset_code):
        self.asset_code = asset_code

    # DEPRECATED
    def get_instance(self):
        return self.namespace

    # DEPRECATED
    def set_instance(self, namespace):
        self.set_namespace(namespace)


    def get_namespace(self):
        return self.namespace

    def set_namespace(self, namespace):
        self.has_namespace_flag = True
        self.namespace = namespace

    def set_node_name(self, node_name):
        self.node_name = node_name


    def get_node_name(self):
        return self.build_node_name()


    def build_node_name(self):
        if self.asset_code == self.namespace or not self.namespace:
            return self.asset_code
        else:
            return "%s__%s" % (self.asset_code, self.namespace)


    def has_instance(self):
        return self.has_namespace()
        
    def has_namespace(self):
        if not hasattr(self, 'has_namespace_flag'):
            raise HoudiniException('Empty node name. It could be caused by trying to load a file published through Manual Publish')
        
        return self.has_namespace_flag


# Try to import the hou module for Houdini 9.  This is a good indicator
# that we are in version 9 and not 8.
try:
    import hou
except:
    pass


class Houdini(Application):

    APPNAME = "houdini"

    def __init__(self, port=None):
        self.name = "houdini"

        # Houdini 9 does not have a port
        if port:
            self.socket = HoudiniSocket()
            self.socket.connect(port)
        else:
            self.socket = None

        # FIXME: this is probably a bad assumption
        # for now, all commands occur at /obj
        self.hscript("opcf /obj")


    def get_socket(self):
        return self.socket


    def get_node_naming(self, node_name=None):
        return HoudiniNodeNaming(node_name)


    def hscript(self, cmd):
        if self.socket:
            return self.socket.hscript(cmd)
        else:
            values = hou.hscript(str(cmd))

            ret_values = []
            for value in values:
                if value == "":
                    continue
                value = value.strip()
                ret_values.append(value)

            value = str("".join(ret_values))
            return value



    # Common houdini operations
    def is_tactic_node(self, node_name):
        # FIXME: why are all nodes TACTIC nodes?
        return True

    def set_project(self, project_dir):
        return

    def get_project(self):
        return ""


    def get_var(self, name):
        return self.hscript("echo $%s" % name)

    def get_node_type(self, node_name):
        return self.hscript('optype -t "%s"' % node_name)


    def set_attr(self, node, attr, value, attr_type=""):
        '''attr_type has no meaning in Houdini.  Everything is a string'''
        if attr == "tacticNodeData":
            return hscript('opcomment -c "%s" %s' % (value,node) )
        else:
            value = value.replace("$", "\\$")
            cmd = 'opparm %s %s "%s"' % (node, attr, value)
            print cmd
            return hscript(cmd)

    def select(self, node):
        return hscript('opset -p on %s' % node)


    # interaction with files
    def import_file(self, path, namespace=":"):
        # In houdini, import is treated as open in append mode
        hscript('mread -m * "%s"' % path)
        return path
        

    def import_reference(self, path, namespace=":"):
        # load the otl
        if path.endswith(".dae"):
            hscript("colladaimport %s" % path )
            return namespace
        elif path.endswith(".obj"):
            hscript("opadd geo %s" % namespace )
            hscript('opparm %s/file1 file ("%s")' % (namespace, path))
            return namespace


        hscript('otload "%s"' % path)


        # get the type from the otl
        results = hscript('otls "%s"' % path)
        results = results.split("\n")
        # result is of the form:
        #Loaded from: Current HIP File
        #    Object/chr001_model
        type = results[-1]
        type = type.strip()
        
        pat = re.compile(r'\w+/\w+')
        if not pat.match(type):
            raise HoudiniException('Invalid OTL path [%s]' %type)
        table, type = type.split("/", 1)

        # instantiate it.  The equivalent of namespace in houdini is 
        # the node_name
        if namespace != ":":
            ret_value = hscript('opadd -v %s %s' % (type, namespace) )
        else:
            ret_value = hscript('opadd -v %s' % type )

        lines = ret_value.split("\n")
        node_name = lines[len(lines)-1]

        return node_name


    def replace_reference(self, node_name, path, top_reference=True):
        # load the new definition
        hscript('otload "%s"' % path)

        # go through the old definitions and remove all but the current one
        # FIXME: assumption of type == asset_code
        #naming = self.get_node_naming(node_name)
        #type = naming.get_asset_code()
        type = hscript('optype -o /obj/%s' %node_name)
        otl_paths = hscript("otls -a %s" % type)
        otl_paths = otl_paths.split("\n")
        for otl_path in otl_paths:
            # skip the one just loaded
            if otl_path == path:
                continue
            hscript('otunload "%s"' % otl_path)

        return path

    def update_reference(self, node_name, path, top_reference=True):
        return self.replace_reference(node_name, path, top_reference)





    def is_reference(self, node_name):
        # if it is an subnet, then this is not a reference
        is_subnet = hscript("optype -o %s" % node_name) == "Object/subnet"
        if is_subnet:
            return False

        is_synced = hscript("otsync -d %s" % node_name)
        if is_synced.startswith("unsynchronized:"):
            return False
        else:
            return True



    def import_anim(self, path, namespace=""):
        if namespace == "":
            basename = os.path.basename(path)
            namespace, ext = os.path.splitext(basename)

        hscript('cmd "%s" /obj/%s' % (path,namespace) )


    def export_anim(self, path, namespace):
        hscript('opscript -g -b %s > "%s"' % (namespace, path) )


    def save(self, path, file_type=None):
        if not path.endswith(".hip"):
            path = "%s.hip" % path
        hscript('mwrite "%s"' % path)
        return path

    def save_node(self, node_name, dir=None, type="hip" ):
        if dir == None:
            path = "%s" % (node_name)
        else:
            path = "%s/%s" % (dir, node_name)

        if type == "hip" and not path.endswith(".hip"):
            path, ext = os.path.splitext(path)
            path = "%s.hip" % path

        return self.save(path)

    def load(self, path):
        hscript('mread "%s"' % path)
        return path


    def export_node(self, node_name, context, dir=None, type=None, filename="", preserve_ref=None, instance=None):
        if not type:
            type = "otl"
        ext = "otl"

        if not self.node_exists(node_name):
            raise HoudiniException("Node '%s' does not exist" % node_name)

        # TODO: put this here for now ... not sure why it can be none?
        if not dir:
            raise HoudiniException("Directory is none: %s" % dir)

        naming = self.get_node_naming(node_name)
        asset_code = naming.get_asset_code()
        instance = naming.get_instance()
        path = "%s/%s.%s" % (dir, asset_code, ext)

        # check the type
        optype = hscript("optype -o /obj/%s" % node_name)
        optype = optype.replace("Object/", "")

        if instance:
            new_type = '%s_%s_%s' %(asset_code, instance, context)
            path = "%s/%s_%s.%s" % (dir, asset_code, instance,  ext)
            temp_path = "%s/%s_%s_temp.%s" % (dir, asset_code, instance, ext)
        else:
            new_type = '%s_%s' %(asset_code, context)
            path = "%s/%s.%s" % (dir, asset_code, ext)
            temp_path = "%s/%s_temp.%s" % (dir, asset_code, ext)

        if optype == "subnet":
            cmd = 'otcreatetypefrom -n %s -N %s -l "%s" /obj/%s' % (new_type, new_type, path, node_name)
            hscript( cmd )
            print cmd
        # if this is another type than the one we are checking into
        elif optype != new_type:
            cmd = 'otcopy -n %s -e %s Object/%s %s' % (new_type, new_type, optype, path)
            print cmd
            ret_val = hscript(cmd)
            if ret_val.find("is not defined") != -1 or ret_val.find("Couldn't load operator definition") != -1:
                raise HoudiniException(ret_val)

        # just write out the otl, keeping the same type
        else:
            cmd = "otwrite -i -z -l -o /obj/%s %s" % (node_name, path)
            print cmd
            hscript(cmd)

        # sync otl with the definition
        #hscript( "otsync %s" % node_name)

        return path


    def get_file_path(self):
        return "untitled.hip"






    # information retrieval functions.  Requires an open Houdini session
    def node_exists(self,node):
        # if there is an exception, then it does not exist
        try:
            node = hscript('opls "/obj/%s"' % node)
        except HoudiniException, e:
            return False

        if not node or node.startswith("\nError"):
            return False
        else:
            return True

            

    def get_nodes_by_type(self, type):
        ret_val = hscript("opfind -t %s" % type)

        # this gives a really weird output
        if ret_val == "":
            return []

        nodes = ret_val.split()
        nodes = [x.lstrip() for x in nodes]
        return nodes



    def get_selected_nodes(self):
        nodes = hscript('echo `opselect(".")`')
        nodes = nodes.split(" ")
        return nodes


    def get_selected_node(self):
        nodes = self.get_selected_nodes()
        if nodes:
            return nodes[0]


    def get_selected_top_nodes(self):
        '''top node are node that are at the /obj level'''
        nodes = hscript('echo `opselect("/obj")`')
        nodes = nodes.split(" ")
        return nodes


    def get_top_nodes(self):
        nodes = hscript("opls /obj")
        nodes = nodes.split("\n")
        return nodes



    def get_reference_nodes(self, top_node=None, sub_references=False, recursive=False ):
        '''gets all of the references under a single dag node'''
        if top_node:
            results = hscript("otinuse -n -l %s" % top_node)
        else:
            results = hscript("otinuse -n -l")
        results = results.split("\n")

        node_paths = []
        for result in results:
            # ignore the builtin otl
            if result.count("houdini/otls/OPlib"):
                continue
            if not result:
                continue 
            node_path, file_path = result.split(" ", 1)

            # ignore the top one
            if node_path == "/obj/%s" % top_node:
                continue

            node_paths.append(node_path)

        return node_paths



    def get_reference_path(self, node_name):
        results = hscript("otinuse -l %s" % node_name)
        results = results.split("\n")
        paths = []
        for result in results:
            # ignore the builtin otl
            if result.count("houdini/otls/OPlib"):
                continue
            paths.append(result)
        # can only return one path even if more than 1 is found
        if paths:
            return paths[0].strip()
        else:
            return ''



    def add_node(self, type, node_name, unique=False):
        ret_value = hscript('opadd -v %s %s' % (type, node_name) )
        return ret_value


    # attributes
    def add_attr(self, node, attribute, type="long"):
        # FIXME: this is not necessary on the tacticNodeData or notes ... this
        # should not be here
        if attribute in ["tacticNodeData", "notes"]:
            return
        print "WARNING: add_attr: ", node, attribute



    def attr_exists(self, node, attribute):
        cmd  = "opparm -d %s %s" % (node, attribute)
        ret_val = hscript(cmd)
        if ret_val.startswith("Operator %s has no" % node):
            return False
        else:
            return True


    def get_attr(self, node, attribute):
        assert node != None and node != ""
        if attribute == "tacticNodeData":
            ret_val = hscript("opcomment %s" % node)
            if ret_val == "No comment":
                return ""
            else:
                return ret_val
        else:
            ret_val = hscript("opparm -d %s %s" % (node, attribute) )
            if ret_val.startswith("Operator %s has no" % node):
                return ""

        p = re.compile(r"\( (.*) \)")
        m = p.search(ret_val)
        value = m.groups()[0]

        if value.startswith("'"):
            value = value.rstrip("'")
            value = value.lstrip("'")
            value = value.replace("\\n", "\n")
            value = value.replace("\\'", "'")
            return value
        else:
            return float(value)

    def get_attr_type(self, node, attribute):
        '''TODO: identify differernt attribute types'''
        return "string"

    def get_all_attrs(self, node_name):
        ret_val = self.hscript("opparm -d %s *" % node_name)

        # value = 'opparm chr001 attr ( 0 0 0 )'
        p = re.compile( r'(\w+) \( \'?(.*?)\'? \)')
        pairs = p.findall(ret_val)

        return pairs



    def get_attr_default(self, node, attr):
        raise HoudiniException("Must override this function")


    def get_workspace_dir(self):
        return self.get_var("HOME")

    # set functions (bundles in houdini)
    def create_set(self, node_name):
        if not self.bundle_exists(node_name):
            self.hscript('opbadd "%s"' % node_name)
        
    def add_to_set(self, set_name, node_name):
        # a quick way of avoiding the add set to set warning msg on shot load
        if node_name in [set_name]:
            return
        self.hscript('opbop "%s" add "%s"' % (set_name, node_name) )

    def get_nodes_in_set(self, set_name):
        nodes = self.hscript('opbls -L "%s"' % set_name )
        if not nodes:
            return []
        else:
            nodes = nodes.split(" ")
            return list(nodes)

    def bundle_exists(self, bundle_name):
        ret_val = hscript('opbls "%s"')
        if ret_val:
            return True
        else:
            return False

    # Houdini Specific functions
    def get_file_references(self, top_node=None):

        if top_node:
            values = self.hscript("opextern -R %s" % top_node)
        else:
            values = self.hscript("opextern -R /")

        nodes = []
        paths = []
        attrs = []

        if values.startswith("No external references found"):
            return nodes,paths,attrs


        values = values.split("\n")

        for value in values:

            node, path = value.split("\t")

            # make sure there are no spaces
            node = node.strip()
            path = path.strip()


            if not os.path.exists(path):
                print "WARNING: path '%s' does not exist" % path
                continue


            # find the attribute
            attr_found = False
            pairs = self.get_all_attrs(node)
            for pair in pairs:
                if pair[1] == path:
                    attrs.append(pair[0])
                    attr_found = True
                    break

            nodes.append(node)
            #nodes.append(node.split("/")[-1])
            paths.append(path)

            # FIXME: put a default in for now
            if not attr_found:
                attrs.append("NULL")


        return nodes,paths,attrs



    # DEPRECATED, use above function
    def get_file_references_old(self, top_node=None):
        # returns [node, attr, path]

        values = self.hscript("fdependls -l")
        values = values.split("\n")

        nodes = []
        paths = []
        attrs = []

        for value in values:

            if value == "Unknown:":
                break

            # if a top node is specified, then filter for these top nodes
            if top_node:
                # filter out any at the top level
                #if not value.startswith("/obj/%s:" % top_node):
                #    continue
               
                # filter out any nodes that do not belong to this top node
                if not value.startswith("/obj/%s/" % top_node):
                    continue

            if value.find(": ") == -1:
                print "WARNING: no node attached to path: '%s'" % value
                continue


            node, path = value.split(": ")

            if not os.path.exists(path):
                print "WARNING: path '%s' does not exist" % path
                continue


            # find the attribute
            attr_found = False
            pairs = self.get_all_attrs(node)
            for pair in pairs:
                if pair[1] == path:
                    attrs.append(pair[0])
                    attr_found = True
                    break

            nodes.append(node)
            #nodes.append(node.split("/")[-1])
            paths.append(path)

            # FIXME: put a default in for now
            if not attr_found:
                attrs.append("NULL")


        return nodes,paths,attrs




    def set_user_environment(self, sandbox_dir, basename):
        pass





    # static functions
    def get():
        '''get the central on stored in the houdini environment'''
        env = HoudiniEnvironment.get()
        return env.get_app()
    get = staticmethod(get)




errors = ["Error", "Warning:", "Unknown command:", "Couldn't find"]

def hscript(cmd):
    '''convenience method to get houdini object and call hscript command'''
    #print "--> %s" % cmd
    houdini = Houdini.get()
    ret_val = houdini.hscript(cmd)
    for error in errors:
        if ret_val.startswith(error):
            raise HoudiniException(ret_val)
    return ret_val





