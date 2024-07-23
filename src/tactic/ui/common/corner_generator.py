###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import tacticenv

from pyasm.common import Environment

import sys, os

# DEPRECATED


class CornerGenerator(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def execute(self):
        from PIL import Image, ImageDraw, ImageFilter

        color = self.kwargs.get("color")
        if not color:
            color = '#FFF'

        if not color.startswith("#"):
            color = "#%s" % color

        basedir = self.kwargs.get("basedir")
        if not basedir:
            basedir = '.'
        else:
            if not os.path.exists(basedir):
                os.makedirs(basedir)

        basename = self.kwargs.get("basename")
        if not basename:
            basename = 'border'

        size = self.kwargs.get("size")
        if not size:
            size = 10



        width = size
        height = size
        scale = 32 
        offset = 0 


        start = 0
        for corner in ['BR', 'BL', 'TL', 'TR']:

            x = width*scale
            y = height*scale

            im = Image.new('RGBA', (x, y), (256, 256, 256, 0))
            dr = ImageDraw.ImageDraw(im)

            x = width*scale
            y = height*scale

            if corner == 'BR':
                bb = (-x-offset, -y-offset, x+offset, y+offset)
            elif corner == 'BL':
                bb = (0-offset, -y-offset, x*2+offset, y+offset)
            elif corner == 'TL':
                bb = (0-offset, 0-offset, x*2+offset, y*2+offset)
            elif corner == 'TR':
                bb = (-x-offset, 0-offset, x+offset, y*2+offset)

            try:
                # For Pillow 10.0 and later
                resampling_filter = Image.Resampling.LANCZOS
            except AttributeError:
                # For older versions of Pillow
                resampling_filter = Image.ANTIALIAS

            dr.pieslice(bb, start, start+360, fill=color)
            im = im.resize((height, width), resampling_filter)

            try:
                start += 90
                path = '%s/%s_%s.png' % (basedir, basename, corner)
                im.save(path)

            except:
                print(sys.exc_info()[0])
                continue



    def generate(color):
        # find the base path
        tactic_base = Environment.get_install_dir()
        basedir = "%s/src/context/ui_proto/roundcorners/rc_%s" % (tactic_base, color.replace("#", ""))

        basename = "rc_%s_10x10" % color
        cmd = CornerGenerator(color=color, basedir=basedir, basename=basename)
        cmd.execute()

        basename = "rc_%s_5x5" % color
        cmd = CornerGenerator(color=color, basedir=basedir, basename=basename, size=5)
        cmd.execute()

    generate = staticmethod(generate)


    def color_exists(color):
        # find the base path
        tactic_base = Environment.get_install_dir()
        basedir = "%s/src/context/ui_proto/roundcorners/rc_%s" % (tactic_base, color.replace("#", ""))
        #print("test for corner: ", color)

        if os.path.exists(basedir):
            return True
        else:
            return False

    color_exists = staticmethod(color_exists)






if __name__ == '__main__':
    color = sys.argv[1]
    CornerGenerator.generate(color)


