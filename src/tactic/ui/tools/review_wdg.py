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

__all__ = ['ReviewTaskElementWdg', 'ReviewWdg', 'ReviewMediaWdg', 'ReviewActionWdg', 'ReviewCmd']


from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from tactic.ui.widget import ActionButtonWdg, EmbedWdg
from tactic.ui.panel import TableLayoutWdg
from tactic.ui.container import ContentBoxWdg

from pyasm.widget import IconWdg
from tactic.ui.widget import IconButtonWdg
from tactic.ui.input import TextInputWdg

from pyasm.common import jsonloads, jsondumps, Environment, TacticException
from pyasm.web import SpanWdg, DivWdg, Canvas, WebContainer, Table, HtmlElement
from pyasm.command import Command
from pyasm.checkin import FileCheckin, BaseMetadataParser
from pyasm.biz import Snapshot, File, Pipeline, IconCreator
from pyasm.search import Search, SearchType
from pyasm.widget import HiddenWdg, TextWdg, TextAreaWdg, SelectWdg, IconButtonWdg


import dateutil
from dateutil import parser
from datetime import datetime, timedelta

import os
import six


class ReviewTaskElementWdg(BaseTableElementWdg):
    '''This widget opens a review session from a sthpw/task
    sObject entry. The review session is based on snapshots 
    checked into the task.'''

    ARGS_KEYS = {
        'show_content_box': { 'type': 'SelectWdg',
            'category': 'Display',
            'default': 'true',
            'values': 'true|false',
            'order': 1,
            'description': 'Wraps the review tool in a content box, which \
                allows for full screen display.'
        }, 
        'review_note_process': { 'type': 'TextWdg',
            'category': 'Review',
            'order': 2,
            'description': 'Notes created in the review tool will have process \
                    <review_note_process>/<snapshot_process>.'
        }
    }

    def init(self):
        self.snapshot_dict = {}
    
    def get_width(self):
        return 50
  
    def _get_pipeline_dict(self):
        '''build a dictionary of pyasm.biz.Pipeline objects
        by task search key.'''
        
        task_pipeline_dict = {}
        
        sobjects = self.sobjects
        
        pipeline_dict = {}
        for task in sobjects:    
            search_key = task.get_search_key()
            parent = task.get_parent()
            pipeline_code = None
            if parent:
                pipeline_code = parent.get_value("pipeline_code", no_exception=True)
             
            if pipeline_code not in pipeline_dict:
                pipeline = Pipeline.get_by_code(pipeline_code)
            else:
                pipeline = pipeline_dict[pipeline_code]
            
            if pipeline:
                pipeline_dict[pipeline_code] = pipeline
                task_pipeline_dict[search_key] = pipeline
            else:
                pipeline_dict[pipeline_code] = None
                task_pipeline_dict[search_key] = None
        
        return task_pipeline_dict

    def preprocess(self):
        '''build a dictionary by task search key which
        stores the latest snapshots checked into parent
        sObject under task review process, and the 
        review and original processes.'''


        task_pipeline_dict = self._get_pipeline_dict()
        snapshot_dict = {}
        
        sobjects = self.sobjects
        
        # Get snapshot information for each task
        for task in sobjects:    
            # Get the process name 
            search_key = task.get_search_key()
            pipeline = task_pipeline_dict[search_key]
            original_process = task.get_process()
            # If the node is an approval node, get the inputted 
            # process as the review process. Otherwise, the
            # original process is under review.
            review_process = original_process
            if pipeline:
                process_object = pipeline.get_process(original_process)
                node_type = None
                if process_object:
                    node_type = process_object.get_type()
                
                input_processes = None
                if node_type == "approval":
                    input_processes = pipeline.get_input_processes(original_process)
                if input_processes:
                    review_process = input_processes[0].get_name()

            # Attempt to find the snapshots under the review process name
            parent = task.get_parent()
            snapshots = []
            if parent:
                #snapshot = Snapshot.get_latest_by_sobject(parent, process=review_process)
                snapshots = Snapshot.get_by_sobject(parent, process=review_process, is_latest=True)
            
            # Build a dictionary of data pertaining to the task.
            snapshot_data = None
            
            # Build a list of snapshots for this task.
            if snapshots:
                snapshot_data = {}
                
                snapshot_sks = [x.get_search_key() for x in snapshots]
                snapshot_data['snapshots'] = snapshot_sks
                
                snapshot_data['review_process'] = review_process
                snapshot_data['original_process'] = original_process
            
            snapshot_dict[search_key] = snapshot_data
        
        self.snapshot_dict = snapshot_dict

    def get_display(self):
        show_content_box = self.get_option('show_content_box')
        review_note_process = self.get_option('review_note_process')
        if not review_note_process:
            review_note_process = "false"
        div = DivWdg()
        div.add_class("hand")

        sobject = self.get_current_sobject()
        search_key = sobject.get_search_key()
         
        snapshot_data = self.snapshot_dict.get(search_key)
        if not snapshot_data:
            return self.top
        
        snapshots = snapshot_data.get('snapshots')
        review_process = snapshot_data.get('review_process')
        original_process = snapshot_data.get('original_process')

        icon_button = IconButtonWdg(name="spt_review_button", icon=IconWdg.EDIT)
        icon_button.add_behavior( {
            'type': 'click_up',
            'search_key': search_key,
            'snapshots': snapshots,
            'review_process': review_process,
            'original_process': original_process,
            'show_content_box': show_content_box,
            'review_note_process': review_note_process,
            'cbjs_action': '''
                var server = TacticServerStub.get();
                var sobject = server.get_by_search_key(bvr.search_key);
                var status = sobject['status'];
                if (status == "Revise") {
                    spt.alert("Check for revision notes under Revisions using the expand tool. \
                            After submitting a revised file, update your task status, then \
                            review again.");
                } else { 
                    var class_name = 'tactic.ui.tools.ReviewWdg';
                    var title = "Review ["+bvr.review_process+"]";
                    kwargs = {
                        'search_key': bvr.search_key,
                        'snapshot_search_keys': bvr.snapshots,
                        'original_process': bvr.original_process,
                        'review_process': bvr.review_process,
                        'show_content_box': bvr.show_content_box,
                        'review_note_process': bvr.review_note_process,
                        'custom_status': status
                    };
                    spt.tab.set_main_body_tab();
                    spt.tab.add_new(title, title, class_name, kwargs); 
                }
            '''
        })
        
        div.add(icon_button)
        return div



class ReviewWdg(BaseRefreshWdg):
    '''The review tool is used to annotate snapshots which
    are then checked into the parent sObject under a revision context.
    Snapshots are retrieved from sthpw/task, vfx/submission or sthpw/snapshot.'''

    def init(self):
        self.task_data = None

    def get_display(self):

        top = self.top
        
        inner = DivWdg()
        top.add(inner)
        inner.add_style("background", "#111")
        inner.add_style("color", "#FFF")
        inner.add_class("spt_review_top")
        custom_status = self.kwargs.get("custom_status")
        inner.add_attr("spt_custom_status", custom_status)
        
        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        } )
        
        '''
        Get the submitted sObjects for review session with (1) of:

        expression: Specify snapshots
        search_keys: Specify vfx/submission or snapshot search_keys
        search_key: Specify snapshot, vfx/submission or sthpw/task.
        
        *sthpw/task for review must be accompanied by task_data kwarg.
        '''

        expression = self.kwargs.get("expression")
        search_keys = self.kwargs.get("search_keys")
        search_key = self.kwargs.get("search_key")

        if search_key:
            search_keys = [search_key]
        elif search_keys: 
            if isinstance(search_keys, six.string_types):
                try:
                    search_keys = jsonloads(search_keys)
                except ValueError:
                    search_keys = search_keys.split(",")
            try:
                self.sobjects = Search.get_by_search_keys(search_keys)
            except:
                print("Error with finding [%s]" % search_keys)
                self.sobjects = []
        elif expression:
            self.sobjects = Search.eval(expression)
        else:
            self.sobjects = []
 
        # Get snapshots for review session
        self.snapshots = []
        for sobject in self.sobjects:
            if sobject.get_base_search_type() == "sthpw/task":
                # Task data from ReviewTaskElementWdg
                snapshot_sks = self.kwargs.get("snapshot_search_keys")
                original_process = self.kwargs.get("original_process")
                review_process = self.kwargs.get("review_process")
                review_note_process = self.kwargs.get("review_note_process")
                
                # Add snapshots to self.snapshots
                snapshots = None
                first_snapshot = None
                if snapshot_sks:
                    snapshots = Search.get_by_search_keys(snapshot_sks)
                    first_snapshot = snapshot_sks[0]
                
                if snapshots:
                    self.snapshots.extend(snapshots)
                
                # Store task data for child widgets
                self.task_data = {
                    'snapshot': first_snapshot, 
                    'original_process': self.kwargs.get("original_process"),
                    'review_process': self.kwargs.get("review_process")
                }
                
                # Store task data in DOM for js
                inner.add_attr("spt_original_process", original_process)
                inner.add_attr("spt_review_process", review_process)
                inner.add_attr("spt_review_note_process", review_note_process)
            elif sobject.get_base_search_type() == "sthpw/snapshot":
                self.snapshots.append(sobject)
            elif sobject.get_base_search_type() == "vfx/submission":
                snapshot_code = sobject.get("snapshot_code")
                snapshot = Snapshot.get_by_code(snapshot_code)
                self.snapshots.append(snapshot)
            else:
                snapshots = Snapshot.get_latest_by_sobject(sobject, process="publish")
                if snapshots:
                    if isinstance(snapshots, list):
                        self.snapshots.extend(snapshots)
                    else:
                        self.snapshots.append(snapshots)


        snapshots = []
        for snapshot in self.snapshots:
            context = snapshot.get_value("context")
            process = snapshot.get_value("process")
            if not context.startswith("%s/" % process) and context.startswith("review/"):
                continue

            snapshots.append(snapshot)
        self.snapshots = snapshots

         
        #mode = "test"
        mode = None
        if mode == "test":
            #search = Search("sthpw/snapshot")
            #search.add_filter("search_type", "test/store%", op="like")

            search = Search("test/asset")
            #sobject = search.get_sobject()
            search.add_limit(15)
            self.sobjects = search.get_sobjects()
        



        self.ui_settings = self.kwargs.get("ui_settings")
        if self.ui_settings:
            top.add_attr("ui_settings", jsondumps(self.ui_settings))

        table = Table()
        inner.add(table)
        table.add_style("width: 100%")
        table.add_style("height: 100%")
        table.add_style("color", "#FFF")

        table.add_row()
        
        show_media_wdg = self.kwargs.get("show_media_wdg")
        if show_media_wdg not in ['false', False, 'False']:
            td = table.add_cell()
            td.add(self.get_media_wdg() )
            td.add_style("vertical-align: top")
            td.add_style("border: solid 1px #333")
            td.add_style("background", "#000")

        td = table.add_cell()
        td.add_style("border: solid 1px #333")
        td.add_style("vertical-align: top")
        td.add_style("width: 300px")
        td.add(self.get_action_wdg() )

        if len(self.snapshots) > 1:
            tr, td = table.add_row_cell()
            td.add_style("border: solid 1px #333")
            td.add_style("vertical-align: top")
            td.add(self.get_sobjects_wdg() )

        if self.kwargs.get("is_refresh"):
            return inner
        else:
            show_content_box = self.kwargs.get("show_content_box")
            if show_content_box in ["true", "True", True]:
                content_box = ContentBoxWdg(icon="G_CALENDAR", title="Review session")
                content_box.widgets = [top]
                return content_box
            else:
                return top


    def get_media_wdg(self):
        div = DivWdg()
        div.add_style("min-width: 800px")
        div.add_style("min-height: 400px")
        div.add_class("spt_review_media")

        # Choose the first one
        if self.sobjects:
            sobject = self.sobjects[0]
        else:
            sobject = None
     
        media_wdg = ReviewMediaWdg(sobject=sobject, task_data=self.task_data)
        div.add(media_wdg)

        return div




    def get_action_wdg(self):
        div = DivWdg()
        div.add_class("spt_review_action")
        
        if self.sobjects:
            sobject = self.sobjects[0]
            search_key = sobject.get_search_key()
        else:
            sobject = None
            search_key = None

        custom_status = self.kwargs.get("custom_status")
        div.add(ReviewActionWdg(search_key=search_key, task_data=self.task_data, ui_settings=self.ui_settings,
                                custom_status=custom_status))
        return div


    def get_sobjects_wdg(self):
        div = DivWdg()
        div.add_class("spt_review_tiles_top")


        div.add_style("width: 100%")
        #div.add_style("height: 200px")
        div.add_style("overflow-y: auto")

        from tactic.ui.panel import TileLayoutWdg
        layout = TileLayoutWdg(
                search_type="sthpw/snapshot",
                show_shelf=False,
                show_search_limit=False,
                show_scale=False,
                scale=50,
                expand_mode='custom',
                script='''spt.review.load(evt, bvr, mouse_411)'''

        )

        layout.set_sobjects(self.snapshots)
        div.add(layout)

        mapping = {}
        
        for i, snapshot in enumerate(self.snapshots):
            # For the review of task, single snapshot or single
            # submission, there will be 1 sobject
            # for all snapshots.
            if len(self.sobjects) == 1:
                sobject = self.sobjects[0]
            else:
                sobject = self.sobjects[i]
            mapping[snapshot.get_search_key(use_id=True)] = sobject.get_search_key()

        div.add_behavior( {
            'type': 'load',
            'mapping': mapping,
            'cbjs_action': '''
            bvr.src_el.mapping = bvr.mapping;
            '''
        } )


        return div





    def get_onload_js(self):

        on_upload_script = self.kwargs.get("on_upload_script") or ""

        return r'''
spt.review = {}

spt.review.get_task_data = function() {
    var top = document.getElement(".spt_review_top");
    var review_process = top.getAttribute("spt_review_process");
    var original_process = top.getAttribute("spt_original_process");
    var review_note_process = top.getAttribute("spt_review_note_process");

    if (review_process) {
        var task_data = {
            review_process:review_process,
            original_process:original_process,
            review_note_process:review_note_process
        };
        return task_data;
    } else {
        return null;
    }
}

spt.review.top = null;
spt.review.note_top = null;

spt.review.mapping = {};

spt.review.set_top = function(top) {
    spt.review.top = top;
    spt.review.note_top = top.getElement(".spt_review_note_top");
}


spt.review.get_canvas = function() {
    var top = spt.review.top;
    var canvas = top.getElement(".spt_review_canvas");
    return canvas;
}

spt.review.get_draw_canvas = function() {
    var top = spt.review.top;
    var canvas = top.getElement(".spt_review_draw_canvas");
    return canvas;
}



spt.review.load = function(evt, bvr, mouse_411) {

    var top = bvr.src_el.getParent(".spt_review_top");
    var media_el = top.getElement(".spt_review_media");
    var action_el = top.getElement(".spt_review_action");

    var tile_top = bvr.src_el.getParent(".spt_tile_top");
    var snapshot_key = tile_top.getAttribute("spt_search_key");
    var tiles_el = top.getElement(".spt_review_tiles_top");
    spt.review.mapping = tiles_el.mapping;
    var search_key = spt.review.mapping[snapshot_key];
    status = top.getAttribute("spt_custom_status");

    var selected_color = media_el.getElement(".spt_palette_selected");
    var color_selected = selected_color.getAttribute("name");
    var selected_brush = media_el.getElement(".spt_brush_selected");
    var brush_selected = selected_brush.getAttribute("name");

   
    var server = TacticServerStub.get();
    
    // If task is under a review, then get the task data
    var task_data = spt.review.get_task_data();
    
    /* When reviewing a task, pass the task data and parent
       search key to both the media wdg and action wdg.
       When reviewing a submission, the action wdg requires
       the submission search_key and the media wdg requires
       the snapshot search_key. */
    if (task_data) {
        task_data['snapshot'] = snapshot_key;
        var kwargs = {
            search_key: search_key,
            task_data: task_data,
            custom_status: status,
            color_selected: color_selected,
            brush_selected: brush_selected
        }
        var action_kwargs = kwargs;
    } else {
        var kwargs = {
            search_key: snapshot_key, 
            color_selected: color_selected,
            brush_selected: brush_selected
        }
        var action_kwargs = {
            search_key: search_key,
            custom_status:status
        };
    }
    
    // Refresh the Media Wdg
    var class_name = 'tactic.ui.tools.ReviewMediaWdg';
    spt.panel.load(media_el, class_name, kwargs, {}, {show_loading: false});

    // Refresh the Action Wdg
    var class_name = 'tactic.ui.tools.ReviewActionWdg';
    spt.panel.load(action_el, class_name, action_kwargs, {}, {show_loading: false});
}



// drawing tools


spt.review.data = {};
spt.review.data.brush_color = "#F00";
spt.review.data.brush_size = 4;

// undo stack
spt.review.data.bbox = {};
spt.review.data.undo_canvas = [];
spt.review.data.undo_bbox = [];


spt.review.toggle_canvas = function() {
    var top = spt.review.top;
    var canvas = top.getElement(".spt_review_canvas");

    var display = canvas.getStyle("display")
    if (display == "none") {
        canvas.setStyle("display", "");
    }
    else {
        canvas.setStyle("display", "none");
    }
}


spt.review.clear_canvas = function(force) {
    var top = spt.review.top;

    if (force != true && !confirm("Are you sure you wish to clear the canvas?")) {
        return;
    }

    var canvas = top.getElement(".spt_review_canvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    var canvas = top.getElement(".spt_review_draw_canvas");
    var ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}



spt.review.get_brush_data = function() {
    return spt.review.data;
}

spt.review.set_brush_color = function(color) {
    spt.review.data.brush_color = color;
}

spt.review.set_brush_size = function(size) {
    spt.review.data.brush_size = size;
}


spt.review.drag_setup = function(evt, bvr, mouse_411) {

    spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );

    var data = spt.review.data;
    spt.review.data.bbox = {};
}


spt.review.last_pos = null;

spt.review.drag_motion = function(evt, bvr, mouse_411) {

    var canvas = spt.behavior.get_bvr_src( bvr );
    var ctx = canvas.getContext("2d");
    var data = spt.review.get_brush_data();

    ctx.lineWidth = 1;
    //ctx.globalCompositeOperation = 'source-overt';
    ctx.stokeStyle = data.brush_color;
    ctx.fillStyle = data.brush_color;

    var parent = canvas.getParent();
    //parent_pos = parent.getPosition();

    // use canvas position instead
    parent_pos = canvas.getPosition();

    var x_offset = parent.getScroll().x;
    var y_offset = parent.getScroll().y;

    var posx = mouse_411.curr_x - parent_pos.x + x_offset;
    var posy = mouse_411.curr_y - parent_pos.y + y_offset;

    var last_pos = spt.review.last_pos;

    if ( last_pos == null) {
        var dx = 0;
        var dy = 0;
        last_pos = {x: posx, y: posy};
    }
    else {
        var dx = posx - last_pos.x;
        var dy = posy - last_pos.y;
    }

    var size = data.brush_size;

    if (Math.abs(dx) > Math.abs(dy)) {
        if (dy == 0) {
            var slope = 0;
        }
        else {
            var slope = dy/dx;
        }

        ctx.beginPath();
        for (var i = 0; i <= Math.abs(dx); i=i+2) {

            var x = last_pos.x + i;
            var y = last_pos.y + i*slope;

            ctx.arc(x, y, size, 0, 2*Math.PI, true);
            spt.review.expand_bbox(x,y,size);
        }
        ctx.fill();
    }
    else {
        if (dy == 0) {
            var slope = 0;
        }
        else {
            var slope = dx/dy;
        }

        ctx.beginPath();
        for (var i = 0; i <= Math.abs(dy); i=i+2) {

            var x = last_pos.x + i*slope;
            var y = last_pos.y + i;

            ctx.arc(x, y, size, 0, 2*Math.PI, true);
            spt.review.expand_bbox(x,y,size);
        }
        ctx.fill();
    
    }


    ctx.beginPath();
    ctx.arc(posx, posy, size, 0, 2*Math.PI, true);
    ctx.fill();

    spt.review.last_pos = {x: posx, y: posy};
}


spt.review.expand_bbox = function(posx, posy, size) {
    var bbox = spt.review.data.bbox;
    if (!bbox.x1 || posx-size*2 < bbox.x1) {
        bbox.x1 = posx-size*2;
    }
    if (!bbox.x2 || posx+size*2 > bbox.x2) {
        bbox.x2 = posx+size*2;
    }
    if (!bbox.y1 || posy-size*2 < bbox.y1) {
        bbox.y1 = posy-size*2;
    }
    if (!bbox.y2 || posy+size*2 > bbox.y2) {
        bbox.y2 = posy+size*2;
    }
}



spt.review.drag_action = function(evt, bvr, mouse_411) {

    var canvas = spt.behavior.get_bvr_src( bvr );
    var draw_ctx = canvas.getContext("2d");
    var data = spt.review.get_brush_data();

    var parent = canvas.getParent();
    canvas_pos = canvas.getPosition();

    var x_offset = parent.getScroll().x;
    var y_offset = parent.getScroll().y;

    var x = mouse_411.curr_x - canvas_pos.x + x_offset;
    var y = mouse_411.curr_y - canvas_pos.y + y_offset;

    var size = data.brush_size;

    draw_ctx.beginPath();
    draw_ctx.arc(x, y, size, 0, 2*Math.PI, true);
    draw_ctx.fill();

    spt.review.last_pos = null;


    var bbox = spt.review.data.bbox;
    //draw_ctx.rect(bbox.x1, bbox.y1, bbox.x2-bbox.x1, bbox.y2-bbox.y1);
    //draw_ctx.stroke();


    // get main canvas
    var main_canvas = spt.review.get_canvas();
    var main_ctx = main_canvas.getContext("2d");

    // get data drawn
    var undo_canvas = document.id(document.createElement("canvas"));
    undo_canvas.setAttribute("width", bbox.x2 - bbox.x1);
    undo_canvas.setAttribute("height", bbox.y2 - bbox.y1);
    var undo_data = main_ctx.getImageData(bbox.x1, bbox.y1, bbox.x2-bbox.x1, bbox.y2-bbox.y1);
    var undo_ctx = undo_canvas.getContext("2d");
    undo_ctx.putImageData(undo_data, 0, 0);

    // push to the undo
    var undo_canvas_list = spt.review.data.undo_canvas;
    var undo_bbox = spt.review.data.undo_bbox;
    undo_canvas_list.push(undo_canvas);
    undo_bbox.push(bbox);


    // draw on main canvas
    var tmp_canvas = document.id(document.createElement("canvas"));
    tmp_canvas.setAttribute("width", bbox.x2 - bbox.x1);
    tmp_canvas.setAttribute("height", bbox.y2 - bbox.y1);
    var draw_data = draw_ctx.getImageData(bbox.x1, bbox.y1, bbox.x2-bbox.x1, bbox.y2-bbox.y1);
    var tmp_ctx = tmp_canvas.getContext("2d");
    tmp_ctx.putImageData(draw_data, 0, 0);

    var image = new Image();
    image.onload = function() {
        main_ctx.drawImage(image, bbox.x1, bbox.y1);
        draw_ctx.clearRect(bbox.x1, bbox.y1, bbox.x2-bbox.x1, bbox.y2-bbox.y1);
    }
    image.src = tmp_canvas.toDataURL("image/png");

}



spt.review.undo = function() {
    var undo_canvas_list = spt.review.data.undo_canvas;
    if (undo_canvas_list.length == 0) {
        return;
    }
    var undo_bbox = spt.review.data.undo_bbox;

    var undo_canvas = undo_canvas_list.pop();
    var undo_ctx = undo_canvas.getContext("2d");
    var bbox = undo_bbox.pop();

    var main_canvas = spt.review.get_canvas();
    var main_ctx = main_canvas.getContext("2d");

    var data = undo_ctx.getImageData(0,0, bbox.x2-bbox.x1, bbox.y2-bbox.y1);
    main_ctx.putImageData(data, bbox.x1, bbox.y1);

}

spt.review.redo = function() {

}




spt.review.save = function(search_key, status) {
    var top = spt.review.top;
    var note_top = spt.review.note_top;
    var canvas = top.getElement(".spt_review_canvas");

    var video = top.getElement("video");
    var image = top.getElement("img");

    var data_url = canvas.toDataURL("image/png");
    var background_src = canvas.getAttribute("spt_background_src");


    var width = canvas.width;
    var height = canvas.height;
    var aspect = width/height;


    // composite the background image iwth the drawing
    if (video) {
        var image = video;
        var image_width = video.videoWidth;
        var image_height = video.videoHeight;

        image_width = height / image_height * image_width;
        image_height = height / image_height * image_height;

        var offset_width = (width - image_width) / 2;

        var data = spt.review.control.get_data();
        var current_time = video.currentTime;
        var frame = parseInt(current_time * data.fps);
    }
    else {
        var image_width = image.getStyle("width");
        var image_height = image.getStyle("height");
        if (image_height == "100%") {
            var size = image.getSize();
            image_height = size.y;
        }
        else {
            image_height = parseInt( image.getStyle("height").replace("px","") );
        }

        var image_width = parseInt( image.getStyle("width").replace("px","") );
        var offset_width = (width - image_width) / 2;
        var image = new Image();
        var current_time = -1;
        var frame = -1;
    }

    // composite the image with the strokes
    var final_canvas = document.id(document.createElement("canvas"));
    final_canvas.setAttribute("width", canvas.width);
    final_canvas.setAttribute("height", canvas.height);
    //document.body.appendChild(final_canvas);
    var final_ctx = final_canvas.getContext("2d");


    image.onload = function() {
        final_ctx.drawImage(image, offset_width, 0, image_width, image_height);

        var image2 = new Image();
        image2.onload = function() {
            final_ctx.drawImage(image2, 0, 0);

            var final_data_url = final_canvas.toDataURL("image/png");
            spt.review.upload(search_key, status, final_data_url, current_time);

            spt.review.clear_canvas(true);
        }
        image2.src = data_url;


    };

    if (video) {
        image.onload()
    }
    else {
        image.src = background_src;
    }


}


spt.review.upload = function(search_key, status, data_url, current_time) {
    spt.app_busy.show("Saving ...");
    
    var top = spt.review.top;
    var note_top = spt.review.note_top;
    var canvas = top.getElement(".spt_review_canvas");
    var background_src = canvas.getAttribute("spt_background_src");

    // Get task data if it exists
    var task_data = spt.review.get_task_data();
    if (task_data) {
        review_note_process = task_data['review_note_process']
        if (!review_note_process) {
            review_note_process = "false";
        }
    } else {
        review_note_process = "false";
    }

    var server = TacticServerStub.get();
    ticket = server.start();

    // All files are uploaded with this filename
    var num = parseInt( Math.random()*10000 );
    var filename = "review-"+num+".png";

    // Get Upload server
    site = server.get_site();
    if (site && site != "default") {
        upload_server = "/tactic/"+site+"/default/UploadServer/"
    }
    else {
        upload_server  = "/tactic/default/UploadServer/"
    }
 
    // Prepare request boundary
    var boundary = '---------------------------';
    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    boundary += Math.floor(Math.random()*32768);
    
    // Prepare request body
    var body = '';
    body += '--' + boundary; 
    body += '\r\n';
    body += 'Content-Disposition: form-data; name="transaction_ticket"';
    body += '\r\n';
    body += '\r\n';
    body += ticket;
    body += '\r\n';
    body += '--' + boundary; 
    body += '\r\n';
    body += 'Content-Disposition: form-data; name="file"; filename="'+filename+'"';
    body += '\r\n';
    body += '\r\n';
    body += data_url;
    body += '\r\n';
    body += '--' + boundary + '--';
    body += '\r\n';
    body += '\r\n';

    var run_cmd = function(try_again) { 
        var values = spt.api.get_input_values(note_top, null, false);

        var note = values.note;
        if (current_time != -1) {
            var data = spt.review.control.get_data();
            var timecode = spt.review.control.get_timecode(current_time, data.fps);
            note = timecode + ": " + note;
        }
        var process = values.process;
        var snapshot_key = values.snapshot_key;

        var cmd = "tactic.ui.tools.ReviewCmd";
        var args = {
            search_key: search_key,
            snapshot_key: snapshot_key,
            process: process,
            review_note_process: review_note_process,
            note: note,
            status: status,
            ticket: ticket,
            filename: filename,
            background_src: background_src,
        }
    
        var on_error = function(err) {
            if (try_again) {
                message = "Upload failed with the following message: " + spt.exception.handler(err) + ". Try again?";
                spt.confirm(message, try_again, function() {server.abort();}, {});
            } else {
                server.abort();
                spt.alert("Upload failed. Contact your system administrator.")
            }
        };
        
        on_complete = function() {
            server.finish();

            ''' + on_upload_script + '''
        };

        var kwargs = {on_complete: on_complete, on_error:on_error};  

        try {
            server.execute_cmd(cmd, args, [], kwargs);
            if (status == "Reject" || status == "Revise") {
                var alert = "Revision checked in under  review/" + process + ".";
            } else if (status == "Approve") {
                var alert = "Revision checked in under approved/" + process + ".";
            } else if (status == "Client") {
                var alert = "Revision checked in under upload/" + filename + ".";
            } else if (status == "Attach") {
                var alert = "Revision checked in under attachment/" + filename + ".";
            }
            spt.app_busy.hide();
            spt.info(alert);
        } catch(err) {
            spt.app_busy.hide();
            on_error(err);
        }
    }
    
    // Upload method 
    upload_request = function(upload_server, boundary, body, try_again) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", upload_server, true);
        xhr.setRequestHeader("Content-Type", 'multipart/form-data; boundary=' + boundary);

        xhr.onreadystatechange = function (e) {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    run_cmd(try_again);
                } else {
 
                    // HACK to bypass error caused by site/project not being registered
                    // resend request.
                    if (xhr.status == "404" && !spt.review.upload_attempt) {
                        spt.review.upload_attempt = true;
                        try_again();
                        spt.review.upload_attempt = false;
                        return;
                    }
                    
                    spt.app_busy.hide(); 
                    if (try_again) {
                        message = "Upload failed with code " + xhr.status + " and message: " + xhr.statusText + ". Try again?";
                        spt.confirm(message, try_again, function() {server.abort();}, {});
                    } else {
                        server.abort();
                        spt.alert("Upload failed again code " + xhr.status + " and message: " + xhr.statusText + ".");
                    }
                }
            } 
        };
        
        xhr.onerror = function (e) {
            // TODO: Create human readable message from e error type
            log.critical(e)
            spt.app_busy.hide(); 
            if (try_again) {
                spt.confirm("Upload failed. Try again?", try_again, function() {server.abort();}, {});
            } else {
                server.abort();
                spt.alert("Upload failed. Contact your system administrator.")
            }
        };    
    
        xhr.send(body)
    }
    
    try_again = function() {
        upload_request(upload_server, boundary, body);
    }

    upload_request(upload_server, boundary, body, try_again);

}

spt.review.show_info = function() {
    var hud_div = bvr.src_el.getElement(".spt_info_hud");
    if (hud_div.style.display == "none"){
        hud_div.style.display = "inline";
    } else {
        hud_div.style.display = "none";
    }
}



        '''





class ReviewMediaWdg(BaseRefreshWdg):
    '''displays image or video from snapshot under review. Includes
    annotation tools.''' 
    
    def get_display(self):
        top = self.top
        top.add_style("position: relative")
        top.add_class("SPT_DTS")
        top.add_class("spt_review_player_top")

        div = DivWdg()
        top.add(div)
        #div.add_style("padding: 15px")
        div.add_attr("data: ", '')
        div.add_style("position: relative")
        #div.add_style("overflow: auto")


        sobject = None
        search_key = self.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
        else:
            sobject = self.kwargs.get("sobject")


        src = None
        if sobject:
            if sobject.get_base_search_type() == "sthpw/snapshot":
                snapshot = sobject
            elif sobject.get_base_search_type() == "sthpw/task":
                task_data = self.kwargs.get('task_data')
                snapshot_sk = task_data.get('snapshot')
                snapshot = Search.get_by_search_key(snapshot_sk)
            elif sobject.get_base_search_type() == "vfx/submission":
                snapshot_code = sobject.get("snapshot_code")
                snapshot = Snapshot.get_by_code(snapshot_code)
            else:
                snapshot = Snapshot.get_latest_by_sobject(sobject, skip_contexts=['review','icon'])
            
            if snapshot:
                src = snapshot.get_web_path_by_type("main")
                web_src = snapshot.get_web_path_by_type("web")
                lib_src = snapshot.get_lib_path_by_type("main")
                file_src = snapshot.get_path_by_type("main", "source")
            else:
                return div
        else:
            div = DivWdg()
            embed = EmbedWdg()
            div.add(embed)
            return div

        #if not src:
        #    src = "/assets/ingest/media/Big Test_v001.mp4"

        
        # Use main file for videos and web version for images
        # TODO: Add file type chooser
        media_type = File.get_media_type_by_path(src)
        is_video = False
        is_document = False
        is_image = False
        if media_type == "video":
            is_video = True
        elif media_type == "document":
            is_document = True
        elif media_type == "image":
            is_image = True
        
        if not web_src:
            web_src = src
        
        if is_image:
            src=web_src
        
        extension = File.get_extension(src)
        accepted_exts = ['mp4', 'mov', 'jpg', 'png', 'ogg', 'webm', 'pdf']
        
        if extension not in accepted_exts:
            message_div = DivWdg()
            div.add(message_div)
            message_div.add(".%s files are not currently viewable in the Review Tool. Supported formats are .jpg, .png, .ogg, .webm, .mov and .mp4" % extension)
            message_div.add_style("text-align", "center")
            message_div.add_style("padding", "300px 50px 300px 50px")
            message_div.add_style("font-size", "1.5em")
            return top

        content_wdg = DivWdg()
        div.add(content_wdg)
        content_wdg.add_style("position: relative")
        content_wdg.add_style("margin-left: 60px")

        embed_div = DivWdg()
        content_wdg.add(embed_div)
        embed_div.add_class("spt_review_image")
        embed_div.add_styles("display: flex; align-items: center; justify-content: center;")

        from pyasm.web import Canvas

        height = 600
        width = 800

        if is_document: 
            from pyasm.web import HtmlElement
            embed = HtmlElement.iframe()
            embed.set_attr('src', src)
            embed.add_style("width: 800px")
            embed.add_style("height: 600px")
            content_wdg.add_style("margin-bottom: 15px")
        elif is_video:
            embed = EmbedWdg(src=src, poster=web_src, preload="auto", controls=False)
            embed_div.add_style("height", height)
            embed_div.add_style("width", width)
            content_wdg.add_style("margin-bottom: 30px")
        else:
            from pyasm.web import HtmlElement
            embed = HtmlElement.img(src)
            embed.add_styles("max-height: 100%; max-width: 100%;")
            embed_div.add_style("height", height)
            embed_div.add_style("width", width)
        embed.add_class("spt_embedded_media")
        embed_div.add(embed)

        # HUD: Display aspect ratio, display repo name and source file name.
        aspect_ratio = None
        parser = BaseMetadataParser.get_parser_by_path(lib_src, prefs={"image": ["PIL"]})
        img_info = parser.get_tactic_metadata()

        
        img_width, img_height = None, None
        if img_info:
            img_width = img_info.get("width")
            img_height = img_info.get("height")
        if img_width and img_height:
            try:
                img_width = float(img_width)
                img_height = float(img_height)
                if img_height > 0:
                    aspect_ratio = (img_width/img_height)
                    if aspect_ratio <= 1:
                        embed.add_style("height", height)
                        width = int(aspect_ratio*height)
                    else:
                        embed.add_style("width", width)
                        height = int(1/aspect_ratio*width)
            except (TypeError, ValueError) as e:
                pass

        if is_video or is_image:
            embed.add_behavior({
                'type': 'load',
                'background_src': src,
                'width': width,
                'height': height,
                'cbjs_action': '''

                embedded_media = bvr.src_el;
                size = embedded_media.getSize();
                width = bvr.width;
                height = bvr.height;
                parent = bvr.src_el.getParent();
                canvas_list = parent.getSiblings(".spt_canvas_element");
                // The canvas size must be set after onload of the image or video
                set_canvas_sizes = function() {
                    if (this) {
                        width = this.width;
                    }
                    for (var i = 0; i<canvas_list.length; i++) {
                        canvas = canvas_list[i];
                        canvas.setAttribute("width", width);
                        canvas.setAttribute("height", height);

                        if (canvas.hasClass("spt_review_image_canvas")) {    
                            var context = canvas.getContext('2d');

                            // load image from data url
                            var imageObj = new Image();
                            imageObj.onload = function() {
                                if (imageObj.height > imageObj.width) {
                                    context.drawImage(this, 0, 0, width, width * imageObj.height / imageObj.width);
                                }
                                else {
                                    context.drawImage(this, 0, 0, height * imageObj.width / imageObj.height, height);
                                }
                            };
                            imageObj.src = bvr.background_src;
                        }
                    } 
                };

                // If the width is 0, then set sizes after load.
                if (width == 0) {
                    embedded_media.onload = set_canvas_sizes; 
                } else {
                    set_canvas_sizes();
                }                
                '''
            })

            embed_div.add_style("pointer-events: none")
            
            image_canvas = Canvas()
            image_canvas.add_class("spt_review_image_canvas")
            image_canvas.add_class("spt_canvas_element")
            content_wdg.add(image_canvas)
            image_canvas.add_style("position", "absolute")
            image_canvas.add_style("top: 0px")
            image_canvas.add_style("left: 0px")
            image_canvas.add_style("z-index", "1")
            image_canvas.add_attr("spt_background_src", src)

            if height >= width:
                image_canvas.add_style("left", "50%")
                image_canvas.add_style("margin-left", "-%d" % (width/2))
            else:
                image_canvas.add_style("top", "50%")
                image_canvas.add_style("margin-top", "-%d" % (height/2))

            # FIXME: is this needed for images?  For video, the low
            # res frame will be put here.
            if not is_video:
                # image is not centered and not necessary
                image_canvas.add_style("opacity", "0")


            canvas = Canvas()
            canvas.add_class("spt_review_canvas")
            canvas.add_class("spt_canvas_element")
            content_wdg.add(canvas)
            canvas.add_style("position", "absolute")
            canvas.add_style("top: 0px")
            canvas.add_style("left: 0px")
            canvas.add_style("z-index", "2")
            canvas.add_attr("spt_background_src", src)

            if height >= width:
                canvas.add_style("left", "50%")
                canvas.add_style("margin-left", "-%d" % (width/2))
            else:
                canvas.add_style("top", "50%")
                canvas.add_style("margin-top", "-%d" % (height/2))


            draw_canvas = Canvas()
            draw_canvas.add_class("spt_review_draw_canvas")
            draw_canvas.add_class("spt_canvas_element")
            content_wdg.add(draw_canvas)
            draw_canvas.add_style("position", "absolute")
            draw_canvas.add_style("top: 0px")
            draw_canvas.add_style("left: 0px")
            draw_canvas.add_style("z-index", "3")
            draw_canvas.add_style("cursor", "crosshair")

            if height >= width:
                draw_canvas.add_style("left", "50%")
                draw_canvas.add_style("margin-left", "-%d" % (width/2))
            else:
                draw_canvas.add_style("top", "50%")
                draw_canvas.add_style("margin-top", "-%d" % (height/2))

            div.add_behavior( {
                'type': 'wheelX',
                'cbjs_action': '''

                var scale = 0;
                if (evt.wheel > 0) {
                    scale = 1.10;
                }
                else {
                    scale = 1/1.10;
                }

                var els = [];
                els.push( bvr.src_el.getElement(".spt_review_canvas") );
                els.push( bvr.src_el.getElement(".spt_review_draw_canvas") );
                els.push( bvr.src_el.getElement(".spt_review_image_canvas") );

                for (var i = 0; i < els.length; i++) {
                    var el = els[i];

                    if (!el.scale) {
                        el.scale = scale;
                    }
                    else {
                        el.scale = el.scale * scale;
                    }
                    el.setStyle("transform", "scale("+el.scale+")");

                }


                '''
            } )



            div.add_behavior( {
                'type': 'smart_drag',
                'bvr_match_class': 'spt_review_draw_canvas',
                'ignore_default_motion' : True,
                "cbjs_setup": 'spt.review.drag_setup( evt, bvr, mouse_411 );',
                "cbjs_motion": 'spt.review.drag_motion( evt, bvr, mouse_411 );',
                "cbjs_action": 'spt.review.drag_action( evt, bvr, mouse_411 );'
            } )


            div.add( self.get_canvas_tool_wdg() )

        # HUD: Display aspect ratio, display repo name and source file name.
        aspect_ratio = None
        if is_image or is_video:
            parser = BaseMetadataParser.get_parser_by_path(lib_src, prefs={"image": ["PIL"]})
            img_info = parser.get_tactic_metadata()
            
            width, height = None, None
            if img_info:
                width = img_info.get("width")
                height = img_info.get("height")
            if width and height:
                try:
                    width = float(width)
                    height = float(height)
                    if height > 0:
                        aspect_ratio = "%.2f" % (width/height)
                except (TypeError, ValueError):
                    pass

        hud_div = DivWdg()
        content_wdg.add(hud_div)
        hud_div.add_class("spt_info_hud")
        hud_div.add_styles("display: none; bottom: 10; left: 10; position: absolute; color: white;\
                           text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; \
                           font-size: 15px; z-index: 5;")
        hud_div.add_style("background-color: rgba(128, 128, 128, 0.5);")
        if aspect_ratio:
            hud_div.add("Aspect ratio: %s\n" % aspect_ratio)
            hud_div.add("</br>")
        hud_div.add("Display source file: %s\n" % os.path.basename(src))
        hud_div.add("</br>")
        hud_div.add("Main source file: %s\n" % os.path.basename(file_src))

        if is_video:
            content_wdg.add_style("z-index: 0")
            controller = ReviewVideoControlWdg(lib_dir=lib_src, web_dir=src)
            top.add(controller)
            controller.add_style("z-index: 4")


        return top


    def get_canvas_tool_wdg(self):
        
        
        div = DivWdg()
        div.add_style("position: absolute")
        div.add_style("top: 0")
        div.add_style("left: 0")
        div.add_class("spt_review_tool")





        div.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_review_button',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "0.5");
            //bvr.src_el.setStyle("border", "solid 1px white");
            '''
        } )

        div.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_review_button',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            //bvr.src_el.setStyle("border", "solid 1px #333");
            '''
        } )
    
        palette_style = HtmlElement.style()
        div.add(palette_style)
        palette_style.add('''
        .spt_palette_outer {
            margin-left: auto;
            margin-right: auto;
            margin-top: 10px;
            margin-bottom: 10px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }

        .spt_palette_outer:before {
            display: block;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #fff;
            height: 1px;
            top: 50%;
            z-index: -1;
        }

        .spt_palette_color {
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-top: 10px;
            margin-bottom: 10px;
            width: 18px;
            height: 18px;
            position: relative;
            border-radius: 50%;
        }

        .spt_palette_color:hover {
            color: #555;
            background: #f5f5f5;
        }

        .spt_palette_color:before {
            content: "";
            display: block;
            background: #fff;
            border-top: 2px solid #ddd;
            position: absolute;
            top: -18px;
            left: -18px;
            bottom: -18px;
            right: -18px;
            z-index: -1;
            border-radius: 50%;
            box-shadow: inset 0px 8px 48px #ddd;
        }

        ''')
        color_selected = self.kwargs.get("color_selected") or 'red'
        
        for i, color in enumerate(['red', 'green', 'blue', 'orange', 'magenta', 'cyan',  '#000', '#FFF']):
            outer_div = DivWdg()
            outer_div.add_class("spt_palette_outer")
            outer_div.add_style("background-color", color)
            outer_div.add_attr("name", color)
            div.add(outer_div)

            color_div = DivWdg()
            color_div.add_class("spt_palette_color")
            outer_div.add(color_div)

            
            if color_selected == color:
                outer_div.add_style("border", "3px solid #99B9FF")
                outer_div.add_class("spt_palette_selected")
                color_div.add_style("display", "none") 
            
            color_div.add_style("box-shadow", "0px 3px 8px #000, inset 0px 2px 3px #fff"); 
            color_div.add_style("background-color", color)

            color_div.add_class("spt_review_color")
            

            color_div.add_behavior( {
                'type': 'click_up',
                'color': color,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_review_top");
                spt.review.set_top( top );
                spt.review.set_brush_color(bvr.color);

                var buttons = top.getElements(".spt_review_color");
                for (var i = 0; i < buttons.length; i++) {
                    buttons[i].setStyle("display", "");
                    outer = buttons[i].getParent(".spt_palette_outer");
                    outer.setStyle("border", "");
                    outer.removeClass("spt_palette_selected");
                }

                bvr.src_el.setStyle("display", "none");
                outer = bvr.src_el.getParent(".spt_palette_outer");
                outer.setStyle("border", "3px solid #99B9FF");
                outer.addClass("spt_palette_selected");
                
                '''
            } )

        div.add("<br/><br/>")
        
        # Pencil icon and pencil size buttons
        pencil_div = DivWdg()
        div.add(pencil_div)
        pencil_div.add_style("height: 24")
        pencil_div.add_style("width: 24")
        pencil_div.add_style("margin: 15px")
        pencil_div.add_style("padding: 3px")

        #icon = IconWdg(icon="FA_EDIT", opacity=1.0, size=16,
        #               name="Select a pencil size")
        #pencil_div.add(icon)

        brush_selected = self.kwargs.get("brush_selected") or "4"
        brush_selected = int(brush_selected)

         
        for size in [ 1, 4, 10, 20 ]:
            brush_div = DivWdg()
            brush_div.add_class("spt_review_button")
            brush_div.add_class("spt_review_brush")
            brush_div.add_attr("name", size)
            div.add(brush_div)
            
            brush_div.add_style("width", 30)
            brush_div.add_style("height", size*1.7+6)
            
            brush_div.add_style("margin-top", "15")
            brush_div.add_style("margin-buttom", "15")
            brush_div.add_style("margin-left", "auto")
            brush_div.add_style("margin-right", "auto")

            
            icon = IconWdg(icon="FA_PAINT_BRUSH", opacity=1.0, size=size,
                           name="Brush Size")
            brush_div.add(icon)
            brush_div.add_style("color", "#000")
            brush_div.add_style("display: flex")
            brush_div.add_style("justify-content: space-around")
            brush_div.add_style("align-items: center")
            brush_div.add_style("border-radius: 5px")
            
            brush_div.add_style("background-color", "white")

            if size == brush_selected:
                brush_div.add_style("border", "1px solid #F00") 
                brush_div.add_style("border-style", "groove") 
                brush_div.add_class("spt_brush_selected")
            
            brush_div.add_behavior( {
                'type': 'click_up',
                'size': size,
                'cbjs_action': '''
                spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
                spt.review.set_brush_size(bvr.size);

                var top = bvr.src_el.getParent(".spt_review_tool");
                var els = top.getElements(".spt_review_brush")
                for (var i = 0; i < els.length; i++) {
                    els[i].setStyle("border", "");
                    els[i].setStyle("border-style", "");
                    els[i].removeClass("spt_brush_selected");
                }

                bvr.src_el.setStyle("border", "1px solid #F00");
                bvr.src_el.setStyle("border-style", "groove");
                bvr.src_el.addClass("spt_brush_selected");
                '''
            } )
     
        div.add("<br/><br/>")

        # Undo button
        undo_div = DivWdg()
        div.add(undo_div)
        undo_div.add_style("height: 24")
        undo_div.add_style("width: 24")
        undo_div.add_style("margin: 15px")
        undo_div.add_style("padding: 3px")
        #undo_div.add_style("-webkit-transform", "scale(-1, 1)")
        undo_div.add_class("hand")

        icon = IconWdg(icon="FA_UNDO", opacity=1.0, size=16,
                       name="Undo your last brush stroke")
        icon.add_class("spt_undo_button")
        undo_div.add(icon)

        undo_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
            spt.review.undo();
            '''
        } )

        # Clear canvas button
        clear_div = DivWdg()
        div.add(clear_div)
        clear_div.add_style("height: 24")
        clear_div.add_style("width: 24")
        clear_div.add_style("margin: 15px 15px 15px 13px")
        clear_div.add_style("padding: 3px")
        clear_div.add_class("hand")

        icon = IconWdg(icon="FA_TRASH", opacity=1.0, size=16,
                       name="Clear your canvas")
        clear_div.add(icon)

        clear_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
            spt.review.clear_canvas();
            '''
        } )

        div.add("<br/><br/>")

        info_div = DivWdg()
        div.add(info_div)
        info_div.add_style("heigh: 24")
        info_div.add_style("width: 24")
        info_div.add_style("margin: 15px")
        info_div.add_style("padding: 3px")
        info_div.add_class("hand")
        icon = IconWdg(icon="FA_INFO", opacity=1.0, size=16,
                       name="Display image info")
        info_div.add(icon)

        info_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
            spt.review.show_info();
            '''
        } )



        return div





class ReviewVideoControlWdg(BaseRefreshWdg):
    '''allow user to select specific frames in 
    review sessions to make annotations.'''
   
    def get_display(self):

        top = self.top
        top.add_class("spt_review_control")
        top.add_style("padding: 20px")




        lib_dir = self.kwargs.get("lib_dir")
        web_dir = self.kwargs.get("web_dir")

        # make sure all of the frames are there
        dirname = os.path.dirname(lib_dir)
        basename = os.path.basename(lib_dir)


        frame_dir = "%s/%s.frames" % (dirname, basename)
        web_frame_dir = "%s.frames" % web_dir

        from subprocess import  Popen, check_output, CalledProcessError, PIPE

        # create frames if the frame directory does not exist
        if not os.path.exists(frame_dir):

            os.makedirs(frame_dir)

            command = [
                'ffmpeg',
                '-i',
                lib_dir,
                '-vf',
                'scale=120:80,fps=2',
                '%s/out%%04d.jpg' % frame_dir
            ]

            try:
                Popen(command, shell=False, stdout=PIPE, stderr=PIPE)
            except CalledProcessError as e:
                # delete frames directory on error
                import shutil
                shutil.rmtree(frame_dir)

                print("Error: %s" % e)

        # extract total number of frames (prefer ffprobe call)
        command = [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                lib_dir
        ]

        try:
            seconds = float(check_output( command, stderr=PIPE ).decode())
            num_thumbs = int(seconds * 2)
        except CalledProcessError as e:
            print("Error: %s" % e)
            items = os.listdir(frame_dir)
            num_thumbs = len(items)

        top.add_attr("spt_frame_dir", web_frame_dir)
        top.add_attr("spt_num_thumbs", num_thumbs)

        top.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            bvr.src_el.setStyle("box-shadow", "0px 0px 15px rgba(255,0,0,0.5)");
            var text = bvr.src_el.getElement(".spt_keypress");
            text.focus();
            '''
        } )

        top.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.setStyle("box-shadow", "");
            var text = bvr.src_el.getElement(".spt_keypress");
            text.blur();
            '''
        } )

        top.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_review_control_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("color", "red");
            '''
        } )
        top.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_review_control_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("color", "");
            '''
        } )



        from pyasm.widget import TextWdg
        text = TextWdg("name", "keypress")
        text.add_style("position", "absolute")
        text.add_style("left", "-500px")
        text.add_class("spt_keypress")
        text.add_attr("tabindex", "1")
        top.add(text)
        text.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_review_player_top");
            var player = spt.video.get_player(top);

            var data = spt.review.control.get_data();

            var key = evt.key;
            if (key == "left") {
                var current_time = player.currentTime;
                var frame = current_time * data.fps;

                if (evt.shift) {
                    frame = frame - 5;
                }
                else {
                    frame = frame - 1;
                }

                var sec = frame / data.fps;
                var sec_per_pixel = data.duration / data.width;
                var pos = sec / sec_per_pixel;

                //spt.review.control.set_to_pos(pos);
                player.currentTime = sec;

            }
            else if (key == "right") {
                var current_time = player.currentTime;
                var frame = current_time * data.fps;

                if (evt.shift) {
                    frame = frame + 5;
                }
                else {
                    frame = frame + 1;
                }

                var sec = frame / data.fps;
                var sec_per_pixel = data.duration / data.width;
                var pos = sec / sec_per_pixel;

                //spt.review.control.set_to_pos(pos);
                player.currentTime = sec;
            }


            '''
        } )




        top.add_behavior({
        'type': 'load',
        'cbjs_action': self.get_onload_js()
        })

        top.add_behavior({
        'type': 'load',
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_review_player_top");
        var player = spt.video.get_player(top);
        var video = spt.video.get_player_el(top);

        spt.review.control.set_top(top);


        var handle = top.getElement(".spt_review_drag_handle");
        var timecode_el = top.getElement(".spt_review_timecode");

        video.addEventListener("timeupdate", function() {

            var data = spt.review.control.get_data();

            var percent = parseInt(video.currentTime/data.duration*1000)/10;
            var pos = percent/100*data.width;

            spt.review.control.set_top(top);
            spt.review.control.set_to_pos(pos);
            //handle.setStyle("left", pos);

            var sec_per_pixel = data.duration / data.width;
            var sec = sec_per_pixel * pos;

            var timecode = spt.review.control.get_timecode(sec, data.fps);
            timecode_el.innerHTML = timecode;

        } )

        video.addEventListener("loadedmetadata", function(evt) {
            spt.review.control.init(top);
            spt.review.control.set_to_pos(0);
        })

        '''
        })


        icon = IconWdg(name="icon", icon="FAS_PLAY")
        icon.add_class("spt_review_control_item")
        icon.add_style("cursor", "pointer")
        icon.add_style("margin-right: 10px")
        top.add(icon)
        icon.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_review_player_top");
            var player = spt.video.get_player(top);
            player.play();
            '''
        })




        icon = IconWdg(name="icon", icon="FAS_PAUSE")
        icon.add_class("spt_review_control_item")
        icon.add_style("cursor", "pointer")
        icon.add_style("margin-right: 10px")
        top.add(icon)
        icon.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_review_player_top");
            var player = spt.video.get_player(top);
            player.pause();
            '''
        })

        timecode_div = DivWdg()
        top.add(timecode_div)
        timecode_div.add_class("spt_review_timecode")
        timecode_div.add_style("display: inline-block")
        timecode_div.add_style("width: 80px")
        timecode_div.add_style("margin: 0px 5px")
        timecode_div.add("00:00")


        timeline_width = 500
        timeline_div = DivWdg()
        top.add(timeline_div)
        timeline_div.add_class("spt_review_timeline")
        timeline_div.add_style("width: %s" % timeline_width)
        timeline_div.add_style("height: 12px")
        timeline_div.add_style("border: solid 1px white")
        timeline_div.add_style("box-shadow: 0px 0px 15px rgba(255,0,0,0.5)")
        timeline_div.add_style("border-radius: 5px")
        timeline_div.add_style("display: inline-block")
        timeline_div.add_style("position: absolute")
        timeline_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_review_top");
            var player = spt.video.get_player(top);
            player.pause();

            setTimeout( function() {
                var pos = bvr.src_el.getPosition();
                var width = bvr.src_el.getSize().x

                var timeline_pos = mouse_411.curr_x - pos.x;
                spt.review.control.set_top(top);
                spt.review.control.set_to_pos(timeline_pos);

                var data = spt.review.control.get_data();
                var fps = data.fps;
                var width = data.width;
                var duration = data.duration;
                var sec_per_pixel = duration / width;

                var sec = sec_per_pixel * timeline_pos;
                player.currentTime = sec;


            }, 200 )

            '''
        } )

        handle_div = DivWdg()
        handle_div.add_class("spt_review_control_item")
        timeline_div.add(handle_div)
        handle_div.add_style("cursor", "ew-resize")
        handle_div.add_class("spt_review_drag_handle")
        handle_div.add_style("width: 10px")
        handle_div.add_style("height: 26px")
        handle_div.add_style("border: solid 1px white")
        handle_div.add_style("position: absolute")
        handle_div.add_style("top: -6")
        handle_div.add_style("left: 0")
        handle_div.add_style("border-radius: 5px")
        handle_div.add_style("background: #999")
        top.add_behavior( {
        'type': 'smart_drag',
        'bvr_match_class': 'spt_review_drag_handle',
        'ignore_default_motion' : True,
        'cbjs_setup': '''
            spt.review.drag_el = spt.get_event_target(evt);
            spt.review.start_pos = {x: mouse_411.curr_x, Y: mouse_411.curr_y};
            var top = bvr.src_el;
            var thumb = top.getElement(".spt_review_drag_image").getElement("img");
            var timeline_el = top.getElement(".spt_review_timeline");
            var timecode_el = top.getElement(".spt_review_timecode");

            var width = timeline_el.getSize().x;
            var left = spt.review.drag_el.getStyle("left");

            spt.review.left = parseInt(left.replace("px", "") );
            spt.review.thumb = thumb;


            var review_top = bvr.src_el.getParent(".spt_review_player_top");
            spt.review.player = spt.video.get_player(review_top);
            spt.review.player_el = spt.video.get_player_el(review_top);
            spt.review.timecode_el = timecode_el;

            var canvas = spt.review.control.top.getElement(".spt_review_image_canvas");
            canvas.setStyle("display", "");


        ''',
        'cbjs_motion': '''
            var dx = mouse_411.curr_x - spt.review.start_pos.x;
            var dy = mouse_411.curr_y - spt.review.start_pos.y;

            var new_pos = spt.review.left + dx;

            var data = spt.review.control.get_data();
            var fps = data.fps;
            var width = data.width;
            var duration = data.duration;
            var sec_per_pixel = duration / width;
            var num_thumbs = data.num_thumbs;


            // FIXME: handle width of handle

            if (new_pos < 0) {
                new_pos = 0;
            }
            if (new_pos > width) {
                new_pos = width;
            }




            var sec = sec_per_pixel * new_pos;
            spt.review.timecode_el.innerHTML = spt.review.control.get_timecode(sec, fps);

            var top = bvr.src_el;
            spt.review.drag_el.setStyle("left", new_pos);

            var frame = parseInt(new_pos/width*num_thumbs) + 1;
            var frame_pad = spt.zero_pad(frame, 4);
            var path = data.frame_dir + "/" + "out"+ frame_pad +".jpg";
            spt.review.thumb.src = path;
            spt.review.control.draw_preview(path);

        ''',
        'cbjs_action': '''
            var dx = mouse_411.curr_x - spt.review.start_pos.x;
            var dy = mouse_411.curr_y - spt.review.start_pos.y;

            var new_pos = spt.review.left + dx;

            var player = spt.review.player;

            var data = spt.review.control.get_data();
            var fps = data.fps;
            var width = data.width;
            var duration = data.duration;
            var sec_per_pixel = duration / width;

            var sec = sec_per_pixel * new_pos;
            player.currentTime = sec;

            var canvas = spt.review.control.top.getElement(".spt_review_image_canvas");
            setTimeout( function() {
                canvas.setStyle("display", "none");
            }, 1000);


        '''
        } )


        thumb_div = DivWdg()
        handle_div.add(thumb_div)
        thumb_div.add_class("spt_review_drag_image")
        thumb_div.add_style("width: 120px")
        thumb_div.add_style("height: 80px")
        thumb_div.add_style("border: solid 1px white")
        thumb_div.add_style("position: absolute")
        thumb_div.add_style("top: -90")
        thumb_div.add_style("left: -55")
        thumb_div.add_style("box-shadow: 0px 0px 15px rgba(255,0,0,0.5)")
        thumb_div.add_style("display: flex")
        thumb_div.add_style("justify-content: center")
        thumb_div.add_style("align-items: center")

        thumb_div.add("<img style='object-fit: contain;'/>")
        thumb_div.add_style("overflow: hidden")

        return top


    def get_onload_js(self):

        return '''

spt.review.control = {}

// Store review and original process
spt.review.task_search_key;
spt.review.review_process;
spt.review.original_process;
spt.review.get_process_data = function() {
    
}
spt.review.get_process_data();


spt.review.control.top = null;
spt.review.control.player = null;
spt.review.control.player_el = null;
spt.review.control.data = {};

spt.review.control.frame_dir = "";
spt.review.control.num_thumbs = "";

spt.review.control.set_top = function(top) {
    spt.review.control.top = top;
    spt.review.control.player = spt.video.get_player(top);
    spt.review.control.player_el = spt.video.get_player_el(top);

    spt.review.control.timecode_el = top.getElement(".spt_review_timecode");
    spt.review.control.handle_el = top.getElement(".spt_review_drag_handle");
    spt.review.control.timeline_el = top.getElement(".spt_review_timeline");
    spt.review.control.thumb_el = top.getElement(".spt_review_drag_image").getElement("img");


    var control_top = top.getElement(".spt_review_control");
    spt.review.control.frame_dir = control_top.getAttribute("spt_frame_dir");
    spt.review.control.num_thumbs = control_top.getAttribute("spt_num_thumbs");

}



spt.review.control.get_data = function() {
    var data = spt.review.control.data;
    return data;
}



spt.review.control.init = function() {
    var video = spt.review.control.player_el;
    var data = spt.review.control.data;

    var timeline_el = spt.review.control.timeline_el;
    var width = parseInt(timeline_el.getStyle("width").replace("px", ""));
    data.width = width;

    var duration = spt.review.control.player.duration;
    data.duration = duration;


    data.fps = 30;

    data.frame_dir = spt.review.control.frame_dir;
    data.num_thumbs = spt.review.control.num_thumbs;

}


spt.review.control.set_to_pos = function(new_pos) {

    var data = spt.review.control.get_data();
    var fps = data.fps;
    var width = data.width;
    var duration = data.duration;
    var sec_per_pixel = duration / width;
    var num_thumbs = data.num_thumbs;
    var frame_dir = data.frame_dir;

    var sec = sec_per_pixel * new_pos;
    spt.review.control.timecode_el.innerHTML = spt.review.control.get_timecode(sec, fps);

    spt.review.control.handle_el.setStyle("left", new_pos);


    var path = spt.review.control.get_path_by_pos(new_pos);
    if (!spt.review.control.thumb_el.onerror) {
        spt.review.control.thumb_el.onerror = function() {
            spt.review.control.thumb_el.src = "/context/icons/common/indicator_snake.gif";
            var im_refresh = setTimeout(
                function() {
                    spt.review.control.thumb_el.src = path;
                },
                1000
            );
        };
    }
    spt.review.control.thumb_el.src = path;
}



spt.review.control.get_path_by_pos = function(pos) {
    var data = spt.review.control.get_data();
    var fps = data.fps;
    var width = data.width;
    var duration = data.duration;
    var num_thumbs = data.num_thumbs;
    var frame_dir = data.frame_dir;

    spt.review.control.handle_el.setStyle("left", pos);

    var frame = parseInt(pos/width*num_thumbs) + 1;
    var frame_pad = spt.zero_pad(frame, 4);
    var preview_path = frame_dir + "/" + "out"+ frame_pad +".jpg";

    return preview_path;
}


spt.review.control.draw_preview = function(path) {
    var canvas = spt.review.control.top.getElement(".spt_review_image_canvas");

    var im = new Image();
    im.onload = function() {
        if (im.getAttribute("src") == "/context/icons/common/indicator_snake.gif") {
            return;
        }
        var ctx = canvas.getContext("2d");
        ctx.drawImage(im, 0, 0, canvas.width, canvas.height);
    };
    im.onerror = function() {
        im.src = "/context/icons/common/indicator_snake.gif";
        var im_refresh = setTimeout(
            function() {
                im.src = path;
            },
            1000
        );
    };
    im.src = path;
}


spt.review.control.get_timecode = function(sec, fps) {
    var frames = parseInt(sec * fps);

    hours = Math.floor( frames / (60*60*fps) );
    minutes = Math.floor(frames / (60*fps)) % 60;
    seconds = (Math.floor(frames / fps) % 60 ) % 60;
    frames = frames % fps % 60 % 60;

    var p = spt.zero_pad;

    var timecode = p(hours,2)+":"+p(minutes,2)+":"+p(seconds,2)+":"+p(frames,2)

    return timecode;


}

        '''





class ReviewActionWdg(BaseRefreshWdg):
    '''A panel containing information about the snapshot's 
    parent sObject, the review approve and reject/revise buttons,
    input for accompanying note and the notes history widget.'''

    def get_display(self):
        
        top = self.top
     
        task_data = self.kwargs.get("task_data")

        # Get search key for task, submission or snapshot
        sobject = None
        search_key = self.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
        else:
            sobject = self.kwargs.get("sobject")
            if sobject:
                search_key = sobject.get_search_key()
            else:
                search_key = None

        if not search_key:
            return top

        custom_status = self.kwargs.get("custom_status")
        ui_settings = self.kwargs.get("ui_settings")
        # Get parent sObject
        parent_search_key = None
        if sobject.get_base_search_type() == "vfx/submission":
            snap_code = sobject.get("snapshot_code")
            snapshot = Search.get_by_code("sthpw/snapshot",snap_code)
            note_process = snapshot.get("process")
            parent = snapshot.get_parent()
            if parent:
                parent_search_key = parent.get_search_key()
        elif sobject.get_base_search_type() == "sthpw/task":
            parent = sobject.get_parent() 
            if parent:
                parent_search_key = parent.get_search_key() 
            note_process = task_data.get("review_process")
        elif sobject.get_base_search_type() == "sthpw/snapshot":
            parent = sobject.get_parent()
            if parent:
                parent_search_key = parent.get_search_key()
            note_process = sobject.get_value("process")
        elif sobject.get_base_search_type() == "workflow/job_asset":
            parent = sobject
            parent_search_key = sobject.get_search_key()

            search_code = parent.get_code()
            search = Search("sthpw/snapshot")
            search.add_filter("search_code", search_code)
            search.add_filter("is_latest", True)
            snapshot_sobject = search.get_sobject()

            search_key = snapshot_sobject.get_search_key()
            note_process = sobject.get_value("process")
            ui_settings = {
                "hide_review_btn": True,
                "hide_approval_btn": True,
                "show_add_btn": True
            }

        if parent_search_key:
            # Add note input and status update buttons
            add_note_wdg = ReviewAddNoteWdg(search_key=search_key, task_data=task_data,
                    parent_search_key=parent_search_key, ui_settings=ui_settings, custom_status=custom_status)
            top.add(add_note_wdg)
            add_note_wdg.set_name("Add")
           
            # Display note history of parent sObject filtered by note process
            notes_wdg = ReviewNotesHistoryWdg(search_key=parent_search_key, process=note_process)
            top.add(notes_wdg)
        
        return top



class ReviewNotesHistoryWdg(BaseRefreshWdg):
    '''display notes for display sObject within review process 
    context.'''

    def get_display(self):
        top = self.top
        top.add_style("margin: 20px 10px")
        top.add_color("background", "background")

        # Get parent sObject related to task, submission
        # or snapshot
        search_key = self.kwargs.get("search_key")
        sobject = self.kwargs.get("sobject")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
        elif sobject:
            search_key = sobject.get_search_key
        else:
            top.add("Nothing Selected")
            return top

        """
        process = self.kwargs.get("process")
        from tactic.ui.widget import DiscussionWdg
        notes_wdg = DiscussionWdg(note_format="full", search_key=search_key, \
             process=process)
        notes_wdg.set_sobject(sobject)
        top.add(notes_wdg)
        """

        return top



class ReviewAddNoteWdg(BaseRefreshWdg):
    '''Contains revise/reject and approval buttons,
    and accompanying note input.'''
     
    def get_display(self):

        top = self.top
        top.add_style("margin: 20px 10px")
        top.add_style("width: auto")
        top.add_class("spt_review_note_top")
 
        # Get task data
        task_data = self.kwargs.get("task_data")

        # Get inputted task, submission or snapshot
        search_key = self.kwargs.get("search_key")
        sobject = self.kwargs.get("sobject")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
        elif sobject:
            search_key = sobject.get_search_key()
        else:
            top.add("Nothing Selected")
            return top

        related_task = None
        review_processes = None  
        original_processes = None
        parent_search_key = self.kwargs.get("parent_search_key")
        
        # Get review and original processes
        if sobject.get_base_search_type() == "vfx/submission":
            related_task = sobject.get_related_sobject("sthpw/task")
            review_process = related_task.get_value("process")
            original_process = review_process 
        elif sobject.get_base_search_type() == "sthpw/task":
            related_task = sobject
            original_process = task_data.get("original_process")
            review_process = task_data.get("review_process")
        else:
            original_process = sobject.get_value("process")
            review_process = original_process
        
        # Get parent sObject (display sObject)
        if not parent_search_key:
            parent_search_key = search_key
            parent = sobject
            original_process = "publish"
            review_process = "publish"
        else:
            parent = Search.get_by_search_key(parent_search_key)
        
        # Add preview
        from pyasm.widget import ThumbWdg
        preview = ThumbWdg()
        preview.set_sobject(parent)
        top.add(preview)
        preview.add_style("position", "relative")
        preview.add_style("left", "-3px")
        top.add("<br/>")
 
        # Details div contains parent and snapshot/task info
        details_div = DivWdg()
        top.add(details_div)
    
        # Display parent label
        label_div = DivWdg()
        details_div.add(label_div)
        
        # Create a parent label for details tab and for display
        title = parent.get_value("name", no_exception=True)
        if not title:
            title = parent.get_value("code", no_exception=True)
        if not title:
            title = parent_search_key

        parent_sType =  parent.get_search_type_obj()
        sType_title = parent_sType.get_title()
        parent_label = "%s (%s)" % (title, sType_title) 

        label_div.add(parent_label)
        label_div.add_class("hand")
        label_div.add_styles("font-size: 1.5em; float: left; text-decoration: underline")
        label_div.add_behavior( {
            'type': 'click_up',
            'label': parent_label,
            'search_key': parent_search_key,
            'cbjs_action': '''
                var class_name = 'tactic.ui.tools.SObjectDetailWdg';
                var kwargs = {
                    search_key: bvr.search_key
                };
                spt.tab.set_main_body_tab(); 
                spt.tab.add_new(bvr.label, bvr.label, class_name, kwargs);
                '''
        } )
        
        details_div.add("<br/>")
        details_div.add("<br/>")

        # Retrieve information about task
        snapshot_key = None
        snapshot_process = None
        snapshot_version = None
        task_process = None
        task_assignee = None
        search_type = sobject.get_base_search_type()
        if search_type == "sthpw/task":
            task_process = review_process
            task_assignee = sobject.get_value("assignee")
        elif search_type == "vfx/submission":
            task_process = related_task.get_value("process") 
            task_assignee = related_task.get_value("assigned")
        else:
            snapshot_process = sobject.get_value("process")
            snapshot_key = sobject.get_search_key()


        # Display information about task and snapshot
        if task_process:
            top.add("Task: %s" % task_process)
            top.add("<br/>")
            top.add("<br/>")

        if task_assignee:
            top.add("Submitted by: %s" % task_assignee)
            top.add("<br/>")
            top.add("<br/>")
        
        if snapshot_process:
            top.add("Process: %s" % snapshot_process)
            top.add("<br/>")
            top.add("<br/>")
       
        #TODO: Display snapshot version
        if snapshot_version:
            top.add("Version: %s" % snapshot_version)
 
        top.add("<hr/>")
        
        # Review options
        note_wdg = DivWdg()
        top.add(note_wdg)
        
        note_wdg.add("Process:")
        note_wdg.add("<br/>")
        
        # Processes
        pipeline = Pipeline.get_by_sobject(parent)
        if pipeline:
            processes = pipeline.get_process_names()
        else:
            processes = [review_process]

        select = SelectWdg("process")
        select.set_option("values", processes)
        if review_process not in processes:
            select.append_option(review_process, review_process)
        select.set_value(review_process)
        select.add_style("margin-top: 5px")
        select.add_style("width: 250px")
        note_wdg.add(select)

        note_wdg.add("<br/>")
        
        note_wdg.add("Note:")
        note_wdg.add("<br/>")
        text = TextAreaWdg("note")
        text.set_attr('title','Add notes here')
        text.add_styles('border-radius: 2px')
        note_wdg.add(text)
        text.add_style("min-width: 200px")
        text.add_style("min-height: 150px")
        text.add_style("margin-top: 5px")
        text.add_class("form-control")
        text.add_style("border: solid 1px #333")
        text.add_style("padding: 5px")
       
        top.add("<br/>")


        snapshot_wdg = HiddenWdg("snapshot_key")
        note_wdg.add(snapshot_wdg)
        snapshot_wdg.set_value(snapshot_key)


   
        # Add approve and reject buttons
        table = Table()
        table.add_style("margin-left: -2px")
        top.add(table)

        table.add_row()
        td = table.add_cell()

        ui_settings = self.kwargs.get("ui_settings") or {}
        hide_review_btn = ui_settings.get("hide_review_btn")
        hide_approval_btn = ui_settings.get("hide_approval_btn")
        show_add_btn = ui_settings.get("show_add_btn")

        if not hide_review_btn:
            # Upon reject/revision action, send_status
            # will update this review tool task
            # with Reject or Revise depending on the process.
            # If process is not found, default to "Revise".
            pipeline_code = parent.get_value("pipeline_code", no_exception=True)
            if pipeline_code:
                pipeline = Pipeline.get_by_code(pipeline_code)
            if pipeline:
                process_obj = pipeline.get_process(original_process)
                if process_obj:
                    node_type = process_obj.get_type()
                    if node_type == "approval":
                        send_status = "Reject"
                    else:
                        send_status = "Revise"
                else:
                    send_status = "Revise"
            else:
                send_status = "Revise"

            revise_button_tip = "Any associated tasks will have a status updated to %s." % send_status
            button = ActionButtonWdg(title=send_status, color="danger", tip=revise_button_tip)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'snapshot_key': snapshot_key,
                'send_status': send_status,
                'cbjs_action': '''
                    spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
                    spt.review.save(bvr.search_key, bvr.send_status);
                '''
            } )


        if not hide_approval_btn:
            td = table.add_cell()
            td.add_style("padding-left", "77px")

            approval_button_tip = "Any associated tasks will have a status updated to Approved."
            button = ActionButtonWdg(title="Approve", color="primary", tip=approval_button_tip)
            td.add(button)
            button.add_behavior({
                'type': 'click_up',
                'search_key': search_key,
                'snapshot_key': snapshot_key,
                'cbjs_action': '''
                    spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
                    spt.review.save(bvr.search_key, "Approved");
                '''
            })


        custom_status = self.kwargs.get("custom_status")
        if show_add_btn:
            td = table.add_cell()
            td.add_style("padding-left", "77px")

            button = ActionButtonWdg(title="Add Feedback", color="primary")
            td.add(button)

            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'snapshot_key': snapshot_key,
                'custom_status': custom_status,
                'cbjs_action': '''
                    spt.review.set_top( bvr.src_el.getParent(".spt_review_top") );
                    spt.review.save(bvr.search_key, bvr.custom_status);
                '''
            } )

            button.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                var input = bvr.src_el.getElement("input");
                if (input) {
                    input.setStyle("width", "auto");
                }
                '''
            } )


        return top



class ReviewCmd(Command):
    '''Check in an annotated file from the ReviewWdg and 
    creates a note. '''

    def execute(self):
        '''
        search_key - snapshot, submission or task search_key used in review session.
        note - input from ReviewWdg note form
        status - update status from ReviewWdg UI to update associated tasks
        filename - the uploaded filename
        review_process - the process to create the note and snapshot under
        ticket - transaction ticket from review session
        
        update_tasks - if false, do not update associated tasks. Default to true.
        review_note_process - if defined, notes will be created with context 
           <review_note_process>/<review_process> and this process. Otherwise,
           the context defaults to review_process/review and the process
           defaults to <review_process>.
        '''

        search_key = self.kwargs.get("search_key")
        snapshot_key = self.kwargs.get("snapshot_key")
        note = self.kwargs.get("note")
        status = self.kwargs.get("status")
        filename = self.kwargs.get("filename")
        review_process = self.kwargs.get("process")
        ticket = self.kwargs.get("ticket")
       
        update_tasks = self.kwargs.get("update_tasks")
        if update_tasks not in ["False", 'false', False]: 
            update_tasks = True

        review_note_process = self.kwargs.get("review_note_process")
        if review_note_process == "false":
            review_note_process = None


        # Get upload path of annotated file
        upload_dir = Environment.get_upload_dir(ticket)
        upload_path = "%s/%s" % (upload_dir, filename)
        if not os.path.exists(upload_path):
            raise TacticException("Upload path [%s] not found" % upload_path)
 
        ''' Get sobject and process for creation of note and snapshot..
            Get the tasks associated with the review sobject.
            The review sobject is the snapshot, task or submission from review.
        '''
        review_sobject = Search.get_by_search_key(search_key)
        if review_sobject.get_base_search_type() == "sthpw/snapshot":
            sobject = review_sobject.get_parent()
           
            # Find the tasks associated with this snapshot
            process = review_sobject.get("process")
            search = Search("sthpw/task")
            search.add_filter("process", process)
            search.add_sobject_filter(sobject)
            tasks = search.get_sobjects()

        elif review_sobject.get_base_search_type() == "sthpw/task":
            tasks = [review_sobject]
            process = review_sobject.get("process")
            sobject = review_sobject.get_parent()

        elif review_sobject.get_base_search_type() == "vfx/submission":
            task = review_sobject.get_related_sobject("sthpw/task")
            process = task.get_value("process")
            sobject = task.get_parent()
            tasks = [task]



        # elif review_sobject.get_base_search_type() == "sthpw/job_asset":
        #     upload_process = "review/%s" % review_process
        #     job_asset = SearchType.create("workflow/job_asset")
        #     job_asset.set_value("job_code", parent.get_code())
        #     job_asset.set_value("process", upload_process)
        #     job_asset.commit()

        if update_tasks:
            for task in tasks:
                if task.get("status") not in ['Revise', 'Reject']:
                    task.set_value("status", status)
                    task.commit()
        
        if not sobject:
            return

        # Add a note 
        note_sobj = None
        note_sobj2 = None
        if status == "Attach" and not note:
            note = "review of " + filename
            
        if note:

            if status == "Attach":
                note_process = sobject.get_value("process")
                note_context = "%s/review" % note_process

                job_code = sobject.get_value("job_code")
                job = Search.get_by_code("workflow/job", job_code)
                from pyasm.biz import Note

                # Not sure if the review should be attached to the job or the asset?
                #note_sobj = Note.create(job, note, process=note_process, context=note_context)
                note_sobj = Note.create(sobject, note, process=note_process, context=note_context)

            else:
                if review_note_process:
                    note_context = "%s/%s" % (review_note_process, review_process)
                    note_process = review_note_process
                else:
                    note_context = "review/%s" % review_process
                    note_process = review_process

                from pyasm.biz import Note
                if not status and sobject.get_search_type() != "workflow/job":
                    job = sobject.get_parent()
                    note_sobj = Note.create(job, note, process=note_process, context=note_context)
                else:
                    note_sobj = Note.create(sobject, note, process=note_process, context=note_context)

        """
        if status in ['Revise', 'Reject']:
            # checkin the revision file
            if process != "publish":
                context =  "review/%s" % review_process
            else:
                context = "review"
        elif status == 'Approved':
            # checkin the revision file
            if process != "publish":
                context =  "approved/%s" % review_process
            else:
                context = "approved"
        """

        review_context = ""
        if status in ['Revise', 'Reject']:
            # checkin the revision file
            if process != "publish":
                review_context = "review/%s" % review_process
                review_process = "%s/review" % review_process
            else:
                review_context = "review/publish"
                review_process = "publish/review"

        elif status == 'Approved':
            # checkin the revision file
            if process != "publish":
                review_context = "approved/%s" % review_process
                review_process = "%s/approved" % review_process
            else:
                review_context = "approved/publish"
                review_process = "publish/approved"

        elif status == 'Client':
            review_context = "upload/%s" % filename 
            review_process = "upload"

        elif status == 'Feedback':
            node_process = sobject.get_value("process")

            review_context = "review/%s" % node_process
            review_process = "%s/review" % node_process

        if status == "Attach":
            file_paths = [upload_path]
            source_paths = [upload_path]
            file_types = ['main']

            if os.path.isfile(upload_path):
                icon_creator = IconCreator(upload_path)
                icon_creator.execute()

                web_path = icon_creator.get_web_path()
                icon_path = icon_creator.get_icon_path()
                if web_path:
                    file_paths = [upload_path, web_path, icon_path]
                    source_paths = [upload_path, web_path, icon_path]
                    file_types = ['main', 'web', 'icon']

            node_process = sobject.get_value("process")

            snapshot_context = "attachment/%s/%s" % (node_process, filename)
            snapshot_process = "%s/attachment" % (node_process)

            checkin = FileCheckin(sobject=note_sobj, file_paths=file_paths, file_types=file_types,
                                  source_paths=source_paths, process=snapshot_process,
                                  context=snapshot_context, checkin_type='strict', description=note)
            checkin.execute()

            if note_sobj2:
                checkin = FileCheckin(sobject=note_sobj2, file_paths=file_paths, file_types=file_types,
                                      source_paths=source_paths, process=snapshot_process,
                                      context=snapshot_context, checkin_type='strict', description=note, mode="move")
                checkin.execute()
 
            return
        else:
            checkin = FileCheckin(sobject, upload_path, process=review_process, context=review_context, description=note)
            checkin.execute()

        review_snapshot = checkin.get_snapshot()
        if note:
            review_snapshot.connect(note_sobj, context="attachment")

        if snapshot_key:
            snapshot = Search.get_by_search_key(snapshot_key)
            review_snapshot.connect(snapshot, context="review")

        self.add_description('ReviewCmd %s [%s]' % (process, sobject.get_search_key()))

        if status == 'Feedback':
            node_process = sobject.get_value("process")

            process = "review/%s" % node_process
            job_asset = SearchType.create("workflow/job_asset")
            job_asset.set_value("job_code", sobject.get_value("job_code"))
            job_asset.set_value("process", process)
            job_asset.commit()

            review_snapshot.set_parent(job_asset)
            review_snapshot.commit()
