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

__all__ = ["RenderCmdBuilder", 'MayaRenderCmdBuilder', 'XsiRenderCmdBuilder']

import re


class RenderCmdBuilder(object):
    '''base class for building render commands'''
    def __init__(self, render_package):
        self.render_package = render_package

        self.options = {}
        self.overrides = {}

        self.frame_range_values = render_package.get_frame_range().get_values()

    def add_override(self, name, value):
        '''override the values a dictacted in the render context'''
        self.overrides['name'] = value


    def set_frame_range(self, start, end, by=1):
        self.frame_range_values = (start, end, by)




class MayaRenderCmdBuilder(RenderCmdBuilder):

    def get_command(self):
        '''build the maya command line renderer'''
        assert self.frame_range_values

        self.options = {}

        # set the frame range
        self.options['frame_range'] = "-s %s -e %s -b %s" % self.frame_range_values


        # set the quality
        extra_settings = self.render_package.get_option("extra_settings", no_exception=True)
        if extra_settings:
            self.options['quality'] = extra_settings

        #if not renderer == "mr":
        #    quality = "-uf true -oi true -eaa 0 -ert true -of iff"
        #    self.options['quality'] = quality



        # set the camera
        camera = self.render_package.get_option("camera", no_exception=True)
        if not camera:
            camera = "persp"
        self.options['camera'] = "-cam %s" % camera


        # set the resolution
        resolution = self.render_package.get_option("resolution", no_exception=True)
        if resolution:
            xres,yres = resolution.split("x")
            self.options['resolution'] = "-x %s -y %s" % (xres, yres)

        # set the output image name
        image_name = self.render_package.get_option("output_prefix", no_exception=True)
        if not image_name:
            image_name = "image"
        self.options['naming_convention'] = "-im %s -fnc name.ext.#" % image_name

        # set the output type
	type = self.render_package.get_option("output_ext", no_exception=True)
        if type:
            self.options['type'] = "-of %s" % type


        # set the output directory
        render_dir = self.render_package.get_option("render_dir")
        padding = 4
        self.options['render_dir'] = "-rd %s -pad %s" % (render_dir, padding)

        # add layer support
        layers = self.render_package.get_option("layer_names", no_exception=True)
        if layers:
            self.options['layer'] = "-l %s" % ":".join(layers)


        # get the input file
        input_path = self.render_package.get_option("input_path")

        # add in overrides
        for name, value in self.overrides.items():
            self.options[name] = value


        # build the command string
        self.options_str = " ".join( self.options.values() )
        cmd = 'Render %s %s' % (self.options_str, input_path)

        return cmd




class XsiRenderCmdBuilder(RenderCmdBuilder):
    '''
    "xsibatch" -r -continue -s QB_FRAME_START,QB_FRAME_END,QB_FRAME_STEP
    -scene
    "S:\MeasureOfaMan\Production\Objects\Texture\Character\ALTAIR\Scenes\Eye_LAnim_v04\\Eye_LAnim_v53_FOR_BIJU.scn" -pass _BEAUTY -skip on -channel_rgba on
    '''


    def get_command(self):
        assert self.frame_range_values

        self.options = {}

        # set the frame range
        self.options['frame_range'] = "-frames %s,%s,%s" % self.frame_range_values

        render_dir = self.render_package.get_option("render_dir")
        self.options['output_dir'] = "-output_dir %s" % render_dir

        # add layer support
        layers = self.render_package.get_option("layers", no_exception=True)
        if layers:
            self.options['layer'] = "-pass %s" % ",".join(layers)


        # set up all of the paths
	type = "tif"
        self.options['type'] = "-file_type %s" % type
        self.options['render_dir'] = "-file_dir %s" % render_dir


        # build the input path
        input_path = self.render_package.get_option("input_path")

        # add in overrides
        for name, value in self.overrides.items():
            self.options[name] = value

        # build the command string
        self.options_str = " ".join( self.options.values() )
        cmd = "xsibatch -render %s %s" % (self.options_str, input_path)

        print cmd
        return cmd
 




