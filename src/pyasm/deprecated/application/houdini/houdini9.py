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

__all__ = ['HoudiniException', 'Houdini9', 'Houdini9NodeNaming', 'hscript']


import sys, types, re, os

from pyasm.application.common import *

from houdini_environment import *
from houdini_socket import *

# import the houdini library
import hou

class HoudiniException(Exception):
    pass


class Houdini9NodeNaming(object):
    def __init__(my, node_name=None):
        # chr001_joe_black
        my.node_name = node_name
        my.namespace = ''

        if node_name:
            if my.node_name.find("_") != -1:
                my.has_namespace_flag = True
                my.asset_code, my.namespace = node_name.split("_",1)
            else:
                my.has_namespace_flag = False
                my.asset_code = my.namespace = node_name

    def get_asset_code(my):
        return my.asset_code

    def set_asset_code(my, asset_code):
        my.asset_code = asset_code

    # DEPRECATED
    def get_instance(my):
        return my.namespace

    # DEPRECATED
    def set_instance(my, namespace):
        my.has_namespace_flag = True
        my.namespace = namespace


    def get_namespace(my):
        return my.namespace

    def set_namespace(my, namespace):
        my.has_namespace_flag = True
        my.namespace = namespace

    def set_node_name(my):
        my.node_name = node_name


    def get_node_name(my):
        return my.build_node_name()


    def build_node_name(my):
        if my.asset_code == my.namespace:
            return my.asset_code
        else:
            return "%s_%s" % (my.asset_code, my.namespace)


    def has_instance(my):
        return my.has_namespace_flag
        
    def has_namespace(my):
        return my.has_namespace_flag




class Houdini9(Application):

    APPNAME = "houdini"

    def __init__(my, port=None):
        my.name = "houdini"

        my.socket = HoudiniSocket()
        my.socket.connect(port)

        # FIXME: this is probably a bad assumption
        # for now, all commands occur at /obj
        my.hscript("opcf /obj")


    def get_socket(my):
        return my.socket


    def get_node_naming(my, node_name=None):
        return HoudiniNodeNaming(node_name)


    def hscript(my, cmd):
        return my.socket.hscript(cmd)



    # Common houdini operations
    def is_tactic_node(my, node_name):
        # FIXME: why are all nodes TACTIC nodes?
        return True

    def set_project(my, project_dir):
        # not implemented
        return

    def get_project(my):
        # not implemented
        return ""


    def get_var(my, name):
        return my.hscript("echo $%s" % name)

    def get_node_type(my, node_name):
        return my.hscript('optype -t "%s"' % node_name)


    def set_attr(my, node, attr, value, attr_type=""):
        '''attr_type has no meaning in Houdini.  Everything is a string'''
        if attr == "tacticNodeData":
            return hscript('opcomment -c "%s" %s' % (value,node) )
        else:
            return hscript('opparm %s %s "%s"' % (node, attr, value) )

    def select(my, node):
        return hscript('opset -p on %s' % node)


    # interaction with files
    def import_file(my, path, namespace=":"):
        # In houdini, since we using OTL's this is meaningless.  Just
        # access import reference
        return my.import_reference(path,namespace)


    def import_reference(my, path, namespace=":"):
        # load the otl

        if path.endswith(".dae"):
            hscript("colladaimport %s" % path )
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




    def is_reference(my, node_name):
        # if it is an subnet, then this is not a reference
        is_subnet = hscript("optype -o %s" % node_name) == "Object/subnet"
        if is_subnet:
            return False

        is_synced = hscript("otsync -d %s" % node_name)
        if is_synced.startswith("unsynchronized:"):
            return False
        else:
            return True



    def import_anim(my, path, namespace=""):
        if namespace == "":
            basename = os.path.basename(path)
            namespace, ext = os.path.splitext(basename)

        hscript('cmd "%s" /obj/%s' % (path,namespace) )


    def export_anim(my, path, namespace):
        hscript('opscript -g -b %s > "%s"' % (namespace, path) )


    ##
    def save(my, path):
        if not path.endswith(".hip"):
            path = "%s.hip" % path
        hou.hipFile.save(path)
        return path

    ##
    def load(my, path):
        hou.hipFile.load(path)
        return path


    def export_node(my, node_name, dir=None, filename="", preserve_ref=None):

        if not my.node_exists(node_name):
            raise HoudiniException("Node '%s' does not exist" % node_name)

        # TODO: put this here for now ... not sure why it can be none?
        if not dir:
            raise HoudiniException("dir is none")

        naming = my.get_node_naming(node_name)
        asset_code = naming.get_asset_code()
        instance = naming.get_instance()
        path = "%s/%s.otl" % (dir, asset_code)

        # check the type
        optype = hscript("optype -o /obj/%s" % node_name)
        optype = optype.replace("Object/", "")


        if optype == "subnet":
            cmd = 'otcreatetypefrom -n %s -N %s -l "%s" /obj/%s' % (asset_code, instance, path, node_name)
            hscript( cmd )

        # if this is another type than the one we are checking into
        elif optype != asset_code:
            ret_val = hscript( 'otcopy -n %s -e %s Object/%s %s' % (asset_code, instance, optype, path) )
            if ret_val.find("is not defined") != -1:
                raise HoudiniException(ret_val)

        # just write out the otl
        else:
            #hscript( "otwrite -z -l Object/%s %s" % (node_name,path) )
            hscript( "otwrite -z -l -o /obj/%s %s" % (node_name,path) )

        # sync otl with the definition
        #hscript( "otsync %s" % node_name)

        return path


    def get_file_path(my):
        return "untitled.hip"






    # information retrieval functions.  Requires an open Houdini session
    def node_exists(my,node):
        node = hscript('opls "/obj/%s"' % node)
        if node == None or node.startswith("\nError"):
            return False
        else:
            return True


    def get_nodes_by_type(my, type):
        ret_val = hscript("opfind -t %s" % type)

        # this gives a really weird output
        if ret_val == "":
            return []

        nodes = ret_val.split()
        nodes = [x.lstrip() for x in nodes]
        return nodes



    def get_selected_nodes(my):
        nodes = hscript('echo `opselect(".")`')
        nodes = nodes.split(" ")
        return nodes



    def get_selected_top_nodes(my):
        '''top node are node that are at the /obj level'''
        nodes = hscript('echo `opselect("/obj")`')
        nodes = nodes.split(" ")
        return nodes


    def get_top_nodes(my):
        nodes = hscript("opls /obj")
        nodes = nodes.split("\n")
        return nodes



    def get_reference_nodes(my, top_node):
        '''gets all of the references under a single dag node'''
        my.hscript("/obj/%s" % top_node)
        nodes = []
        my.hscript("/obj")
        return nodes



    def get_reference_path(my, node):
        raise HoudiniException()


    def add_node(my, type, node_name, unique=False):
        ret_value = hscript('opadd -v %s %s' % (type, node_name) )
        return ret_value


    # attributes
    def add_attr(my, node, attribute, type="long"):
        print "WARNING: add_attr: ", node, attribute



    def attr_exists(my, node, attribute):
        ret_val = hscript("opparm -d %s %s" % (node, attribute) )
        if ret_val.startswith("Operator %s has no" % node):
            return False
        else:
            return True


    def get_attr(my, node, attribute):
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

    def get_attr_type(my, node, attribute):
        '''TODO: identify differernt attribute types'''
        return "string"

    def get_all_attrs(my, node_name):
        ret_val = my.hscript("opparm -d %s *" % node_name)

        # value = 'opparm chr001 attr ( 0 0 0 )'
        p = re.compile( r'(\w+) \( \'?([\w\ \/:\.]+)\'? \)')
        pairs = p.findall(ret_val)

        return pairs



    def get_attr_default(my, node, attr):
        raise HoudiniException("Must override this function")


    def get_workspace_dir(my):
        return my.get_var("HOME")


    # Houdini Specific functions
    def get_file_references(my, top_node=None):
        # returns [node, attr, path]

        values = my.hscript("fdependls -l")
        values = values.split("\n")

        paths = []
        for value in values:

            if value == "Unknown:":
                break

            # if a top node is specified, then filter for these top nodes
            if top_node:
                if not value.startswith("/obj/%s:" % top_node) and \
                        not value.startswith("/obj/%s/" % top_node):
                    continue

            if value.find(": ") == -1:
                print "WARNING: no node attached to path: '%s'" % value
                continue


            node, path = value.split(": ")

            # currently do not embed embedded paths
            node = node.replace("/obj/", "")

            if not os.path.exists(path):
                print "WARNING: path '%s' does not exist" % path
                continue

            pairs = my.get_all_attrs(node)
            for pair in pairs:
                if pair[1] == path:
                    paths.append( [node, pair[0], path] )
                    break

        return paths




    def set_user_environment(my, sandbox_dir, basename):
        pass





    # static functions
    def get():
        '''get the central on stored in the houdini environment'''
        env = HoudiniEnvironment.get()
        return env.get_app()
    get = staticmethod(get)




errors = ["Error", "Warning:", "Unknown command:", "Couldn't find"]

def hscript(cmd):
    '''convenience method to get maya object and call hscript command'''
    print "--> %s" % cmd
    houdini = Houdini.get()
    ret_val = houdini.hscript(cmd)
    for error in errors:
        if ret_val.startswith(error):
            raise HoudiniException(ret_val)
    return ret_val





