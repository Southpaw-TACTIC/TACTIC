/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 


function PyMaya() {
    this.name           = "maya";
    this.user           = null;
    this.local_dir      = null;
    this.context_url    = null;
    this.base_url       = null;
    this.upload_url     = null;
    this.sandbox_dir    = null;
    this.asset_dir      = null;
    this.project_code   = null;
    this.use_java       = true;
    this.port           = 4444;
}



PyMaya.prototype.get_ticket = function() {
    // before every download, add the ticket and set the server
    var ticket = spt.Environment.get().get_ticket()
    return ticket
}



/**
  * Initializes the maya session to handle running of scripts on the client
  * side through pymaya
  */
PyMaya.prototype.init = function()
{
    // before every download, add the ticket and set the server
    var ticket = this.get_ticket()
    if (ticket.indexOf(';') >= 0 )
    {
        //alert('Bad cookie detected. Please clear the cookie in your browser and relogin')
        ticket = ticket.split(';')[0]
    }
        
    this.has_connect_error = false
    
    this.mel('// Tactic: Please select "Allow All"')
   
    this.maya_version = this.mel('getApplicationVersionAsFloat()')
    if (this.maya_version == null)
        this.maya_version = 8.5
    else
        this.maya_version = parseFloat(this.maya_version)
    
    this.mel('string $tactic_ticket = "'+ticket+'"')

    // and set the xmlrpc server
    var xmlrpc_server = this.base_url + "/tactic/default/XMLRPC"
    this.mel('string $tactic_xmlrpc = "'+xmlrpc_server+'"')

    // and set the upload server
    this.mel('string $tactic_upload = "'+this.upload_url+'"')
    // and set the user
    this.mel('string $tactic_user = "'+this.user+'"')

    // and set the tmpdir server
    var tmp_dir = this.local_dir+"/temp"
    this.mel('string $tactic_tmpdir = "'+tmp_dir+'"')
    // set the sandbox dir
    var sandbox_dir = this.local_dir+"/temp"
    this.mel('string $tactic_sandbox_dir = "'+sandbox_dir+'"')
    this.mel('string $tactic_project_code = "'+ this.project_code +'"')
    this.mel('string $tactic_base_url = "'+ this.base_url +'"')

}

PyMaya.prototype.get_init_script = function()
{
    var list = new Array();
    
    
    var ticket = spt.Environment.get().get_ticket();
    list.push('string $tactic_ticket="' + ticket + '";');
    //xmlrpc_server = this.base_url + this.context_url+"/XMLRPC;";
    var xmlrpc_server = this.base_url + "/tactic/default/XMLRPC"
    list.push('string $tactic_xmlrpc="' + xmlrpc_server + '";');
    list.push('string $tactic_upload="' + this.upload_url + '";');
    list.push('string $tactic_user="' + this.user + '";');
    var tmp_dir = this.local_dir+"/temp"
    list.push('string $tactic_tmpdir="' + tmp_dir + '";');

    sandbox_dir = this.local_dir+"/temp"
    list.push('string $tactic_sandbox_dir="' + sandbox_dir + '";');
    list.push('string $tactic_project_code="' + this.project_code + '";');
    list.push('string $tactic_base_url="' + this.base_url + '";');
    
    list.push('global proc tactic_publish() {');
    str = list.join('\\n') + '\\n';
    return str;

}

PyMaya.prototype.get_temp_path = function(prefix)
{
    var dir =  "C:/sthpw/temp/";
    var path = dir + prefix;
    var ext = '.ma';
    var tmp = new Array();
    tmp.push(path);
    tmp.push(ext);
    return tmp;

}

PyMaya.prototype.batch_write_cbk = function(bvr, values, kwargs)
{
    var cmd_list = new Array();
    cmd_list.push('from pyasm.application.common.interpreter.tactic_client_lib import *');
    cmd_list.push('from pyasm.application.common import AppEnvironment')
    cmd_list.push('env = AppEnvironment.get()')
    cmd_list.push('ticket = env.get_ticket()')
    cmd_list.push('project = env.get_project_code()');
    cmd_list.push('server_name = env.get_server()')
    cmd_list.push('client_server = TacticServerStub(setup=False)')
    cmd_list.push('client_server.set_server(server_name)');
    cmd_list.push('client_server.set_project(project)');
    cmd_list.push('client_server.set_ticket(ticket)');

    values_str = JSON.stringify(values)
    values_str = values_str.replace(/"/g, "'")
    cmd_list.push("rtn = client_server.execute_cmd('" + bvr.cbk + "',args=" +
        "{'search_type': '" + bvr.search_type +
        "','texture_search_type': '" + bvr.texture_search_type + "'}, values=" + values_str  + ")");
    cmd_list.push("\\\\nif rtn: print '\\\\\\\\n%s' %rtn.get('description')");
    cmd_str = cmd_list.join(';'); 
    cmd_str = 'python "' + cmd_str +  '";';
    this.batch_write(bvr.batch_path, cmd_str, {write_mode: kwargs.write_mode});
    this.batch_write(bvr.batch_path, '}', {write_mode: kwargs.write_mode});

}

PyMaya.prototype.linesep = '\\n';

// write a string to a batch file
PyMaya.prototype.batch_write = function(batch_path, cmd, kwargs)
{
    if (!kwargs)
        var write_mode = 'w';
    else
        var write_mode = kwargs.write_mode;
    var cmd_list = new Array()
    if (typeof(cmd) == 'string')
        cmd_list.push(cmd);
    else
        cmd_list = cmd;
    for (var i=0; i< cmd_list.length; i++) {
        var cmd = cmd_list[i];
        cmd =  cmd.replace(/"/g, '\\"');
        this.mel('$file = `fopen "' + batch_path + '" "' + write_mode + '"`;' 
                + 'fprint $file ("' + cmd + this.linesep + '");'
                + 'fclose $file;');
    }
    // this.py("file = open('" + batch_path + "', '" + write_mode + "'); file.write('" 
    //        + cmd_str + this.linesep + "'); file.close();");

}

PyMaya.prototype.get_open_script = function(file_path)
{
    str = 'file -f  -typ "mayaAscii" -o "' + file_path + '";';
    //str = str.replace(/"/g, '\\"');
    return str;
}

PyMaya.prototype.batch_write_py_file = function()
{
    var batch_path = arguments[0];
    if (this.maya_version >= 8.5) {
        var arg_list = new Array();
        arg_list.push(arguments[1]);
        arg_list.push('maya');
        for (var i = 2; i < arguments.length; i++) {
            arg_list.push(arguments[i]);
        }

        path = this.local_dir + "/download"
        var cmd = 'python "import sys; sys.path.insert(0,\'' +path+ '\'); import delegator; delegator.start(\'' + arg_list.join("','") + '\')";';
    }
    else {
        // use PyMaya plugin

        //var cmd = 'python -r -f "' + arguments[0] + '" '
        var cmd = 'python -f "' + arguments[1] + '" '
        var args = " maya"
        for (var i = 2; i < arguments.length; i++)
        {
            args = args + " \"" + arguments[i] + "\""
        }
        var cmd = cmd + " " + args + ";";
    }
    this.batch_write(batch_path, cmd, {write_mode : 'a'});
}

PyMaya.prototype.run_batch = function(file_path)
{
    //alert('Batch script generated. Please run \n mayabatch -script  -c "source \\\"' + file_path + '\\\";tactic_publish()"');
    
    //crazy escaping
    var file_path = '\\\\\\"' + file_path + '\\\\\\"';
    var mel_cmd = 'system("start cmd.exe /K mayabatch -script -c \\\"source ' + file_path + ';tactic_publish();\\\"")';
    
    this.mel(mel_cmd);
    
}
/**
 * Call an arbitrary mel command through Maya
 */
PyMaya.prototype.mel = function(cmd)
{
    
    if (this.maya_version <= 7.0) {
        document.location = "mel://" + cmd
    }
    else {
        if (this.use_java == true) {
            var port = this.port;
            if (port == null || typeof(port) == 'undefined') {
                port = 4444;
            }
            if (this.has_connect_error)
                return;
            var applet = spt.Applet.get();
            var result = applet.command_port('127.0.0.1', port, cmd)
            var error = result[1]
            if (error != '' && !this.has_connect_error)
            {
                //alert("Java connector chosen in TACITC Preferences. Connect Error: " + 
                //error + "\nRun MEL on start-up: commandPort -n \"127.0.0.1:" + port + "\"")
                this.has_connect_error = true;
                alert("Cannot connect to port 127.0.0.1:" + port + "\nRun MEL on start-up: commandPort -n \"127.0.0.1:" + port + "\"\n or in Win 7\n" + 
"commandPort -n \":4444\"; commandPort -n \"127.0.0.1:4444\"; Please refresh this page."
                );

            }

            return result[0]

        }
        else {
            try {
                var result = MWT_Execute(cmd)
                return result
            } catch(e) {
                Overlay.hide_progress()
                throw(e)
            }
        }

    }

}




/**
 * Call an arbitrary python command through PyMaya
 */
PyMaya.prototype.py = function(cmd)
{
    var cmd;
    if (this.maya_version < 8.5) {
        cmd = 'python -e "' + cmd + '"';
    }
    else {
        cmd = 'python "' + cmd + '"';
    }
    this.mel(cmd);
}


/**
  * Make a system call through Maya
  */
PyMaya.prototype.system = function(cmd)
{
    var cmd = 'system("' + cmd + '")'
    this.mel(cmd);
}


/**
 * Exectue a python file through PyMaya
 */
PyMaya.prototype.py_file = function()
{
    if (this.maya_version >= 8.5) {
        var args = "'" + arguments[0] + "', 'maya'"
        for (var i = 1; i < arguments.length; i++) {
            args = args + ", '" + arguments[i] + "'"
        }

        path = this.local_dir + "/download"
        var cmd = "python \"import sys; sys.path.insert(0,'"+path+"'); import delegator; delegator.start(" + args + ")\""
        this.mel(cmd)
    }
    else {
        // use PyMaya plugin

        //var cmd = 'python -r -f "' + arguments[0] + '" '
        var cmd = 'python -f "' + arguments[0] + '" '
        var args = " maya"
        for (var i = 1; i < arguments.length; i++)
        {
            args = args + " \"" + arguments[i] + "\""
        }

        var cmd = cmd + " " + args
        this.mel(cmd)   
    }
}




/**
  * Download an arbitrary file to the client
  */
PyMaya.prototype.py_download = function(url, to_path)
{
    var b=to_path.match(/^(.*)[\/|\\]([^\\\/]+)$/);
    var to_dir = b[1]

    cmd = "import os, urllib, sys;"
    this.py(cmd)
    cmd = "if not os.path.exists('"+to_dir+"'): os.makedirs('"+to_dir+"');"
    this.py(cmd)
    cmd = "f = urllib.urlopen('"+url+"');   file = open('"+to_path+"', 'wb');    file.write(f.read());    file.close();"
    this.py(cmd)

}



function py_download_delegator()
{

    // call the global app initializer

    app.init()

    // test downloading the zip file
    var zip = app.local_dir+"/download/tactic.zip"
    app.py_download(app.base_url+"/context/client/tactic.zip", zip)

    // test downloading the zip file
    /*
    var zip = app.local_dir+"/download/custom.zip"
    app.py_download(app.base_url+"/context/client/custom.zip", zip)
    */

    var script_name = "delegator.py"
    var script = app.local_dir+"/download/" + script_name
    app.py_download(app.base_url+"/context/client/"+script_name+".xx", script)

    return script

}




/* create a set */
function create_set(set_name, cat_name, context)
{
    script_path = py_download_delegator()
    app.py_file(script_path, "create_set_asset.create", set_name, cat_name, context)
     
    introspect() 
    return true 
}    

function select_checkbox(selected, match)
{
    var selected_value = selected.value

    // go through each checkbox and uncheck all those that are not the selected
    var checkboxes = document.form.sobject_levels
    for (var i = 0; i < selected.length; i++) {
        var value = checkboxes[i].value
        if (value == undefined)
            continue

        var tmp = value.split("|")
        if (tmp[0] != match)
            continue

        if (value != selected_value)
            checkboxes[i].checked = false
    }

}



function get_selected_checkboxes(name)
{
    var selected = new Array()

    // dump and upload all of the checked ones
    var checkboxes = document.getElementsByName(name)
    if (checkboxes == undefined)
        return selected;
  
    if ( checkboxes != undefined && checkboxes.length == undefined) {

        if ( checkboxes.checked == true );
           selected.push(checkboxes.value);
    }
    else {
        var count = 0
        for ( var i = 0; i < checkboxes.length; i++ )
        {
            if ( checkboxes[i].checked == true )
            {
                selected.push(checkboxes[i].value)
                count++
            }
        }

    }
    return selected

}


/* Checkin functions */

function checkin_set(set_name, set_code, context)
{
    Overlay.display_progress('Publishing ...', false)
    var script_path = py_download_delegator()
    app.py_file(script_path, "checkin.checkin_set", set_name, set_code, context)
    Overlay.hide_progress()
    return true
}

/* This Function group defines the execution of different checkins
 */
Publish = new function()
{
    this.asset = function(button_name, bvr)
    {
        var search_type = bvr.search_type;
        var selected = get_selected_checkboxes("asset_instances")
        var set_selected = get_selected_checkboxes("set_instances")
        // get all of the loader options
        var options = new Array()
        var top = spt.get_parent_panel(bvr.src_el);
       
        var file_type = spt.api.Utility.get_input(top, 'file_type');
        options.push("file_type=" + file_type.value)
        // get the export type
        var export_method = get_selected_checkboxes("export_method")
        for (var count = 0; count < export_method.length; count++) {
            options.push("export_method=" + export_method[count])
        }

        // batch option
        var use_batch = spt.api.Utility.get_input(top,"use_batch").checked;
        bvr.use_batch = use_batch;
        
        // get the currency setting
        var export_method = get_selected_checkboxes("currency")
        for (var count = 0; count < export_method.length; count++) {
            options.push("currency=" + export_method[count])
        }

        var context = spt.api.Utility.get_input(top, search_type + '_context');
        options.push("context=" + context.value)

        var snap_type = spt.api.Utility.get_input(top,'checkin_snapshot_type');
        if (snap_type)
            options.push("snapshot_type=" + snap_type.value)
      
        // auto_version is the opposite of use_filename
        var use_filename = spt.api.Utility.get_input(top,"auto_version");
        if (selected.length + set_selected.length > 1){
            use_filename.checked = true;
        }

        options.push("use_filename=" + !use_filename.checked)

        var handle_tex = spt.api.Utility.get_input(top, "handle_texture_dependency");
        var handle_tex_value = handle_tex.value;
        
        if ( handle_tex_value=='true' || handle_tex.checked) 
            handle_tex = 'true'
        else
            handle_tex = 'false'

        options.push("handle_texture_dependency=" + handle_tex);

        var handoff_opt = spt.api.Utility.get_input(top, "use_handoff_dir");
        var handoff_opt_value = handoff_opt.value;
        if ( handoff_opt_value=='true' || handoff_opt.checked) 
            handoff_opt = 'true'
        else
            handoff_opt = 'false'
        options.push("use_handoff_dir=" + handoff_opt);
        
        // get the texture match method
        var tex_match = get_selected_checkboxes("texture_match")
        for (var count = 0; count < tex_match.length; count++) {
            options.push("texture_match=" + tex_match[count])
        }
        
        var script_path = py_download_delegator();
        var batch_dir = bvr.batch_dir;
        
        // write the init vars if use_batch is true;
        if (bvr.use_batch) {
            var kwargs = {write_mode: 'w'};
            var init_script =  app.get_init_script();
            if (!init_script) {
                alert ('Batch script has not been implemented for this app.');
                return
            }
            
            var date_obj = new Date()
            var suffix = date_obj.getFullYear().toString()+(date_obj.getMonth() + 1).toString()
                + date_obj.getDate().toString()+date_obj.getHours().toString() 
                + date_obj.getMinutes().toString() + date_obj.getSeconds().toString(); 
            var batch_path = batch_dir + '/' +  'app_batch' + '_' + suffix + '.py';
            
            bvr.batch_path = batch_path;
            
            app.batch_write(batch_path, init_script, kwargs);
            
            //save the file in temp dir
            var tmp_path_list = app.get_temp_path('batch_script_' + app.user );
            
            var new_tmp_path = tmp_path_list[0] + '_' + suffix  + tmp_path_list[1];
            
            //save and then copy the file to a new location with a suffix
            tmp_path = tmp_path_list[0] + tmp_path_list[1];
            app_save_file(tmp_path);
            
            app_copy_file(tmp_path, new_tmp_path);
            var open_script = app.get_open_script(new_tmp_path);
            app.batch_write(bvr.batch_path, open_script, {write_mode: 'a'});

        }

        for (var count = 0; count < selected.length; count++) {

            // get all of the info
            var tmp = selected[count].split("|");
            var namespace = tmp[0];
            var asset_code = tmp[1];
            var instance = tmp[2];
            // add the handlers
            var handlers = spt.api.Utility.get_input(top, 'handler_'+asset_code);
            if (handlers)
                handlers = handlers.value;
            else
                handlers = '';
           
            // only clean_up when it begins
            if (count==0) 
                options.push('clean_up=true');
            else if (count==1) 
                options.pop();


            if (bvr.use_batch){ 
                app.batch_write_py_file(batch_path, script_path, "checkin.checkin_asset", namespace, asset_code, instance, options.join("|"), handlers);
            }
            else {
                app.py_file(script_path, "checkin.checkin_asset", namespace, asset_code, instance, options.join("|"), handlers);
            }

        }


        for (var count = 0; count < set_selected.length; count++) {
            // get all of the info
            var tmp = set_selected[count].split("|");
            var namespace = tmp[0];
            var asset_code = tmp[1];
            var instance = tmp[2];
            app.py_file(script_path, "checkin.checkin_set", namespace, asset_code, options.join("|"));
        }
        this.done(button_name, bvr);
    }

    this.anim = function(button_name, bvr)
    {
        var selected = get_selected_checkboxes("asset_instances")
        var script_path = py_download_delegator()
        
        var options = new Array()

        var top = spt.get_parent_panel(bvr.src_el);
        var context = spt.api.Utility.get_input(top, 'prod/shot_instance_context');

        options.push("context=" + context.value);
        options.push("use_filename=false");
        
        var handoff_opt = spt.api.Utility.get_input(top, "use_handoff_dir");
        var handoff_opt_value = handoff_opt.value;
        if ( handoff_opt_value=='true' || handoff_opt.checked) 
            handoff_opt = 'true'
        else
            handoff_opt = 'false'
        options.push("use_handoff_dir=" + handoff_opt);
        for (var count = 0; count < selected.length; count++) {
            // get all of the info
            var tmp = selected[count].split("|")
            var namespace = tmp[0]
            var asset_code = tmp[1]
            var instance = tmp[2]
            // only clean_up when it begins
            if (count==0) 
                options.push('clean_up=true');
            else if (count==1) 
                options.pop();

            app.py_file(script_path, "checkin.checkin_anim", namespace, asset_code, instance, options.join('|'))
        }
        this.done(button_name, bvr)
    }

    this.shot = function(button_name, bvr)
    {
        var options = new Array()
        var top = spt.get_parent_panel(bvr.src_el);

        var search_type = bvr.search_type;
        var shot_code = spt.api.Utility.get_input(top,"shot_code").value;
        var context = spt.api.Utility.get_input(top, search_type + "_context").value;
        var checkin_status = spt.api.Utility.get_input(top,'checkin_status');
        if (checkin_status) {
            if (checkin_status.value == '')
            {
                alert("Please select a checkin status first.");
                return false;
            }
        }
    
        //auto_version is the opposite of use_filename
        var use_filename = ! spt.api.Utility.get_input(top,"auto_version").checked;
        options.push("use_filename=" + use_filename)
       

        var handle_tex = spt.api.Utility.get_input(top, "handle_texture_dependency");
        var handle_tex_value = handle_tex.value;
        if ( handle_tex_value=='true' || handle_tex.checked ) 
            handle_tex = 'true'
        else
            handle_tex = 'false'
        options.push("handle_texture_dependency=" + handle_tex);

        var handoff_opt = spt.api.Utility.get_input(top,"use_handoff_dir");
        var handoff_opt_value = handoff_opt.value;
        if ( handoff_opt_value=='true' || handoff_opt.checked) 
            handoff_opt = 'true'
        else
            handoff_opt = 'false'
        options.push("use_handoff_dir=" + handoff_opt);
        // add the handlers
        var handlers = spt.api.Utility.get_input(top, 'handler_'+ shot_code);
        if (handlers)
            handlers = handlers.value;
        else
            handlers = '';

        // shot has no batch option now
        bvr.use_batch = false;
        // initiates clean_up
        options.push('clean_up=true');
        // no need to pass in checkin_as and currency here since 
        // the Cbk is taking care of it
        var script_path = py_download_delegator()
        app.py_file(script_path, "checkin.checkin_shot", shot_code, context, options.join('|'), handlers)
        this.done(button_name, bvr)
    }

    this.shot_set = function(button_name, bvr)
    {
        //TODO: these element names should be passed in
        var shot_code = document.form.elements["shot_code"].value
        var process = document.form.elements["shot_process"].value
        var context = document.form.elements["shot_context"].value
        var sub_context = document.form.elements["shot_sub_context"].value
        var checkin_as = document.form.elements["checkin_as"].value
        var currency = document.form.elements["currency"].value



        if (sub_context != "")
            context = context + "/" + sub_context
        var unknown_ref = document.form.elements["unknown_ref"].value
        var desc = document.form.elements[shot_code + "_set_description"].value
        var set_names = get_selected_checkboxes("shot_set_instances")
        if (set_names.length == 0)
        {
            alert('Please select a checkbox for the shot set ')
            return false
        }
        var options = new Array()

        var script_path = py_download_delegator()
        
        // auto_version is the opposite of use_filename
        var auto_version_cb = spt.api.Utility.get_input(document,"auto_version");
        if (set_names.length > 1){
            auto_version_cb.checked = true;
        }

        options.push("use_filename=" + !auto_version_cb.checked)
        var handle_tex = spt.api.Utility.get_input(document, "handle_texture_dependency");
        var handle_tex_value = handle_tex.value;
        if ( handle_tex_value=='true' || handle_tex.checked) 
            handle_tex = 'true'
        else
            handle_tex = 'false'
        options.push("handle_texture_dependency=" + handle_tex);
        for (var k=0; k < set_names.length; k++)
        {
            // only clean_up when it begins
            if (k==0) 
                options.push('clean_up=true');
            else if (k==1) 
                options.pop();
            var set_name = set_names[k]
            app.py_file(script_path, "checkin.checkin_shot_set", shot_code, 
                set_name, process, context, checkin_as, currency, unknown_ref, desc, !auto_version_cb.checked, options.join('|'))
        }
    }

    // turn on the button to pass the check of Cbk
    this.done = function(button_name, bvr)
    {
        var top = spt.get_parent_panel(bvr.src_el);
        spt.api.Utility.get_input(top, button_name).value = button_name;
        //TODO, make it work with popup window also
        //var values = spt.api.Utility.get_input_values("main_body");
        var values = spt.api.Utility.get_input_values(top);
        try {
            if (bvr.use_batch) {
                app.batch_write_cbk(bvr, values, {write_mode: 'a'});
           
            }
            else { 
                server = new TacticServerStub.get();
                var rtn = server.execute_cmd(bvr.cbk,
                {'search_type': bvr.search_type, 'texture_search_type': bvr.texture_search_type}, values);
            }
        }
        catch(e) {
            var error_str = spt.exception.handler(e);
            spt.alert( "Checkin Error: " + error_str );
            return;
        }
        // Jump to Log Link
        //TODO: double check these parameters, popup doesn't display very well
        // due to the fact that the menu bar disappears sometimes in the top
        // of the browser client area
        if (bvr.use_batch) {
            //alert('Saved batch script in ' + bvr.batch_path);
            //run the script
            app.run_batch(bvr.batch_path);
        }
        else {
            //var class_name ="pyasm.prod.web.PublishLogWdg";
            var class_name ="tactic.ui.panel.ViewPanelWdg";
            var element_name ="checkin_log";
            var title = "Checkin Log";
            var options = {  "view" : "log",
                             "search_view" : "search",
                             "search_type" : "sthpw/snapshot",
                             "state": {
                                "snapshot_filter_enabled": "on",
                                "publish_search_type": bvr.search_type}
                };
            var values = {};
            /*
            var bvr2 =  {    
                    //"target_id": "main_body", 
                    "options": {"class_name": "pyasm.prod.web.PublishLogWdg",
                                "publish_search_type": bvr.search_type, "path": "/Project_view/application/checkin_log", 
                                "element_name": "checkin_log",
                                "view" : "log",
                                "snapshot_filter_enabled": "on"},
                    "title": "Checkin Log",
                    "is_popup": false
                    };
                    */
            spt.tab.add_new(element_name, title, class_name, options, values)
            //spt.side_bar.display_link_cbk(null, bvr2);
        }
    }

}

function checkin_selected_assets(button_name, bvr)
{
    // get selected checkboxes
    var selected = get_selected_checkboxes("asset_instances")
    var set_selected = get_selected_checkboxes("set_instances")
    
    if (selected.length == 0 && set_selected.length == 0)
    {
        alert("One or more checkboxes have to be checked first");
        return false;
    }
    var top = spt.get_parent_panel(bvr.src_el);
    var checkin_status = spt.api.Utility.get_input(top, 'checkin_status');
    if (checkin_status) {
        if (checkin_status.value == '')
        {
            alert("Please select a checkin status first.");
            return false;
        }
    }

    //Overlay.display_progress('Publishing ...', false);
    spt.app_busy.show( 'Publish', 'Publishing Asset ...');
       
    setTimeout(function() {Publish.asset( button_name , bvr);
                            spt.app_busy.hide();}, 200);
    return true;
}




function checkin_selected_anim(button_name, bvr)
{
    // get selected checkboxes
    var selected = get_selected_checkboxes("asset_instances");
    if (selected.length == 0)
    {
        alert("One or more checkboxes have to be checked first")
        return false
    }
    //Overlay.display_progress('Publishing ...', false);
    //show busy message
    spt.app_busy.show( 'Publish', 'Publishing Asset Instance in Shot');
       
    setTimeout(function() {Publish.anim( button_name , bvr);
                            spt.app_busy.hide();
                    }, 20 );
}



function checkin_shot(button_name, bvr)
{
    //Overlay.display_progress('Publishing ...', false);
    //show busy message
    spt.app_busy.show( 'Publish', 'Publishing Shot');
       
    setTimeout(function() {Publish.shot( button_name , bvr);
                            spt.app_busy.hide();
                    }, 20 );

    return true;
}

function checkin_shot_set(button_name, bvr)
{
    //Overlay.display_progress('Publishing ...', false);
    spt.app_busy.show( 'Publish', 'Publishing Shot Set');
    setTimeout(function() {Publish.shot_set( button_name , bvr);
                            spt.app_busy.hide();
                    }, 20 );
    return true;
}




function checkin_selected_sobjects()
{
    // get selected checkboxes
    var selected = get_selected_checkboxes("search_key")
    if (selected.length == 0)
        return false

    var script_path = py_download_delegator()

    for (var count = 0; count < selected.length; count++) {
        // get all of the info
        search_key = selected[count]
        app.py_file(script_path, "checkin.checkin_layer", search_key)
    }

    return true
}






/* Function that uses the pipeline interpreter to checkin */
function checkin_custom()
{
    // get selected checkboxes
    var selected = get_selected_checkboxes("search_key")
    if (selected.length == 0 )
    {
        alert("One or more checkboxes have to be checked first")
        return false
    }

    var ui_elements = new Array()
    ui_elements.push('checkin_snapshot_type')


    var options = ''
    for (var i = 0; i < ui_elements.length; i++) {
        ui_element = ui_elements[i]
        var value = get_elements(ui_element).get_values()
        options += ui_element + "=" + value
        
    }
    options = $('form').toQueryString()

    var ticket = app.get_ticket()

    var script_path = py_download_delegator()
    app.py_file(script_path, "pyasm.application.common.interpreter.callback.callback", ticket, options)
    //this.done(button_name)

    /*
    Overlay.display_progress('Publishing ...', false)
    setTimeout("Publish.asset('" + button_name + "')", 100)
    //Overlay.hide_progress()
    */
    return true
}



/* Function that uses the pipeline interpreter to checkin */
function execute_client_callback(callback)
{
    // get all of the elements
    options = $('form').toQueryString()

    // TODO: not sure if ticket should be passed this way 
    var ticket = app.get_ticket()

    var script_path = py_download_delegator()
    app.py_file(script_path, "pyasm.application.common.interpreter.callback.callback", ticket, callback, options)
    //this.done(button_name)

    /*
    Overlay.display_progress('Publishing ...', false)
    setTimeout("Publish.asset('" + button_name + "')", 100)
    //Overlay.hide_progress()
    */
    return true
}






function get_load_options(prefix, kwargs)
{
    // prefix: 'prod/asset', 'prod/shot_instance', or 'prod/shot'
    // get all of the loader options
    var options = {};
    var top = document;

    if (kwargs && kwargs.bvr){
        top = spt.get_parent_panel(kwargs.bvr.src_el);
    }
       
    var input_array = ['connection', 'instantiation','dependency'];
    for (var k=0; k< input_array.length; k++)
    {
        var option = input_array[k];
        var inputs = spt.api.Utility.get_input_values(top, 'input[name='  + prefix+"_" + option + ']');
        input_list = inputs[prefix + "_" + option];
        if (input_list) {
            for (var count = 0; count < input_list.length; count++) {
                var value = input_list[count];
                if (value) {
                    options[option] = value;
                }
            }
        }

    }
    if (kwargs && kwargs.is_array) {
        options_array = new Array();
        for (i in options){
            options_array.push(i+'=' +options[i]);
        }
        return options_array;
    }
    return options;
}

/*
function import_instance(instance)
{
    app.mel('file -importReference "' + instance  + '"')
}
*/

/* swaping the message of the Load button */
function swap_msg(control, msg)
{
    var selected = get_selected_checkboxes("load_snapshot")
    if (selected.length > 0)
        control.innerHTML = msg  
}

/* This Function group defines the execution of different types of loading
 */
Load = new function()
{
    this.asset = function(prefix, cb_name, bvr)
    {   
        var is_anim = false;
        if (prefix=="prod/shot_instance")
            is_anim = true;

        var options = get_load_options(prefix, {'bvr': bvr});

        // the bvr can override instantiation
        if (bvr.instantiation) {
            options["instantiation"] = bvr.instantiation;
        }
        
        options_array = new Array();
        for (i in options){
            options_array.push(i+'=' +options[i]);
        }
        var selected = get_selected_checkboxes(cb_name);

        // get the multiplier
        var multiplier_el = spt.get_cousin(bvr.src_el, ".spt_view_panel", ".load_multiplier");
        var multiplier = "";
        if (multiplier_el)
            multiplier = multiplier_el.value;
        if (multiplier == "")
            multiplier = 1;
        
        for (var count = 0; count < selected.length; count++) {
            var info = selected[count];
            if (is_anim == false) {
                // convert value into a snapshot_code and a context
                var values = info.split("|");
                var snapshot_code = values[0];
                var context = values[1];
                var ns =  values[2];
                //snap_node_name = values[3]

                for (var i=0; i < multiplier; i++)
                    this.load_snapshot(snapshot_code, context, options_array.join("|"));
            }
            else
            {
                var values = info.split("|");
                var snapshot_code = values[0];
                var shot_code = values[1];
                var instance = values[2];
                var context = values[3];
                var ns = values[4];
                //snap_node_name = values[5]
                this.load_anim_snapshot(snapshot_code,shot_code,instance,context,options_array.join("|"));
            }
            
        } 
        introspect(bvr);
        send_warning();

        //Overlay.hide_progress();
        spt.app_busy.hide();
       
        //var evt = {};
        //spt.dg_table.search_cbk(evt, bvr);
    }

    this.load_snapshot = function(snapshot_code, context, options)
    {
        var script_path = py_download_delegator()
        app.py_file(script_path, "tactic_load.load", snapshot_code, context, options)

        /*
        var error_txt = this.local_dir+"/temp/error.txt";
        var applet = spt.Applet.get();
        var error_msg =  applet.read_file(error_txt);
        if (error_msg)
            spt.alert(error_msg);
        */
        return true
    }



    this.load_anim_snapshot = function(snapshot_code, shot_code, instance, context, options)
    
    {
        var script_path = py_download_delegator()
        app.py_file(script_path, "tactic_load.load_anim", snapshot_code, shot_code, instance, context, options)
        return true
    }
}

function load_selected_snapshots_cbk(prefix, cb_name, bvr)
{
    var panel;
    var src_el;
    var activator = spt.smenu.get_activator(bvr);
    if (activator != null) {
        src_el = activator;
    }
    else {
        src_el = bvr.src_el;
    }

    var panel = spt.get_parent_panel(src_el);
    /*
    var panel = src_el.getParent(".spt_view_panel");
    if (panel == null) {
        panel = src_el.getParent(".spt_panel");
    }

    */

    var table = panel.getElement(".spt_table");

    //var search_types = spt.dg_table.get_selected_search_keys(table);
    var selected = spt.dg_table.get_selected(table);
    for (var i = 0; i < selected.length; i++) {
        var select = selected[i];
        inputs = spt.api.Utility.get_inputs(select, cb_name);
        for (var j = 0; j < inputs.length; j++) {
            inputs[j].checked = true;
        }
    }

    var selected = get_selected_checkboxes(cb_name)
    if (selected.length == 0) {
        alert("Nothing selected to load");
        return false
    }


    // FIXME: this is using Load.asset - probably not general enough

    spt.app_busy.show( 'Load', 'Loading ' + prefix + ' ...');
    setTimeout(function(){ Load.asset( prefix , cb_name, bvr );
                            spt.app_busy.hide();}, 100) 
    
    return true
}

/* label a particular snapshot as e.g. approved, ref, test */
function label_snapshot(cb_name)
{
    var e=get_elements(cb_name)
    document.form.elements['snapshot_code'].value = e.get_value()
    document.form.elements['snapshot_attr'].value = 'label' 
}
    
/* update the tactic session info */
function update_snapshot(snapshot_code, asset_code, namespace, context)
{
    Overlay.display_progress('Updating ...', false)
    var script_path = py_download_delegator()
    app.py_file(script_path, "tactic_load.update", snapshot_code,
         asset_code, namespace, context)
    introspect()
    Overlay.hide_progress()
    return true
}






/* Introspection */
function introspect(bvr)
{
    spt.app_busy.show("Introspect", "Inspecting session for contents");
    var script_path = py_download_delegator();
    app.py_file(script_path, "tactic_introspect.introspect");
    //transitioning to bvr
    var top = null;
    if (bvr) {
        top = spt.get_parent_panel(bvr.src_el);
        if(!top){
            //use activator
             var activator = spt.smenu.get_activator(bvr);
             top = spt.get_parent_panel(activator);
        }
    }
   
        
    
    if (top) 
        spt.panel.refresh(top, {}, true);
    else
        spt.tab.reload_selected();

    spt.app_busy.hide();
    return true;
}

function introspect_select()
{
    var script_path = py_download_delegator()
    app.py_file(script_path, "tactic_introspect.introspect_select")
    return true
}


/* Common functions */
function send_warning()
{
    //FIXME: Skip this step for IE: it goes nuts after doing a load into 
    // Maya 
    if (spt.browser.is_IE() ) { 
        return true; 
    }

    var script_path = py_download_delegator()
    app.py_file(script_path, "common.upload_warning")
    return true
}

function py_select(is_anim)
{

    // get selected checkboxes
    var selected = get_selected_checkboxes("load_snapshot")
    if (selected.length == 0) {
        alert("Nothing selected")
        return false
    }
    
    var script_path = py_download_delegator()
    for (var i=0; i < selected.length; i++)
        app.py_file(script_path, "tactic_select.select", selected[i], is_anim.toString())
    return true
}


function py_delete(is_anim)
{

    // get selected checkboxes
    var selected = get_selected_checkboxes("load_snapshot")
    if (selected.length == 0) {
        alert("Nothing selected")
        return false
    }


    var script_path = py_download_delegator()
    for (var i=0; i < selected.length; i++)
    {
        var value = confirm("Are you sure you want to remove '"+selected[i]+"'")
        if ( value == false )
            continue
        app.py_file(script_path, "tactic_select.delete", selected[i], is_anim.toString())
    }
    introspect()
    spt.tab.reload_selected();
    return true
}


function py_update(is_anim)
{
    var options = get_load_options(is_anim, {'is_array': true})

    // get selected checkboxes
    var selected = get_selected_checkboxes("load_snapshot")
    if (selected.length == 0) {
        alert("Nothing selected")
        return false
    }

    var value = confirm("Are you sure you want to delete and replace with '"+selected[0]+"'")
    if ( value == false )
        return false

    script_path = py_download_delegator()
    
    for (var i=0; i < selected.length; i++)
        app.py_file(script_path, "tactic_select.update", selected[i], 
            is_anim.toString(), options.join("|"))
    introspect()
    spt.tab.reload_selected();
    return true
}



/*
 * This function updates not by deleting (as done by py_update), but tries
 *  to replace the underlying reference
 */
function py_replace_reference(bvr, prefix, input_name)
{
    var options = get_load_options(prefix,  {'is_array': true});
    // get selected checkboxes
    var top = spt.get_parent_panel(bvr.src_el);
    if(!top){
        //use activator
         var activator = spt.smenu.get_activator(bvr);
         top = spt.get_parent_panel(activator);
    }

    if (input_name == null)
        input_name = 'load_snapshot';

    //var selected = spt.api.Utility.get_input_values(top, "input[name=" + input_name + "]");
    //selected = selected[input_name];
    selected = get_selected_checkboxes(input_name);
    
    
    if (selected.length == 0) {
        alert("Nothing selected")
        return false
    }
    
    // just take the node name
    selection = new Array()
    for (var i=0; i < selected.length; i++)
    {
        tmp = selected[i].split('|')
        selection.push(tmp[tmp.length-1])
    }
    value = confirm("Are you sure you want to update by replacing all of the references '"
        +selection.join(', ')+"'")
    if ( value == false )
        return false
    
    var script_path = py_download_delegator()
    for (var i=0; i < selected.length; i++)
    {
        app.py_file(script_path, "tactic_select.replace_reference", selected[i],
            prefix, options.join("|"))
    }
    introspect(bvr)
    return true
}


function py_replace_reference_selected(bvr, prefix, input_name)
{
    var options = get_load_options(prefix,  {'is_array': true})
    options.push('replace_selected=true')
    // get selected checkboxes
    var top = spt.get_parent_panel(bvr.src_el);
    if (!top){
        //use activator
         var activator = spt.smenu.get_activator(bvr);
         top = spt.get_parent_panel(activator);
    }

    if (input_name == null)
        input_name = 'load_snapshot';

    selected = get_selected_checkboxes(input_name);
    //var selected = spt.api.Utility.get_input_values(top, "input[name=" + input_name + "]");
    //selected = selected[input_name];

    

    if (selected.length == 0) {
        alert("A checkbox for a particular snapshot must be selected")
        return false
    }
    
    if (selected.length > 1) {
        alert("Select one checkbox at a time.")
        return false
    }
    value = confirm("Are you sure you want to update the reference of the selected node(s)?")
    if ( value == false )
        return false
    
    var script_path = py_download_delegator()
    app.py_file(script_path, "tactic_select.replace_reference", selected,
            prefix, options.join("|"))
   
    introspect(bvr)
    return true
}

function app_exec(command)
{
    var script_path = py_download_delegator()
    app.py_file(script_path, command)
    return true
}


function app_save_file(path)
{
    var script_path = py_download_delegator()
    //always overwrite
    return app.py_file(script_path, "tactic_select.save_file", path, 1) 
}

function app_copy_file(path, new_path)
{
    var script_path = py_download_delegator()
    return app.py_file(script_path, "tactic_select.copy_file", path, new_path) 
}

function app_save_sandbox_file(path)
{
    spt.app_busy.show( 'Save To Sandbox', 'Save' );
    setTimeout(function() {
        var script_path = py_download_delegator();
        app.py_file(script_path, "tactic_select.save_sandbox_file", path);
        spt.app_busy.hide();
    }, 50);

}

function app_explore(dir)
{
    /*
    applet = document.general_applet
    applet.makedirs(dir)
    applet.exec("explorer file://" + dir )
    */
    var script_path = py_download_delegator()
    app.py_file(script_path, "common.explore", dir) 
}


function app_set_user_environment(project_dir, file_name, bvr)
{
    var script_path = py_download_delegator()
    spt.app_busy.show( 'Setting Project', 'Set Project' );
    setTimeout(function() {
        var script_path = py_download_delegator();
        app.py_file(script_path, "tactic_select.set_user_environment", project_dir, file_name)
        introspect(bvr)
        spt.app_busy.hide();
    }, 50);
}







/*
 * DEPRECATED: this is not being used
 */

/* namespace functions */
/*
function add_node_to_namespace(namespace_select)
{
    var namespace = get_elements(namespace_select).get_value()
    var script_path = py_download_delegator()
    if (namespace == ':')
        namespace = ''

    app.py_file(script_path, "tactic_select.assign_namespace", namespace) 
}    
    
function set_namespace(namespace_select)
{
    var namespace = get_elements(namespace_select).get_value()
    alert("Namespace set to [" + namespace + "]")
    app.mel('namespace -set "' + namespace  + '"')
    introspect()

    //script_path = py_download_delegator()
    //app.py_file(script_path, "tactic_select.set_namespace", namespace)
    //introspect() 
}


function get_namespace_contents()
{
    var value = app.mel("namespaceInfo -ls")

    var element = document.form.elements["namespace_info"]
    element.value = value
    document.form.submit()
}
*/






