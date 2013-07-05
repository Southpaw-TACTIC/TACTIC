// -----------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to
//   Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// 
// -----------------------------------------------------------------------------


// Upload: class that abstracts the uploading of files


// DEPRECATED: this is all done through applet now

spt.Upload = new Class({


initialize: function(key, kwargs)
{
    // the key is used to uniquely identify this uploader
    this.key = key;

    this.file_list = [];
    var env = spt.Environment.get();
    var server_url = env.get_server_url();

    // swfupload specific functions
    var settings = {
        button_placeholder_id : this.key + "Button",

        upload_url : server_url + "/tactic/default/UploadServer/",

        
        post_params: {
            login_ticket: env.get_ticket(),
            project: env.get_project(),
            action: 'create'
        },
        //file_queue_limit: 1,
        //file_upload_limit: 1,
        file_size_limit: 0,
        flash_url : "/context/spt_js/swfupload/swfupload.swf",
        button_width: 100,
        button_height: 20,
        //button_text: "Browse ...",
        //button_text_left_padding: 8,
        //button_text_style: "color: #777; font-size:18pt;",
        button_image_url: '/context/icons/common/browseButton.png',
        button_window_mode : SWFUpload.WINDOW_MODE.TRANSPARENT,
        button_cursor: SWFUpload.CURSOR.HAND,
        debug: false,

        upload_progress_handler: this.upload_progress_cbk,
        upload_complete_handler: this.upload_complete_cbk,
        file_queued_handler: this.file_queued_cbk
    };

    // override the settings
    var override = kwargs['settings'];
    for (name in override) {
        var value = override[name];
        // handlers have to be evaluated from their string value
        if (name.search("_handler$") != -1) {
            settings[name] = eval(value);
            if (typeof(settings[name]) == "undefined") {
                alert("WARNING: handler ["+value+"] is undefined");
            }
        }
        else {
            settings[name] = value;
        }
    }

    this.upload = new SWFUpload(settings);

    // set the key to this upload widget
    this.upload.customSettings.key = key;

    // set the id of the container widget
    var top_id = kwargs['top_id'];
    if (typeof(top_id) == "undefined") {
        top_id = key;
    }
    this.upload.customSettings.top_id = top_id;

    // set the context
    var context = kwargs['context'];
    if (typeof(context) != "undefined") {
        this.upload.customSettings.context = context;
    }

    // this is passed in for EditWdg, inline editing does not use this
    if (kwargs.spt_search_key) {
        this.upload.customSettings.spt_search_key = kwargs.spt_search_key;
    }
    if (kwargs.spt_parent_search_key) {
        this.upload.customSettings.spt_parent_search_key = kwargs.spt_parent_search_key;
    }
    this.upload.customSettings.server = null;


},


// set to a different key
set_key: function(key)
{
    this.key = key;
    this.upload.customSettings.key = key;
},


get_state: function()
{
    return this.upload.customSettings.state;
},


start_upload: function()
{
    var server = this.upload.customSettings.server;
    if (! server)
        server = TacticServerStub.get();
    
    var post_params = {
        //login_ticket: env.get_ticket(),
        login_ticket: server.get_transaction_ticket(),
        project: env.get_project(),
        action: 'create'
    };
    this.upload.setPostParams( post_params );

    var stats = this.upload.getStats();
    
    // add number of files queued
    if (stats.files_queued > 0) {
        this.upload.startUpload();
    }
},



// Callbacks
// NOTE: in the callbacks, "this" is actually the upload object



file_queued_cbk: function(file_object)
{
    var upload_el = $(this.customSettings.top_id);
    var upload_info = upload_el.getElement(".spt_upload_info");
    var upload_bar = upload_el.getElement(".spt_upload_bar");
    var upload_stats = upload_el.getElement(".spt_upload_stats");

    upload_info.innerHTML = "1 - " + file_object.name;

    var stats = this.getStats();

    // add number of files queued
    var stats_msg = stats.files_queued + " file/s queued";
    upload_stats.innerHTML = stats_msg;


},



// Updates the progress information
upload_progress_cbk: function(file_object, bytes_complete, bytes_total)
{
    var percentage = parseInt((bytes_complete / bytes_total) * 100);

    var xbytes_complete = parseInt(bytes_complete / 1000000);
    var xbytes_total = parseInt(bytes_total / 1000000);
    var units = "MB";
    
    if (xbytes_total < 10) {
        xbytes_complete = parseInt(bytes_complete / 1000);
        xbytes_total = parseInt(bytes_total / 1000);
        units = "KB";
    }

    var upload_el = $(this.customSettings.top_id);
    var upload_info = upload_el.getElement(".spt_upload_info");
    var upload_bar = upload_el.getElement(".spt_upload_bar");

    var msg = xbytes_complete + " / " + xbytes_total + " " + units + " ( " + percentage + "% )";

    upload_info.innerHTML = file_object.name + " : " + msg;
    upload_bar.setStyle("width", percentage + "%");
    upload_bar.setStyle("background", "blue");
},




// upon completion, startup a new upload
upload_complete_cbk: function(file_object)
{
    // set the name of the file
    var file_name = file_object.name;
    file_name = file_name.replace(" ", "_");
    
    var upload_el = $(this.customSettings.top_id);
    if (!upload_el)
        log.warning('Upload Element missing... Retry');
    var instance = spt.Upload.get(this.customSettings.top_id);
    instance.file_list.push(file_name);
     

    var upload_info = upload_el.getElement(".spt_upload_info");
    var upload_bar = upload_el.getElement(".spt_upload_bar");
    var upload_stats = upload_el.getElement(".spt_upload_stats");
    var upload_path = upload_el.getElement(".spt_upload_path");
    var upload_context = upload_el.getElement(".spt_upload_context").value;
    
    upload_bar.setStyle("background", "lime");

    

    upload_path.value = file_name;
    var stats = this.getStats();
    
    //FIXME:  this files_queued does not count down on its own
    // start a new upload
    if (stats.files_queued > 0) {
        this.startUpload();
    }
    else {

        var server = TacticServerStub.get();
        var option = {'mode': 'uploaded'};
       
        // FIXME: need search key
        server.simple_checkin(instance.search_key, upload_context,
            instance.file_list[0], option);
        instance.file_list.pop();

        // update stats message
        var stats_msg = instance.file_list.length + " file/s queued";
        upload_stats.innerHTML = stats_msg;

        //TODO: add more files if needed
        //for (var i=1; i<instance.file_list.length; i++) {
        var top = document.getElement(".spt_table_top");
        //TODO: change it back to fire_event when the bug is fixed
        //spt.named_events.fire_event('update|' + instance.search_key, {});
        spt.panel.refresh("main_body_table|" + instance.search_key);
    }


}



})


// Static functions
spt.Upload.instances = {};

/*
 * kwargs:
 *  create: force the creation of a new instance
 */
spt.Upload.get = function(key, kwargs)
{
    if (!kwargs) {
        kwargs = {};
    }

    var create = kwargs['create'];
    var instance = spt.Upload.instances[key];
    if (create == true && !instance) {
        instance = new spt.Upload(key, kwargs);

        // record the instance
        spt.Upload.instances[key] = instance;
    }
    
    return instance;

}


spt.Upload.set = function(key, instance)
{
    // record the instance
    spt.Upload.instances[key] = instance;
}


spt.Upload.setup_cbk = function(evt, bvr)
{
    var key = bvr.key;
    var settings = bvr.settings;
    var top_id = bvr.top_id;
    var context = bvr.context;
    var search_key = bvr.search_key;
    var parent_search_key = bvr.parent_search_key;
    /*
    if (bvr.renew) {
        spt.Upload.set(key, null);
    }
    */
    var kwargs =  {
        'create': true,
        'settings': settings,
        'top_id': top_id,
        'context': context,
        'spt_search_key': search_key,
        'spt_parent_search_key': parent_search_key
    }
    //delete first
    spt.Upload.set(key, null);

    var upload_obj = spt.Upload.get(key, kwargs);
}


//spt.Upload.upload_cbk = function(evt, bvr)
spt.Upload.upload_cbk = function(bvr)
{
    var key = bvr.key;
    if (typeof(key) == 'undefined') {

        var src_el = bvr.src_el;
        // FIXME: this should not be the case!!!!
        //src_el = src_el.parentNode;
        //src_el = src_el.parentNode;
        // container of the uploadwdg in the CellEditWdg got the key
        src_el = bvr.src_el.getParent('.spt_upload');
        src_el = src_el.parentNode;
        key = src_el.getAttribute("id");
    }
    // start the upload
    var upload_obj = spt.Upload.get(key);
    // FIXME: this should not be empty
    if (!upload_obj) {
        log.warning("Key ["+key+"] has no upload object");
        return;
    }

    // move this to the the global container
    //var upload = src_el.getParent(".spt_upload");
    //src_el.inject( $("global_upload") );

    var stats = upload_obj.upload.getStats();
    
    //FIXME:  this files_queued does not count down on its own
    // start a new upload
    if (stats.files_queued == 0) {
        // remove the upload obj
        spt.Upload.set(key, null);
        return;
    }
    if (bvr.start_transaction) {
        var server = TacticServerStub.get();
        server.start({'title':'File Upload'});
        upload_obj.upload.customSettings.server = server;
    }
    upload_obj.start_upload();
}


spt.Upload.submit_cbk = function(bvr)
{
    var key = bvr.key;
   
    // get the upload
    var upload_obj = spt.Upload.get(key);

    if (!upload_obj) {
        alert('Submission of an existing sobject is expected! Close pop-up and try again');
        log.warning("Key ["+key+"] has no upload object");
        return;
    }

    var stats = upload_obj.upload.getStats();
    
    // start a new upload
    if (stats.files_queued == 0) {
        spt.Upload.set(key, null);
        return;
    }
    var top_id = 'edit_popup';
    var key = 'edit';
    var values = spt.api.Utility.get_input_values(top_id , null, false);
    var bin_id = values[key + '|bin_select'].strip();
    if (!bin_id) {
        alert('A valid bin must be selected first');
        return;
    }
    var parent_skey = values['parent_search_key'];

    if (bvr.start_transaction) {
        var server = TacticServerStub.get();
        server.start({'title':'Submission',
         'description': 'Submission for ' + parent_skey});

        upload_obj.upload.customSettings.server = server;
    }
    upload_obj.start_upload();
}

spt.Upload.append_cbk = function(bvr)
{
    var key = bvr.key;
   
    // get the upload
    var upload_obj = spt.Upload.get(key);

    if (!upload_obj) {
        alert('Appending of an existing sobject is expected!');
        log.warning("Key ["+key+"] has no upload object");
        return;
    }

    var stats = upload_obj.upload.getStats();
    
    // start a new upload
    if (stats.files_queued == 0) {
        spt.Upload.set(key, null);
        return;
    }
    var top_id = 'edit_popup';
    var values = spt.api.Utility.get_input_values(top_id , null, false);
    var search_type = values['search_type'];
    var search_id = values['search_id'];

    if (bvr.start_transaction) {
        var server = TacticServerStub.get();
        server.start({'title':'Append To Snapshot',
         'description': 'Append to ' + search_type + "|" + search_id});
        upload_obj.upload.customSettings.server = server;
    }
    upload_obj.start_upload();
}

// used for inline editing of icons
spt.Upload.icon_complete = function(file_object)
{
    var instance = spt.Upload.get(this.customSettings.top_id);

    //var upload_context = "icon";
    var upload_context = this.customSettings.context;
    var file_name = file_object.name;
    file_name = spt.path.get_filesystem_name(file_name);
    
    // get the search key from the table
    var upload_el = $(this.customSettings.top_id);
    var tbody = upload_el.getParent(".spt_table_tbody");
    var search_key = tbody.getAttribute("spt_search_key");

    var server = TacticServerStub.get();
    var option = {'mode': 'uploaded'};

    // check in the uploaded file 
    try {
    server.simple_checkin(search_key, upload_context,
        file_name, option);
    } catch(e) {
        var error_str = spt.exception.handler(e);
        alert( "Checkin Error: " + error_str );
    }

    // update stats message
    //var stats_msg = instance.file_list.length + " file/s queued";
    //upload_stats.innerHTML = stats_msg;
    spt.named_events.fire_event('update|' + search_key, {});

        
    // remove the upload obj
    var key = this.customSettings.key;
    spt.Upload.set(key, null);
}

spt.Upload.edit_wdg_complete = function(file_object)
{
    //var instance = spt.Upload.get(this.customSettings.top_id);
    //var upload_context = "icon";
    //var upload_context = this.customSettings.context;
    var top_id = 'EditWdg';
    var key = this.customSettings.key;
    var values = spt.api.Utility.get_input_values(top_id , null, false);
    var upload_context = values[key + '|context'];
    var upload_subcontext = values[key + '|subcontext'];
    if (upload_subcontext)
        upload_context = upload_context + '/' + upload_subcontext;

    var upload_desc = values[key + '|description'];
    var upload_is_revision = values[key + '|is_revision'] == 'on';
    
    var file_name = file_object.name;
    file_name = spt.path.get_filesystem_name(file_name); 
    // get the search key from initial set-up
    var search_key = this.customSettings.spt_search_key;
    var parent_search_key = this.customSettings.spt_parent_search_key;

    var server = this.customSettings.server;
    if (! server)
        server = TacticServerStub.get();
    var option = {'mode': 'uploaded', 'description': upload_desc,
                    'is_revision': upload_is_revision};
        
    // check in the uploaded file 
    try {
        server.simple_checkin(search_key, upload_context,
        file_name, option);
    } catch(e) {
        var error_str = spt.exception.handler(e);
        alert( "Checkin Error: " + error_str );
    }

    // update stats message
    //var stats_msg = instance.file_list.length + " file/s queued";
    //upload_stats.innerHTML = stats_msg;

    server.finish();
    spt.named_events.fire_event('update|' + search_key, {});
    
    // for Note Attachment
    if (parent_search_key)
        spt.named_events.fire_event('update|' + parent_search_key, {});

    // remove the upload obj
    spt.Upload.set(key, null);
    spt.named_events.fire_event('close_EditWdg', {})
}

spt.Upload.submit_complete = function(bvr)
{
    var top_id = 'edit_popup';
    var key = 'edit';
    var values = spt.api.Utility.get_input_values(top_id , null, false);
    var upload_context = 'publish';
    // if using UploadWdg
    //var upload_context = values[key + '|submit|context'];

    var bin_id = values[key + '|bin_select'];
    var submit_artist = values[key + '|artist'];
    var desc = values[key + '|description'];
    
    var top = spt.get_parent(bvr.src_el, ".spt_upload_top");
    var hidden = top.getElement(".spt_upload_hidden");
    var ticket_hidden = top.getElement(".spt_upload_ticket");

    var file_name = spt.path.get_basename(hidden.value);
    file_name = spt.path.get_filesystem_name(file_name); 

    var parent_st = values['parent_search_type'];
    var parent_sid = values['parent_search_id'];
    var parent_context = values['parent_context'];
    var parent_version = values['parent_version'];

    //var server = this.customSettings.server;
    //if (! server)
    var server = TacticServerStub.get();
    if (ticket_hidden.value)
        server.set_ticket(ticket_hidden.value);
    var option = {'mode': 'uploaded', 'description': 'Submission Checkin',
        'checkin_cls': 'pyasm.prod.checkin.SubmissionCheckin'};
                
    // insert the bin
    var search_type = 'prod/submission';

    var insert_data = {'search_type': parent_st,
                   'search_id': parent_sid,
                   'description': desc, 
                    'artist': submit_artist};
    if (parent_context){
        insert_data['context'] = parent_context;
        insert_data['version'] = parent_version;
    }

    try {
        var result = server.insert(search_type, insert_data);
        submit_search_key = result.__search_key__;


        // insert submission in bin
        search_type = 'prod/submission_in_bin';
        insert_data = {'submission_id': result.id,
                        'bin_id': bin_id};
        result = server.insert(search_type, insert_data);
        // check in the uploaded file 
        server.simple_checkin(submit_search_key, upload_context,
        file_name, option);
    } catch(e) {
        var error_str = spt.exception.handler(e);
        alert( "Submission Error: " + error_str );
    }
    

    //server.finish();

    spt.popup.destroy( spt.popup.get_popup( $('edit_popup') ) );
}

spt.Upload.append_complete = function(file_object)
{
    var top_id = 'edit_popup';
    var key = 'edit';
    var values = spt.api.Utility.get_input_values(top_id , null, false);
    var upload_context = 'publish';
    var search_type = values['search_type'];
    var search_id = values['search_id'];
    var file_type = values['edit|file_type'];
    var keep_file_name = values['edit|keep_file_name'];
    if (keep_file_name == 'on')
        keep_file_name = true;
    else
        keep_file_name = false;
   
    
    var file_name = file_object.name;
    file_name = file_name.replace(" ", "_");
    // get the search key from initial set-up
    var search_key = this.customSettings.spt_search_key;

    var server = this.customSettings.server;
    if (! server)
        server = TacticServerStub.get();

    var option = {'mode': 'uploaded', 'description': 'Append Checkin',
        'checkin_cls': 'pyasm.checkin.SnapshotAppendCheckin',
        'file_type': file_type, 'keep_file_name': keep_file_name,
        'create_icon': false};
                
     
    // check in the uploaded file 
    try {
        server.simple_checkin(search_key, upload_context,
        file_name, option);
    } catch(e) {
        var error_str = spt.exception.handler(e);
        alert( "Checkin Error: " + error_str );
    }
    
    //spt.named_events.fire_event('update|' + search_key, {});

    server.finish();

    // remove the upload obj
    spt.Upload.set(key, null);
    //spt.named_events.fire_event('close_EditWdg', {})
    spt.popup.destroy( spt.popup.get_popup( $('edit_popup') ) );
}

//this is TableLayoutWdg specific
spt.Upload.icon_file_queued = function(file_object)
{
    var upload_el = $(this.customSettings.top_id);
    var upload_info = upload_el.getElement(".spt_upload_info");
    var upload_bar = upload_el.getElement(".spt_upload_bar");
    var upload_stats = upload_el.getElement(".spt_upload_stats");

    upload_info.innerHTML = file_object.name;

    var stats = this.getStats();

    // add number of files queued
    var stats_msg = stats.files_queued + " file/s queued";
    upload_stats.innerHTML = stats_msg;

    // make sure bar is empty
    upload_bar.innerHTML = "";


    // Add some text code 
    var row = upload_el.getParent("tr");
    var tbody = upload_el.getParent(".spt_table_tbody");
    var td = upload_el.getParent(".spt_table_td");

    // add a value changed to the row, but not the cell
    tbody.addClass("spt_value_changed");
    //td.addClass("spt_value_changed");

    // skip the commit button for now 
    return;

    //td.setStyle("background-color", "#020");
    row.setStyle("background-color", "#020");

    // make the commit button appear
    spt.dg_table._toggle_commit_btn(td, false);


}




// function to clone the upload widget
/*
spt.Upload.clone_upload = function(evt, bvr)
{
    var src_el = bvr.src_el;

    var tbody = src_el.getParent(".spt_table_tbody");
    var table = src_el.getParent(".spt_table");
    var td = src_el.getParent(".spt_table_td");
    var search_key = tbody.getAttribute("spt_search_key");

    // find all of the uploads
    var exists = false;


    // find out if this element exists yet
    var uploads = table.getElements(".spt_upload");
    var clone = null;
    for (var i = 0; i < uploads.length; i++) {
        var test_search_key = uploads[i].getAttribute("spt_search_key");
        if (test_search_key == search_key) {
            exists = true;
            clone = uploads[i];
            break;
        }
    }

    // if it doesn't already exist, clone it
    if (! exists ) {
        var clone = spt.behavior.clone('cow_button');
        // make sure the margin is back to normal
        clone.setStyle("margin-left", "0px");


        // add it to the dom
        // NOTE: should probably add it to the header
        clone.setAttribute("spt_search_key", search_key);
        clone.inject(tbody, 'before' );

        // set the id so the that the swf can replace the corrent one
        var top_id = "preview";
        var key = "preview|" + search_key;


        var button = clone.getElement(".spt_upload_button");
        button.setAttribute("id", key+"Button");

        // create a new swf
        var settings = {
            'upload_complete_handler':  'spt.Upload.icon_complete',
            'file_queued_handler':  'spt.Upload.icon_file_queued',
        }
        upload = spt.Upload.get(key, {
            create: true,
            settings: settings,
            top_id: top_id,
        } );



    }

    var position = src_el.getPosition();
    clone.setStyle("position", "absolute");
    clone.setStyle('top', position.y);
    clone.setStyle('left',position.x);

    if (exists) {
        clone.setStyle('left',"500px");
    }
}
*/


// used for license renewal
spt.Upload.license_complete = function(file_object)
{
    var top_id = this.customSettings.top_id;
    var instance = spt.Upload.get(top_id);

    var file_name = file_object.name;
    file_name = file_name.replace(" ", "_");

    // get the search key from the table

    var server = TacticServerStub.get();
    var class_name = 'tactic.ui.app.RenewLicenseCbk';
    var info = server.execute_cmd(class_name, {file_name:file_name});
    var key = this.customSettings.key; 
    if (info['status'] == 'OK') {
        // remove the upload obj
        spt.Upload.set(key, null);
        spt.refresh_page();
        //window.location.reload();
    }
    else {
        alert("Error uploading file");
    }
}

spt.Upload.csv_complete = function(file_object)
{
    var top_id = this.customSettings.top_id;
    var instance = spt.Upload.get(top_id);

    var file_name = file_object.name;
    file_name = spt.path.get_filesystem_name(file_name); 
    var class_name = 'tactic.ui.widget.CsvImportWdg';
    var values = spt.api.Utility.get_input_values('csv_import_main');
    values['file_name'] = file_name;
    var info = spt.panel.load('csv_import_main', class_name, {}, values);
   
    spt.Upload.set(top_id, null);

    
   
}





