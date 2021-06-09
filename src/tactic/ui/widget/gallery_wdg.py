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

import urllib

from pyasm.biz import Snapshot, File
from pyasm.search import Search
from pyasm.web import HtmlElement, DivWdg, Table
from pyasm.widget import TextWdg, IconWdg

from tactic.ui.common import BaseRefreshWdg



class GalleryWdg(BaseRefreshWdg):

    def init(self):
        self.curr_path = None

    def get_display(self):

        self.sobject_data = {}

        top = self.top
        top.add_style
        top.add_class("spt_gallery_top")

        inner = DivWdg()
        top.add(inner)

        # make the whole Gallery unselectable
        inner.add_class('unselectable')
        inner.add_style("position: fixed")
        inner.add_style("top: 0px")
        inner.add_style("left: 0px")
        inner.add_style("width: 100%")
        inner.add_style("bottom: 0px")
        inner.add_style("padding-bottom: 40px")

        #inner.add_style("background: rgba(0,0,0,0.5)")
        inner.add_style("background: rgba(0,0,0,1)")
        inner.add_style("z-index: 2000")


        width = self.kwargs.get("width")
        height = self.kwargs.get("height")

        # default to top.
        align = self.kwargs.get("align")
        if not align:
            align = "top"


        if not width:
            width = 1300
        else:
            width = int(width)


        paths = self.get_paths(file_type='main')

        # icon type may be too small
        thumb_paths = self.get_paths(file_type='web')

        descriptions = []
        for path in paths:
            sobject = self.sobject_data.get(path)
            if not sobject:
                descriptions.append("")
            else:
                description = sobject.get("description")
                if not description:
                    description = ""
                descriptions.append(description)

        total_width = width * len(paths)
        inner.add_behavior( {
        'type': 'load',
        'width': width,
        'total_width': total_width,
        'descriptions': descriptions,
        'cbjs_action': '''
        spt.gallery = {};
        // 1250 is defined also in the css styles
        spt.gallery.portrait = window.innerWidth < 1250;
        spt.gallery.portrait = false


        spt.gallery.top = bvr.src_el;
        spt.gallery.content = spt.gallery.top.getElement(".spt_gallery_content");
        spt.gallery.shelf = spt.gallery.top.getElement(".spt_gallery_shelf");
        spt.gallery.content.setStyle('opacity','0.1')
        spt.gallery.desc_el = spt.gallery.top.getElement(".spt_gallery_description");

        //window.addEvent('domready', function() {
        setTimeout(function() {
		// set the img h or w directly
		var items = bvr.src_el.getElements('.spt_gallery_item img');
		// fade in
        spt.gallery.content.set('tween', {duration: 250}).fade('in');

        }, 50)

        spt.gallery.width = bvr.width;
        spt.gallery.descriptions = bvr.descriptions;
        spt.gallery.index = 0;
        spt.gallery.last_index = 0;
        spt.gallery.total = bvr.descriptions.length;
        spt.gallery.left_arrow = bvr.src_el.getElement('.spt_left_arrow');
        spt.gallery.right_arrow = bvr.src_el.getElement('.spt_right_arrow');
        spt.gallery.videos = {};


        spt.gallery.init = function() {

        }

        spt.gallery.stack = [];

        spt.gallery.push_stack = function(key) {
            spt.gallery.stack.push(key);
        }


        spt.gallery.show_next = function(src_el) {
            if (!src_el)
                src_el = spt.gallery.right_arrow;

            if (spt.gallery.index >= spt.gallery.total-2) {
                spt.hide(src_el);
            }
            if (spt.gallery.index == spt.gallery.total-1) {
                return;
            }
            spt.gallery.index += 1;
            spt.gallery.show_index(spt.gallery.index);
        }

        spt.gallery.show_prev = function(src_el) {
            if (!src_el)
                src_el = spt.gallery.left_arrow;
            if (spt.gallery.index <= 1) {
                spt.hide(src_el);

            }
            if (spt.gallery.index == 0) {
                return;
            }

            spt.gallery.index -= 1;
            spt.gallery.show_index(spt.gallery.index);
        }


        spt.gallery.show_index = function(index) {

            let last_index = spt.gallery.last_index;

            // stop all videos
            var videos = spt.gallery.top.getElements(".video-js");
            for (var i = 0; i < videos.length; i++) {
                try {
                    var video = videos[i];
                    var video_id = video.get("id");
                    var video_obj = videojs(video_id,  {"nativeControlsForTouch": false});
                    video_obj.pause();

                }
                catch(e) {
                }
            }


            // can't tween percentage with this library???
            var width = spt.gallery.width;
            var margin = - width * index;
            var content = spt.gallery.content;
            //content.setStyle("margin-left", margin + "px");
            new Fx.Tween(content,{duration: 250}).start("margin-left", margin);


            spt.gallery.index = index;
            var total = spt.gallery.total;


            if (index == 0) {
                spt.hide(spt.gallery.left_arrow);
                spt.show(spt.gallery.right_arrow);
            }
            else if (index == total - 1) {
                spt.show(spt.gallery.left_arrow);
                spt.hide(spt.gallery.right_arrow);
            }
            else {
                spt.show(spt.gallery.left_arrow);
                spt.show(spt.gallery.right_arrow);
            }


            // move the shelf
            let shelf_top = spt.gallery.shelf;
            let items = shelf_top.getElements(".spt_gallery_shelf_item");
            let last_item = items[last_index];
            last_item.setStyle("border", "solid 3px transparent");
            last_item.setStyle("opacity", 0.5)


            let item = items[index];
            item.setStyle("border", "solid 3px red");
            item.setStyle("opacity", 1.0);

            let offset = (index * 110) + 55;
            //offset = "calc(50% - "+offset+"px)";
            offset = screen.width/2 - offset;
            new Fx.Tween(shelf_top,{duration: 250}).start("margin-left", offset);

            spt.gallery.last_index = index;

 

            var description = spt.gallery.descriptions[index];
            if (!description) {
                description = (index+1)+" of "+total;
            }
            else {
                description = (index+1)+" of "+total+" - " + description;
            }
            spt.gallery.set_description(description);
        }


        spt.gallery.close = function() {
            var content = spt.gallery.content;
            var gallery_top = content.getParent(".spt_gallery_top");
            var top = gallery_top.getParent(".spt_top");
            spt.behavior.destroy_element(gallery_top);

            // header is sometimes not in view after closing, if a header exists
            // make sure it is scrolled into view
            if (top) {
                var index_header = top.getElement(".spt_index_header");
                if (index_header) {
                    index_header.scrollIntoView();
                }
            }
        }


        spt.gallery.set_description = function(desc) {
            var desc_el = spt.gallery.desc_el;
            desc_el.innerHTML = desc;
        }

        '''
        } )




        scroll = DivWdg(css='spt_gallery_scroll')
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





        content = DivWdg()
        top.add_attr('tabindex','-1')

        scroll.add(content)
        content.add_class("spt_gallery_content")

        # make the items vertically align to bottom (flex-emd)
        # on a regular monitor, align to top (flex-start) is better
        if align == 'bottom':
            align_items = 'flex-end'
        else:
            align_items = 'flex-start'
        content.add_styles("display: flex; flex-flow: row nowrap; align-items: %s; justify-content: center;"%align_items)

        content.add_style("width: %s" % total_width)
        content.add_style("height: calc(100% - 100px)")

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.focus();
            '''
        } )

        top.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.focus();
            '''
        } )
        top.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.blur();
            '''
        } )


        top.add_behavior( {
            'type': 'keydown',
            'cbjs_action': '''
            var key = evt.key;

            if (key == "left") {
                spt.gallery.push_stack(key);
                spt.gallery.show_prev();
            }
            else if (key == "right") {
                spt.gallery.push_stack(key);
                spt.gallery.show_next();
            }
            else if (key == "esc" || key == "enter") {
                spt.gallery.close();
            }



            '''
        } )



        curr_index = 0
        for i, path in enumerate(paths):
            path_div = DivWdg(css='spt_gallery_item')
            content.add(path_div)
            #path_div.add_style("float: left")
            path_div.add_style("display: inline-block")
            path_div.add_style("vertical-align: middle")

            if path == self.curr_path:
                curr_index = i

            try:
                thumb_path = thumb_paths[i]
            except IndexError:
                print("Cannot find the thumb_path [%s] "%i )
                thumb_path = ''

            #path_div.add_style("width: %s" % width)
            #if height:
            #    path_div.add_style("height: %s" % height)
            path_div.add_style("width: 100%")
            path_div.add_style("height: 100%")
            path_div.add_style("overflow-x: hidden")
            path_div.add_style("overflow-y: hidden")

            from tactic.ui.widget import EmbedWdg
            embed = EmbedWdg(src=path, click=False, thumb_path=thumb_path, index=i, controls="true", layout="fit")
            path_div.add(embed)




        content.add_behavior({
            'type': 'load',
            'index': curr_index,
            'cbjs_action': '''
            if (!bvr.index) bvr.index = 0;
            spt.gallery.show_index(bvr.index);
            '''
        } )



        shelf = DivWdg()
        inner.add(shelf)
        shelf.add_style("width: 100%")
        shelf.add_style("height: 100px")
        shelf.add_style("overflow: hidden")
        shelf.add_style("padding-top: 3px")

        inner_shelf = DivWdg()
        shelf.add(inner_shelf)
        inner_shelf.add_class("spt_gallery_shelf")
        inner_shelf.add_style("display: flex")
        inner_shelf.add_style("height: 100%")
        for i, path in enumerate(paths):
            thumb = DivWdg()
            inner_shelf.add(thumb)
            thumb.add_class("spt_gallery_shelf_item")
            thumb.add_style('''background-image: url("%s")''' % path)
            thumb.add_style("background-size", "cover")
            thumb.add_style("background-position", "center")
            thumb.add_style("height: 94px")
            thumb.add_style("width: 100px")
            thumb.add_style("min-width: 100px")
            thumb.add_style("margin: 0px 5px")
            thumb.add_style("border: solid 3px transparent")
            thumb.add_style("box-sizing: border-box")
            thumb.add_style("opacity: 0.5")
            thumb.add_attr("spt_index", i)

        shelf.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': "spt_gallery_shelf_item",
            'cbjs_action': '''


            let index = parseInt(bvr.src_el.getAttribute("spt_index"));
            spt.gallery.show_index(index);

            /*
            let shelf_top = bvr.src_el.getParent(".spt_gallery_shelf");
            let items = shelf_top.getElements(".spt_gallery_shelf_item");
            items.forEach( (item) => {
                item.setStyle("border", "solid 3px transparent");
                item.setStyle("opacity", "0.7")
            } );

            let index = parseInt(bvr.src_el.getAttribute("spt_index"));
            bvr.src_el.setStyle("border", "solid 3px #DDD");
            bvr.src_el.setStyle("opacity", 1.0);

            let offset = (index * 110) + 220;
            //offset = "calc(50% - "+offset+"px)";
            offset = screen.width/2 - offset;
            new Fx.Tween(shelf_top,{duration: 250}).start("margin-left", offset);
            spt.gallery.show_index(index);
            */
            '''
        } )



        icon = IconWdg(title="Close", icon="/context/icons/glyphs/close.png", width="40px")
        inner.add(icon)
        icon.add_style("position: absolute")
        icon.add_style("cursor: pointer")
        icon.add_style("top: 30px")
        icon.add_style("right: 38px")
        icon.add_style("opacity: 0.5")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            spt.gallery.close();
            '''
        } )
        icon.add_style("background", "rgba(48,48,48,0.7)")
        icon.add_style("border-radius", "5px")


        icon = IconWdg(title="Previous", icon="FAS_CHEVRON_LEFT", size="3rem")
        inner.add(icon)
        icon.add_class('spt_left_arrow')
        icon.add_style("cursor: pointer")
        icon.add_style("position: absolute")
        icon.add_style("top: 40%")
        icon.add_style("left: 20px")
        #icon.add_style("opacity: 0.5")
        icon.add_behavior( {
            'type': 'click_up' ,
            'cbjs_action': '''
            var arrow = bvr.src_el;
            spt.gallery.show_prev(arrow);
            '''
        } )
        icon.add_style("background", "rgba(48,48,48,0.7)")
        icon.add_style("border-radius", "5px")


        icon = IconWdg(title="Next", icon="/context/icons/glyphs/chevron_right.png")
        icon = IconWdg(title="Previous", icon="FAS_CHEVRON_RIGHT", size="3rem")
        inner.add(icon)
        icon.add_class('spt_right_arrow')
        icon.add_style("position: absolute")
        icon.add_style("cursor: pointer")
        icon.add_style("top: 40%")
        icon.add_style("right: 20px")
        #icon.add_style("opacity: 0.5")
        icon.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var arrow = bvr.src_el;
            spt.gallery.show_next(arrow);
            '''
        } )
        icon.add_style("background", "rgba(48,48,48,0.7)")
        icon.add_style("border-radius", "5px")




        desc_div = DivWdg()
        desc_div.add_class("spt_gallery_description")
        desc_div.add_style("height: 30px")
        desc_div.add_style("width: %s" % width)
        desc_div.add_style("text-align: center")
        desc_div.add_style("background: rgba(0,0,0,1)")
        desc_div.add_style("color: #bbb")
        desc_div.add_style("font-weight: bold")
        desc_div.add_style("font-size: 16px")
        desc_div.add_style("padding-top: 10px")
        desc_div.add_style("margin-left: -%s" % (width/2))
        desc_div.add_style("z-index: 1000")
        desc_div.add("")

        desc_outer_div = DivWdg()
        inner.add(desc_outer_div)
        desc_outer_div.add_style("position: fixed")
        desc_outer_div.add(desc_div)
        desc_outer_div.add_style("bottom: 0px")
        desc_outer_div.add_style("left: 50%")



        return top



    def get_paths(self, file_type='main'):

        # this is the selected one
        search_key = self.kwargs.get("search_key")

        search_keys = self.kwargs.get("search_keys")
        paths = self.kwargs.get("paths")

        if not paths:
            paths = []


        if search_keys:
            sobjects = Search.get_by_search_keys(search_keys, keep_order=True)

            # return_dict=True defaults to return the first of each snapshot list
            # and so works well with is_latest=True
            if sobjects and sobjects[0].get_base_search_type() == "sthpw/snapshot":
                sobj_snapshot_dict = {}
                for sobject in sobjects:
                    tmp_search_key = sobject.get_search_key()
                    sobj_snapshot_dict[tmp_search_key] = sobject
                snapshots = sobjects

            else:
                sobj_snapshot_dict = Snapshot.get_by_sobjects(sobjects, is_latest=True, return_dict=True)

                snapshots = sobj_snapshot_dict.values()

            file_dict = Snapshot.get_files_dict_by_snapshots(snapshots, file_type=file_type)
            for sobject in sobjects:
                path = ''
                snapshot = sobj_snapshot_dict.get(sobject.get_search_key())
                # it is supposed to get one (latest), just a precaution
                if isinstance(snapshot, list):
                    snapshot = snapshot[0]
                if not snapshot:
                    continue

                file_list = file_dict.get(snapshot.get_code())
                if not file_list:
                    paths.append("")
                    continue



                # NOTE: there should only be one file
                tmp_paths = []
                for file_object in file_list:
                    path = file_object.get_web_path()

                    # If the file type is not supported by web browsers, get the web version
                    # as a fallback.
                    # TODO: Note that this will disable
                    # the retrieval of a sequence of files as in ####.tif case, where
                    # the asset is a sequence of files. So it will only display the web
                    # version of the first file in the asset list.
                    extension = File.get_extension(path)
                    accepted_exts = ['mp4', 'mov', 'jpg', 'png', 'ogg', 'webm']
                    if file_type == 'main' and extension not in accepted_exts:
                        path= snapshot.get_web_path_by_type(type="web")

                    # If the asset is a sequence of files, retrieve all the file paths.
                    # NOTE: In this case, web versions do not exist for all of the files.
                    # The web version is generated only  for the first one in the sequence.
                    if path.find("#") != -1:
                        expanded_paths = snapshot.get_expanded_web_paths()
                        path = "|".join(expanded_paths)

                    tmp_paths.append(path)

                path = "|".join(tmp_paths)
                self.sobject_data[path] = sobject
                paths.append(path)

	            # set the current path the user clicks on
                if not self.curr_path and sobject.get_search_key() == search_key and file_type=='main':
                    self.curr_path = path


        elif paths:
            return paths

        else:
            # TEST
            paths = [
                '/assets/test/store/The%20Boxter_v001.jpg',
                '/assets/test/store/Another%20one_v001.jpg',
                '/assets/test/store/Whatever_v001.jpg'
            ]

        """
        for index,path in enumerate(paths):
            path = urllib.pathname2url(path)
            paths[index] = path
        """

        return paths




