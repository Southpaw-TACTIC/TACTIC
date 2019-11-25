###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


# ALPHA: do not use

__all__ = ['CGApp']

import types

from tactic_client_lib import TacticServerStub


class CGAppException(Exception):
    pass
    


class CGApp(object):

    def __init__(self):

        # need to set up the environment (don't fight it for now!)
        from pyasm.application.common import BaseAppInfo

        from pyasm.application.common import AppEnvironment
        from pyasm.application.maya import Maya85
        self.env = AppEnvironment.get()
        self.env.set_tmpdir("C:/Temp")

        self.app = Maya85()
        self.env.set_app(self.app)


    #
    # High level methods
    #
    def checkin(self, tactic_node, search_key, context):
        '''Standard checkin mechanism.  This is a sample checkin mechanism
        that is full featured enough to handle many situations.

        @params:
          tactic_node: the tactic node to be checkedin
          search_key: the search key to check into
          context: the context to check into

        @return
          snapshot: a dictionary representing the final snapshot
          
        
        '''
        server = TacticServerStub.get()

        # verify that this is not a reference!!!


        # create a snapshot
        snapshot = server.create_snapshot(search_key, context)

        # find all of the dependencies
        dependent_nodes = self.get_dependent_nodes(tactic_node)
        for node in dependent_nodes:
            # find out if there is a node there is a file associated with
            # this tactic node
            files = self.get_dependent_references(node)
            print(files)


        # update the tactic node with the latest snapshot data.  Also, update
        # the tactic node name as it likely has changed
        node_data = self.set_introspect_data(tactic_node, snapshot)
        tactic_node = node_data.get_app_node_name()


        # add the files to the snapshot
        handler = BaseFileExtractionHandler(tactic_node)
        paths = handler.execute()
        #paths = self.extract_to_files(top_node)
        for path in paths:
            print("path: ", path)
            server.add_file(snapshot.get("code"), path, mode='upload')

        return snapshot


    def load(self, search_key, context, version=-1, file_type='main', mode='reference',namespace=''):
        '''Generic loading function used by TACTIC interface by default

        @params:
        search_key: the search key of the sobject to be loaded
        context: the context of the snapshot to be loaded
        version: the version of the snapshot to be loaded
        file_type: the specific file in the snapshot to be loaded

        mode: reference|import|open: the mode in which to bring the file in
        
        
        '''
        server = TacticServerStub.get()

        # FIXME: do we really need to make 2 calls?
        snapshot = server.get_snapshot(search_key, context=context, version=version)
        if not snapshot:
            raise CGAppException("No snapshot found for [%s]" % search_key)


        paths = server.get_paths(search_key, context, version, file_type)
        web_paths = paths.get("web_paths")

        for path in web_paths:
            to_path = self.download(path)
            self.load_file(to_path, namespace=namespace, mode=mode)


        # FIXME: if the instance already exists, it will be auto renmaed by
        # the application ... this gets tricky to discover
        snapshot_code = snapshot.get('code')
        if namespace:
            tactic_node = "%s:tactic_%s" % (namespace, snapshot_code)
        else:
            tactic_node = "tactic_%s" % snapshot_code
        return tactic_node



    #
    # Node methods
    #


    def get_tactic_nodes(self, top_node=None):
        return self.app.get_tactic_nodes()


    def is_tactic_node(self, node):
        '''determines if a node is a tactic node or not

        @param
        node_name: name of the maya node

        @return
        True/False

        '''
        return self.app.is_tactic_node(node)




    #
    # Dependency methods
    #
    def get_dependent_nodes(self, tactic_node):
        '''find all of the dependent TACTIC nodes'''
        return ['chr001']

    def get_dependent_references(self, tactic_node):
        '''determine all of the files that are part of this tactic_node'''
        return ['file1.ma', 'file2.ma']


    def is_node_repo(self, tactic_node):
        '''determines is a TACTIC node is local or from the repo'''
        pass

    def get_dependent_textures(self, tactic_node):
        '''determine all of the files that are part of this tactic_node'''
        return {
            'file1': '/home/apache/whatever.png',
            'file2': '/home/apache/whatever2.png'
        }


    #
    # Loading methods
    #
    def load_file(self, path, mode='reference', namespace=''):
        '''Load a file in the session
        
        @params:
          path: the full path of the file to be loaded into the session
          mode: reference|import|load
          namespace:
        '''
        if mode == 'reference':
            self.app.import_reference(path, namespace=namespace)
        elif mode == 'load':
            self.app.load(path)
        elif mode == 'import':
            self.app.import_file(path, namespace=namespace)
        else:
            raise CGAppException("Load mode [%s] not supported" % mode)



    #
    # Extraction methods
    #
    def extract_to_files(self, tactic_node, dir=None):

        # first get the node to be extracted
        top_node = self.app.get_parent( tactic_node )
        if not top_node:
            top_node = tactic_node

        tmp_dir = self.env.get_tmpdir()
        file_type = 'mayaAscii'
        preserve_ref = True

        context = 'temp_context'    # Should not be necessary
        filename = '%s.ma' % tactic_node
        instance = 'whatever'       # Should not be necessary


        # use the old export node method to extract
        path = self.app.export_node(top_node, context, tmp_dir,
            type=file_type, preserve_ref=preserve_ref, filename=filename,
            instance=instance)

        return [path]


    #
    # Introspect methods
    #
    def introspect(self):
        '''introspects the session and updates the database'''
        pass

    def set_introspect_data(self, tactic_node, snapshot):
        '''adds intropection data to a tactic node
        
        @params:
          tactic_node: the node in the maya session to add the
            introspection data
          snapshot: the snapshot from which to add the information

        @return
        NodeData object
        '''
        #if not self.is_tactic_node(tactic_node):
        #    raise CGAppException("Node [%s] is not a Tactic node" % tactic_node)

        # add the attr if it doesn't exist
        #self.app.add_attr(tactic_node, "tacticNodeData")

        # rename to tactic_<snapshot_code>
        snapshot_code = snapshot.get("code")
        new_tactic_node = "tactic_%s" % snapshot_code

        tactic_node = self.app.rename_node(tactic_node, new_tactic_node)
        assert tactic_node == new_tactic_node

        snapshot_code = snapshot.get('code')

        from pyasm.application.common import NodeData
        node_data = NodeData(tactic_node, self.app)
        node_data.create()
        node_data.set_attr("snapshot", "code", snapshot_code)
        node_data.commit()

        return node_data





    #
    # Common methods
    #
    def download(self, url, to_dir=''):
        return self.env.download(url, to_dir)





class BaseFileExtractionHandler(object):

    def __init__(self, tactic_node):
        self.tactic_node = tactic_node

        from pyasm.application.common import AppEnvironment
        self.env = AppEnvironment.get()
        self.app = self.env.get_app()

    def execute(self):

        # first get the node to be extracted
        top_node = self.app.get_parent( self.tactic_node )
        if not top_node:
            top_node = self.tactic_node

        tmp_dir = self.env.get_tmpdir()
        file_type = 'mayaAscii'
        preserve_ref = True

        context = 'temp_context'    # Should not be necessary
        filename = '%s.ma' % self.tactic_node
        instance = 'whatever'       # Should not be necessary


        # use the old export node method to extract
        path = self.app.export_node(top_node, context, tmp_dir,
            type=file_type, preserve_ref=preserve_ref, filename=filename,
            instance=instance)

        return [path]





