#########################################################
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

__all__ = ['MayaException', 'Maya', 'Maya85', 'MayaNodeNaming']


import sys, types, re, os

from .maya_environment import *
from pyasm.application.common import NodeData, Common, Application, AppException

class MayaException(AppException):
    pass


class MayaNodeNaming:
    def __init__(self, node_name=None):
        self.node_name = node_name
        self.namespace = ''
        self.asset_code = ''
        if self.node_name:
            if self.node_name.find(":") != -1:
                self.has_namespace_flag = True
                self.namespace, self.asset_code = self.node_name.split(":",1)
            else:
                self.has_namespace_flag = False
                self.asset_code = self.namespace = self.node_name
        if self.namespace:
            self.namespace = self.namespace.replace(' ', '_')

        
    def get_asset_code(self):
        return self.asset_code

    def set_asset_code(self, asset_code):
        self.asset_code = asset_code

    
    #TODO: deprecate the instance methods    
    def get_instance(self):
        return self.namespace

    def set_instance(self, namespace):
        self.has_namespace_flag = True
        self.namespace = namespace

    def get_namespace(self):
        return self.namespace

    def set_namespace(self, namespace):
        self.has_namespace_flag = True
        self.namespace = namespace

    def set_node_name(self, node_name):
        self.node_name = node_name

    # HACK: this is REALLY bad code.  FIXME: Tactic needs a much better
    # node naming implementation.  Functions should pass around the naming
    # object, not the node_name
    def get_node_name(self):
        if not self.node_name:
            if self.asset_code:
                self.node_name = "%s:%s" % (self.namespace, self.asset_code)
            else: # user-created node has no asset code
                self.node_name = self.namespace
                return self.node_name
            app = Maya.get()
            if not app.node_exists(self.node_name):
                self.node_name = self.namespace
            if not app.node_exists(self.node_name):
                self.node_name = self.asset_code

        return self.node_name

    def build_node_name(self):
        node_name = "%s:%s" % (self.namespace, self.asset_code)
        # prevent problems when no namespace or asset code is given
        if node_name == ":":
            node_name = ""
        return node_name


    def has_instance(self):
        return self.has_namespace_flag

    def has_namespace(self):
        return self.has_namespace_flag

pymel = None
maya = None

class Maya(Application):
    '''encapsulates the pymaya plugin and its functionality.  It also provides
    a possbility to created a distributed maya server that will not be
    run on the web server'''

    APPNAME = "maya"

    def __init__(self, init=False):
        self.name = "maya"

        try:
            exec("import pymel as pymel")
        except Exception as e:
            print("exception")
            raise MayaException(e)

        if init == True:
            pymel.maya_init("default")

        super(Maya, self).__init__()

        self.mel("loadPlugin -quiet animImportExport")


    def is_tactic_node(self, node):
        return NodeData.is_tactic_node(node)

    def new_session(self):
        return mel("file -f -new")


    def get_node_naming(self, node_name=None):
        return MayaNodeNaming(node_name)



    def mel(self, cmd, verbose=None):
        if self.buffer_flag == True:
            self.buffer.append(cmd)
        else:
            if not pymel:
                exec("import pymel as pymel", globals(), locals())
            if verbose == True or (verbose == None and self.verbose == True):
                print("->", cmd)
            return pymel.mel(cmd)



    def cleanup(self):
        exec("import pymel as pymel")
        pymel.maya_cleanup()



    # Common maya operations
    #   These abstract and interface to maya version so that implementations
    # for each version of maya can made.  Versions between Maya can be
    # highly volatile for in terms of stability and functionality.
    # This attempts to protect tactic from changes between Maya versions.
    # As few basic operations as possible into maya are defined to simplify
    # porting.

    def get_var(self, name):
        value = mel('$%s = $%s' % (name, name) ) 
        #value = value.replace("||", "/")
        #print("value: ", name, value)
        return value


    def get_node_type(self, node_name):
        type = mel('nodeType "%s"' % node_name)
        if not type:
            raise MayaException("Node '%s' does not exist" % node_name)
        return type

    def get_parent(self, node_name):
        parent = mel('firstParentOf %s' % node_name)
        return parent


    def get_children(self, node_name, full_path=True, type='transform', recurse=False):
        '''Get the children nodes. type: transform, shape'''
        full_path_switch = ''
        recurse_switch = ''
        if full_path:
            full_path_switch = '-fullPath'
        if recurse:
            recurse_switch = '-ad'
        children = mel('listRelatives %s %s -type %s "%s"' %(full_path_switch, recurse_switch, type, node_name))
        if children:
            return list(children)
        else:
            return []
    
    # action functions
    def set_attr(self, node, attr, value, attr_type=""):
        if attr_type == "string":
            mel('setAttr %s.%s -type "string" "%s"' % (node,attr,value))
        # maya doesn't work too well with this
        # elif attr_type:
        #    mel('setAttr %s.%s -type %s %s' % (node,attr, attr_type, value))
        else:
            '''attr_type is optional for numeric value'''
            mel('setAttr %s.%s %s' % (node,attr,value))


    # selection functions
    def select(self, node):
        mel('select -noExpand "%s"' % node )

    def select_add(self, node):
        mel('select -noExpand -add "%s"' % node )

    def select_none(self):
        mel('select -cl')

    def select_restore(self, nodes):
        self.select_none()
        for node in nodes:
            self.select_add(node)

    def select_hierarchy(self, node):
        mel("select -hi %s" %node)

    # interaction with files
    def import_file(self, path, namespace=":"):
        if namespace in ['',":"]:
            mel('file -pr -import "%s"' % (path) )
        else:
            mel('file -namespace "%s" -pr -import "%s"' % (namespace, path) )


    def import_reference(self, path, namespace=":"):
        if namespace in ['',":"]:
            mel('file -pr -reference "%s"' % (path) )
        else:
            mel('file -namespace "%s" -pr -reference "%s"' % (namespace, path) )

    def is_reference(self, node_name):
        is_ref = mel('reference -q -inr "%s"' % node_name)
        if is_ref:
            return True
        else:
            return False


    def replace_reference(self, node_name, path, top_reference=True):
        '''load using references. If top reference is False, 
            it will replace the sub reference if any (To be verified!)'''
        switch = '-rfn'
        if top_reference:
            switch = '%s -tr' %switch
        ref_node = mel('referenceQuery %s "%s"' % (switch, node_name ))
        #ref_node = mel('referenceQuery -rfn "%s"' % ref_path )

        # replace the reference
        return mel('file -loadReference "%s" "%s"' % (ref_node, path) )



    def is_keyed(self, node_name, attr):
        is_keyed = mel('connectionInfo -id %s.%s' %(node_name, attr))
        if is_keyed:
            return True
        else:
            return False

    def import_anim(self, path, namespace=":"):
        mel('file -import -type animImport "%s"' % path)
    
    def import_static(self, buffer, node_name):
        lines = buffer.split("\n")
        pat = re.compile('(.+) -type (.+) -default (.+) -value (.+)') 
        for line in lines:
            m = pat.match(line)
            if m:
                attr, attr_type, value = m.group(1), m.group(2),  m.group(4)
                self.set_attr(node_name, attr, value, attr_type)
            
        
    

    def export_anim(self, path, namespace=":"):
        mel('file -force -exportAnim -op "-heirarchy none" -type "animExport" "%s"' % path)
        return path

        

    

    def delete(self, node_name):
        # set has no namespace
        if self.is_set(node_name):
            mel('delete "%s"' % node_name)
            return
        
        # clean out and remove the namespace
        naming = self.get_node_naming(node_name)
        instance = naming.get_instance()
        if naming.has_instance():
            self.set_namespace(instance)
            # if the namespace is already removed, skip
            current = mel("namespaceInfo -cur")
            if current == instance:
                
                garbage_nodes = mel("namespaceInfo -listNamespace")
                if garbage_nodes:
                    for garbage_node in garbage_nodes:
                        if not self.is_reference(node_name) and "lightLinker" in garbage_node:
                            self.delete_nondeletable_node(garbage_node)
                        else:
                            mel('delete "%s"' % garbage_node) 
        
        
        
        self.set_namespace()
        
        self.remove_namespace(instance)
        
        if self.is_reference(node_name):
            reference_file = mel('reference -q -filename "%s"' % node_name)
            mel('file -removeReference "%s"' % reference_file)

        else:
            # delete an imported node
            mel('delete "%s"' % node_name) 


    # file utilities

    def load(self, path):
        if path.endswith(".ma"):
            mel('file -f -options "v=0"  -typ "mayaAscii" -o "%s"' % path)
        else:
            mel('file -f -options "v=0"  -typ "mayaBinary" -o "%s"' % path)
        return path


    def rename(self, path):
        '''rename the file so that "save" will go to that directory'''
        print("renaming: ", path)
        if path.endswith("/") or path.endswith("\\"):
            path = "%suntitled.ma" % path
        elif not path:
            path = "untitled.ma"
        #elif not path.endswith(".ma"):
        #    path = "%s.ma" % path

        mel('file -rename "%s"' % path)
        if path.endswith(".ma"):
            mel('file -type "mayaAscii"')
        elif path.endswith(".mb"):
            mel('file -type "mayaBinary"')


    def save(self, path, file_type=None):
        if not file_type:
            file_type="mayaAscii"

        if file_type == "mayaAscii" and not path.endswith(".ma"):
            path, ext = os.path.splitext(path)
            path = "%s.ma" % path
        elif file_type == "mayaBinary" and not path.endswith(".mb"):
            path, ext = os.path.splitext(path)
            path = "%s.mb" % path

        self.rename(path)
        mel('file -force -save -type %s' % file_type)
        return path

    def save_node(self, node_name, dir=None, type="mayaAscii", as_ref=False ):
        naming = self.get_node_naming(node_name)
        asset_code = naming.get_asset_code()

        if dir == None:
            path = "%s" % (asset_code)
        else:
            path = "%s/%s" % (dir, asset_code)
        if type == "mayaAscii" and not path.endswith(".ma"):
            path, ext = os.path.splitext(path)
            path = "%s.ma" % path
        elif type == "mayaBinary" and not path.endswith(".mb"):
            path, ext = os.path.splitext(path)
            path = "%s.mb" % path


        return self.save(path, file_type=type)

    
    def get_file_path(self):
        # switching because file -q -loc does not return anything until you
        # actually save
        #path = mel("file -q -loc")
        #if path == "unknown":
        paths = mel("file -q -list")
        if type(paths) in (types.ListType, types.TupleType):
            path = paths[0]

        if path.endswith("untitled"):
            return ""

        return path

 
    
    def export_node(self, node_names, context, dir=None, type="mayaAscii", as_ref=False, preserve_ref=True, filename='', instance=None ):
        '''exports top node(s) in maya'''

        asset_code = ''
        if isinstance(node_names, list):
            if not list:
                raise MayaException('The list to export is empty')
            self.select_none()
            for node_name in node_names:
                self.select_add(node_name)
            # we just pick a node_name for asset_code which is part of
            # a filename, if used
            if self.is_tactic_node(node_names[0]):
                naming = self.get_node_naming(node_names[0])
                instance = naming.get_instance()
            else:
                instance = node_names[0]
                
        else:        
            self.select( node_names )
            naming = self.get_node_naming(node_names)
            instance = naming.get_instance()

        export_mode = "-es"
        if as_ref:
            export_mode = "-er"

        if preserve_ref:
            export_mode = '-pr %s' %export_mode

        # find the desired extension
        if type == "mayaAscii":
            type_key = type
            ext = "ma"
        elif type == "mayaBinary":
            type_key = type
            ext = "mb"
        elif type == "collada":
            type_key = "COLLADA exporter"
            ext = "dae"
        elif type == "obj":
            type_key = "OBJexport"
            ext = "obj"
        else:
            type_key = "mayaAscii"
            ext = "ma"


        # build the file name
        if filename:
            filename, old_ext = os.path.splitext(filename)
        elif not instance:
            filename = "untitled"
        else:
            filename = instance

        filename = "%s.%s" % (filename, ext)
        filename = Common.get_filesystem_name(filename) 

        if dir == None:
            path = mel('file -rename "%s"' % filename )
        else:
            path = "%s/%s" % (dir, filename)

        mel('file -rename "%s"' % path )
        cmd = 'file -force -op "v=0" %s -type "%s"' % (export_mode, type_key)
        print("cmd: ", cmd)
        mel(cmd)
        
        return path
    
    def export_collada(self, node_name, dir=None):
        type = "COLLADA exporter"
        return self.export_node(node_name, dir, type)

    def export_obj(self, node_name, dir=None):
        type = "OBJexport"
        return self.export_node(node_name, dir, type)


    def delete_nondeletable_node(self, node_name):
        #TODO keep current selection
        self.select_none()

        tmp_dir = "%s/temp" % MayaEnvironment.get().get_tmpdir()
        reference_file =  self.export_node(node_name, tmp_dir, as_ref=True)
        mel('file -removeReference "%s"' % reference_file)


    # namespace commands
    def set_namespace(self, namespace=":"):
        mel('namespace -set "%s"' % namespace)

    def add_namespace(self, namespace):
        if not self.namespace_exists(namespace):
            mel('namespace -add "%s"' % namespace)

    def remove_namespace(self, namespace):
        mel('namespace -removeNamespace "%s"' % namespace)

    def namespace_exists(self, namespace):
        return mel('namespace -exists "%s"' % namespace)

    def get_namespace_info(self, option='-lon'):
        return mel('namespaceInfo %s' %option)

    def rename_node(self, node_name, new_name):
        '''it assumes the new name is under the root namespace'''
        return mel('rename %s %s' %(node_name, new_name))
        
    # set functions
    def get_sets(self):
        #all_sets = mel('listSets -allSets')
        # change to this.  The above does not give the full namespace name
        all_sets = set(mel('ls -type objectSet'))
        delight_set = set() 
        try:
            delight_list = mel('ls -type delightShapeSet')
            if delight_list:
                delight_set = set(delight_list)
        except Exception as e:
            pass

        ignore_set = set(['defaultLightSet', 'defaultObjectSet']).union(delight_set)
        #ignore_set = set(['defaultLightSet', 'defaultObjectSet'])
        render_set = set()
        deformer_set = set()


        # shadingEngine is strangely a subset of -type objectSet in Maya 7 at least
        render_set_list = mel('ls -type shadingEngine')
        deformer_set_list = mel('listSets -type 2')
        
        if render_set_list:
            render_set = set(render_set_list)
        if deformer_set_list:
            deformer_set = set(deformer_set_list)   
        all_sets = all_sets - render_set - deformer_set - ignore_set
       
        # remove any set with the suffix of the deformer_set_list
      
        
        sets = []
        if deformer_set_list:
            regex = '|'.join(['skinCluster\d*Set','cluster\d*Set', 'tweakSet\d*'] )
            deformer_pat = re.compile(r'(%s)$' %regex)
            sets = [ x for x in all_sets if not deformer_pat.search(x) ] 
        else:
            sets = list(all_sets)
       
        '''
        
        for x in all_sets:
            # cannot use this because sets do not usually have this at the
            # beginning
            #elif not self.attr_exists(x, "tacticNodeData"):
            #    continue
           
            sets.append(x)
        '''
            
        return sets

    def is_set(self, node_name):
        if node_name in self.get_sets():
            return True
        else:
            return False

    def create_set(self, node_name):
        if not self.node_exists(node_name):
            mel('sets -n "%s"' % node_name)
        
    def add_to_set(self, set_name, node_name):
        # a quick way of avoiding the add set to set warning msg on shot load
        if node_name in [set_name, ':%s'%set_name]:
            return
        mel('sets -add "%s" "%s"' % (set_name, node_name) )


    def get_nodes_in_set(self, set_name):
        nodes = mel('sets -q "%s"' % set_name )
        if not nodes:
            return []
        else:
            return list(nodes)





    # information retrieval functions.  Requires an open Maya session
    def node_exists(self,node):
        node = mel("ls %s" % node)
        if node == None:
            return False
        else:
            return True

    def get_nodes_by_type(self, type):
        return mel("ls -type %s" % type)



    def get_selected_node(self):
        nodes = mel("ls -sl")
        if nodes:
            return nodes[0]
        else:
            return None

    def get_selected_nodes(self):
        nodes = mel("ls -sl")
        return nodes


    def get_selected_top_nodes(self):
        return mel("ls -sl -as")

   

    def get_top_nodes(self):
        # maya 7.0 bug: "ls -as" produces garbage
        nodes  = mel("ls -tr -l")

        top_level = []
        for node in nodes:
            node = node.lstrip('|')

            if node.count("|") > 0:
                continue

            # ignore default cameras
            if node in ['persp', 'front', 'top', 'side']:
                continue

            top_level.append(node)

        return top_level




    def get_tactic_nodes(self, top_node=None):
        '''Much simpler method to get TACTIC nodes using new definition of
        TACTIC nodes
        '''
        nodes = mel('ls "*:tactic_*"')
        if not nodes:
            return []
        tactic_nodes = []
        for node in nodes:
            # TODO: check if nodes have the attribute "tacticNodeData"

            tactic_nodes.append(node)
        return tactic_nodes
            


    def get_reference_nodes(self, top_node=None, sub_references=False, recursive=False):
        '''Want to get all of the tactic nodes that exist under a single
        entity.  This entity can be one of 3 items.  The maya file itself,
        a set containing a number of top nodes or a single top node.  These
        are treated as the containment entity'''
        # FIXME: misnamed ... this gets all of the tactic nodes, not all the
        # reference nodes

        # get a list of nodes that could possibly be Tactic nodes

        if top_node == None:
            # find all of the top nodes in the file
            top_nodes = self.get_top_nodes()
        elif self.get_node_type(top_node) == "objectSet":
            # if this is a set: get all of the nodes in the set
            top_nodes = mel('sets -q -nodesOnly "%s"' % top_node)
        else:
            top_nodes = [top_node]

        # ensure that top_nodes is a list, because mel isn't very consistent
        # with returned types.
        if type(top_nodes) not in (types.ListType, types.TupleType):
            top_nodes = [top_nodes]

        # this is a top transform node. we look down the hierarchy for
        # tactic nodes.  Only nodes with one namespace greater than the
        # top node are considered
        
        num_parts = 0
        if not recursive:
            if top_node:
                parts = top_node.split(":")
                num_parts = len(parts)
            else:
                num_parts = 1


        # look through transforms
        node_type = "transform"
        nodes = []
        for node in top_nodes:
            tmp_nodes = mel('ls -type %s -recursive true -dag -allPaths "%s"' % (node_type, node) )
            if not tmp_nodes:
                continue

            if type(tmp_nodes) in (types.ListType, types.TupleType):
                nodes.extend(tmp_nodes)
            else:
                nodes.append(tmp_nodes)

        references = []
        if not nodes:
            return references

        for node in nodes:
            # only consider nodes that have one namespace greater than the
            # top node.
            if node and not recursive:
                parts = node.split(":")
                if len(parts) > num_parts + 1:
                    continue

            # sub refs are always maya references
            is_ref = mel('reference -q -isNodeReferenced "%s"' % node)
            if is_ref:
                # found a potential node ...
                # make sure this has a tacticNodeData attribute
                if self.attr_exists(node, "tacticNodeData"):
                    references.append(node)


        return references


    def get_reference_path(self, node):
        path = mel("reference -q -filename %s" % node)
        if path:
            return path
        else:
            return ""



    def add_node(self, type, node_name, unique=False):
        return mel("createNode -n %s %s" % (node_name, type) )


    # attributes
    def add_attr(self, node, attribute, type="long"):
        # do nothing if it already exists
        if self.attr_exists(node,attribute):
            return
        if type == "string":
            return mel('addAttr -ln "%s" -dt "string" %s' % (attribute, node) )
        else:
            return mel('addAttr -ln "%s" -at "long" %s' % (attribute, node) )


    def attr_exists(self, node, attribute):
        # don't bother being verbose with this one
        return self.mel("attributeExists %s \"%s\"" % (attribute, node), verbose=False )

    def get_attr(self, node, attribute):
        if not self.attr_exists(node, attribute):
            return ""
        value = mel("getAttr %s.%s" % (node, attribute) )
        # never return None for an attr
        if value == None:
            return ""
        else:
            return value

    def get_attr_type(self, node, attribute):
        ''' get the attribute type e.g. int, string, double '''
        if not self.attr_exists(node, attribute):
            return ""
        value = mel("getAttr -type %s.%s" % (node, attribute) )
        # never return None for an attr
        if not value:
            return ""
        else:
            return value

    def get_all_attrs(self, node):
        keyable = mel("listAttr -keyable %s" % node )
        user_defined = mel("listAttr -userDefined %s" % node)
        attrs = []
        attrs.extend(keyable)
        if user_defined:
            attrs.extend(user_defined)
        return attrs

    def get_attr_default(self, node, attr):
         return mel("attributeQuery -node %s -listDefault %s" % \
            (node, attr) )



    # layer functions
    def get_all_layers(self):
        '''get all of the render layers'''
        return mel("ls -type renderLayer")

    def get_layer_nodes(self, layer_name):
        '''get all of the tactic nodes in a render layer'''
        return mel("editRenderLayerMembers -q %s" % layer_name)



    



    # MAYA specific functions


    # namespaces
    # these 2 can be replaced with get_namespace_info()
    def get_namespace_contents(self):
        '''retrieves the contents of the current namespac'''
        contents = mel('namespaceInfo -listNamespace')
        return contents


    def get_all_namespaces(self):
        return mel('namespaceInfo -listOnlyNamespaces')



    def get_workspace_dir(self):
        return mel("workspace -q -rootDirectory")


    def set_project(self, dir):
        mel('setProject "%s"' % dir)        

    def get_project(self):
        return mel("workspace -q -rootDirectory")


    def get_window_title(self):
        return mel('window -q -title $gMainWindow')

    def set_window_title(self, title):
        mel('window -edit -title "%s" $gMainWindow' % title )





    # static functions
    maya = None
    def get():
        # the current version is stored in MayaEnvironment
        env = MayaEnvironment.get()
        return env.get_app()
    get = staticmethod(get)



# importing 8.5 maya module
try:
    import maya as mm
except:
    pass


class Maya85(Maya):
    def __init__(self, init=True):
        self.name = "maya"

        # don't use the Maya constructor
        super(Maya, self).__init__()


        self.mel("loadPlugin -quiet animImportExport")


    def mel(self, cmd, verbose=None):
        if self.buffer_flag == True:
            self.buffer.append(cmd)
        else:
            if verbose == True or (verbose == None and self.verbose == True):
                print("->", cmd)
            try:
                return mm.mel.eval(cmd)
            except Exception as e:
                if cmd.startswith("MayaManInfo"):
                    print("Warning: ", cmd)
                else:
                    print("Error: ", cmd)
                    # Let the MEL keep running
                    raise MayaException(cmd)

    # FIXME: reference command is Obsolete
    def is_reference(self, node_name):
        is_ref = mel('reference -q -inr "%s"' % node_name)
        if is_ref:
            return True
        else:
            return False


    # FIXME: reference command is Obsolete
    def get_reference_path(self, node):
        path = mel("reference -q -filename %s" % node)
        if path:
            return path
        else:
            return ""




    def cleanup(self):
        '''do nothing'''
        pass


def mel(cmd):
    '''convenience method to get maya object and call mel command'''
    maya = Maya.get()
    return maya.mel(cmd)


