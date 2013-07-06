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

import os, re
import shutil
from common import *
from pyasm.application.common import NodeData, Common



def _get_nodes(instance):
    '''gets all the nodes related to this instance'''

    info = TacticInfo.get()
    app = info.get_app()

    instance_nodes = []

    # HACK: use namespace: select the instance as well
    if app.name == "maya" and app.namespace_exists(instance):
        # get all of the assemblies
        top_nodes = app.get_top_nodes()
        for top_node in top_nodes:
            if top_node.startswith("%s:" % instance):
                instance_nodes.append(top_node)

    else:
        # handle as a set
        node_names = app.get_nodes_in_set(instance)
        instance_nodes.extend(node_names)

    return instance_nodes

    
    



def select(select_info, is_anim):
    if is_anim =='instance':
        snapshot_code, shot_code, instance, context, ns, snap_node_name = select_info.split("|")
    else:
        snapshot_code, context,  ns, snap_node_name = select_info.split("|")

    info = TacticInfo.get()
    app = info.get_app()

    # don't think it's necessary, the user can just click on the viewport
    #app.select_none()

    node_names = _get_nodes(ns)
    for node_name in node_names:
        app.select_add(node_name)



def delete(select_info, is_anim):
    if is_anim =='instance':
        snapshot_code, shot_code, instance, context, ns, snap_node_name = select_info.split("|")
    else:
        snapshot_code, context, ns, snap_node_name = select_info.split("|")
    info = TacticInfo.get()
    app = info.get_app()

    #node_names = app.get_nodes_in_set(instance)

    # select all the nodes in a set via namespace
    node_names = _get_nodes(ns)
    for node_name in node_names:
        app.delete(node_name)

    # remove if the instance is a set
    if app.node_exists(ns):
        app.delete(ns)



def update(select_info, is_anim, options):

    from tactic_load import load_anim, load

    # remove the set
    delete(select_info, is_anim)

    # and reload it
    if is_anim =='instance':
        snapshot_code, shot_code, instance, context, ns, snap_node_name = select_info.split("|")
        load_anim(snapshot_code, shot_code, instance, context, options)
    else:
        # this assumes only 1 instance of this asset exist
        snapshot_code, context, ns, snap_node_name = select_info.split("|")
        load(snapshot_code, context, options)




def replace_reference(select_info, prefix, options):
    from tactic_load import load_anim, load
    # quick hack
    '''
    if options.find("connection=file system") != -1:
        options = "load_mode=replace|connection=file system"
    else:
        options = "load_mode=replace|connection=http"
    '''
    info = TacticInfo.get() 
    server = info.get_xmlrpc_server()
    ticket = info.get_ticket()
   
    option_dict  = Common.get_option_dict(options)
    option_dict['load_mode'] = 'replace'

    
    # check if user wants to pick a node to update
    user_selected_nodes = []
    if option_dict.get('replace_selected') =='true':
        user_selected_nodes = info.get_app().get_selected_nodes()
        if not user_selected_nodes:
            raise TacticException('A minimum of 1 node must be selected for this "replace selected reference" operation')

    # some instance reference is actually just replace assets from model pipeline
    # In that case, there are only 4 items
    items = select_info.split("|")
    if prefix =='prod/shot_instance' and len(items) == 6:
        snapshot_code, shot_code, instance, context, ns, snap_node_name = \
            select_info.split("|")
        if not user_selected_nodes:
            user_selected_nodes = [snap_node_name]

        for user_selected_node in user_selected_nodes:
            node_name = _check_node_exists(user_selected_node, ns) 
            if node_name:
                option_dict['replacee']= node_name
            options = Common.get_option_str(option_dict)
            load_anim(snapshot_code, shot_code, instance, context, options)
       

    else:
        # this assumes only 1 instance of this asset exist
        snapshot_code, context, ns, snap_node_name = select_info.split("|")
        
        if not user_selected_nodes:
            user_selected_nodes = [snap_node_name]

        for user_selected_node in user_selected_nodes:
            node_name = _check_node_exists(user_selected_node, ns) 

            if node_name:
                option_dict['replacee']= node_name
            options = Common.get_option_str(option_dict)
            load(snapshot_code, context, options)


def _check_node_exists(snap_node_name, ns):
    '''check if node_name or ns:node_name exists in the session'''
    info = TacticInfo.get() 
    app = info.get_app()
    node_name = ''
    if app.node_exists(snap_node_name):
        node_name = snap_node_name
    elif app.node_exists('%s:%s' %(ns, snap_node_name)):
        node_name = '%s:%s' %(ns, snap_node_name)
    return node_name

def assign_namespace(namespace):
    info = TacticInfo.get()
    app = info.get_app()
    top_nodes = app.get_selected_nodes()
    renamed_top_nodes = []
    
    # select the hierarchy downstream
    for node in top_nodes:
        app.select_hierarchy(node)
        hi_nodes = app.get_selected_nodes()

        for node in hi_nodes:
            node_name = node
            # shape nodes may have been renamed indirectly already
            if not app.node_exists(node_name):
                continue
            
            new_name = _get_new_name(node, namespace)
            
            # the returned name may be different if it already exists
            new_name = app.rename_node(node_name, new_name)
            if node in top_nodes:
                renamed_top_nodes.append(new_name)

    # restore selection
    app.select_restore(renamed_top_nodes)

def _get_new_name(node_name, namespace):
    ''' get the new name with the given namespace'''
    new_name = ''
    if ":" in node_name:
        parts = node_name.split(":")
        parts[0] = namespace
        new_name = ':'.join(parts)
    else:
        new_name = '%s:%s' %(namespace, node_name)
    return new_name

def set_namespace(namespace):
    info = TacticInfo.get()
    app = info.get_app()
    app.set_namespace(namespace)



def save_file(path, overwrite=False):
    '''save a file or save current scene if a path is not given'''
    info = TacticInfo.get()
    app = info.get_app()

    if not path:
        path = app.get_file_path()

    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    if overwrite:
        app.save(path)
    else:
        if not os.path.exists(path):
            app.save(path)
        else:
            info.report_error('This file already exists. Please save it manually with another name.')
    return path

def get_prefix(filename):
    '''get the prefix (without the version part if available) based on a filename'''
    basename, extension = os.path.splitext(filename)
    pattern = re.compile( r'(\w+)v(\d+)')
    m = pattern.match(basename)
    if m:
        prefix = m.groups()[0]
        number = int(m.groups()[1])
    else:
        prefix = '%s_' %basename
        number = 0
    return prefix, number

def save_sandbox_file(path):
    '''new way of saving sandbox file by trying to get the next valid file name'''
    org_prefix = ''
    highestnumbers = {}
    highestfiles = {}
    #path = 'C:/tactic_projects/racoon/sandbox/boris/shot/HT001_051/Scenes/untitled_layout_v001.scn'
    dir, org_file = os.path.split(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    org_basename, org_extension = os.path.splitext(org_file)
    for filename in os.listdir(dir):
        basename, extension = os.path.splitext(filename) 
        if extension != org_extension:
            continue
        prefix, number = get_prefix(filename) 
        if path.endswith(filename):
            org_prefix = prefix
        if number > highestnumbers.get(prefix):
            highestnumbers[prefix] = number
            highestfiles[prefix] = prefix, extension
    if not org_prefix:
        new_path = path
    else:
        basename, extension = highestfiles.get(org_prefix)
        number  = highestnumbers.get(org_prefix)
        new_file_name = '%sv%0.3d%s' %(basename, number+1, extension)
        new_path = '%s/%s' %(dir, new_file_name)
    save_file(new_path)


def set_user_environment(project_path, filename):

    info = TacticInfo.get()
    app = info.get_app()

    impl = info.get_app_implementation()
    # get the current filename
    if not filename:
        current_path = app.get_file_path()
        filename = os.path.basename(current_path)

    if not os.path.exists(project_path):
        os.makedirs(project_path)
        #info.report_error("[%s] does not exist yet. Please try to save file to this" \
        #    " sandbox folder before setting it as a Project." %project_path)
    impl.set_user_environment(project_path, filename)

def copy_file(path, new_path):
    try:
        dir = os.path.dirname(new_path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copy(path, new_path)
    except IOError:
        print "Error copying file [%s] to [%s]" %(path, new_path)



