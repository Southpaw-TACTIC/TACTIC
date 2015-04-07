###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["EmbedWdg"]

from pyasm.common import Environment
from pyasm.biz import File, Snapshot
from pyasm.web import DivWdg, HtmlElement, SpanWdg


from tactic.ui.common import BaseRefreshWdg

import os


class EmbedWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            }

    def add_style(my, name, value=None):
        my.top.add_style(name, value)


    def add_class(my, name):
        my.top.add_class(name)



    def get_display(my):

        top = my.top

        src = my.kwargs.get("src")
        file = my.kwargs.get("file")
        if file:
            src = file.get_web_path()


        opacity = 1.0
        if not src:
            src = "/context/icons/logo/tactic_silver.png"
            opacity = 0.6


        height = my.kwargs.get("height")
        width = my.kwargs.get("width")
        index = my.kwargs.get("index")


        #div = DivWdg()
        #top.add(div)
        div = top
        div.add_style("opacity", opacity)
        div.add_style("overflow-x: hidden")
        div.add_style("overflow-y: hidden")
        div.add_style("margin-left: auto")
        div.add_style("margin-right: auto")
        div.add_style("text-align: center")
        if height:
            div.add_style("height", height)
        if width:
            div.add_style("width", width)


        parts = os.path.splitext(src)
        ext = parts[1]
        ext = ext.lower()

        click = my.kwargs.get("click")
        if click in [False, 'false']:
            click = False
        else:
            click = True

        preload = my.kwargs.get("preload")
        if not preload:
            preload = "none"

        ext = ext.lstrip(".")
        if ext in File.IMAGE_EXT:
            embed = HtmlElement.img(src)
        elif ext in File.VIDEO_EXT:
            from tactic.ui.widget import VideoWdg
            embed = DivWdg()


            thumb_path = my.kwargs.get("poster")
            
            if not thumb_path:
                thumb_path = "/context/icons/logo/tactic_silver.png"
            controls = my.kwargs.get("controls")
            if not controls:
                controls = "true"

            video_id = None
            sources = [src]
            source_types = ["video/mp4"]
            poster = thumb_path
            width = '100%'
            height = '100%'
            #width = "640"
            #height = "480"
            video = VideoWdg(video_id=video_id, sources=sources, source_types=source_types, poster=poster, preload=preload, controls=controls, width=width, height=height, index=index)
            embed.add(video)
            video.get_video().add_class("spt_resizable")

            click = False

        else:
            #embed = HtmlElement.embed(src)
            from pyasm.widget import ThumbWdg
            link = ThumbWdg.find_icon_link(src)
            img = HtmlElement.img(link)
            img.add_style("width: 50%")
            img.add_style("margin: 20px 20px")
            embed = DivWdg(img)
        div.add(embed)

        if click:
            embed.add_behavior( {
                'type': 'click_up',
                'src': src,
                'cbjs_action': '''
                window.open(bvr.src);
                '''
            } )
            embed.add_class("hand")

        #embed.add_style("width", "100%")
        # NOTE: to keep true original aspect ratio, don't set this height
        # and let GalleryWdg inner load script to take care of it on load
        # that js portion needs uncommenting as well
        embed.add_style("height", "100%")
        #embed.set_box_shadow("1px 1px 1px 1px")
        return top

    
