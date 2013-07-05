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

__all__ = ['BaseRenderContext', 'AssetRenderContext', 'ShotRenderContext']

import os

from pyasm.common import *
from pyasm.prod.biz import FrameRange



class BaseRenderContext(Base):
    '''The context under which a render take place.  This includes all
    of the settings and specific flags for a particular render'''

    def __init__(my, policy=None):
        my.sobject = None

        my.snapshot = None
        my.snapshot_xml = None
        my.snapshot_sobject = None

        my.context = None

        my.policy = policy

        # by default, just render the first frame
        my.frame_range = FrameRange(1,1,1)

        # FIXME: this is maya specific
        my.camera = "persp"
        my.layer_names = []

        my.override = ""


        # FIXME: not general enough
        my.shot = None


    def set_policy(my, policy):
        my.policy = policy

    def set_override(my, override):
        '''set overrides to render parameters'''
        my.override = override

    def get_override(my):
        return my.override


    # information from policy
    def get_resolution(my):
        return my.policy.get_resolution()


    def get_layer_names(my):
        return my.layer_names

    def add_layer(my, layer_name):
        my.layer_names.append(layer_name)



    def get_input_path(my):
        '''gets the input file to be rendered'''
        snapshot = my.get_snapshot()
        lib_dir = snapshot.get_lib_dir()

        # FIXME: big assumption that snapshot type == file_type
        # FIXME: maya files only ????
        filename = snapshot.get_file_name_by_type("maya")
        if not filename:
            filename = snapshot.get_file_name_by_type("xsi")

        if not filename:
            filename = snapshot.get_file_name_by_type("main")

        if not filename:
            raise TacticException("Cannot render snapshot [%s] because file is not supported" % snapshot.get_code() )

        input_path = "%s/%s" % (lib_dir,filename)
        return input_path


    def get_output_prefix(my):
        # FIXME: should get this from naming conventions
        return "image_test"

    def get_output_ext(my):
        # FIXME: should take this from render policy
        return "png"

    def get_output_padding(my):
        return 4

    def get_output_pattern(my):
        # ie: "image.jpg.####"
        return "%s.%s.####" % (my.get_output_prefix(), my.get_output_ext() )



    def get_render_dir(my):
        ticket = Environment.get_security().get_ticket_key()
        tmpdir = Environment.get_tmp_dir()
        render_dir = "%s/temp/%s" % (tmpdir, ticket)

        System().makedirs(render_dir)

        return render_dir



    def set_shot(my, shot):
        my.shot = shot

        # setting the shot always sets the frames
        my.frame_range = shot.get_frame_range()


    def get_shot(my):
        return my.shot


    def set_sobject(my, sobject):
        '''set the sobject that is being rendered'''
        my.sobject = sobject

    def get_sobject(my):
        return my.sobject



    def set_camera(my, camera):
        print "Overriding camera: ", camera
        my.camera = camera

    def get_camera(my):
        return my.camera



    def set_frame_range(my, frame_range):
        my.frame_range = frame_range

        # if the policy sets a frame by, then use it
        frame_by = my.policy.get_value("frame_by")
        if frame_by:
            my.frame_range.set_frame_by(int(frame_by))
            

    def set_frame_range_values(my, start, end, by):
        frame_range = FrameRange(start, end, by)
        my.set_frame_range(frame_range)
            


    def get_frame_range(my):
        return my.frame_range



    def set_snapshot(my, snapshot):
        assert snapshot != None
        my.snapshot = snapshot
        my.snapshot_xml = snapshot.get_value("snapshot")
        #my.sobject = my.snapshot.get_sobject()
        my.snapshot_sobject = my.snapshot.get_sobject()

    def set_snapshot_xml(my, snapshot_xml):
        my.snapshot_xml = snapshot_xml

    def get_snapshot(my):
        return my.snapshot


    def get_snapshot_xml(my):
        return my.snapshot_xml

    def set_context(my, context):
        my.context = context

    def get_context(my):
        return my.context

    def set_policy(my, policy):
        my.policy = policy

    def get_extra_settings(my):
        # these extra settings are determined by the policy
        return my.policy.get_value("extra_settings")


    def get_name(my):
        return my.__class__.__name__


    def get_xml_data(my):
        '''create an XML document which can be stored in the queue for
        for informaiton about this render context.'''
        xml = Xml()
        xml.create_doc("data")
        root = xml.get_root_node()


        if my.snapshot:
            element = xml.create_text_element("search_key", my.sobject.get_search_key())
            root.appendChild(element)
            element = xml.create_text_element("snapshot_code", my.snapshot.get_code())
            root.appendChild(element)

 
        elif my.sobject:
            element = xml.create_text_element("search_key", my.sobject.get_search_key())
            root.appendChild(element)
           


        #  add information about the frames
        element = xml.create_text_element("prefix", my.get_output_prefix() )
        root.appendChild(element)
        element = xml.create_text_element("ext", my.get_output_ext() )
        root.appendChild(element)
        element = xml.create_text_element("padding", str(my.get_output_padding() )) 
        root.appendChild(element)
        element = xml.create_text_element("file_range", my.frame_range.get_key() )
        root.appendChild(element)
        element = xml.create_text_element("pattern", my.get_output_pattern() )
        root.appendChild(element)



        # add layer information
        for layer_name in my.layer_names:
            element = xml.create_text_element("layer_name", layer_name )
            root.appendChild(element)

        return xml.to_string()

        








class AssetRenderContext(BaseRenderContext):
    '''Convenience class to render assets thumbnails'''

    def __init__(my, sobject):
        super(AssetRenderContext,my).__init__()
        my.set_sobject(sobject)
        my.set_context("publish")

        # check if there is an associate render_stage sobject.
        search = Search("prod/render_stage")
        search.add_sobject_filter(sobject)
        search.add_filter("context", my.context)
        render_stage = search.get_sobject()

        if render_stage != None:
            snapshot = Snapshot.get_latest_by_sobject(render_stage, my.context)
        else:
            loader_context = ProdLoaderContext()
            snapshot = loader_context.get_snapshot_by_sobject( \
                sobject, my.context)

        my.set_snapshot(snapshot)


        if snapshot == None:
            raise RenderException("snapshot for [%s] [%s] does not exist" % \
                (sobject.get_search_type(), sobject.get_id() ))


        # TODO: should look for cameras and render all of them
        snapshot_xml = snapshot.get_snapshot_xml()
        instances = snapshot_xml.get_values("snapshot/ref/@instance")
       
        for instance in instances:
            if instance.startswith("camera"):
                # HACK
                #my.camera = instance
                my.camera = "%s:%s" % (instance, "camera100")

        camera = my.camera


        # set up the asset with a camera
        if camera == "persp":
            my.set_snapshot_xml('''
            <snapshot>
            <ref snapshot_code='%s'/>
            <mel>
            select -clear
            xform -ro -25 -45 0 %s
            viewFit %s
            setAttr %s.preScale 1.5
            </mel>
            </snapshot>
            ''' % (snapshot.get_code(), camera, camera, camera)
            )
        else:
            my.set_snapshot_xml('''
            <snapshot>
            <ref snapshot_code='%s'/>
            </snapshot>
            ''' % (snapshot.get_code())
            )


        # extra commands to add a light set
        #<ref search_type='prod/asset?prod=prod2' search_id='36' version='-1' context='publish'/>
        #viewFit -f 10 %s





class ShotRenderContext(BaseRenderContext):
    pass




