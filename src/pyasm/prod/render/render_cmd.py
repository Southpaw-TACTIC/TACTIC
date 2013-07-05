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

__all__ = ["RenderException", "MayaAssetRenderCmd", "MayaRenderCmd"]

from pyasm.command import *
from pyasm.search import *
from pyasm.prod.load import *
from pyasm.prod.biz import FrameRange
from pyasm.checkin import SnapshotBuilder, SnapshotCheckin, FileCheckin

from render_context import *


class RenderException(Exception):
    pass




class MayaAssetRenderCmd(Command):
    '''Render the latest checkin of an sobject'''

    def set_project(my, project):
        my.project = project

    def set_search_key(my, search_key):
        my.search_key = search_key


    def get_title(my):
        return "Asset Render"


    def execute(my):

        SearchType.set_project(my.project)

        sobject = Search.get_by_search_key(my.search_key)

        # set the render policy
        render_policy = MayaBeautyRenderPolicy()

        # set up the render
        render_context = AssetRenderContext(sobject)
        render_context.set_policy(render_policy)

        # execute the render
        render = MayaRenderCmd()
        render.set_render_context(render_context)

        render.execute()





class MayaRenderCmd(Command):
    '''Very basic render command that renders a snapshot'''

    def __init__(my):
        super(MayaRenderCmd, my).__init__()
        my.render_context = None


    def get_title(my):
        return "Maya Render"


    def set_render_context(my, render_context):
        my.render_context = render_context



    def execute(my):

        assert my.render_context


        # get the build file
        execute_xml = my.build_maya_file()

        # write xml to a temp file
        render_dir = my.render_context.get_render_dir()
        path = "%s/maya_render" % render_dir
        file = open(path, 'w')
        file.write(execute_xml)
        file.close()

        # Run the result through the maya builder.
        # This is done in a separate
        # process to avoid having maya session in web app
        ticket = Environment.get_security().get_ticket_key()
        from pyasm.application.maya.maya_builder_exec import maya_builder_exec
        maya_builder_exec(path, ticket)

        # get the render command and execute
        render_command = my.get_render_command()
        print render_command
        os.system(render_command)

        my.convert_images()
        #my.checkin_render()



    def build_maya_file(my):

        # get the necessary info from the render context
        snapshot = my.render_context.get_snapshot()
        snapshot_xml = my.render_context.get_snapshot_xml()
        shot = my.render_context.get_shot()
        context = my.render_context.get_context()
        render_dir = my.render_context.get_render_dir()


        # set up the loader context
        loader_context = ProdLoaderContext()
        loader_context.set_options("proxy=no|textures=high|connection=server_fs")
        loader_context.set_context(context)
        loader_context.set_shot(shot)

        # build the execute xml
        loader = MayaGroupLoaderCmd()
        loader.set_snapshot(snapshot)
        loader.set_snapshot_xml(snapshot_xml)
        loader.set_loader_context(loader_context)
        loader.execute()
        execute_xml = loader.get_execute_xml()


        return execute_xml.to_string()



    def get_render_command(my):
        '''render in a separate process'''
        '''NOTE: Highly specific to Maya render'''

        options = {}

        # get information from the context
        #frame_range = my.render_context.get_frame_range()
        #frame_range_values = frame_range.get_values()
        #options['frame_range'] = "-s %s -e %s -b %s" % frame_range_values

	quality = "-uf true -oi true -eaa 0 -ert true -of iff"
        options['quality'] = quality

        options['camera'] = "-cam %s" % my.render_context.get_camera()

        xres, yres = my.render_context.get_resolution()
        options['resolution'] = "-x %s -y %s" % (xres, yres)


        # set up all of the paths
        file_root = "maya_render"
        padding = 4
	type = "png"


        render_dir = my.render_context.get_render_dir()
        maya_path = "%s/%s.ma" % (render_dir,file_root)
        options['render_dir'] = "-rd %s -pad %s" % (render_dir, padding)


        # do the render
        options_str = " ".join( options.values() )
        cmd = 'Render %s %s' % (options_str, maya_path)

        return cmd




    def convert_images(my):

        render_dir = my.render_context.get_render_dir()

        # copy for now
        file_root = "maya_render"
        padding = 4
	type = "png"

        # check the expected images
        single = True
        if single == True:
            render_path = "%s/%s.iff" % (render_dir,file_root)
            final_path = "%s/%s.%s" % (render_dir,file_root,type)
            cmd = "imgcvt -f iff -t %s %s %s" % \
                (type, render_path, final_path)
            print cmd
            os.system(cmd)



            # create a render log entry
            file = open("%s/session.xml" % render_dir, "r")
            session_xml = file.read()
            file.close()

            # attach the sobject and snapshot to the render
            snapshot = my.render_context.get_snapshot()
            sobject = my.render_context.get_sobject()

            frame_range = my.render_context.get_frame_range()

            render = Render.create(sobject, snapshot, session_xml, frame_range.get_key(), version=1)

            # checkin the render
            icon_creator = IconCreator(final_path)
            icon_creator.create_icons()

            web = icon_creator.get_web_path()
            icon = icon_creator.get_icon_path()
            paths = [final_path,web,icon]
            types = ["main","web","icon"]

            my.description = "Rendered image"

            # check in the sobject
            checkin = FileCheckin(sobject, paths, types, \
                context="icon", column="images")
            checkin.execute()

            # check in the render
            checkin = FileCheckin(render, paths, types, \
                context="render", column="images")
            checkin.execute()




        else:
            render_path = "%s/%s.iff.####" % (render_dir,file_root)
            final_path = "%s/%s.####.%s" % (render_dir,file_root,type)

            frame_range = my.render_context.get_frame_range()
            render_paths = FileGroup.expand_paths(render_path,frame_range.get_key())
            final_paths = FileGroup.expand_paths(final_path,frame_range.get_key())


            for i in range(0, len(render_paths)):

                # convert the image
                cmd = "imgcvt -f iff -t %s %s %s" % \
                    (type, render_paths[i], final_paths[i])
                print cmd
                os.system(cmd)





    def checkin_render(my):

        render_dir = my.render_context.get_render_dir()


        # create a render log entry
        file = open("%s/session.xml" % render_dir, "r")
        session_xml = file.read()
        file.close()

        # attach the sobject and snapshot to the render
        snapshot = my.render_context.get_snapshot()
        sobject = my.render_context.get_sobject()
        file_range = my.render_context.get_frame_range().get_key()
        render = Render.create(sobject, snapshot, file_range, session_xml)

        my.description = "Rendered image"

        # create a reference snapshot
        snapshot_builder = SnapshotBuilder()
        snapshot_builder.add_ref_by_snapshot(snapshot)

        checkin = SnapshotCheckin( sobject, snapshot_builder.to_string, \
            snapshot_type="set", context="render" )
        checkin.execute()


        # checkin the rendered files to the render object
        paths = []
        types = []
        paths.append( final_path )
        types.append( "frame" )

        file_range = my.render_context.get_frame_range()
        snapshot_type = "frame"

        checkin = FileGroupCheckin(render, snapshot_type, "render", "snapshot", paths, types, file_range.get_key() )
        checkin.add_input_snapshot(snapshot)
        checkin.execute()



