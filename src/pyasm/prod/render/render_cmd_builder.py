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
    def __init__(my, render_package):
        my.render_package = render_package

        my.options = {}
        my.overrides = {}

        my.frame_range_values = render_package.get_frame_range().get_values()

    def add_override(my, name, value):
        '''override the values a dictacted in the render context'''
        my.overrides['name'] = value


    def set_frame_range(my, start, end, by=1):
        my.frame_range_values = (start, end, by)




class MayaRenderCmdBuilder(RenderCmdBuilder):

    def get_command(my):
        '''build the maya command line renderer'''
        assert my.frame_range_values

        my.options = {}

        # set the frame range
        my.options['frame_range'] = "-s %s -e %s -b %s" % my.frame_range_values


        # set the quality
        extra_settings = my.render_package.get_option("extra_settings", no_exception=True)
        if extra_settings:
            my.options['quality'] = extra_settings

        #if not renderer == "mr":
        #    quality = "-uf true -oi true -eaa 0 -ert true -of iff"
        #    my.options['quality'] = quality



        # set the camera
        camera = my.render_package.get_option("camera", no_exception=True)
        if not camera:
            camera = "persp"
        my.options['camera'] = "-cam %s" % camera


        # set the resolution
        resolution = my.render_package.get_option("resolution", no_exception=True)
        if resolution:
            xres,yres = resolution.split("x")
            my.options['resolution'] = "-x %s -y %s" % (xres, yres)

        # set the output image name
        image_name = my.render_package.get_option("output_prefix", no_exception=True)
        if not image_name:
            image_name = "image"
        my.options['naming_convention'] = "-im %s -fnc name.ext.#" % image_name

        # set the output type
	type = my.render_package.get_option("output_ext", no_exception=True)
        if type:
            my.options['type'] = "-of %s" % type


        # set the output directory
        render_dir = my.render_package.get_option("render_dir")
        padding = 4
        my.options['render_dir'] = "-rd %s -pad %s" % (render_dir, padding)

        # add layer support
        layers = my.render_package.get_option("layer_names", no_exception=True)
        if layers:
            my.options['layer'] = "-l %s" % ":".join(layers)


        # get the input file
        input_path = my.render_package.get_option("input_path")

        # add in overrides
        for name, value in my.overrides.items():
            my.options[name] = value


        # build the command string
        my.options_str = " ".join( my.options.values() )
        cmd = 'Render %s %s' % (my.options_str, input_path)

        return cmd




class XsiRenderCmdBuilder(RenderCmdBuilder):
    '''
    "xsibatch" -r -continue -s QB_FRAME_START,QB_FRAME_END,QB_FRAME_STEP
    -scene
    "S:\MeasureOfaMan\Production\Objects\Texture\Character\ALTAIR\Scenes\Eye_LAnim_v04\\Eye_LAnim_v53_FOR_BIJU.scn" -pass _BEAUTY -skip on -channel_rgba on
    '''


    def get_command(my):
        assert my.frame_range_values

        my.options = {}

        # set the frame range
        my.options['frame_range'] = "-frames %s,%s,%s" % my.frame_range_values

        render_dir = my.render_package.get_option("render_dir")
        my.options['output_dir'] = "-output_dir %s" % render_dir

        # add layer support
        layers = my.render_package.get_option("layers", no_exception=True)
        if layers:
            my.options['layer'] = "-pass %s" % ",".join(layers)


        # set up all of the paths
	type = "tif"
        my.options['type'] = "-file_type %s" % type
        my.options['render_dir'] = "-file_dir %s" % render_dir


        # build the input path
        input_path = my.render_package.get_option("input_path")

        # add in overrides
        for name, value in my.overrides.items():
            my.options[name] = value

        # build the command string
        my.options_str = " ".join( my.options.values() )
        cmd = "xsibatch -render %s %s" % (my.options_str, input_path)

        print cmd
        return cmd
 




