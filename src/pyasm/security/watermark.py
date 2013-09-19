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

__all__ = ["Watermark"]


import tacticenv
from pyasm.common import Environment

import Image, ImageEnhance, ImageChops, ImageFont, ImageDraw
import types

class Watermark(object):

    # http://code.activestate.com/recipes/362879-watermark-with-pil/

    def reduce_opacity(my, im, opacity):
        '''Returns an image with reduced opacity.'''
        assert opacity >= 0 and opacity <= 1
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        else:
            im = im.copy()
        alpha = im.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        im.putalpha(alpha)
        return im

    def execute(my, im, mark, position, opacity=1):
        '''Adds a watermark to an image.'''
        if opacity < 1:
            mark = my.reduce_opacity(mark, opacity)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        # create a transparent layer the size of the image and draw the
        # watermark in that layer.
        layer = Image.new('RGBA', im.size, (0,0,0,0))
        if position == 'tile':
            for y in range(0, im.size[1], mark.size[1]):
                for x in range(0, im.size[0], mark.size[0]):
                    layer.paste(mark, (x, y))
        elif position == 'scale':
            # scale, but preserve the aspect ratio
            ratio = min(
                float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
            w = int(mark.size[0] * ratio)
            h = int(mark.size[1] * ratio)
            mark = mark.resize((w, h))
            layer.paste(mark, ((im.size[0] - w) / 2, (im.size[1] - h) / 2))
        else:
            layer.paste(mark, position)
        # composite the watermark with the layer
        return Image.composite(layer, im, layer)


    def generate(my, texts, font_sizes=15):
        if isinstance(texts, basestring):
            texts = [texts]

        if type(font_sizes) == types.IntType:
            font_sizes = [font_sizes]

        font_size = font_sizes[0]
            

        length = len(texts[0])
        width = int(font_size * 0.6 * length + 50)

        im = Image.new("RGBA", (width, 100))
        draw = ImageDraw.Draw(im)

        install_dir = Environment.get_install_dir()
        #/home/apache/tactic/src/pyasm/security/arial.ttf
        font_path = "%s/src/pyasm/security/arial.ttf" % install_dir
        for i, text in enumerate(texts):
            font = ImageFont.truetype(font_path, font_sizes[i])
            interval = int(font_size)
            offset = int(font_size/2)
            draw.text((20, i*interval), text, font=font, fill='#000')
            draw.text((20+offset, i*interval+offset), text, font=font, fill='#FFF')

                

        return im




    def add_watermark(my, in_path, out_path, quality=0.5, texts=[], sizes=[]):

        import Image
        from pyasm.security.watermark import Watermark
        from datetime import datetime

        s_in = None
        try:
            #s_in = StringIO(filter.read())
            s_in = open(in_path)
            im_in = Image.open(s_in)
            if im_in.size[0] <= 120 and im_in.size[1] <= 80:
                return

            # reduce quality by making small and scaling
            if quality < 1:
                sizex = im_in.size[0]
                sizey = im_in.size[1]
                max_res = sizex * quality
                max_width = sizex
                im_in = im_in.resize( (max_res, int(sizey/(sizex/float(max_res)))) )
                im_in = im_in.resize( (max_width, int(sizey/(sizex/float(max_width)))) )

            # add the watermark
            #watermark = Watermark()
            now = datetime.today().strftime("%Y/%m/%d, %H:%M")
            if not texts:
                texts = ['Do Not Copy', now]
            if not sizes:
                sizes = [20, 10]

            mark = my.generate(texts, sizes)
            im_out = my.execute(im_in, mark, 'tile', 0.5)
            im_out.save(out_path)
        finally:
            if s_in:
                s_in.close()

 


def test():
    watermark = Watermark()

    texts = ['Do Not Copy', 'Joe Smith', 'id=12345', 'Feb 12, 2011']
    #watermark_path = './sample-watermark.png'
    #mark = Image.open(watermark_path)

    path = '/home/apache/california_web.jpg'
    im = Image.open(path)

    for i in range(1, 10):
        mark = watermark.generate(texts, i*5)
        im2 = watermark.execute(im, mark, 'tile', 0.5)
        im2.save("./test/tile%s.jpg" % i)

    #im3 = watermark.execute(im, mark, 'scale', 1.0)
    #im3.save("./test/scale.jpg")
    #im4 = watermark.execute(im, mark, (100, 100), 0.5)
    #im4.save("./test/pos.jpg")


if __name__ == '__main__':
    test()


