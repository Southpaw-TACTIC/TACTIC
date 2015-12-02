##########################################################
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

__all__ = ['XSIException', 'XSI', 'XSINodeNaming', 'XSINodeData']


import sys, types, re, os
from xsi_environment import *
from pyasm.application.common import NodeData, Common, Application, AppException, BaseAppInfo


# library of XSI constants
try:
    from win32com.client import constants as c
except ImportError:
    #print("Warning: xsi.py requires module [win32com.client]")
    pass

class XSIException(AppException):
    pass




class XSINodeNaming(object):
    def __init__(my, node_name=None):
        # chr001__joe_black
        my.node_name = node_name
        my.namespace = ''
        my.has_namespace_flag = False
        if node_name:
            if my.node_name.find("__") != -1:
                my.has_namespace_flag = True
                my.asset_code, my.namespace = node_name.split("__",1)
            else:
                my.has_namespace_flag = False
                my.asset_code = my.namespace = node_name
            '''
            pat = re.compile('tactic_(.*)')
            m = pat.match(node_name)
            if m:
                node_type = m.groups()[0]
                node_data = XSINodeData( node_name)
                asset_code = node_data.get_attr('%s_snapshot'%node_type, 'asset_code')
                if asset_code:
                    my.asset_code = asset_code
            '''

    def get_asset_code(my):
        return my.asset_code

    def set_asset_code(my, asset_code):
        my.asset_code = asset_code


    def set_node_name(my, node_name):
        my.node_name = node_name

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


    def get_node_name(my):
        return my.build_node_name()


    def build_node_name(my):
        if my.asset_code == my.namespace or not my.namespace:
            return my.asset_code
        else:
            return "%s__%s" % (my.asset_code, my.namespace)


    def has_instance(my):
        return my.has_namespace_flag
        
    def has_namespace(my):
        return my.has_namespace_flag


class XSINodeData(NodeData):
    '''XSI has a slightly different place to put a node data'''

    ATTR_NAME = "tacticNodeData"

    def commit(my):
        xml = my.dom.toxml()
        xml = xml.replace("\n", "\\n")
        xml = xml.replace('"', "'")

        my.create()

        my.app.set_attr(my.app_node_name, my.ATTR_NAME, xml, "string" )
        #my.app.xsi.LogMessage('Set %s.%s to %s' %(my.app_node_name, my.ATTR_NAME, xml)) 

    def create(my):
        '''create the necessary attributes if they do not exists'''
        # special case ... use base
        my.app.add_attr(my.app_node_name, "tacticNodeData", type="string")



class XSI(Application):

    APPNAME = "xsi"

    def __init__(my, xsi, toolkit, init=True):

        # try getting directly from win32
        #import win32
        #import win32com.client
        #my.xsi = win32com.client.Dispatch("XSI.Application")
        my.xsi = xsi
        my.toolkit = toolkit
        my.name = "xsi"
        
        my.buffer_flag = False
        my.buffer = None

        my.verbose = False
        my.root = my.xsi.ActiveProject.ActiveScene.Root
        assert my.root

    def is_tactic_node(my, node):
        return True
        # FIXME: doesn't work for some reason
        return XSINodeData.is_tactic_node(node)

    def get_node_data(my, node_name):
        return XSINodeData(node_name)


    def get_node_naming(my, node_name=None):
        return XSINodeNaming(node_name)



    # Common XSI operations

    def set_project(my, project_dir):
        '''to not create all the standard XSI folders, avoid calling 
           CreateProject'''
        #my.xsi.ActiveProject2 = my.xsi.CreateProject(project_dir)
        if not os.path.exists('%s/system'%project_dir):
            os.makedirs('%s/system'%project_dir)
            env = XSIEnvironment.get()  
            server = env.get_server()
            env.download('http://%s/context/template/dsprojectinfo'% server,\
                '%s/system' %project_dir)
        my.xsi.ActiveProject = project_dir
        my.message('Setting project to [%s]' %project_dir)
        return my.xsi.ActiveProject.Path

    def get_var(my, name):
        value = my.xsi.GetGlobal(name)
        if not value:
            return ""
        else:
            return value

    def get_node_type(my, node_name):
        return "transform"


    def get_top_nodes(my):
        root_nodes = my.xsi.ActiveProject.ActiveScene.Root.FindChildren('', '' ,'' , False)
        node_names = [ str(node.fullname) for node in root_nodes ]
        
        return node_names


    def get_reference_nodes(my, top_node=None, sub_references=False, recursive=False):
        '''Want to get all of the tactic nodes that exist under a single
        entity.'''
        root = my.xsi.ActiveProject.ActiveScene.Root
        if top_node:
            node = root.FindChild(top_node)
            if not node:
                return []
        else:
            node = root

        ref_nodes = []
        my.xsi.LogMessage("node: [%s]" % node)

        try:
            fs = node.ExternalFiles
        except AttributeError:
            return []

        for f in fs:
            if not f:
                continue
            path = f.ResolvedPath
            owner = str(f.Owners[0])

            # this is normal for xsi if it has a offloaded resolution
            if not path:
                my.message("WARNING: external file for node [%s] is empty" % node)
                continue

            # HACK:
            # if the owner ends with .res1, then this is then this is ref??
            #if not owner.endswith(".res1"):
            #    continue
            if not f.FileType == 'Models':
                continue

            node_name, tmp = owner.split(".", 1)
            if my.is_reference(node_name, recursive=True):
                if node_name not in ref_nodes:
                    ref_nodes.append(node_name)

        return ref_nodes



    def get_reference_path(my, node_name):
        '''Find the reference path that belongs to this node'''

        root = my.xsi.ActiveProject.ActiveScene.Root
        node = root.FindChild(node_name)
        try:
            fs = node.ExternalFiles
        except AttributeError:
            return ""

        for f in fs:
            if not f:
                continue
            path = f.ResolvedPath
            
            if path:
                return path

        return ""
 


    # attributes
    def add_attr(my, node_name, attribute, type="long"):
        node = my.root.FindChild(node_name)
        if not node:
            return

        property = node.Properties(attribute)
        if not property:
            node.AddProperty("Annotation", False, attribute)



    def attr_exists(my, node_name, attribute):
        # my.root may not have been initialized
        my.root = my.xsi.ActiveSceneRoot
        node = my.root.FindChild(node_name)
        if not node:
            return False

        property = node.Properties(attribute)
        if not property:
            return False
        else:
            return True


    def get_attr(my, node_name, attribute):
        # my.root may not have been initialized
        my.root = my.xsi.ActiveSceneRoot
        node = my.root.FindChild(node_name)
        if not node:
            return ""
        property = node.Properties(attribute)
        if not property:
            return ""

        return property.Parameters("text").Value
        

    def set_attr(my, node_name, attribute, value, attr_type="", extra_data={}):
        ''' this method was originally made for setting some Properties of a node.
            But texture is set differently in that the attribute is not really used'''
        my.message("[%s] setting [%s] to [%s]" % (node_name, attribute,value))
        # identifier for texture attribute
        if attribute == 'SourceFileName':
            my.message("Setting Texture path for [%s]" %(node_name))
            return my.set_texture_path(node_name, value, extra_data)

        my.root = my.xsi.ActiveSceneRoot
        node = my.root.FindChild(node_name)
        if not node:
            return False

        property = node.Properties(attribute)
        if not property:
            return False
        parameter = property.Parameters("text")
        parameter.Value = value

    def set_texture_path(my, node_name, value, extra_data):
        import win32com.client
        o = win32com.client.Dispatch( "XSI.Collection" )
        o.Items = node_name
        info = BaseAppInfo.get()
        # this node_name has to be uniquely identifiable in XSI
        if len(o) == 1:
            #o[0].Parameters('SourceFileName').PutValue2(0, value)
            source = o[0].Parameters('SourceName').GetValue2()
            
            file_range = extra_data.get('file_range')
            if file_range:
                impl = info.get_app_implementation()
                value = impl.get_app_file_group_path(value, file_range)
            my.xsi.SetValue('Sources.%s.FileName'%source, value)
            return True 
        else:
            info.report_warning('Texture setting skipped', \
                '[%s] not found. Texture path remains as checked in.' %node_name)
            return False
        '''
        else: # try to search thru the top node
            node_name_parts = node_name.split('.')
            node = my.root.FindChild(node_name_parts[0])
            if not node:
                return False

            # can only take Model
            if 'model' not in node.Type:
                return False
            
            ext_files = node.ExternalFiles
            
            ext_model_dict = {}
            for f in ext_files:
                
                if f.FileType == 'Pictures':
                    owner = str(f.Owners[0])
                    if owner == attribute:
                        f.Path = value
                        new_owner = str(f.Owners[0])
                        return new_owner
        ''' 
    # selection functions
    def select(my, node_name):
        node = my.root.FindChild(node_name)
        if not node:
            return False
        my.xsi.SelectObj(node_name, "", "")


    # file operations
    def import_file(my, path, namespace=''):
        
        if path.endswith('.scn'):
            raise XSIException('.scn file can only be opened. Please select the open option')
        
        reference = False
        parent = None
        value = None
        collection = None

        my.message("Import path: %s [%s]" % (path, namespace))
        if path.endswith(".xsi"):
            my.xsi.ImportDotXSI(path)
            return namespace
        elif path.endswith(".obj"):
            collection = my.xsi.ObjImport(path)
            return namespace
        elif path.endswith(".eani"):
            my.xsi.ImportAction("", path, namespace, -1)
            return namespace
        else:
            # return ISIVTCollection
            collection = my.xsi.ImportModel(path, parent, reference, value, namespace)
            if collection and len(collection) >= 2:
                return str(collection[1])
            else:
                return namespace




    def import_reference(my, path, namespace=""):
        if path.endswith('.scn'):
            raise XSIException('.scn file can only be opened. Please select the open option')
        reference = True
        parent = None
        root = my.xsi.ActiveSceneRoot
        my.message("Reference path: %s" % path)
        if path.endswith(".xsi"):
            my.xsi.ImportDotXSI(path, parent)
            return namespace
        elif path.endswith(".eani"):
            my.xsi.ImportAction("", path, namespace, -1)
            return namespace
        else:
            collection = my.xsi.ImportModel(path, parent, reference, root, namespace )
            if len(collection) >= 2:
                return str(collection[1])
            else:
                return namespace

       
        
    
    def is_reference(my, node_name, recursive=False):
        # just look at top node
        my.message("node_name: [%s]" % node_name)
        model = my.root.FindChild(node_name, '', '', recursive)
        if not model:
            return False
        
        # can only take Model ... Scene which does not really apply here
        if 'model' not in model.Type:
            return False

        # check the first file reference
        fs = model.ExternalFiles
        if len(fs) > 0:
            for f in fs:
                owner = f.Owners[0]
                if f.FileType == 'Models':
                    owner_node = re.sub('\.%s'%owner.Name,  "", str(owner))
                    if owner_node == node_name and owner.LockType == 3:
                        return True
        else:
            return False
    
    def update_reference(my, node_name, path, top_reference=False):
        '''does not use resolution'''
        # set to recursive = True, Type and Family to '' for now
        model = my.root.FindChild(node_name, '', '', not top_reference)

        if not model:
            return False

        # can only take Model
        if 'model' not in model.Type:
            return False
        ext_files = model.ExternalFiles
        
        ext_model_dict = {}
        for f in ext_files:
            if f.FileType == 'Models':
                base_path = os.path.basename(f.Path)
                ext_model_dict[base_path] = f
        
        new_base_path = os.path.basename(path)
        f = ext_model_dict.get(new_base_path)
        if f:
            f.Path =  path
        else:
            my.xsi.LogMessage('Nothing to update')

    def replace_reference(my, node_name, path, top_reference=False):
        '''load using references. If top reference is False, 
            it will replace the sub reference if any (To be enabled).
            Resolution is used here'''
        
        # set to recursive = True, Type and Family to '' for now
        model = my.root.FindChild(node_name, '', '', not top_reference)

        if not model:
            return False

        # can only take Model
        if 'model' not in model.Type:
            return False
        
        ext_files = model.ExternalFiles
        ext_model_dict = {}
        for f in ext_files:
            if f.FileType == 'Models':
                key_path = f.Path.replace('\\','/')
                ext_model_dict[key_path] = f
        

        f = ext_model_dict.get(path)
        if f:
            #owner = f.Owners[0]
            #f.Path =  path
            #my.xsi.LogMessage("Replace reference with [%s] " % path)
            #LogMessage(f.Owners[0])
            idx = my._get_resolution_index_by_path(model, path)
            act_res = idx
            my.xsi.SetValue('%s.active_resolution' %node_name, idx)

        else:
            resolutions = my._get_all_resolutions(model)
            if not resolutions: # not a referenced model
                my.message("This is not a referenced model. Skip.")
                return ""
            res_name = "new_res%s" %len(resolutions)
            #res_name = "new_res"
            my.xsi.AddRefModelResolution( model, res_name, path)
            
            idx = my._get_resolution_index_by_name(model, res_name)
            act_res = idx
            
        # set it to new resolution
        if act_res == -1:
            # failed to locate the active res
            return ""

        my.xsi.SetValue('%s.active_resolution' %node_name, act_res)
        my.message('Set active resolution to %s' %act_res)
            
        return path

    def _get_all_resolutions(my, in_oRefModel ):
        objs =  in_oRefModel.NestedObjects
        for oCurrentContainer in objs:
            if oCurrentContainer.Name == "Resolutions":
                return oCurrentContainer.NestedObjects

    def _get_resolution_index_by_name(my, in_oModel, in_sResName):
        ''' Visit each resolution and check its name against the specified name
            eg. res1 and res2 '''
        oResolutions = my._get_all_resolutions( in_oModel );
        for idx, res in enumerate(oResolutions):
            res_value = my.xsi.GetValue(res.NestedObjects("name"))
            if res_value == in_sResName:
                return idx

        #If not found, return a negative value
        return -1

    def _get_resolution_index_by_path(my, in_oModel, in_Path):
        '''get the path list of a referenced model'''
        oResolutions = my._get_all_resolutions( in_oModel );
        in_Path = in_Path.replace('\\','/')
        for idx, res in enumerate(oResolutions):
            for info in res.NestedObjects:
                if info.Name =='file':
                    info_path = info.Value.replace('\\','/')
                    if info_path == in_Path:
                        return idx

        return -1

    
     
    def load(my, path):
        if path.endswith('.scn'):
            my.xsi.OpenScene(path, True)
        else:
            raise XSIException('path [%s] is not a valid scn file. Files like .emdl should be imported' % path)
        return path

    def save(my, path):
        '''if called directly, check for system folder existence first'''
        dir, filename = os.path.split(path)
        dir = dir.replace('\\', '/')
        env = XSIEnvironment.get()  
        tmp_dir = env.get_tmpdir()
        if dir == tmp_dir:
            project_dir = dir
        else:
            tmp_dirs = dir.split('/')
            project_dir = '/'.join(tmp_dirs[:-1])
        if not os.path.exists('%s/system'%project_dir):
            my.set_project(project_dir)
        my.xsi.SaveSceneAs(path, "")
        return path

    def get_save_dir(my):
        dir = my.get_project()
        dir = '%s/TacticTemp' % dir
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def save_node(my, node_name, dir=None, type="scn" ):
        # HACK, always use the project-based save dir 
        dir = my.get_save_dir()
        if dir == None:
            path = "%s" % (node_name)
        else:
            path = "%s/%s" % (dir, node_name)

        if type == "scn" and not path.endswith(".scn"):
            path, ext = os.path.splitext(path)
            path = "%s.scn" % path
        return my.save(path)

    def export_node(my, node_name, context, dir=None, type="emdl", filename="", preserve_ref=None, instance=None ):
        if not my.node_exists(node_name):
            raise XSIException("Node '%s' does not exist" % node_name)

        naming = my.get_node_naming(node_name)
        asset_code = naming.get_asset_code()

        # context not used for now
        if type == "dotXSI":
            ext = "xsi"
            path = "%s/%s.%s" % (dir, asset_code, ext)
            my.xsi.ExportDotXSI(node_name, path)
        elif type == "obj":
            ext = "obj"
            path = "%s/%s.%s" % (dir, asset_code, ext)
            #TODO: NOT working yet. All the options are needed for OBJ export
            my.xsi.ObjExport(path)
        else:
            ext = "emdl"
            path = "%s/%s.%s" % (dir, asset_code, ext)
            include_submodel = True
            copy_extfiles = True
            my.xsi.ExportModel(node_name, path, include_submodel, copy_extfiles)

        return path



    def import_dotxsi(my, path, namespace=""):
        my.xsi.ImportDotXSI(path)



    def get_file_path(my):
        scene_name = str(my.xsi.GetValue("Project.Scene"))
        project_path = my.get_project()
        if scene_name == 'Scene':
            return "%s/untitled.scn" %project_path
        else:
            return "%s/%s.scn" %(project_path, scene_name)

    def get_project(my):
        path = my.xsi.ActiveProject.Path
        return path

    def create_set(my, node_name):
        '''add a null instead'''
        if not my.node_exists(node_name):
            my.xsi.ActiveProject.ActiveScene.Root.AddNull(node_name)

    # information retrieval functions.  Requires an open XSI session
    def node_exists(my,node):
        # this forms a valid list even if the node cannot be found in session
        my.xsi.SelectObj('%s, ' %node)
        if my.xsi.Selection.GetAsText() == node:
            return True
        else:
            return False

    def message(my, message):
        my.xsi.LogMessage(message)



    def get_file_references(my, top_node=None):
        
        nodes = []
        paths = []
        attrs = []

        model = my.root.FindChild(top_node)
        if not model:
            return nodes, paths, attrs

        paths = model.ExternalFiles
        for file in files:
            Application.LogMessage(file)

        return nodes, paths, attrs


    def get_nodes_in_set(my, set_name):
        model = my.root.FindChild(set_name)
        if not model:
            return []
        else:
            return model.Name

    def get_selected_node(my, resolve_parent=True):
        nodes = my.get_selected_nodes()
        if nodes:
            node = nodes[0]
            if "." in node and resolve_parent:
                node, sub_node = node.split('.', 1)
            #my.message("SELECTED NAME " + node)
            return node

        else:
            return None

    def get_selected_nodes(my):
        nodes = my.xsi.Selection
        node_names = nodes.GetAsText()
        if node_names:
            return node_names.split(',')
        else:
            return []

    def has_flex_range(my):
        '''has flexible file range for file sequence definition'''
        return False

    # static functions
    xsi = None
    def get():
        env = XSIEnvironment.get()
        return env.get_app()
    get = staticmethod(get)


