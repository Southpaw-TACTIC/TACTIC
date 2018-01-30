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

    def __init__(self, policy=None):
        self.sobject = None

        self.snapshot = None
        self.snapshot_xml = None
        self.snapshot_sobject = None

        self.context = None

        self.policy = policy

        # by default, just render the first frame
        self.frame_range = FrameRange(1,1,1)

        # FIXME: this is maya specific
        self.camera = "persp"
        self.layer_names = []

        self.override = ""


        # FIXME: not general enough
        self.shot = None


    def set_policy(self, policy):
        self.policy = policy

    def set_override(self, override):
        '''set overrides to render parameters'''
        self.override = override

    def get_override(self):
        return self.override


    # information from policy
    def get_resolution(self):
        return self.policy.get_resolution()


    def get_layer_names(self):
        return self.layer_names

    def add_layer(self, layer_name):
        self.layer_names.append(layer_name)



    def get_input_path(self):
        '''gets the input file to be rendered'''
        snapshot = self.get_snapshot()
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


    def get_output_prefix(self):
        # FIXME: should get this from naming conventions
        return "image_test"

    def get_output_ext(self):
        # FIXME: should take this from render policy
        return "png"

    def get_output_padding(self):
        return 4

    def get_output_pattern(self):
        # ie: "image.jpg.####"
        return "%s.%s.####" % (self.get_output_prefix(), self.get_output_ext() )



    def get_render_dir(self):
        ticket = Environment.get_security().get_ticket_key()
        tmpdir = Environment.get_tmp_dir()
        render_dir = "%s/temp/%s" % (tmpdir, ticket)

        System().makedirs(render_dir)

        return render_dir



    def set_shot(self, shot):
        self.shot = shot

        # setting the shot always sets the frames
        self.frame_range = shot.get_frame_range()


    def get_shot(self):
        return self.shot


    def set_sobject(self, sobject):
        '''set the sobject that is being rendered'''
        self.sobject = sobject

    def get_sobject(self):
        return self.sobject



    def set_camera(self, camera):
        print "Overriding camera: ", camera
        self.camera = camera

    def get_camera(self):
        return self.camera



    def set_frame_range(self, frame_range):
        self.frame_range = frame_range

        # if the policy sets a frame by, then use it
        frame_by = self.policy.get_value("frame_by")
        if frame_by:
            self.frame_range.set_frame_by(int(frame_by))
            

    def set_frame_range_values(self, start, end, by):
        frame_range = FrameRange(start, end, by)
        self.set_frame_range(frame_range)
            


    def get_frame_range(self):
        return self.frame_range



    def set_snapshot(self, snapshot):
        assert snapshot != None
        self.snapshot = snapshot
        self.snapshot_xml = snapshot.get_value("snapshot")
        #self.sobject = self.snapshot.get_sobject()
        self.snapshot_sobject = self.snapshot.get_sobject()

    def set_snapshot_xml(self, snapshot_xml):
        self.snapshot_xml = snapshot_xml

    def get_snapshot(self):
        return self.snapshot


    def get_snapshot_xml(self):
        return self.snapshot_xml

    def set_context(self, context):
        self.context = context

    def get_context(self):
        return self.context

    def set_policy(self, policy):
        self.policy = policy

    def get_extra_settings(self):
        # these extra settings are determined by the policy
        return self.policy.get_value("extra_settings")


    def get_name(self):
        return self.__class__.__name__


    def get_xml_data(self):
        '''create an XML document which can be stored in the queue for
        for informaiton about this render context.'''
        xml = Xml()
        xml.create_doc("data")
        root = xml.get_root_node()


        if self.snapshot:
            element = xml.create_text_element("search_key", self.sobject.get_search_key())
            root.appendChild(element)
            element = xml.create_text_element("snapshot_code", self.snapshot.get_code())
            root.appendChild(element)

 
        elif self.sobject:
            element = xml.create_text_element("search_key", self.sobject.get_search_key())
            root.appendChild(element)
           


        #  add information about the frames
        element = xml.create_text_element("prefix", self.get_output_prefix() )
        root.appendChild(element)
        element = xml.create_text_element("ext", self.get_output_ext() )
        root.appendChild(element)
        element = xml.create_text_element("padding", str(self.get_output_padding() )) 
        root.appendChild(element)
        element = xml.create_text_element("file_range", self.frame_range.get_key() )
        root.appendChild(element)
        element = xml.create_text_element("pattern", self.get_output_pattern() )
        root.appendChild(element)



        # add layer information
        for layer_name in self.layer_names:
            element = xml.create_text_element("layer_name", layer_name )
            root.appendChild(element)

        return xml.to_string()

        








class AssetRenderContext(BaseRenderContext):
    '''Convenience class to render assets thumbnails'''

    def __init__(self, sobject):
        super(AssetRenderContext,self).__init__()
        self.set_sobject(sobject)
        self.set_context("publish")

        # check if there is an associate render_stage sobject.
        search = Search("prod/render_stage")
        search.add_sobject_filter(sobject)
        search.add_filter("context", self.context)
        render_stage = search.get_sobject()

        if render_stage != None:
            snapshot = Snapshot.get_latest_by_sobject(render_stage, self.context)
        else:
            loader_context = ProdLoaderContext()
            snapshot = loader_context.get_snapshot_by_sobject( \
                sobject, self.context)

        self.set_snapshot(snapshot)


        if snapshot == None:
            raise RenderException("snapshot for [%s] [%s] does not exist" % \
                (sobject.get_search_type(), sobject.get_id() ))


        # TODO: should look for cameras and render all of them
        snapshot_xml = snapshot.get_snapshot_xml()
        instances = snapshot_xml.get_values("snapshot/ref/@instance")
       
        for instance in instances:
            if instance.startswith("camera"):
                # HACK
                #self.camera = instance
                self.camera = "%s:%s" % (instance, "camera100")

        camera = self.camera


        # set up the asset with a camera
        if camera == "persp":
            self.set_snapshot_xml('''
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
            self.set_snapshot_xml('''
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




