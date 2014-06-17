###########################################################
#
# Copyright (c) 2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['VideoWdg']

from tactic.ui.common import BaseRefreshWdg
from pyasm.web import Video, HtmlElement, DivWdg


class VideoWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        "sources": {
            'description': 'List of URLs representing the sources for the videos, separate by "|"',
            'type': 'TextAreaWdg',
            'category': 'Options',
        },
        'width': 'The width to display the video',
        'height': 'The height to display the video',
        'poster': 'Link to an image for the poster representing the video',
    }

    def init(my):
        my.video = Video()
        my.index = my.kwargs.get('index')

    def get_video(my):
        return my.video

    def get_display(my):

        top = my.top

        sources = my.kwargs.get("sources")
        if sources and isinstance(sources, basestring):
            sources = sources.split("|")

        source_types = my.kwargs.get("source_types")
        if not source_types:
            source_types = []


        poster = my.kwargs.get("poster")
        width = my.kwargs.get("width")
        height = my.kwargs.get("height")
        preload = my.kwargs.get("preload")
        controls = my.kwargs.get("controls")


        is_test = my.kwargs.get("is_test")
        is_test = False
        if is_test in [True, 'true']:
            poster = "http://video-js.zencoder.com/oceans-clip.png"
            sources = ["http://video-js.zencoder.com/oceans-clip.mp4"]
            sources = ["http://video-js.zencoder.com/oceans-clip.mp4"]
            sources = ["http://techslides.com/demos/sample-videos/small.ogv"]


        video = my.video
        video.add_class("video-js")
        video.add_class("vjs-default-skin")
        top.add(video)

        my.video_id = my.kwargs.get("video_id")
        if not my.video_id:
            my.video_id = video.set_unique_id()
        else:
            video.set_attr("id", my.video_id)
        if my.index == 0: 
            overlay = DivWdg()
            overlay.add_class('video_overlay')
            overlay.add_styles('background: transparent; z-index: 300; position: fixed; top: 38%; left: 12%;\
                margin-left: auto; margin-right: auto; width: 75%; height: 45%' )

           
            overlay.add_behavior({'type':'click_up',
                'cbjs_action': '''
                var overlay = bvr.src_el;
                
                var idx = spt.gallery.index;
                var video_id = spt.gallery.videos[idx];
                
                if (!video_id) return;

                var player = videojs(video_id, {"nativeControlsForTouch": false});
                if (player.paused()) {
                    player.play();
                    //console.log("play " + video_id)
                }
                else 
                    player.pause();
                '''
                })


            top.add(overlay) 
        

        top.add_behavior( {
            'type': 'load',
            'index' : my.index,
            'video_id': my.video_id,
            'cbjs_action': '''
            if (!bvr.index) bvr.index = 0;

            var video_id = bvr.video_id;
            spt.dom.load_js(["video/video.js"], function() {
                var player = videojs(video_id, {"nativeControlsForTouch": false}, function() {
                } );
                //videojs(bvr.video_id).play();
            });
            if (spt.gallery) {
                
                spt.gallery.videos[bvr.index] = video_id;
            }
            if (!spt.gallery.portrait) {
                var overlay = bvr.src_el.getElement('.video_overlay');
                if (overlay)
                    overlay.setStyles({'top': '4%', 'left': '5%', 
                        'width': '90%', 'height':'87%'});
            }
            
            '''
        } )
        #video.add_attr("data-setup", "{}")




        if width:
            video.add_attr("width", width)
        if height:
            video.add_attr("height", height)

        if poster:
            video.add_attr("poster", poster)


        if not preload:
            preload = "none"
        video.add_attr("preload", preload)

        if not controls:
            controls = "true"
        if controls not in [False, 'false']:
            video.add_attr("controls", controls)



        for i, src in enumerate(sources):

            source = HtmlElement(type="source")
            source.add_attr("src", src)

            if len(source_types) > i:
                source_type = source_types[i]
                source.add_attr("type", source_type)

            video.add(source)

        #print top.get_buffer_display()
        return top



