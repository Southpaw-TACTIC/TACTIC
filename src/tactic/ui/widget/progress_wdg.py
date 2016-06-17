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

__all__ = ['ProgressWdg', 'RadialProgressWdg']

#from tactic_client_lib import TacticServerStub

from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg, Canvas

class ProgressWdg(BaseRefreshWdg):
    '''A simple widget which displays the progress and an upload'''

    def init(my):
        my.progress_div = DivWdg()
        my.progress_id = my.progress_div.set_unique_id()


    def get_progress_id(my):
        return my.progress_id


    def get_display(my):
        top = my.top
        top.add_class("spt_progress_top")
        top.add_style("height: 10px")
        top.add_style("width: 200px")
        top.add_style("overflow: hidden")
        top.add_border()

        top.add(my.progress_div)
        my.progress_div.add_style("width: 0%")
        my.progress_div.add_gradient("background", "background2", 20)
        my.progress_div.add_style("height: 100%")
        my.progress_div.add("&nbsp;")
        my.progress_div.add('<img height="10px" src="/context/icons/common/indicator_snake.gif" border="0"/>')

        return top



def get_onload_js():
    return '''
spt.progress = {};

// list of jobs in the queue
spt.progress.jobs = [];
spt.progress.num_jobs = -1;
spt.progress.current_job = [];
spt.progress.current_index = -1;

// list of all the interval ids
spt.progress.interval_ids = [];

// status of current job
spt.progress.complete = 0;
spt.progress.total = -1;
spt.progress.path = '';

// dom id of the element to set progress to
spt.progress.progress_id = '';

//
// Job methods

spt.progress.add_path = function(path, options) {
    if (typeof(options) == 'undefined') {
        options = {};
    }
    options['path'] = path;
    spt.progress.add_job(options);
} 

spt.progress.add_job = function(job) {
    spt.progress.jobs.push(job);
}


spt.progress.set_current_job = function(job, index) {
    spt.progress.reset();
    spt.progress.path = job.path;
    spt.progress.progress_id = job.progress_id;

    spt.progress.current_job = job;
    spt.progress.current_index = index;
}


spt.progress.get_current_job = function() {
    return spt.progress.current_job;
}


spt.progress.run_jobs = function(options) {

    if (typeof(options) == 'undefined') {
        options = {};
    }


    var jobs = spt.progress.jobs;
    var server = TacticServerStub.get()
    server.clear_upload_dir();

    var num_jobs = jobs.length;
    spt.progress.num_jobs = num_jobs;

    var id = setInterval( function() {

        if (spt.progress.is_in_progress() ) {
            return;
        }


        if (jobs.length == 0) {
            clearInterval(id);
            if (typeof(options.on_complete) != 'undefined') {
                options.on_complete();
            }

            spt.progress.reset();
            spt.progress.jobs = [];
            return;
        }


        // run next job
        //console.log("Starting new job ...");
        var job = jobs.shift();
        var index = num_jobs - jobs.length;
        spt.progress.set_current_job(job, index);
        spt.progress.do_job();

    }, 200 )

    spt.progress.interval_ids.push(id);

}

// FIXME: this doesn't work too well: it doesn't stop the java upload of
// a large file.
spt.progress.cancel_jobs = function(total) {
    var ids = spt.progress.interval_ids;
    for (var i = 0; i < ids.length; i++) {
        //console.log("Cancelling: " + ids[i]);
        clearInterval(ids[i]);
    }
    spt.progress.reset();
    spt.progress_interval_ids = [];
}


spt.progress.reset = function(total) {
    spt.progress.total = -1;
    spt.progress.complete = 0;
    spt.progress.path = '';
    spt.progress.progress_id = '';
}

spt.progress.is_in_progress = function() {
    if (spt.progress.total == -1) {
        return false;
    }
    else {
        return true;
    }
}



spt.progress.set_path = function(path) {
    spt.progress.path = path;
}


spt.progress.set_total = function(total) {
    spt.progress.total = total;
}

spt.progress.set_complete = function(complete) {
    if (typeof(complete) == 'undefined') {
        spt.progress.complete = spt.progress.total;
    }
    else {
        spt.progress.complete = complete;
    }
}


spt.progress.set_error = function() {
    spt.progress.set_progress("error");
}




spt.progress.set_progress_id = function(progress_id) {
    spt.progress.progress_id = progress_id;
}



spt.progress.get_percent_complete = function() {
    var percent = spt.progress.complete / spt.progress.total * 100;
    return percent;
}


// get the currently uploading path
spt.progress.get_path = function() {
    return spt.progress.path;
}

spt.progress.get_complete = function() {
    return spt.progress.complete;
}

spt.progress.get_index = function() {
    return spt.progress.current_index;
}

spt.progress.get_num_jobs = function() {
    return spt.progress.num_jobs;
}


spt.progress.set_progress = function(complete) {
    var progress_id = spt.progress.progress_id;
    if (typeof(progress_id) == 'undefined') {
        return;
    }

    var progress_el = $(progress_id);

    if (complete == 'error') {
        progress_el.setStyle("width", "100%");
        progress_el.setStyle("background", "#F00");
        return;
    }

    var percent = spt.progress.complete / spt.progress.total * 100;
    progress_el.setStyle("width", percent + "%");
}



spt.progress.do_job = function() {

    if (spt.progress.is_in_progress() ) {
        spt.alert("Upload already in progress");
        return;
    }


    var server = TacticServerStub.get()

    path = spt.progress.get_path();

    if (path == '') {
        spt.alert("No path to upload");
        spt.progress.set_complete();
        return;
    }

    // get the size of the file
    var applet = spt.Applet.get();
    var info = applet.get_path_info(path)
    if (info == null) {
        spt.progress.set_error();
        return;
    }


    var size = info.size;
    spt.progress.set_total(size);
    var count = 0;

    // the interval is based on the file size
    // 100ms for every MB
    var mb = size / (1024*1024);
    var interval = 100*mb;
    if (interval < 100) {
        interval = 100;
    }
    if (interval > 1000) {
        interval = 1000;
    }
    //console.log(interval);

    var last_size = -1;
    var id = setInterval( function() {

        var job = spt.progress.get_current_job();
        var start_cbk = job.on_start;
        if (typeof(start_cbk) != 'undefined') {
            start_cbk();
        }

        var size = server.get_upload_file_size(path);
        //console.log("size: " + size);
        if (size == 0) {
            return;
        }
        // generally this means the file does not exist
        /*
        if (size == -1) {
            clearInterval(id);
            spt.progress.reset();
            return;
        }
        */

        var percent_complete = spt.progress.get_percent_complete();

        if (size == last_size) {
            count += 1;
        }
        else {
            count = 0;
        }

        //console.log("Percent: " + percent_complete);
        if (count < 10 && percent_complete < 100)  {
            spt.progress.set_complete(size);
            spt.progress.set_progress();
        }
        else {
            clearInterval(id);
            // run one last time
            if (typeof(job.on_update) != 'undefined') {
                job.on_update();
            }
            spt.progress.reset();
            return;
        }
        last_size = size;

        // run the callback
        if (typeof(job.on_update) != 'undefined') {
            job.on_update();
        }

    }, interval )


    spt.progress.interval_ids.push(id);



    setTimeout( function() {
        // actually do the job
        var job = spt.progress.get_current_job();
        var action_cbk = job.on_action;
        if (typeof(action_cbk) != 'undefined') {
            action_cbk();
        }
        else {
            var ticket = job.ticket;
            if (typeof(ticket) == 'undefined') {
                server.upload_file(path);
            }
            else {
                server.upload_file(path, ticket);
            }
        }

        spt.progress.set_complete();
        spt.progress.set_progress();
    }, 100 );



    return;
}





spt.progress.run_jobs_serial = function(options) {

    if (typeof(options) == 'undefined') {
        options = {};
    }


    var jobs = spt.progress.jobs;
    var server = TacticServerStub.get()
    server.clear_upload_dir();

    var num_jobs = jobs.length;
    spt.progress.num_jobs = num_jobs;

    for (var i = 0; i < jobs.length; i++) {
        // run next job
        var job = jobs[i];
        spt.progress.set_current_job(job, i);
        spt.progress.do_job_serial();
    }


    if (typeof(options.on_complete) != 'undefined') {
        options.on_complete();
    }

    spt.progress.reset();
    spt.progress.jobs = [];

}


spt.progress.do_job_serial = function() {

    var server = TacticServerStub.get()

    var path = spt.progress.get_path();

    if (path == '') {
        spt.alert("No path to upload");
        spt.progress.set_complete();
        return;
    }

    // get the size of the file
    var applet = spt.Applet.get();
    var info = applet.get_path_info(path)
    if (info == null) {
        spt.progress.set_error();
        return;
    }


    var size = info.size;
    spt.progress.set_total(size);
    var count = 0;

    // the interval is based on the file size
    // 100ms for every MB
    var mb = size / (1024*1024);
    var interval = 100*mb;
    if (interval < 100) {
        interval = 100;
    }
    if (interval > 1000) {
        interval = 1000;
    }

    // This is the check fnction
    var last_size = -1;
    var check_id = setInterval( function() {

        var job = spt.progress.get_current_job();

        var size = server.get_upload_file_size(path);
        //console.log(spt.progress.get_path() + " = " + size);

        var percent_complete = spt.progress.get_percent_complete();

        spt.progress.set_complete(size);
        spt.progress.set_progress();


        // run the callback
        if (typeof(job.on_update) != 'undefined') {
            job.on_update();
        }

    }, interval )


    // actually do the job
    try {
        var job = spt.progress.get_current_job();

        // run the callback
        if (typeof(job.on_update) != 'undefined') {
            job.on_update();
        }


        var action_cbk = job.on_action;
        if (typeof(action_cbk) != 'undefined') {
            action_cbk();
        }
        else {
            var ticket = job.ticket;
            if (typeof(ticket) == 'undefined') {
                server.upload_file(path);
            }
            else {
                server.upload_file(path, ticket);
            }
        }


        // run the callback
        if (typeof(job.on_update) != 'undefined') {
            job.on_update();
        }

        spt.progress.set_complete();
        spt.progress.set_progress();
    }
    catch(e) {
        //console.log("Error: " + e);
        clearInterval(check_id);
        throw(e);
    }



    clearInterval(check_id);

    return;
}


    '''



__all__.append( 'TestProgressWdg' )
class TestProgressWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style("padding: 10px")
        top.add_border()
        top.add_color("background", "background")

        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Upload")
        top.add(button)

        cancel = ActionButtonWdg(title="Cancel")
        top.add(cancel)
        cancel.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''spt.progress.cancel_jobs()'''
        } )


        top.add_behavior( {
            'type': 'load',
            'cbjs_action': get_onload_js()
        } )



        from pyasm.web import Table
        table = Table()
        top.add(table)

        paths = []
        #paths = ['C:/Data/ab.avi', 'C:/Data/ab2.avi']
        paths = ['C:/Data/ab.avi']
        for i in range(0, 7):
            paths.append("C:/Data/Test2/test%0.2d.nkple"  % i)
        progress_ids = []
        for path in paths:
            table.add_row()
            td = table.add_cell()
            td.add_style("padding: 5px")

            path_div = DivWdg()
            td.add(path_div)
            path_div.add_style("width: 100%")
            path_div.add(path)

            td = table.add_cell()
            progress_wdg = ProgressWdg()
            td.add(progress_wdg)

            progress_id = progress_wdg.get_progress_id()
            progress_ids.append(progress_id)


        button.add_behavior( {
        'type': 'click_up',
        'paths': paths,
        'progress_ids': progress_ids,
        'cbjs_action': '''

        var applet = spt.Applet.get();

        var update_cbk = function() {
            var progress = spt.progress.complete;
            var path = spt.progress.get_path();
            var index = spt.progress.get_index();
            var num_jobs = spt.progress.get_num_jobs();
            //console.log("job [" + index + " of " +num_jobs+ "] = " + path + ": " + progress);
        };

        for (var i = 0; i < bvr.paths.length; i++) {
            var path = bvr.paths[i] + "";
            path = path.replace(/\\\\/g, "/");
            var progress_id = bvr.progress_ids[i];
            if (!progress_id) {
                progress_id = bvr.progress_ids[0];
            }
            var job = {
                progress_id: progress_id,
                path: path,
                on_update: update_cbk
            }
            spt.progress.add_job(job);
        }
        spt.progress.run_jobs();

        '''
        } )

        return top



__all__.append( 'TestProgressWdg2' );
class TestProgressWdg2(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Upload")
        top.add(button)


        # just a file name and a percentage
        from pyasm.web import Table
        table = Table()
        top.add(table)
        top.add_class("spt_progress_test")

        paths = []
        #paths = ['C:/Data/ab.avi']
        for i in range(0, 7):
            paths.append("C:/Data/Test2/test%0.2d.nkple"  % i)

        table.add_row()
        td = table.add_cell()
        td.add_style("padding: 5px")
        path_div = DivWdg()
        td.add(path_div)
        td.add_class("spt_progress_path")

        td = table.add_cell()
        td.add_style("padding: 5px")
        complete_div = DivWdg()
        td.add(complete_div)
        td.add_class("spt_progress_complete")


        button.add_behavior( {
            'type': 'click_up',
            'paths': paths,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_progress_test");
            var complete_el = top.getElement(".spt_progress_complete");
            var path_el = top.getElement(".spt_progress_path");

            path_el.innerHTML = "Starting ...";

            var snake = '<img src="/context/icons/common/indicator_snake.gif" border="0"/>';

            // cusotom update
            var update_cbk = function() {
                var complete = spt.progress.get_percent_complete();
                var path = spt.progress.get_path();

                complete = complete + "";
                complete = complete.split(".")[0];

                complete_el.innerHTML = complete + "%";
                path_el.innerHTML = path;

                spt.notify.show();
                spt.notify.set_message(snake + " Uploading: " + path + " ("+complete+"%)");
            };

            var complete_cbk = function() {
                spt.notify.hide();
            }

            var action_cbk = function() {
                //console.log( "action_cbk: ");
                //console.log( "path: ", spt.progress.get_path() );

                // use a custom uploader?
                //var src = spt.progress.get_src();
                //var handoff = spt.progress.get_handoff();
                // The server expects it to be either in the upload or handoff
                // directory.  We just need to get it there.
                var applet = spt.Applet.get();
                //applet.copy_file(src, handoff);
                // or
                //applet.exec("aspera_cp", src, dst);
                // or whatever
            }


            for (var i = 0; i < bvr.paths.length; i++) {
                var path = bvr.paths[i] + "";
                path = path.replace(/\\\\/g, "/");

                var job = {
                    path: path,
                    on_update: update_cbk,
                    on_action: action_cbk
                }
                spt.progress.add_job(job);
            }
            spt.progress.run_jobs();

            '''
        } )

        return top



__all__.append( 'TestProgressWdg3' )
class TestProgressWdg3(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        from tactic.ui.widget import ActionButtonWdg
        button = ActionButtonWdg(title="Upload")
        top.add(button)


        # just a file name and a percentage
        from pyasm.web import Table
        table = Table()
        top.add(table)
        top.add_class("spt_progress_test")

        paths = []
        paths = ['C:/Data/ab.avi']
        for i in range(0, 7):
            paths.append("C:/Data/Test2/test%0.2d.nkple"  % i)

        table.add_row()
        td = table.add_cell()
        td.add_style("padding: 5px")
        path_div = DivWdg()
        td.add(path_div)
        td.add_class("spt_progress_path")

        td = table.add_cell()
        td.add_style("padding: 5px")
        complete_div = DivWdg()
        td.add(complete_div)
        td.add_class("spt_progress_complete")

        button.add_behavior( {
            'type': 'load',
            'paths': paths,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_progress_test");
            var complete_el = top.getElement(".spt_progress_complete");
            var path_el = top.getElement(".spt_progress_path");
            path_el.innerHTML = bvr.paths.length + " files to check in";
            '''
            } )

        button.add_behavior( {
            'type': 'click_up',
            'paths': paths,
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_progress_test");
            var complete_el = top.getElement(".spt_progress_complete");
            var path_el = top.getElement(".spt_progress_path");

            path_el.innerHTML = "Starting ...";

            var snake = '<img src="/context/icons/common/indicator_snake.gif" border="0"/>';

            // cusotom update
            var update_cbk = function() {
                var complete = spt.progress.get_percent_complete();
                var path = spt.progress.get_path();

                complete = complete + "";
                complete = complete.split(".")[0];

                complete_el.innerHTML = complete + "%";
                path_el.innerHTML = path;

                spt.notify.show();
                spt.notify.set_message(snake + " Uploading: " + path + " ("+complete+"%)");
            };

            var complete_cbk = function() {
                var complete = spt.progress.get_percent_complete();
                var path = spt.progress.get_path();

                complete_el.innerHTML = '';
                path_el.innerHTML = 'Complete';
                spt.notify.set_message('Upload Complete');
                spt.notify.hide();

            }

            for (var i = 0; i < bvr.paths.length; i++) {
                var path = bvr.paths[i] + "";
                path = path.replace(/\\\\/g, "/");

                var job = {
                    path: path,
                    on_update: update_cbk,
                }
                spt.progress.add_job(job);
            }
            //spt.progress.run_jobs({on_complete: complete_cbk});
            //spt.progress.run_jobs_serial({on_complete: complete_cbk});
            setTimeout( function() {
                spt.progress.run_jobs_serial({on_complete: complete_cbk});
            }, 0 );

            '''
        } )

        return top


class RadialProgressWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style("margin: 5px")

        percent = my.kwargs.get("percent")

        count = my.kwargs.get("count")
        total = my.kwargs.get("total")

        if percent == None and count != None and total != None:
            if total:
                percent = int( 100 * (float(count) / float(total)) )
            else:
                percent = 0

        if percent == None:
            percent = 0;

        color = my.kwargs.get("color")
        if not color:
            color = '#1b458b'

        #size = 100
        size = 60 


        top.add_style("width", size)
        top.add_style("height", size)
        top.add_style("position: relative")

        canvas = Canvas()
        top.add(canvas)
        canvas.add_attr("width", size)
        canvas.add_attr("height", size)
        canvas.add_behavior( {
            'type': 'load',
            'percent': percent,
            'color': color,
            'size': size,
            'cbjs_action': '''

            var canvas = bvr.src_el;
            var context = canvas.getContext("2d");

            var percent = bvr.percent;

            function drawOval(x, y, rw, rh)
            {
              context.scale(1,  rh/rw);
              context.beginPath();
              context.arc(x, y, rw, 0,  2 * Math.PI);
              context.restore();
              context.lineWidth=6;
              context.strokeStyle = '#EEE';
              context.stroke();  


              context.beginPath();
              context.arc(x, y, rw+3, 0,  2 * Math.PI);
              context.restore();
              context.lineWidth=1;
              context.strokeStyle = '#DDD';
              context.stroke();  


              context.beginPath();
              context.arc(x, y, rw-3, 0,  2 * Math.PI);
              context.restore();
              context.lineWidth=1;
              context.strokeStyle = '#DDD';
              context.stroke();  





              context.beginPath();
              context.arc(x, y, rw, Math.PI, (1 + percent/100*2) * Math.PI);
              context.restore();
              context.lineWidth=6;
              context.strokeStyle = bvr.color;
              context.stroke();  
 
            }

            var centerX = canvas.width / 2;
            var centerY = canvas.height / 2;
            drawOval(centerX, centerY , centerX-5, centerY-5); 

            return;


            '''
        } )


        div = DivWdg()
        top.add(div)
        if count != None:
            div.add("%s/%s" % (count, total))
        else:
            div.add("%s%%" % percent)
        div.add_style("position: absolute")
        div.add_color("color", "color")
        div.add_style("width", size)
        div.add_style("text-align: center")
        div.add_style("font-size: 1.2em")
        #div.add_style("font-weight: bold")
        div.add_style("top: %spx" % (size/2-10))


        return top



