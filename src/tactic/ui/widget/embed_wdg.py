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
from pyasm.search import Search
from pyasm.web import DivWdg, HtmlElement, SpanWdg

from tactic.ui.common import BaseRefreshWdg

import os
import urllib

class EmbedWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            }

    def add_style(self, name, value=None):
        self.top.add_style(name, value)


    def add_class(self, name):
        self.top.add_class(name)



    def get_display(self):

        top = self.top

        layout = self.kwargs.get("layout") or "landscape"

        search_key = self.kwargs.get("search_key")
        file = self.kwargs.get("file")

        if search_key:
            sobject = Search.get_by_search_key(search_key)
            if sobject.get_base_search_type() == "sthpw/snapshot":
                snapshot = sobject
            else:
                snapshot = Snapshot.get_latest_by_sobject(sobject)
            src = snapshot.get_web_path_by_type()
        elif file:
            src = file.get_web_path()
        else:
            src = self.kwargs.get("src")

        opacity = 1.0
        if not src:
            src = "/context/icons/logo/tactic_silver.png"
            opacity = 0.6


        height = self.kwargs.get("height")
        width = self.kwargs.get("width")
        index = self.kwargs.get("index")

        if not height:
            height = "100%"
        if not width:
            width = "100%"

        # don't hard code width and height
        #width = "100%"
        #height = "auto"


        #div = DivWdg()
        #top.add(div)
        div = top
        div.add_class("unselectable")
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

        click = self.kwargs.get("click")
        if click in [False, 'false']:
            click = False
        else:
            click = True

        thumb_path = self.kwargs.get("thumb_path")
        preload = self.kwargs.get("preload")
        if not preload:
            preload = "none"

        ext = ext.lstrip(".")
        if ext in File.IMAGE_EXT:

            embed = DivWdg()
            embed.add_style("display: inline-block")
            embed.add_style("vertical-align: top")

            if layout == "landscape":
                embed.add_style("width: auto")
                embed.add_style("height: 100%")
            else:
                embed.add_style("width: 100%")
                embed.add_style("height: auto")


            if src.find("#") != -1:

                file_range = self.kwargs.get("file_range")
                for i in range(1, 16):
                    expand = src.replace("####", "%0.4d" % i)
                    item = HtmlElement.img(expand)
                    embed.add(item)
                    item.add_style("width: 25%")

                embed.add_style("overflow-y: auto")
                embed.add_style("text-align: left")

                #embed.add_behavior( {
                #    'type': 'load',
                #    'cbjs_action': '''
                #    new Scrollable(bvr.src_el)
                #    '''
                #} )


            elif src.find("|") != -1:
                paths = src.split("|")
                for path in paths:
                    item = HtmlElement.img(path)
                    embed.add(item)
                    item.add_style("width: 25%")

                embed.add_style("overflow-y: auto")
                embed.add_style("text-align: left")

            else:

                if isinstance(src, unicode):
                    src = src.encode("utf-8")
                src = urllib.pathname2url(src)


                img = HtmlElement.img(src)
                embed.add(img)

                if layout == "landscape":
                    img.add_style("width: auto")
                    img.add_style("height: 100%")
                else:
                    img.add_style("width: 100%")
                    img.add_style("height: auto")


        elif ext in File.VIDEO_EXT:
            from tactic.ui.widget import VideoWdg
            embed = DivWdg()


            #if not thumb_path:
            #    thumb_path = "/context/icons/logo/tactic_sml.png"
            controls = self.kwargs.get("controls")

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
            if thumb_path:
                img = HtmlElement.img(thumb_path)
            else:
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


        return top

    
