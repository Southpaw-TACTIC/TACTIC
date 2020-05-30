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

__all__ = ["Snapshot","SnapshotType","SObjectNotFoundException"]


import os, string, types
import re

from pyasm.common import Container, Xml, Environment, Common, Config
from pyasm.search import *
from .project import Project
from .file import File, FileRange, FileGroup

import six
basestring = six.string_types

class SObjectNotFoundException(Exception):
    pass



class SnapshotType(SObject):
    SEARCH_TYPE = "sthpw/snapshot_type"

    '''
    def get_by_code(cls, code):
        sobject = super(SnapshotType, cls).get_by_code(code)
        if not sobject:
            search_type = "sthpw/snapshot_type"
            search = Search(search_type)
            search.add_filter("code", code)
            sobject = search.get_sobject()

        return sobject
    get_by_code = classmethod(get_by_code)
    '''





class Snapshot(SObject):

    SEARCH_TYPE = "sthpw/snapshot"

    def __init__(self, search_type=None, columns=None, results=None, fast_data=None):
        super(Snapshot, self).__init__(search_type, columns, results, fast_data=fast_data)

        self.files_dict = None




    def get_defaults(cls):
        '''specifies the defaults for this sobject'''
        defaults = {
            "version": 1,
            "revision": 0
        }

        return defaults
    get_defaults = classmethod(get_defaults)


    def get_sobject(self, prefix="search"):
        '''get the sobject it is pointing to'''

        # this is caching of sobjects. Should probably be held
        # centrally
        search_type = self.get_value("%s_type" % prefix)
        search_id = self.get_value("%s_id" % prefix, no_exception=True)
        search_code = self.get_value("%s_code" % prefix, no_exception=True)
        if not search_type:
            return None

        sobject = None
        if search_code and isinstance(search_code, basestring):
            sobject = Search.get_by_code(search_type, search_code, show_retired=True)
        else:
            sobject = Search.get_by_id(search_type, search_id, show_retired=True)
        if sobject == None:
            if search_id:
                sobject = Search.get_by_id(search_type, search_id)

            if not sobject:
                raise SObjectNotFoundException('SObject [%s,%s] or [%s,%s]  not found for snapshot [%s]' \
                    %(search_type, search_id, search_type, search_code, self.get_code()))
            
            #Container.put(key, sobject)

        return sobject



    def set_sobject(self, sobject):
        self.set_value("search_type", sobject.get_search_type() )
        self.set_value("search_id", sobject.get_id() )


    def get_level(self):
        return self.get_sobject(prefix="level")
 
    def set_level(self, sobject):
        self.set_value("level_type", sobject.get_search_type() )
        self.set_value("level_id", sobject.get_id() )

       


    def get_code(self):
        return self.get_value("code")


    def get_snapshot_type(self):
        return self.get_value("snapshot_type")


    def get_snapshot_xml(self):
        return self.get_xml_value("snapshot")

    def get_label(self):
        return self.get_value('label')

    def get_repo(self,snapshot=None):
        repo =  self.get_sobject().get_repo(self)
        return repo


    def get_ref_snapshot(self, name, value, mode='explicit', show_retired=False):
        '''get the referred reference snapshot'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot//ref[@%s='%s']" % (name, value) )
        return self.get_ref_snapshot_by_node(node, show_retired=show_retired )


    def get_ref_snapshots(self, name, value, mode='explicit', show_retired=False):
        '''get the referred reference snapshot'''
        xml = self.get_snapshot_xml()
        nodes = xml.get_nodes("snapshot//ref[@%s='%s']" % (name, value) )

        snapshots = []
        for node in nodes:
            snapshot = self.get_ref_snapshot_by_node(node, show_retired=show_retired )
            if snapshot:
                snapshots.append(snapshot)
        return snapshots



    def get_ref_snapshot_by_node(cls, node, mode='explicit', show_retired=False):
        '''get the ref snapshot represented by this node'''
        search_type = Xml.get_attribute(node, "search_type")
        search_code = Xml.get_attribute(node, "search_code")
        if not search_code:
            search_id = Xml.get_attribute(node, "search_id")
            # assign search_id to the search_code variable
            search_code = int(search_id)

        context = Xml.get_attribute(node, "context")
        snapshot_code = Xml.get_attribute(node, "snapshot_code")

        #add level_support
        level_type = Xml.get_attribute(node, "level_type")
        level_id = Xml.get_attribute(node, "level_id")

        if mode == 'latest':
            version = -1
        elif mode == 'current':
            version = 0
        elif mode == 'explicit':
            if snapshot_code and not level_type:
                snapshot = cls.get_by_code(snapshot_code, show_retired=show_retired)
                return snapshot
            version = Xml.get_attribute(node, "version")
        else:
            version = Xml.get_attribute(node, "version")

        snapshot = cls.get_by_version(search_type, search_code, context, version, level_type=level_type, level_id=level_id, show_retired=show_retired )

        return snapshot

    get_ref_snapshot_by_node = classmethod(get_ref_snapshot_by_node)


    def get_all_ref_snapshots(self, mode='explicit', type='ref', show_retired=False):
        '''look at the snapshot a get the referred snapshot'''
        xml = self.get_snapshot_xml()
        nodes = xml.get_nodes("snapshot//%s" % type)
        snapshots = []
        for node in nodes:
            snapshot = self.get_ref_snapshot_by_node(node, mode=mode,  show_retired=show_retired)
            if snapshot:
                snapshots.append(snapshot)
        return snapshots



    def get_version(self):
        return self.get_value("version")
    
    def get_context(self):
        return self.get_value("context")

    def get_type(self):
        return self.get_value("snapshot_type")

    def get_previous(self):
        version = self.get_value("version")
        if version == 1:
            return None

        search_type = self.get_value("search_type")
        search_id = self.get_value("search_id")
        context = self.get_value("context")

        prev_version = version - 1

        return self.get_by_version(search_type, search_id, context, prev_version)

    def get_file_type(self):
        '''this will just get the first one if there are more than 1'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file")
        if node is not None:
            return Xml.get_attribute(node, "type")
        else:
            return ''

    def get_all_file_types(self):
        '''get all file types'''
        xml = self.get_snapshot_xml()
        types = xml.get_nodes_attr('snapshot/file', 'type')
        return types

    def get_all_file_objects(self, exclude_file_types=[]):
        '''get all of the file objects in a snsapshot'''
        file_objects = []
        xml = self.get_snapshot_xml()
        file_codes = xml.get_values("snapshot//file/@file_code")
        file_types = xml.get_values("snapshot//file/@type")
        if not file_codes:
            return []


        filtered_codes = []
        for file_code, file_type in zip(file_codes, file_types):
            if file_type in exclude_file_types:
                continue
            filtered_codes.append(file_code)
    
        search = Search("sthpw/file")
        search.add_filters("code", filtered_codes)
        file_objects = search.get_sobjects()

        return file_objects



    def get_files_by_snapshots(cls, snapshots, file_type=None):
        '''get all of the file objects in a snsapshot'''
        if not snapshots:
            return []

        all_file_codes = []
        for snapshot in snapshots:
            file_codes = snapshot.get_all_file_codes()
            all_file_codes.extend(file_codes)

        if not all_file_codes:
            return []

        search = Search("sthpw/file")
        search.add_filters("code", all_file_codes)
        if file_type:
            search.add_filter("type", file_type)
        search.add_order_by("code")
        file_objects = search.get_sobjects()
        return file_objects
    get_files_by_snapshots = classmethod(get_files_by_snapshots)



    def get_files_dict_by_snapshots(cls, snapshots, attr="snapshot_code", file_type=None):
        '''gets all of the file objects in a dict of lists.  The keys are
        sorted by the attr argument'''
        # preprocess and get all file objects
        all_files = {}
        files = Snapshot.get_files_by_snapshots(snapshots, file_type=file_type)
        for file in files:
            snapshot_code = file.get_value(attr)

            file_list = all_files.get(snapshot_code)
            if not file_list:
                file_list = []
                all_files[snapshot_code] = file_list

            file_list.append(file)
        return all_files 
    get_files_dict_by_snapshots = classmethod(get_files_dict_by_snapshots)




    def get_type_by_file_name(self, file_name):
        '''gets the name of the file reference'''
        xml = self.get_snapshot_xml()

        node = xml.get_node('snapshot/file[@name="%s"]' % file_name)
        if node is not None:
            return Xml.get_attribute(node, "type")
        else:
            return ''


    def get_type_by_file_code(self, file_code):
        '''gets the name of the file reference'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file[@file_code='%s']"%file_code)
        if node is not None:
            return Xml.get_attribute(node, "type")
        else:
            return ''





    def get_name_by_type(self, type):
        '''gets the name of the file reference'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is not None:
            return Xml.get_attribute(node, "name")
        else:
            return ''


    def get_names_by_type(self, type):
        '''gets the name of the file reference'''
        xml = self.get_snapshot_xml()
        nodes = xml.get_nodes("snapshot/file[@type='%s']"%type)

        names = []
        for node in nodes:
            name = Xml.get_attribute(node, "name")
            names.append(name)
        return names



    def get_file_name_by_type(self, type):
        '''gets the full filename of the file reference as it is on disk'''
        '''Note that this is now the same as "get_name_by_type" because the
        snapshot now contains the full file name'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        return file_name

    def get_all_file_names(self):
        file_names = []

        xml = self.get_snapshot_xml()
        nodes = xml.get_nodes("snapshot/file")
        if not nodes:
            return file_names

        for node in nodes:
            file_name = self._get_file_name(node)
            file_names.append(file_name)

        return file_names


    def get_all_file_codes(self):
        xml = self.get_snapshot_xml()
        file_codes = xml.get_values("snapshot//file/@file_code")
        return file_codes


    def get_files_by_type(self, type):
        '''gets the name of the file reference'''
        xml = self.get_snapshot_xml()
        nodes = xml.get_nodes("snapshot/file[@type='%s']"%type)

        codes = []
        for node in nodes:
            code = Xml.get_attribute(node, "file_code")
            codes.append(code)

        search = Search("sthpw/file")
        search.add_filters("code", codes)
        search.add_order_by("code")
        file_objects = search.get_sobjects()
        return file_objects


    def get_file_by_type(self, type):
        '''gets the name of the file reference'''
        file_objects = self.get_files_by_type(type)
        if file_objects:
            return file_objects[0]
        else:
            return None




    def get_file_code_by_type(self, type):
        '''gets the file_code'''
        xml = self.get_snapshot_xml()
        if type.find("'") != -1:
            node = xml.get_node('snapshot/file[@type="%s"]'%type)
        else:
            node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is not None:
            return Xml.get_attribute(node, "file_code")
        else:
            return ''


    def get_file_range(self, type='main'):
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            file_range_str = "0-0"
        else:
            file_name = self._get_file_name(node)
            file_range_str = Xml.get_attribute(node, "file_range")

        file_range = FileRange.get(file_range_str)
        return file_range



    def get_expanded_file_names(self, type='main'):
        '''get all of the file names in the range'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file[@type='%s']"%type)
        file_name = self._get_file_name(node)

        file_range_str = Xml.get_attribute(node, "file_range")
        if not file_range_str:
            file_range_str = "1-1/1"

        file_range = FileRange.get(file_range_str)

        expanded_names = FileGroup.expand_paths(file_name, file_range)

        return expanded_names


    def get_expanded_lib_paths(self, type='main'):
        '''get all of the file names in the range'''
        lib_dir = self.get_lib_dir()
        expanded_file_names = self.get_expanded_file_names(type=type)
        expanded_paths = ["%s/%s" % (lib_dir, x) for x in expanded_file_names]

        return expanded_paths



    def get_expanded_web_paths(self, type='main'):
        '''get all of the file names in the range'''
        web_dir = self.get_web_dir()
        expanded_file_names = self.get_expanded_file_names(type=type)
        expanded_paths = ["%s/%s" % (web_dir, x) for x in expanded_file_names]

        return expanded_paths





    def get_web_path_by_type(self, type='main'):
        ''' get the lib path by specifying a file type '''
        xml = self.get_snapshot_xml()

        web_dir = self.get_web_dir()

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        web_path = "%s/%s" % (web_dir,file_name)
        
        return web_path



    def get_remote_web_path_by_type(self, type='main'):
        ''' get the lib path by specifying a file type '''
        xml = self.get_snapshot_xml()

        web_dir = self.get_remote_web_dir()

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        web_path = "%s/%s" % (web_dir,file_name)
        
        return web_path



    def get_lib_path_by_type(self, type='main'):
        ''' get the lib path by specifying a file type '''
        xml = self.get_snapshot_xml()

        lib_dir = self.get_lib_dir(file_type=type)
        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        file_path = "%s/%s" % (lib_dir,file_name)
        
        return file_path


    def get_client_lib_path_by_type(self, type):
        ''' get the lib path by specifying a file type '''
        xml = self.get_snapshot_xml()

        client_lib_dir = self.get_client_lib_dir(file_type=type)

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        file_path = "%s/%s" % (client_lib_dir,file_name)
        
        return file_path



    def get_sandbox_path_by_type(self, type):
        ''' get the lib path by specifying a file type '''
        xml = self.get_snapshot_xml()

        sandbox_dir = self.get_sandbox_dir(file_type=type)

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        file_path = "%s/%s" % (sandbox_dir,file_name)
        
        return file_path


    def get_env_path_by_type(self, type):
        ''' get the env path by specifying a file type '''
        xml = self.get_snapshot_xml()

        env_dir = self.get_env_dir()

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

        file_name = self._get_file_name(node)
        file_path = "%s/%s" % (env_dir,file_name)
        
        return file_path




    def get_path_by_type(self, type, mode="lib", filename_mode=None):
        dirname = self.get_dir(mode, file_type=type, file_object=None)

        xml = self.get_snapshot_xml()

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

 
        # get the source file name
        if filename_mode == 'source':
            file_code = xml.get_attribute(node, "file_code")
            context = self.get_value("context")

            file_object = Search.get_by_code("sthpw/file", file_code)
            #file_name = os.path.basename(file_object.get_value("source_path"))

            basename = os.path.basename(file_object.get_value("source_path"))
            context = self.get_value("context")
            parts = context.split("/")

            rel_dir = "/".join(parts[1:-1])
            file_name = "%s/%s" % (rel_dir, basename)
 

        else:
            file_name = self._get_file_name(node)

        file_path = "%s/%s" % (dirname,file_name)
        
        return file_path



    def get_paths_by_type(self, type, mode="lib", filename_mode=None, expand_paths=True):
        dirname = self.get_dir(mode, file_type=type, file_object=None)
        repo_dirname = self.get_dir("lib", file_type=type, file_object=None)

        xml = self.get_snapshot_xml()

        node = xml.get_node("snapshot/file[@type='%s']"%type)
        if node is None:
            return ''

 
        # get the source file name
        if filename_mode == 'source':
            file_code = xml.get_attribute(node, "file_code")
            context = self.get_value("context")

            file_object = Search.get_by_code("sthpw/file", file_code)

            basename = os.path.basename(file_object.get_value("source_path"))
            context = self.get_value("context")
            parts = context.split("/")

            rel_dir = "/".join(parts[1:-1])
            file_name = "%s/%s" % (rel_dir, basename)
            #file_name = os.path.basename(file_object.get_value("source_path"))

            repo_file_name = self._get_file_name(node)
        else:
            file_name = self._get_file_name(node)
            repo_file_name = file_name

        file_paths = []

        if expand_paths:
            repo_file_path = "%s/%s" % (repo_dirname, repo_file_name)
            if os.path.isdir(repo_file_path):
                for root, dirnames, basenames in os.walk(repo_file_path):
                    for basename in basenames:
                        path = "%s/%s" % (root, basename)
                        rel_path = path.replace(repo_file_path, "")
                        path = "%s/%s/%s" % (dirname, file_name, rel_path)
                        file_paths.append(path)
            else:
                file_path = "%s/%s" % (dirname,file_name)
                file_paths.append(file_path)
        else:
            file_path = "%s/%s" % (dirname,file_name)
            file_paths.append(file_path)
        
        return file_paths





 
    def get_all_web_paths(self):
        xml = self.get_snapshot_xml()

        web_dir = self.get_web_dir()

        nodes = xml.get_nodes("snapshot/file")
        paths = []
        for node in nodes:
            file_name = self._get_file_name(node)
            file_path = "%s/%s" % (web_dir,file_name)

            paths.append(file_path)

        return paths


    def get_all_remote_web_paths(self):
        xml = self.get_snapshot_xml()

        web_dir = self.get_remote_web_dir()

        nodes = xml.get_nodes("snapshot/file")
        paths = []
        for node in nodes:
            file_name = self._get_file_name(node)
            file_path = "%s/%s" % (web_dir,file_name)

            paths.append(file_path)

        return paths


    
    def _get_files_dict(self, xml):
        if self.files_dict != None:
            return self.files_dict
            
        nodes = xml.get_nodes("snapshot//file")
        # get all of the codes
        file_codes = [Xml.get_attribute(x, "file_code") for x in nodes]
        search = Search("sthpw/file")
        search.add_filters("code", file_codes)
        files = search.get_sobjects()
        self.files_dict = {}
        for file in files:
            self.files_dict[file.get_value("code")] = file

        return self.files_dict


    def get_dir(self, mode, file_type='main',file_object=None):
        '''get the repo dir given a mode'''
        dir = ''
        if mode in ['lib', 'repo']:
            dir = self.get_lib_dir(file_type=file_type,file_object=file_object)
        elif mode == 'client_repo':
            dir = self.get_client_lib_dir(file_type=file_type,file_object=file_object)
        elif mode == 'sandbox':
            # sandbox always uses naming, so no file object needs to be
            # included
            dir = self.get_sandbox_dir(file_type=file_type)
        elif mode == 'local_repo':
            dir = self.get_local_repo_dir(file_type=file_type,file_object=file_object)
        elif mode in ['web', 'browser']:
            dir = self.get_web_dir(file_type=file_type,file_object=file_object)
        elif mode == 'relative':
            dir = self.get_relative_dir(file_type=file_type,file_object=file_object)
        return dir



    def get_all_lib_paths(self, mode='lib', expand_paths=False, filename_mode=None, exclude_file_types=[]):
        '''Get paths for different modes, default to lib mode which is the repo
        server path
        '''
        xml = self.get_snapshot_xml()
        files_dict = self._get_files_dict(xml)
        assert mode in ['lib', 'client_repo', 'sandbox', 'local_repo', 'web', 'relative', 'browser']
        paths = []
        nodes = xml.get_nodes("snapshot/file")

        # have to get all of the file objects here
        #file_objects = self.get_all_file_objects()
        for i, node in enumerate(nodes):
            file_type = Xml.get_attribute(node, "type")
            file_code = Xml.get_attribute(node, "file_code")
            if not file_type:
                file_type = 'main'

            if file_type in exclude_file_types:
                continue

            file_object = files_dict.get(file_code)
            # may have been deleted
            if not file_object:
                continue

            dir = self.get_dir(mode, file_type=file_type, file_object=file_object)

            # check to see if it is a sequence
            base_type = file_object.get_value("base_type")
            if expand_paths and base_type == "sequence":
                file_names = self.get_expanded_file_names(file_type)

            elif expand_paths and base_type == 'directory':
                # find the server repo path
                repo_dir = self.get_dir("repo", file_type=file_type, file_object=file_object)
                file_name = self._get_file_name(node)
                repo_dir = "%s/%s" % (repo_dir, file_name)
                if os.path.isdir(repo_dir):
                    file_names = [file_name]
                    new_names = os.listdir(repo_dir)
                    for new_name in new_names:
                        file_names.append("%s/%s" % (file_name, new_name))
                else:
                    file_names = [file_name]

            else:

                # get the source file name
                if filename_mode == 'source':
                    basename = os.path.basename(file_object.get_value("source_path"))
                    context = self.get_value("context")
                    parts = context.split("/")

                    rel_dir = "/".join(parts[1:-1])
                    file_name = "%s/%s" % (rel_dir, basename)

                else:
                    file_name = self._get_file_name(node)

                file_names = [file_name]



            for file_name in file_names:
                file_path = "%s/%s" % (dir,file_name)
                paths.append(file_path)

        return paths





    # DEPRECATED: use client_repo methods below
    def get_all_client_lib_paths(self, expand_paths=False):
        return self.get_all_lib_paths("client_repo", expand_paths=expand_paths)
    def get_all_client_lib_paths_dict(self):
        paths = self.get_all_paths_dict('client_repo') 
        return paths

    def get_all_client_repo_paths(self, expand_paths=False):
        return self.get_all_lib_paths("client_repo", expand_paths=expand_paths)
    def get_all_client_repo_paths_dict(self):
        paths = self.get_all_paths_dict('client_repo') 
        return paths



    def get_all_local_repo_paths(self, expand_paths=False):
        return self.get_all_lib_paths("local_repo", expand_paths=expand_paths)
    def get_all_local_repo_paths_dict(self):
        paths = self.get_all_paths_dict('local_repo') 
        return paths





    def get_all_web_paths_dict(self):
        paths = self.get_all_paths_dict('web') 

        return paths

    def get_all_paths_dict(self, mode='lib'):
        '''this is the general one and  should be called instead of 
            the specific get_all_web_paths_dict'''
        xml = self.get_snapshot_xml()

        nodes = xml.get_nodes("snapshot/file")

        # have to get all of the file objects here
        file_objects = self.get_all_file_objects()

        # ensure that the number of file objects is the same as the number
        # of nodes
        if len(nodes) != len(file_objects):
            print("ERROR: number of nodes does not match number of file objects for snapshot[%s]" % self.get_code())
            return {}


        paths = {}
        for i, node in enumerate(nodes):
            type = Xml.get_attribute(node, "type")
            if not type:
                type = 'main'
            repo_dir = self.get_dir(mode, file_type=type, file_object=file_objects[i])
            file_name = self._get_file_name(node)
            file_path = "%s/%s" % (repo_dir, file_name)

            paths_list = paths.get(type)
            if not paths_list:
                paths_list = []
                paths[type] = paths_list
                
            paths_list.append(file_path)


        return paths



    def get_all_sandbox_paths(self, expand_paths=False):
        return self.get_all_lib_paths("sandbox", expand_paths=expand_paths)




    def get_node_name(self):
        ''' gets the node name of the asset that is published'''
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot/file")
        if node is not None:
            return Xml.get_attribute(node, 'node_name')
        else:
            return ''

    def get_process(self):
        xml = self.get_snapshot_xml()
        node = xml.get_node("snapshot")
        return Xml.get_attribute(node, 'process')
            
    def _get_file_name(cls, node):
        '''Get the file name from the snapshot node.'''
        # get the file name
        name = Xml.get_attribute(node, "name")
        return name
    _get_file_name = classmethod(_get_file_name)

    def _get_file_code(cls, node):
        '''Get the file code from the snapshot node.'''
        # get the file name
        name = Xml.get_attribute(node, "file_code")
        return name
    _get_file_code = classmethod(_get_file_code)

    def _get_file_type(cls, node):
        '''Get the file code from the snapshot node.'''
        # get the file name
        name = Xml.get_attribute(node, "type")
        return name
    _get_file_type = classmethod(_get_file_type)

    def _get_node_name(cls, node):
        '''Get the file code from the snapshot node.'''
        # get the file name
        name = Xml.get_attribute(node, "node_name")
        return name
    _get_node_name = classmethod(_get_node_name)

    def get_use_naming_by_type(self, file_type):
        '''determines whether a given file uses naming convention to find
        it's path'''
        xml = self.get_snapshot_xml()
        if file_type.find("'") != -1:
            use_naming = xml.get_value('snapshot/file[@type="%s"]/@use_naming' % file_type)
        else:
            use_naming = xml.get_value("snapshot/file[@type='%s']/@use_naming" % file_type)
        if use_naming in ["false"]:
            return False
        else:
            return True





    def is_latest(self):
        '''determines if this snapshot is the latest or not'''
        is_latest = self.get_value("is_latest")
        if is_latest:
            return True
        else:
            return False


    def set_latest(self, commit=True, update_versionless=True):
        # Set the snapshot to be the latest and find the last latest and
        # remove it as the latest
        search_type = self.get_value("search_type")
        search_id = self.get_value("search_id")
        search_code = self.get_value("search_code")
        context = self.get_value("context")


        # clear all the is_latest (in case, for some reason, there are
        # duplicates
        search_key = self.get_search_key()
        search = Search("sthpw/snapshot")
        search.add_filter("search_type", search_type)
        search.add_filter("search_code", search_code)

        # level support (DEPRECATED)
        level_type = self.get_value("level_type")
        level_id = self.get_value("level_id")
        if level_type:
            search.add_filter("level_type", level_type)
            search.add_filter("level_id", level_id)

        search.add_filter("context", context)
        other_snapshots = search.get_sobjects()
        
        
        for other_snapshot in other_snapshots:
            # skip this "self" snapshot 
            if other_snapshot.get_search_key() == search_key:
                continue
            is_latest = other_snapshot.get_value("is_latest")
            if is_latest == True:
                other_snapshot.set_value("is_latest", False)
                other_snapshot.commit()

        # if there is a versionless, point it to this snapshot
        if update_versionless:
            self.update_versionless("latest")

        self.set_value("is_latest", True)
        if commit:
            self.commit()


    integral_trigger_added = False
    def add_integral_trigger(cls):
        # a special trigger which cannot be shut off because it 
        # is an integral part of the software: ie: is_latest
        from pyasm.search import SearchType
        from pyasm.command import Trigger

        if cls.integral_trigger_added:
            #print("WARNING: snapshot.add_integral_trigger already run")
            return

        events = ["change|sthpw/snapshot"]
        for event in events:
            trigger = SearchType.create("sthpw/trigger")
            trigger.set_value("event", event)
            trigger.set_value("mode", "same process,same transaction")
            trigger.set_value("class_name", "pyasm.command.SnapshotIsLatestTrigger")
            Trigger.append_integral_trigger(trigger, startup=True)

        cls.integral_trigger_added = True


    add_integral_trigger = classmethod(add_integral_trigger)



    def is_current(self):
        '''determines if this snapshot is current or not'''
        is_current = self.get_value("is_current")
        if is_current:
            return True
        else:
            return False




    def set_current(self, commit=True, update_versionless=True):
        # Set the snapshot to be the current and find the last current and
        # remove it as the current
        search_type = self.get_value("search_type")
        search_id = self.get_value("search_id")
        search_code = self.get_value("search_code")
        context = self.get_value("context")

        level_type = self.get_value("level_type")
        level_id = self.get_value("level_id")



        # clear all the is_current
        search_key = self.get_search_key()
        search = Search("sthpw/snapshot")
        search.add_filter("search_type", search_type)
        search.add_filter("search_code", search_code)

        # level support???
        level_type = self.get_value("level_type")
        level_id = self.get_value("level_id")
        if level_type:
            search.add_filter("level_type", level_type)
            search.add_filter("level_id", level_id)

        search.add_filter("context", context)
        other_snapshots = search.get_sobjects()
        for other_snapshot in other_snapshots:
            if other_snapshot.get_search_key() == search_key:
                continue
            is_current = other_snapshot.get_value("is_current")
            if is_current == True:
                other_snapshot.set_value("is_current", False)
                other_snapshot.commit()


       

        self.set_value("is_current", True)
        if commit:
            self.commit()

        if update_versionless:
            self.update_versionless("current")


    def get_full_snapshot_xml(self):
        '''builds a full xml snapshot xml including all metadata'''
        snapshot_xml = self.get_xml_value("snapshot")

        from pyasm.checkin import SnapshotBuilder
        builder = SnapshotBuilder(snapshot_xml)
        root = builder.get_root_node()

        version = self.get_value("version")
        Xml.set_attribute(root, "version", version )

        description = self.get_value("description")
        Xml.set_attribute(root, "description", description )


        # find the path for each file
        file_nodes = snapshot_xml.get_nodes("snapshot/file")
        for file_node in file_nodes:
            file_code = Xml.get_attribute(file_node, "file_code")
            file_object = File.get_by_code(file_code)

            checkin_dir = file_object.get_value("checkin_dir")
            source_path = file_object.get_value("source_path")

            to_name = file_object.get_full_file_name()

            file_type = Xml.get_attribute(file_node, "type")
            client_dir = self.get_client_lib_dir(file_type=file_type)
            web_dir = self.get_remote_web_dir(file_type=file_type)

            file_node = snapshot_xml.get_node("snapshot/file[@name='%s']" % to_name)
            assert file_node is not None
            Xml.set_attribute(file_node, "checkin_dir", checkin_dir )
            Xml.set_attribute(file_node, "client_dir", client_dir )
            Xml.set_attribute(file_node, "web_dir", web_dir )
            Xml.set_attribute(file_node, "source_path", source_path )

        return builder.to_string()


        
    def get_preallocated_path(self, file_type='main', file_name='', mkdir=True, protocol=None, ext='', parent=None, checkin_type=''):
        from pyasm.checkin import FileCheckin
        return FileCheckin.get_preallocated_path(self, file_type, file_name, mkdir=mkdir, protocol=protocol, ext=ext, parent=parent, checkin_type=checkin_type)




    def remove_file(self, file_type):

        xml = self.get_xml_value('snapshot')

        # remove the file
        files = self.get_files_by_type(file_type)
        for file in files:
            file_code = file.get_code()
            root = xml.get_node("snapshot")
            node = xml.get_node("snapshot/file[@file_code='%s']" % file_code)
            xml.remove_child(root, node)

            # remove the file on disk
            file_name = file.get_value("file_name")
            dir = self.get_lib_dir(file_type=file_type)
            path = "%s/%s" % (dir, file_name)
            FileUndo.remove(path)

            file.delete()

        # change the snapshot
        self.set_value('snapshot', xml.to_string())
        self.commit()



    def add_file(self, file_path, file_type='main', mode=None, create_icon=False):

        # FIXME: not sure what this mode does??? This code is taken from the
        # client api and it doesn't seem to make sense here on server code
        if mode:
            assert mode in ['move', 'copy', 'preallocate', 'upload', 'manual','inplace']

        # file_path can be an array of files:
        if type(file_path) != types.ListType:
            is_array = False
            file_paths = [file_path]
        else:
            is_array = True
            file_paths = file_path
        if type(file_type) != types.ListType:
            file_types = [file_type]
        else:
            file_types = file_type

        assert len(file_paths) == len(file_types)
        snapshot_code = self.get_code()

        if mode in ['preallocate','inplace']:
            keep_file_name = True
        else:
            keep_file_name = False


        from pyasm.checkin import FileAppendCheckin

        for i, file_path in enumerate(file_paths):
            # store the passed in path as a source path
            source_paths = []
            source_paths.append(file_path)

            file_type = file_types[i]

            file_path = file_path.replace("\\", "/")
            old_filename = os.path.basename(file_path)
            filename = File.get_filesystem_name(old_filename)

            sub_file_paths = [file_path]
            sub_file_types = [file_type]

            # if this is a file, then try to create an icon
            if create_icon and os.path.isfile(file_path):
                icon_creator = IconCreator(file_path)
                icon_creator.execute()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()
                if web_path:
                    sub_file_paths = [file_path, web_path, icon_path]
                    sub_file_types = [file_type, 'web', 'icon']
                    source_paths.append('')
                    source_paths.append('')


            checkin = FileAppendCheckin(snapshot_code, sub_file_paths, sub_file_types, keep_file_name=keep_file_name, mode=mode, source_paths=source_paths)
            checkin.execute()
            snapshot = checkin.get_snapshot()



    def add_ref_by_snapshot(self, snapshot, type='ref', tag='main', commit=True):
        from pyasm.checkin import SnapshotBuilder
        xml = self.get_xml_value("snapshot")
        builder = SnapshotBuilder(xml)
        builder.add_ref_by_snapshot(snapshot, type=type, tag=tag)
        self.set_value("snapshot", builder.to_string() )
        if commit:
            self.commit()




    ##################
    # Static Methods
    ##################
    def get_default_context():
        return "publish"
    get_default_context = staticmethod(get_default_context)


    #def get_by_sobject(sobject, context=None):
    #    return Snapshot.get_by_sobject( sobject, context )
    #get_by_sobject = staticmethod(get_by_sobject)


    def get_by_sobject(sobject, context=None, process=None, is_latest=False, order_by="timestamp desc", status=None):
        search = Search(Snapshot.SEARCH_TYPE)

        if context != None:
            search.add_filter("context", context)

        if process != None:
            search.add_filter("process", process)

        if status != None:
            search.add_filter("status", status)

        if is_latest:
            search.add_filter('is_latest', True)

        search.add_sobject_filter(sobject)
        search.add_order_by(order_by)

        return search.do_search()
    get_by_sobject = staticmethod(get_by_sobject)


    def get_by_search_type(search_type,search_id=None,context=None):

        search = Search(Snapshot.SEARCH_TYPE)
        search.add_filter("search_type", search_type)
        if context != None:
            search.add_filter("context", context)

        if search_id != None:
            if isinstance(search_id, basestring):
                search.add_filter("search_code", search_id)
            else:
                search.add_filter("search_id", search_id)


        search.add_order_by("timestamp desc")

        return search.do_search()
    get_by_search_type = staticmethod(get_by_search_type)



    def get_snapshot(search_type, search_id, context=None, version=None, \
            revision=None, show_retired=False, use_cache=True, \
            level_type=None, level_id=None, level_parent_search=True,
            process=None, skip_contexts=[]
            ):
        '''General snapshot function

        @params
        search_type: the type of sobject ie: prod/asset
        search_id: the id of the this sobject
        context: the context of view of the checkin
        version: the version of the checkin to look for
        revision: the revision of the checkin to look for
        show_retired: flag (True or False) for determining whether to include
            retired snapshots
        use_cache: determents whether to attempt to get the sobject from cache
            Set this to False is you have just checked in a file
        level_type: the sobject level at which this is checked into
        level_id: the sobject id of the level at which this is checked into
        level_parent_search: if set to True, it would try to search the snapshot of the level's parent is a level search_type, search_id are given
        skip_contexts: list of contexts to skip
        @return
        snapshot sobject
        '''
        # get from the database
        snapshot = Snapshot._get_by_version(search_type, search_id,
            context=context, version=version,
            revision=revision, show_retired=show_retired,
            use_cache=False,
            level_type=level_type, level_id=level_id,
            process=process, skip_contexts=skip_contexts
        )
        

        if snapshot or not level_parent_search:
            return snapshot
        # if no level_type is specified, then this was all that need to be
        # checked
        if not level_type:
            return None

        from .schema import Schema
        schema = Schema.get()
        if not schema:
            return None

        # get the parent of the level_type
        level_types = []
        tmp_type = level_type
        while 1:
            parent_type = schema.get_parent_type(tmp_type)
            if not parent_type:
                break
            level_types.append(parent_type)
            tmp_type = parent_type


        # go up the hierarchy one by one and get the sobjects
        level_sobjs = []
        cur_level_id = level_id
        for cur_level_type in level_types:

            parent_type = schema.get_parent_type(cur_level_type)
            if not parent_type:
                break

            search_type_obj = SearchType.get(parent_type)
            foreign_key = search_type_obj.get_foreign_key()

            search = Search(cur_level_type)
            search.add_id_filter(level_id)
            current = search.get_sobject()

            parent_code = current.get_value(foreign_key)
            parent = Search.get_by_code(parent_type, parent_code)

            parent_id = parent.get_id()

            snapshot = Snapshot._get_by_version(search_type, search_id, context=context, version=0, use_cache=False, level_type=parent_type, level_id=parent_id, skip_contexts=skip_contexts)
            if snapshot:
                return snapshot

    
        # try at the top level
        snapshot = Snapshot._get_by_version(search_type, search_id, context=context, version=0, use_cache=False, level_type=None, level_id=None, process=process, skip_contexts=skip_contexts)
        return snapshot

    get_snapshot = staticmethod(get_snapshot)



    # DEPRECATED: use get_snapshot()
    def get_by_version(search_type, search_id, context=None, version=None, \
            revision=None, show_retired=False, use_cache=True, \
            level_type=None, level_id=None, process=None):
        return Snapshot.get_snapshot(search_type, search_id, context=context,version=version, \
            revision=revision, show_retired=show_retired, use_cache=use_cache, \
            level_type=level_type, level_id=level_id, process=None)
    get_by_version = staticmethod(get_by_version)


    def _get_by_version(search_type, search_id, context=None, version=None, \
            revision=None, show_retired=False, use_cache=True, \
            level_type=None, level_id=None, process=None, skip_contexts=[]):
        '''General snapshot function

        @params
        search_type: the type of sobject ie: prod/asset
        search_id: the id of the this sobject
        context: the context of view of the checkin
        version: the version of the checkin to look for: 0, -1, max, None
        revision: the revision of the checkin to look for: 0, -1, None
        show_retired: flag (True or False) for determining whether to include
            retired snapshots
        use_cache: determents whether to attempt to get the sobject from cache
            Set this to False is you have just checked in a file
        level_type: the sobject level at which this is checked into
        level_id: the sobject id of the level at which this is checked into
        skip_contexts: list of contexts to skip

        @return
        snapshot sobject
        '''
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_filter("search_type", search_type)

        # NOTE: Backwards compatibility with search_id
        if isinstance(search_id, basestring):
            if not isinstance(search_id, list):
                search_code = search_id
                search.add_filter("search_code", search_code)
            else:
                search.add_filters("search_code", search_code)
        else:
            if not isinstance(search_id, list):
                search.add_filter("search_id", search_id)
            else:
                search.add_filters("search_id", search_id)


        # if a level_type and level_id is specified, then the search
        # is considerably more complicated
        if level_type and level_id:
            # first look for a checkin with the parent
            search.add_filter("level_type", level_type)
            search.add_filter("level_id", level_id)
        else:
            search.add_where('"level_type" is NULL')
            search.add_where('"level_id" is NULL')

        # version of zero is current
        if version in [0, '0']:
            search.add_filter("is_current", True)

        # use caching to speed up redundant searches
        key = "%s:%s" % ( search_type, search_id )
        
        if level_type and level_id:
            key = "%s:%s:%s" % (key, level_type, level_id )
        if process != None:
            if isinstance(process, list):
                search.add_enum_order_by("process", process)
                search.add_filters("process", process)
            else:
                search.add_filter("process", process)
            key = '%s:process=%s' %(key, process)
        if context not in [None, '']:
            search.add_filter("context", context)
            key = '%s:%s' %(key, context)
        if skip_contexts:
            search.add_filters('context',skip_contexts, op='not in')
            key = '%s:!%s' %(key, skip_contexts)

        if version not in [None, '', -1, "-1", 0, "0", "max"]:
            search.add_filter("version", version)
            key = '%s:%s' %(key, version)
        elif version in [-1, '-1']:
            search.add_filter('is_latest', True)
            key = '%s:is_latest' %(key)


        if revision in [ None, 0 ]:
            search.add_filter('revision', 0)
        elif revision not in [-1, "-1"]:
            search.add_filter("revision", revision)
            key = '%s:%s' %(key, revision)
        elif revision in [-1, '-1']: 
            # Avoid filtering is_current or is_latest for revision as they 
            # are sort of meant for version, but shared by revision.
            # Latest revision of a version does not necessarily have is_latest set to True
            pass    
            #search.add_filter('is_latest', True)
       

        search.set_show_retired(show_retired)

        # order backwards
        search.add_order_by("version desc")
        search.add_order_by("revision desc")
        search.add_order_by("timestamp desc")

        if not isinstance(search_id, list):
            # only cache if search_id is not a list
            if use_cache:
                sobject = Snapshot.get_cached_obj(key)
            else:
                sobject = None

            dict = {}
            if not sobject:
                sobject = search.get_sobject()
                dict = Snapshot.get_cache_dict()
                if sobject:
                    dict[key] = sobject
                else:
                    # to record that this key does not return anything
                    dict[key] = '__NONE__'
            elif sobject == '__NONE__':
                return None

            return sobject
        else:
            return search.get_sobjects()
        
    _get_by_version = staticmethod(_get_by_version)




    def get_latest(search_type, search_id, context=None, use_cache=True, \
            level_type=None, level_id=None, show_retired=False, \
            process=None, skip_contexts=[]):
        snapshot = Snapshot.get_snapshot(search_type, search_id, context, use_cache=use_cache, level_type=level_type, level_id=level_id, show_retired=show_retired, version='-1', revision='-1', level_parent_search=False, process=process, skip_contexts=skip_contexts)
        return snapshot
    get_latest = staticmethod(get_latest)



    def get_latest_by_sobject(sobject, context=None, show_retired=False, \
            process=None, skip_contexts=[]):
        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code")
        if not search_code:
            search_code = sobject.get_id()
        snapshot = Snapshot.get_latest(search_type, search_code, \
                context=context, show_retired=show_retired, process=process, \
                skip_contexts=skip_contexts
        )
        return snapshot
    get_latest_by_sobject = staticmethod(get_latest_by_sobject)



    def get_versionless(cls, search_type, search_id, context, mode='current', create=True, snapshot_type='versionless', process=None, commit=True):
        '''the versionless is assumed to exist if asked for, unless create = False. it is then just querying'''

        assert mode in ['current','latest']

        from pyasm.biz import Project
        search_type = Project.get_full_search_type(search_type)
        if mode == 'latest':
            version = -1
        else:
            version = 0

        # just a simple query
        if not create:
            search = Search("sthpw/snapshot")
            search.add_filter("search_type", search_type)

            if isinstance(search_id, int):
                search.add_filter("search_id", search_id)
            else:
                search.add_filter("search_code", search_id)

            if process:
                search.add_filter("process", process)

            search.add_filter("context", context)
            # we can't search by this since the versionless snapshot 
            # inherits the snapshot_type of the originating snapshot
            #search.add_filter("snapshot_type", 'versionless')
            search.add_filter("version", version)

            snapshot = search.get_sobject()
            return snapshot

        search = Search("sthpw/snapshot")
        search.add_filter("search_type", search_type)
        if isinstance(search_id, int):
            search.add_filter("search_id", search_id)
        else:
            search.add_filter("search_code", search_id)
        
        if process:
            search.add_filter("process", process)
        search.add_filter("context", context)


        search.add_filter("version", version)
        snapshot = search.get_sobject()

        if not snapshot:
            if isinstance(search_id, int):
                sobject = Search.get_by_id(search_type, search_id)
            else:
                sobject = Search.get_by_code(search_type, search_id)

            # should be passed in
            #snapshot_type = 'versionless'
            snapshot = Snapshot.create(sobject, snapshot_type, context, column="snapshot", description="Versionless", is_current=False, is_latest=False, commit=False, process=process)
            snapshot.set_value("version", version)

            if commit:
                snapshot.commit()
        return snapshot
    get_versionless = classmethod(get_versionless)





    def get_by_sobjects(cls, sobjects, context=None, is_latest=False, is_current=False, show_retired=False, return_dict=False, version=None, process=None, status=None ):
        '''NOTE: if context=None, is_latest=True, the result could be more than 1 since there can be multiple 
        is_latest per parent given several contexts. use return_dict=True in that case to get the latest for each subgroup
        of snapshots.
        @param:
            sobjects - list of sobjects
        @keyparam:
            context - snapshot context
            is_latest - is latest for this context
            is_current - is current for this context
            show_retired - deprecated
            return_dict - return a dictonary of latest per search key. useful when context = None '''
        if not sobjects:
            return []

        search_type = sobjects[0].get_search_type()

        # quickly go through the sobjects to determine if their search types
        # are the same
        multi_stypes = False
        for sobject in sobjects:
            if sobject.get_search_type() != search_type:
                multi_stypes = True
                break


        search = Search("sthpw/snapshot")

        # assume they are of the same type
        if not multi_stypes:
            search.add_filter('search_type', search_type)
            has_code = SearchType.column_exists(search_type, "code")
            if not has_code:
                search_ids = []
                use_id = True
                for x in sobjects:
                    id = x.get_id()
                    try:
                        id = int(id)
                    except:
                        use_id  = False
                    search_ids.append(id)
                if use_id:
                    search.add_filters('search_id', search_ids)
                else:
                    search.add_filters('search_code', search_ids)
            else:
                search_codes = [x.get_value("code") for x in sobjects if x]
                search.add_filters('search_code', search_codes)
        else:
            # FIXME: why doesn't the ops work here?
            filters = []
            for sobject in sobjects:
                search_type = sobject.get_search_type()
                has_code = SearchType.column_exists(search_type, "code")
                if not has_code:
                    search_id = sobject.get_id()
                    filters.append("search_type = '%s' and search_id = '%s'" % (search_type, search_id))
                else:
                    search_code = sobject.get_value("code")
                    filters.append("search_type = '%s' and search_code = '%s'" % (search_type, search_code))
            search.add_where(" or ".join(filters))

        if context:
            if isinstance(context, list):
                search.add_filters("context", context)
            else:
                search.add_filter("context", context)
        if process:
            if isinstance(process, list):
                search.add_filters("process", process)
            else:
                search.add_filter("process", process)

        if status:
            if isinstance(status, list):
                search.add_filters("status", status)
            else:
                search.add_filter("status", status)




        if is_latest:
            search.add_filter("is_latest", True)
        if is_current:
            search.add_filter("is_current", True)
        elif version:
            search.add_filter("version", version)

        if show_retired:
            raise Exception("ERROR: Unsupported show retired flag")

        if not return_dict:
            search.add_order_by("search_code")
            search.add_order_by("version desc")


        snapshots = search.get_sobjects()

        # sort them like timestamp desc if returning dict
        if return_dict:
            # dictioary to be returned
            data = {}
            # account for possible multiple is_latest     
            for snapshot in snapshots:
                search_key = snapshot.get_parent_search_key()
                snapshot_dict = data.get(search_key)
                if not snapshot_dict:
                    data[search_key] = {snapshot.get_value('timestamp'): snapshot}
                else:
                    snapshot_dict[snapshot.get_value('timestamp')] = snapshot

            # sort reversely to get the latest for each search key
            for key, value in data.items():
                latest_snap_list = Common.sort_dict(value, reverse=True)
                data[key] = list(latest_snap_list)[0]
            
            return data


        return snapshots
 
    get_by_sobjects = classmethod(get_by_sobjects)





    def get_current(search_type, search_code, context=None, level_type=None, level_id=None, return_search=False):
        '''There should only be one current for each context'''
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_filter("search_type", search_type)

        # search on code or id depending on the type
        if isinstance(search_code, basestring):
            search.add_filter("search_code", search_code)
        else:
            search_id = search_code
            search.add_filter("search_id", search_id)

        if context:
            search.add_filter("context", context)

        search.add_order_by("version desc")

        if level_type:
            search.add_filter("level_type", level_type)
            search.add_filter("level_id", level_id)

        search.add_filter("is_current", True)
        if return_search:
            return search

        current = search.get_sobject()
        return current

    get_current = staticmethod(get_current)


    def get_current_by_sobject(sobject, context=None):
        search_type = sobject.get_search_type()
        code_exists = SearchType.column_exists(search_type, "code")
        if code_exists:
            search_code = sobject.get_value("code")
        else:
            search_code = sobject.get_id()

        snapshot = Snapshot.get_current(search_type, search_code, context)
        return snapshot
    get_current_by_sobject = staticmethod(get_current_by_sobject)

    def get_all_current_by_sobject(sobject):
        '''get all the current snapshots without specifying context'''
        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code")

        snapshot_search = Snapshot.get_current(search_type, search_code, return_search=True)
        snapshot_search.add_group_aggregate_filter(['search_type','search_id','context'], "version")
        snapshots = snapshot_search.get_sobjects()
        return snapshots

    get_all_current_by_sobject = staticmethod(get_all_current_by_sobject)




    def get_contexts(search_type, search_code):
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_filter("search_type", search_type)

        code_exists = SearchType.column_exists(search_type, "code")
        if code_exists:
            search.add_filter("search_code", search_code)
        else:
            search.add_filter("search_id", search_code)


        search.add_op("begin")
        search.add_filter("is_latest", True)
        search.add_filter("is_current", True)
        search.add_op("or")
        #search.add_where("(\"is_latest\" = '1' or \"is_current\" = '1')")
        snapshots = search.get_sobjects()

        contexts = []
        for snapshot in snapshots:
            context = snapshot.get_value("context")


            # FIXME: make this a flag
            # only show contexts without subcontexts
            if context.find("/") != '-1':
                parts = context.split("/")
                context = parts[0]



            if context not in contexts:
                contexts.append(context)


        return contexts

    get_contexts = staticmethod(get_contexts)



    def get_by_path(path):
        file_object = File.get_by_path(path)
        if not file_object:
            return None
        snapshot = file_object.get_parent()
        return snapshot
    get_by_path = staticmethod(get_by_path)



    def is_locked(sobject, context):
        '''determines if a context is locked'''

        # get all of the snapshots for this sobject
        search = Search("sthpw/snapshot")
        search.add_parent_filter(sobject)
        search.add_filter("context", context)
        # lock information is always on the version 1!!!!
        search.add_filter("version", 1)
        snapshot = search.get_sobject()

        if snapshot:
            lock_login = snapshot.get_value("lock_login")
            lock_date = snapshot.get_value("lock_date")
        
            if lock_login:
                return True

        return False

    is_locked = staticmethod(is_locked)


    def lock(cls, sobject, context):
        # get all of the snapshots for this sobject
        search = Search("sthpw/snapshot")
        search.add_parent_filter(sobject)
        search.add_filter("context", context)
        # lock information is always on the version 1!!!!
        search.add_filter("version", 1)
        snapshot = search.get_sobject()

        # if there are no snapshots then it means nothing to lock ??
        # Besides, presently, there is nothing to store lock information in
        if not snapshot:
            return

        login = Environment.get_user_name()
        snapshot.set_value("lock_login", login)
        snapshot.set_now("lock_date")
        snapshot.commit()
    lock = classmethod(lock)


    def unlock(cls, sobject, context):
        # get all of the snapshots for this sobject
        search = Search("sthpw/snapshot")
        search.add_parent_filter(sobject)
        search.add_filter("context", context)
        # lock information is always on the version 1!!!!
        search.add_filter("version", 1)
        snapshot = search.get_sobject()

        # if there are no snapshots then it means nothing to lock ??
        # Besides, presently, there is nothing to store lock information in
        if not snapshot:
            return

        login = Environment.get_user_name()
        snapshot.set_value("lock_login", "NULL", quoted=False)
        snapshot.set_value("lock_date", "NULL", quoted=False)
        snapshot.commit()
    unlock = classmethod(unlock)





    def create(sobject, snapshot_type, context, column="snapshot", \
            description="No description", \
            snapshot_data=None, is_current=None, is_revision=False, \
            level_type=None, level_id=None, commit=True, is_latest=True,
            is_synced=True, process=None, version=None, triggers=True,
            set_booleans=True):

        # Provide a default empty snapshot definition
        if snapshot_data == None:
            if sobject.has_value(column):
                snapshot_data = sobject.get_value(column)
            if not snapshot_data:
                snapshot_data = "<snapshot/>"


        if not process:
            # if not specified ...
            # by default process is the first element of the context
            context_parts = context.split("/")
            process = context_parts[0]

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        search_code = sobject.get_value("code", no_exception=True)
        # temp var
        search_combo = search_code
        if not search_code:
            search_combo = search_id
        """
        rev = None
        if is_revision:
            rev = -1
        """
        # we are always interested in revision = -1 when finding the last one
        rev = -1
        # to find the version number, we have to find the highest number
        # of a particular snapshot
        old_snapshot = Snapshot._get_by_version(search_type, search_combo, context, version="max", revision=rev, use_cache=False, level_type=level_type, level_id=level_id, show_retired=True)
        # have to clear the cache here, because after it is created
        # it shouldn't be None anymore
        if not old_snapshot:
            Snapshot.clear_cache()

        # handle revisions, with no previous version, revision starts at 1
        revision = 1
        if old_snapshot and is_revision:
            revision = old_snapshot.get_value("revision", no_exception=True)
            if revision:
                revision = int(revision) + 1
            else:
                revision = 1

            # keep the same version
            version = old_snapshot.get_value("version")
            if version:
                version = int(version)
            else:
                version = 1
        else:
            if version != None:
                # force the version
                pass
            elif old_snapshot:
                old_version = old_snapshot.get_value("version")
                # in case only the versionless snapshot is left behind
                if old_version == -1:
                    old_version = 0
                version = int(old_version) + 1
            else:
                version = 1

        snapshot = Snapshot(Snapshot.SEARCH_TYPE)
        snapshot.set_value("search_type", search_type )
        if SearchType.column_exists("sthpw/snapshot", "search_id"):
            if isinstance(search_id, int):
                snapshot.set_value("search_id", search_id )

        snapshot.set_value("search_code", search_code )
        snapshot.set_value("column_name", column )
        snapshot.set_value("snapshot", snapshot_data )
        snapshot.set_value("snapshot_type", snapshot_type )

        snapshot.set_value("version", version)

        
        if is_revision:
            snapshot.set_value("revision", revision)

        # add level type and level_id
        if level_type:
            assert level_id
            snapshot.set_value("level_type", level_type)
            snapshot.set_value("level_id", level_id)


        # add the description
        if description == None or description == "":
            if version == 1:
                description = "Initial insert"
            else:
                description = "No comment"
        snapshot.set_value("description", description )

        # get the login
        security = Environment.get_security()
        login_name = security.get_login().get_login()
        snapshot.set_value("login", login_name)

        # extract the timestamp from the snapshot
        snapshot_xml = Xml()
        snapshot_xml.read_string(snapshot_data)
        #snapshot.set_value("timestamp", timestamp )

        snapshot.set_value("context", context )
        snapshot.set_value("process", process )
        snapshot.set_value("project_code", sobject.get_project_code())

        snapshot.set_value("is_synced", is_synced)

        server = Config.get_value("install", "server")
        if server:
            snapshot.set_value("server", server)



        # if commit is false, then just return the snapshot.  Do not run
        # any of the latest or current code.
        if not commit:
            return snapshot
       
        # if this is a simple snapshot create like API method create_snapshot(),
        # it defaults to running set_boolean
        if set_booleans:
            Snapshot.set_booleans(sobject, snapshot, is_latest=is_latest, is_current=is_current)

        snapshot.commit(triggers=triggers)

        return snapshot

    create = staticmethod(create)

    def set_booleans(sobject, snapshot, is_latest=True, is_current=None):
        '''Set the is_latest and is_current booleans. 
           This method should not contain any snapshot.commit() since this is an in-between step'''

        # set the new snapshot as the current 
        # (must be done after setting context)
        if is_latest:
            if is_current != None:
                if is_current:
                    #snapshot.set_current(commit=False)
                    snapshot.set_value("is_current", True)
                else:
                    pass
            elif sobject.has_auto_current():
                #snapshot.set_current(commit=False)
                snapshot.set_value("is_current", True)
            else:
                # otherwise only set current if there is no current
                current = Snapshot.get_current(search_type, search_id, context)
                if not current:
                    #snapshot.set_current(commit=False)
                    snapshot.set_value("is_current", True)

        if is_latest:
            snapshot.set_value("is_latest", True)
        elif is_latest == False:
            snapshot.set_value("is_latest", False)

        return snapshot

    set_booleans = staticmethod(set_booleans)





    def update_versionless(self, snapshot_mode='current', sobject=None, checkin_type=None, naming=None):

        if self.get_value("context") == "icon":
            return


        # NOTE: no triggers are run on this operation (for performance reasons)

        if not checkin_type:
            # find out from the snapshot itself
            snapshot_xml = self.get_snapshot_xml()
            checkin_type = Xml.get_value(snapshot_xml, "snapshot/@checkin_type")

        # by default, use strict
        if not checkin_type:
            checkin_type = "strict"

        if not sobject:
            sobject = self.get_parent()
        # if there is no parent to this snapshot, then it's not possible
        # to update the versionless
        if not sobject:
            return

        # check to see if there is already versionless defined
        from pyasm.biz import Naming
        has_versionless = Naming.has_versionless(sobject, self, versionless=snapshot_mode)

        if checkin_type == 'strict' and not has_versionless:
            return

        # with auto mode, don't use current latest by default ...
        # unless there is a naming defined for it.
        if snapshot_mode == 'current' and not has_versionless:
            return


        # if the mode is current then return if this isn't a current snapshot
        if snapshot_mode == 'current':
            is_current = self.get_value("is_current")
            if not is_current:
                return
        # if the mode is latest then return if this isn't a latest snapshot
        elif snapshot_mode == 'latest':
            is_latest = self.get_value("is_latest")
            if not is_latest:
                return

        
        
        # if os is linux, it should be symbolic link as a default
        if os.name == 'posix':
            versionless_mode = 'symlink'
        else:
            versionless_mode = 'copy'
        # overrides
        from pyasm.prod.biz import ProdSetting
        proj_setting = ProdSetting.get_value_by_key('versionless_mode')
        if proj_setting:
            versionless_mode = proj_setting
        else:
            config_setting = Config.get_value('checkin', 'versionless_mode')
            if config_setting:
                versionless_mode = config_setting





        snapshot_xml = self.get_xml_value("snapshot")
        context = self.get_value("context")

        # get the versionless snapshot
        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code", no_exception=True)
        search_id = sobject.get_id()



        # this makes it work with 3d App loader, but it removes the attribute that it's a versionless type
        snapshot_type = self.get_value('snapshot_type')

        # Get the versionless snapshot.  This is used as a template to build
        # the next snapshot definition. 
        if search_code:
            versionless = Snapshot.get_versionless(search_type, search_code, context, mode=snapshot_mode, snapshot_type=snapshot_type, commit=False)
        elif search_id:
            versionless = Snapshot.get_versionless(search_type, search_id, context, mode=snapshot_mode, snapshot_type=snapshot_type, commit=False)

        v_snapshot_xml = versionless.get_xml_value("snapshot")

        #assert versionless.get_id() != -1


        # compare the two snapshots to see if anything has changed
        # FIXME: this is a rather weak comparison, but will suffice for most
        # applications for now
        nodes = snapshot_xml.get_nodes("snapshot/*")
        v_nodes = v_snapshot_xml.get_nodes("snapshot/*")

        # delete the old file objects
        file_objects = versionless.get_all_file_objects()
        for file_object in file_objects:
            file_object.delete()


        # create a new xml for the versionless
        from pyasm.checkin import SnapshotBuilder
        old_builder = SnapshotBuilder(snapshot_xml)
        old_root = old_builder.get_root_node()
        process = Xml.get_attribute(old_root, 'process')
        builder = SnapshotBuilder()
        if process:
            builder.add_root_attr('process', process)


        builder.add_root_attr('ref_snapshot_code', self.get_code() )
        
        file_objects = []

        paths = {}
        rejected  = False
        for node in nodes:
            node_name = Xml.get_node_name(node)

            if node_name in  ["ref", "input_ref"]:
                builder.copy_node(node, None)
                continue



            file_name = self._get_file_name(node)

            file_code = self._get_file_code(node)
            file_type = self._get_file_type(node)
            node_name = self._get_node_name(node)


            path_by_type = self.get_path_by_type(file_type)

            orig_file_object = File.get_by_code(file_code)

            if not orig_file_object:
                print("WARNING: cannot find orig_file_object [%s]" % file_code)
                continue

            src_path = orig_file_object.get_value('source_path')
            src_file_name = os.path.basename(src_path)

            base_type = orig_file_object.get_value('base_type')
            st_size = orig_file_object.get_value('st_size')

            # create a new file object
            file_object = SearchType.create("sthpw/file")
            file_objects.append(file_object)
            file_object.set_value("search_type", sobject.get_search_type() )

            
            if search_code:
                file_object.set_value("search_code", search_code )
            if search_id and isinstance(search_id, int):
                file_object.set_value("search_id", search_id )

            file_object.set_value("snapshot_code", versionless.get_code() )
            file_object.set_value("type", file_type)
            file_object.set_value("base_type", base_type)
            if st_size:
                file_object.set_value("st_size", st_size)

            if base_type == 'directory':
                ext = None
            else:
                base, ext = os.path.splitext(src_file_name)

            # use src file name
            if src_file_name:
                file_object.set_value("file_name", src_file_name)
            else: # otherwise make use of the updated file name from the original file object
                file_object.set_value("file_name", file_name)


            # get the path from the reference file_object
            ref_file_object = self.get_file_by_type(file_type)
            lib_dir = self.get_lib_dir(file_type=file_type, file_object=ref_file_object)
            file_path = "%s/%s" % (lib_dir, file_name)
            if not os.path.exists(file_path):
                raise Exception("Cannot create versionless.  Referenced path [%s] from file_object [%s] does not exist" % (file_path, file_object.get_code()))


            # build the file name
            # if there is a versionless naming, use it
            if checkin_type == 'strict' or has_versionless:
                file_naming = Project.get_file_naming()
                file_naming.set_sobject(sobject)
                file_naming.set_snapshot(versionless)
                file_naming.set_file_object(file_object)
                file_naming.set_ext(ext)
                file_name = file_naming.get_file_name()

                dir_naming = None
            else:
                # These naming conventions are for the versionless file, not the checked in file
                
                from pyasm.biz import FileNaming
                file_expr = FileNaming.VERSIONLESS_EXPR
                
                if not naming and not rejected and not has_versionless and checkin_type == 'auto':
                   
                    naming = Naming.get(sobject, self, file_path=file_path)
                    # reject the naming if it is meant for strict
                    if naming and naming.get_value('checkin_type') == 'strict':
                        naming = None
                        rejected = True
            


                if naming:
                    file_expr = naming.get_value('file_naming')
                    # case-insensitive v or V are considered
                    file_expr = re.sub(r'(?i)_v{version}|_v{snapshot.version}', '' , file_expr)
                    

                
                # with checkin_type = auto ..
                file_naming = FileNaming(naming_expr=file_expr)
                file_naming.set_sobject(sobject)
                file_naming.set_snapshot(versionless)
                file_naming.set_file_object(file_object)
                file_naming.set_ext(ext)
                file_name = file_naming.get_file_name()


                # this expects the naming expr
                has_code = sobject.get_value("code", no_exception=True)

                # break apart the context
                parts = context.split("/")
                if len(parts) > 2:
                    subdir = "/".join( parts[1:-1] )
                else:
                    subdir = ""

                if naming:
                    dir_naming = naming.get_value('dir_naming')
                    dir_naming = dir_naming.replace('.versions', '')
                    if subdir:
                        dir_naming = '%s/%s'%(dir_naming, subdir)

                else:
                    # build dir_naming
                    parts = []
                    parts.append("{project.code}")
                    parts.append("{search_type.table_name}")
                    if has_code:
                        parts.append("{code}")
                    else:
                        parts.append("{id}")
                    parts.append("{snapshot.process}")

                    # versionless is not in the version dir
                    #parts.append(".versions")

                    if subdir:
                        parts.append(subdir)

                    dir_naming = "/".join(parts)


            
            # reset the versionless file sobject to the new name
            file_object.set_value("file_name", file_name)

            # commit first to get the file_code for builder
            file_object.commit(triggers="none")

            info = {'type': file_type }
              
            if node_name:
                info['node_name'] = node_name
            builder.add_file(file_object, info=info)


            # build the directory
            new_lib_dir = Project.get_project_lib_dir(sobject, versionless, file_object=file_object, file_type=file_type, dir_naming=dir_naming)

            new_path = "%s/%s" % (new_lib_dir, file_name)
            new_relative_dir = Project.get_project_relative_dir(sobject, versionless, file_object=file_object, file_type=file_type, dir_naming=dir_naming)

            file_object.set_value("checkin_dir", new_lib_dir)
            file_object.set_value("relative_dir", new_relative_dir)

            # commit again
            file_object.commit(triggers="none")

            FileUndo.symlink(file_path, new_path, mode=versionless_mode)


        versionless.set_value("snapshot", builder.to_string())
        
        versionless.commit(triggers="none")

        versionless_code = versionless.get_code()

        for file_object in file_objects:
            file_object.set_value("snapshot_code", versionless_code)
            # add commit again
            file_object.commit()




