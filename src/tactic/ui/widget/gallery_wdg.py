###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['GalleryWdg']

from pyasm.biz import Snapshot, File
from pyasm.search import Search
from pyasm.web import HtmlElement, DivWdg, Table
from pyasm.widget import TextWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg



class GalleryWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style
        top.add_class("spt_gallery_top")

        inner = DivWdg()
        top.add(inner)
        inner.add_style("position: fixed")
        inner.add_style("top: 0")
        inner.add_style("left: 0")
        inner.add_style("width: 100%")
        inner.add_style("height: 100%")
        #inner.add_style("background: rgba(0,0,0,0.5)")
        inner.add_style("background: rgba(0,0,0,1)")
        inner.add_style("z-index: 1000")
        """
        inner.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_gallery_top");
            spt.behavior.destroy_element(top);
            '''
        } )
        """


        icon = IconWdg(title="Close", icon="/plugins/remington/pos/icons/close.png")
        inner.add(icon)
        icon.add_style("position: absolute")
        icon.add_style("cursor: hand")
        icon.add_style("bottom: 0px")
        icon.add_style("right: 0px")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_gallery_top");
            spt.behavior.destroy_element(top);
            '''
        } )


        icon = IconWdg(title="Previous", icon="/plugins/remington/pos/icons/chevron_left.png")
        inner.add(icon)
        icon.add_style("cursor: hand")
        icon.add_style("position: absolute")
        icon.add_style("top: 0px")
        icon.add_style("left: 0px")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            spt.gallery.show_prev(); 
            '''
        } )


        icon = IconWdg(title="Next", icon="/plugins/remington/pos/icons/chevron_right.png")
        inner.add(icon)
        icon.add_style("position: absolute")
        icon.add_style("cursor: hand")
        icon.add_style("top: 0px")
        icon.add_style("right: 0px")
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.gallery.show_next(); 
            '''
        } )


        width = my.kwargs.get("width")
        height = my.kwargs.get("height")
        if not width:
            width = 1024



        inner.add_behavior( {
        'type': 'load',
        'width': width,
        'cbjs_action': '''

        spt.gallery = {};

        spt.gallery.top = bvr.src_el;
        spt.gallery.width = bvr.width;
        spt.gallery.content = spt.gallery.top.getElement(".spt_gallery_content");

        spt.gallery.init = function() {
            
        }

        spt.gallery.show_next = function() {
            var width = spt.gallery.width;
            var content = spt.gallery.content;
            var pos = content.getStyle("margin-left");
            pos = parseInt(pos.replace("px", ""))
            new Fx.Tween(content,{duration: 250}).start("margin-left", pos-width);
        }

        spt.gallery.show_prev = function() {
            var width = spt.gallery.width;
            var content = spt.gallery.content;
            var pos = content.getStyle("margin-left");
            pos = parseInt(pos.replace("px", ""))
            new Fx.Tween(content,{duration: 250}).start("margin-left", pos+width);
        }
        '''
        } )








        scroll = DivWdg()
        inner.add(scroll)
        scroll.set_box_shadow()

        scroll.add_style("width: %s" % width)
        if height:
            scroll.add_style("height: %s" % height)
        scroll.add_style("overflow-x: hidden")
        scroll.add_style("overflow-y: hidden")
        scroll.add_style("background: #000")

        #scroll.add_style("position: absolute")
        scroll.add_style("margin-left: auto")
        scroll.add_style("margin-right: auto")


        paths = my.get_paths()


        total_width = width * len(paths)

        content = DivWdg()
        scroll.add(content)
        content.add_class("spt_gallery_content")

        content.add_style("width: %s" % total_width)

        scroll.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
 
        scroll.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").focus();
            '''
        } )
        scroll.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.getElement(".spt_input").blur();
            '''
        } )



        input = TextWdg("keydown")
        content.add(input)
        input.add_style("position: absolute")
        input.add_style("left: -5000px")

        input.add_behavior( {
            'type': 'keydown',
            'width': width,
            'cbjs_action': '''
            var key = evt.key;
            console.log(key);
            if (key == "left") {
                spt.gallery.show_prev();
            }
            else if (key == "right") {
                spt.gallery.show_next();
            }
            else if (key == "esc" || key == "enter") {
                var top = bvr.src_el.getParent(".spt_gallery_top");
                spt.behavior.destroy_element(top);
            }



            '''
        } )




        content.add_behavior({
            'type': 'load',
            'cbjs_action': '''
            // find all of the widths of the images

            '''
        } )
        for path in paths:
            path_div = DivWdg()
            content.add(path_div)
            path_div.add_style("float: left")

            path_div.add_style("width: %s" % width)
            if height:
                path_div.add_style("height: %s" % height)

            img = HtmlElement.img(path)
            path_div.add(img)
            img.add_style("width: 100%")
            #img.add_style("height: 100%")


        return top



    def get_paths(my):

        search_keys = my.kwargs.get("search_keys")
        paths = my.kwargs.get("paths")

        if search_keys:
            sobjects = Search.get_by_search_keys(search_keys)
            snapshots = Snapshot.get_by_sobjects(sobjects)
            file_objects = File.get_by_snapshots(snapshots, file_type='main')
            paths = [x.get_web_path() for x in file_objects]

        elif paths:
            return paths

        else:
            # TEST
            paths = [
                '/assets/test/store/The%20Boxter_v001.jpg',
                '/assets/test/store/Another%20one_v001.jpg',
                '/assets/test/store/Whatever_v001.jpg'
            ]

        return paths




