// -----------------------------------------------------------------------------
//
//  Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//
//  PROPRIETARY INFORMATION.  This software is proprietary to
//  Southpaw Technology Inc., and is not to be reproduced, transmitted,
//  or disclosed in any way without written permission.
//
// -----------------------------------------------------------------------------
//
//


TacticServerStub = function() {
    this.url = null;
    this.transaction_ticket = null;
    this.login_ticket = null;
    this.server_name = null;
    this.project = null;

    this.set_ticket = function(login_ticket) {
        this.login_ticket = login_ticket;
        //this.transaction_ticket = login_ticket;
    }

    this.get_login_ticket = function() {
        return this.login_ticket;
    }


    this.set_url = function(url) {
        this.url = url;
    }

    this.get_url = function() {
        return this.url;
    }

    this.set_project = function(project) {
        this.project = project;
        //this.set_project_state(project);
    }
    this.get_project = function() {
        return this.project;
    }


    this.set_palette = function(palette) {
        var env = spt.Environment.get();
        env.set_palette(palette);
    }
    this.get_palette = function() {
        var env = spt.Environment.get();
        return env.get_palette();
    }



    this.set_server = function(server_name) {
        this.server_name = server_name;
        var env = spt.Environment.get();
        this.url = env.get_api_url(this.server_name);
    }


    this.get_transaction_ticket = function() {
        return this.transaction_ticket;
    }


    this.build_search_key = function(search_type, code, project_code, column) {
        if (project_code == null) {
            project_code = this.project;
        }
        if (column == null) {
            column = 'code';
        }
        var search_key;
        if (search_type.test(/^sthpw\//))
            search_key = search_type +"?"+ column +"="+ code;
        else
            search_key = search_type +"?project="+ project_code +"&"+ column +"="+ code;
        return search_key;
    }

    this.split_search_key = function(search_key) {
        
        var list = [];
        if (!search_key)
            return search_key;

        if (search_key.test(/&/))
            var tmps = search_key.split('&');
        else
            var tmps = search_key.split('?');
        var codes = tmps[1].split('=')
        //assert len(codes) == 2;
        list.push(tmps[0]);
        list.push(codes[1]);
        return list;
    }


    this.generate_ticket = function() {
        return this._delegate("generate_ticket");
    }


    this.get_ticket = function(login, password) {
        var func_name = "get_ticket";
        var client = new AjaxService( this.url, '' );
        var ret_val = client.invoke( func_name, arguments );
        ret_val = this._handle_ret_val(func_name, ret_val, 'string');
        ret_val = ret_val.replace(/(\r\n|\n|\r)/gm, '');
        return ret_val;
    }


    this.get_server_version = function(project) {
        var kwargs = null;
        return this._delegate("get_server_version", arguments, kwargs);
    }

    this.get_server_api_version = function(project) {
        var kwargs = null;
        return this._delegate("get_server_api_version", arguments, kwargs);
    }


    /*
     * Transaction methods
     */
    this.set_project_state = function(project) {
        var kwargs = null;
        return this._delegate("set_project", arguments, kwargs);
    }



    this.start = function(kwargs) {
        if (this.project == null) {
            alert("Project is null on start()");
            throw("Project is null on start()");
        }



        var client = new AjaxService( this.url, '' );
        var args = [];
        var ticket = {
            'ticket': this.login_ticket,
            'project': this.project,
            'palette': this.get_palette(),
            'language': 'javascript'
        };
        //args.push(this.login_ticket);
        args.push(ticket);
        args.push(this.project);
        args.push(kwargs);
        var ret_val = client.invoke( "start", args );

        this.transaction_ticket = this._parse_result(ret_val, "start");

        // put this transaction on the undo queue
        //var server_cmd = new TacticServerCmd(this);
        //Command.add_to_undo(server_cmd);

        return this.transaction_ticket;
    }

    this.finish = function(kwargs) {
        var ret_val = this._delegate("finish", arguments, kwargs);
        this.transaction_ticket = null;
        return ret_val;
    }

    this.abort = function() {
        return this._delegate("abort", arguments);
    }

    this.undo = function(kwargs) {
        return this._delegate("undo", arguments, kwargs);
    }

    this.redo = function(kwargs) {
        return this._delegate("redo", arguments, kwargs);
    }

    /*
     * Simple Ping Test
     */
    this.ping = function() {
        return this._delegate("ping");
    }


    this.get_connection_info = function() {
        return this._delegate("get_connection_info");
    }



    /*
     * Logging facilities
     */
    this.log = function(level, message, kwargs) {
        return this._delegate("log", arguments);
    }


    /*
     * Checkin/checkout methods
     */
    this.upload_file = function(file_path, ticket, subdir) {
        if (typeof(ticket) == 'undefined') {
            ticket = this.login_ticket;
        }
        var applet = spt.Applet.get();
        applet.upload_file(file_path, ticket, subdir);
    }


    this.upload_directory = function(dir_path, ticket) {
        if (typeof(ticket) == 'undefined') {
            ticket = this.login_ticket;
        }
        var applet = spt.Applet.get();
        return applet.upload_directory(dir_path, ticket);
    }



    this.get_upload_file_size = function(file_path) {
        return this._delegate("get_upload_file_size", arguments);
    }



   
    this.create_snapshot = function(search_key, context, kwargs) {
        return this._delegate("create_snapshot", arguments, kwargs);
    }


    this._find_source_path = function(path) {
        var applet = spt.Applet.get();

        var sandbox_root = null;
        var parts = path.split("/");
        for (var i = parts.length-1; i > 0; i--) {
            var dir = parts.slice(0, i);
            dir = dir.join("/");
            root_dir = dir + "/.tactic/sandbox_root";
            if (applet.exists(root_dir) ) {
                sandbox_root = dir;
                break;
            }
        }

        if (sandbox_root == null) {
            return path;
        }

        var pattern = sandbox_root + "/";
        path = path.replace(pattern, "")
        return path;
    }


    this.simple_checkin = function(search_key, context, file_path, kwargs) {
        if (typeof(kwargs) == "undefined") {
            kwargs = {__empty__:true};
        }
        var mode_options = ['upload','uploaded', 'copy', 'move', 'inplace','local'];
        //file_path = spt.path.get_filesystem_path(file_path); 
        var mode = kwargs['mode'];
        if (mode == undefined) mode = "upload";
        if (typeof(file_path) != 'string') {
            spt.alert("file_path should be a string instead of an array.");
            return;
        }
        var applet = null;
        if (mode != 'uploaded') {
            // put in a check for Perforce for the moment because file.exists()
            // is very slow when looking for //depot
            if (file_path.substr(0, 2) != '//') {
                var applet = spt.Applet.get();
                if (applet.is_dir(file_path)){
                    alert('[' + file_path + '] is a directory. Exiting...');
                    return;
                }
            }
        }

        if (mode == 'upload') {
            var ticket = this.transaction_ticket;
            
            this.upload_file(file_path, ticket);
            file_path = spt.path.get_filesystem_path(file_path); 
            kwargs.use_handoff_dir = false;
        }
        // already uploaded
        else if (mode == 'uploaded') {
            kwargs.use_handoff_dir = false;
            file_path = spt.path.get_filesystem_path(file_path); 
        }
        else if (['copy', 'move'].contains(mode)) {
            var handoff_dir = this.get_handoff_dir();
            kwargs.use_handoff_dir = true;
            applet.makedirs(handoff_dir);
            applet.exec("chmod 777 " + handoff_dir);
            var basename = spt.path.get_basename(file_path);

            if (mode == 'move') {
                applet.move_file(file_path, handoff_dir + '/' +  basename);
            }
            else if (mode == 'copy') {
                applet.copy_file(file_path, handoff_dir + '/' +  basename);
            }

            // this is meant for 3.8, commented out for now
            /*
            var delayed = true;
            if (delayed) {
                mode = 'local'; // essentially, local just means delayed
                kwargs.mode = 'local';
            }*/
        }


        // find the source path
        // DISABLING for now until client can recognize this
        //var source_path = this._find_source_path(file_path);
        //console.log("source_path: " + source_path);
        //kwargs['source_path'] = source_path;



        // do the checkin
        var snapshot = this._delegate("simple_checkin", arguments, kwargs);
        var files = snapshot['__file_sobjects__'];

        if (mode == 'local') {
            var applet = spt.Applet.get();
            var files = this.eval("@SOBJECT(sthpw/file)", {search_keys:snapshot});
            var base_dirs = this.get_base_dirs();
            var client_repo_dir = base_dirs.win32_local_repo_dir;
            if (typeof(client_repo_dir) == 'undefined' || client_repo_dir == '')
            {
                client_repo_dir = base_dirs.win32_local_base_dir + "/repo";
            }


            // move the files directly to the local repo
            for (var i = 0; i < files.length; i++) {
                var file = files[i];
                var rel_path = file.relative_dir + "/" + file.file_name;
                var repo_path = client_repo_dir + "/" + rel_path
                applet.copy_file(file_path, repo_path);
                var md5 = applet.get_md5(repo_path);
                this.update(file, {md5: md5});

            }
        }

        return snapshot;
    }




    this.group_checkin = function(search_key, context, file_path, file_range, kwargs)
    {
        if (typeof(kwargs) == 'undefined') {
            kwargs = {__empty__:true};
        }

        var mode = kwargs.mode;
        // default is "uploaded"??
        //if (typeof(mode) == 'undefined') mode = 'copy';

        var mode_options = ['upload', 'copy', 'move'];
        if (typeof(mode) != "undefined") {
            //if mode not in mode_options:
            //    raise TacticApiException('Mode must be in %s' % mode_options);

            // brute force method
            //dir = os.path.dirname(file_path)
            var handoff_dir = this.get_handoff_dir();

            var expanded_paths;
            if (typeof(file_path) == 'object') {
                expanded_paths = file_path;
            }
            else {
                expanded_paths = spt.file.expand_paths(file_path, file_range);
            }

            if (mode == 'move') {
                for (var i = 0; i < expanded_paths.length; i++) {
                    var path = expanded_paths[i];
                    var parts = path.split("/");
                    var basename = parts[parts.length-1];
                    applet = spt.Applet.get();
                    applet.move_file(path, handoff_dir+'/'+basename);
                }
                use_handoff_dir = true;
            }
            else if (mode == 'copy') {
                for (var i = 0; i < expanded_paths.length; i++) {
                    var path = expanded_paths[i];
                    var parts = path.split(/[\/\\]/);
                    var basename = parts[parts.length-1];
                    applet = spt.Applet.get();
                    applet.copy_file(path, handoff_dir+'/'+basename);
                }
                use_handoff_dir = true;
            }
            // use a custom protocol
            else if (mode == 'custom') {

                var command = kwargs.command;
                if (typeof(command) == 'undefined') {
                    return "No command defined";
                }
                for (var i = 0; i < expanded_paths.length; i++) {
                    var path = expanded_paths[i];
                    var parts = path.split(/[\/\\]/);
                    var basename = parts[parts.length-1];
                    applet = spt.Applet.get();
                    actual = command;
                    actual = actual.replace("%s", path);
                    actual = actual.replace("%s", handoff_dir+'/'+basename);
                    // convert all of the paths back to windows paths??
                    actual = actual.replace(/\//g, "\\");
                    applet.makedirs(handoff_dir);
                    applet.exec(actual);
                }
                use_handoff_dir = true;

                
            }
            else if (mode == 'upload') {
                applet = spt.Applet.get();
                for (var i = 0; i < expanded_paths.length; i++) {
                    var path = expanded_paths[i];
                    applet.upload_file(path);
                }
                use_handoff_dir = false;
            }
        }

        delete(kwargs.command);
        return this._delegate("group_checkin", arguments, kwargs);

    }


    this.directory_checkin = function(search_key, context, dir, kwargs)
    {
        if (typeof(kwargs) == 'undefined') {
            kwargs = {__empty__:true};
        }

        //if mode not in ['copy', 'move', 'inplace']:
        //    raise TacticApiException('mode must be either [move] or [copy]')

        if (!kwargs.mode) {
            kwargs.mode = 'copy';
        }
        var mode = kwargs.mode;

        // make sure that handoff dir is empty
        var applet = spt.Applet.get();

        if (!applet.is_dir(dir)){
            alert('[' + dir + '] is not a directory. Exiting...');
            return;
        }

        // remove trailing / or \
        dir = dir.replace(/[\/\\]+$/, '');
        // replace all slashes
        dir = dir.replace(/\\/g, "/");

        if (mode == 'move' || mode == 'copy') {
            var handoff_dir = this.get_handoff_dir();
            applet.rmtree(handoff_dir);
            applet.makedirs(handoff_dir);
            applet.exec("chmod 777 " + handoff_dir);
            
            // copy or move the tree
            var parts = dir.split(/[\/\\]/);
            var dirname = parts.splice(0, parts.length-1).join("/");
            var basename = parts[parts.length-1];

            if (mode == 'move') {
                applet.move(dir, handoff_dir + "/" + basename);
                kwargs.use_handoff_dir = true;
            }
            else if (mode == 'copy') {
                applet.copytree(dir, handoff_dir + "/" + basename);
                kwargs.use_handoff_dir = true;
            }
        }
        else if (mode == 'upload') {
            var files = applet.upload_directory(dir);
            kwargs.use_handoff_dir = false;

        }
        else if (mode == 'uploaded') {
            kwargs.use_handoff_dir = false;
        }
            

        return this._delegate("simple_checkin", arguments, kwargs);

    }



    this.add_dependency = function(snapshot_code, file_path, kwargs) {
        return this._delegate("add_dependency", arguments, kwargs);
    }


    this.add_dependency_by_code = function(to_snapshot_code, from_snapshot_code, kwargs) {
        return this._delegate("add_dependency_by_code", arguments, kwargs);
    }

    this.add_directory = function(snapshot_code, dir, kwargs) {
        if (!kwargs) {
            kwargs = {__empty__:true};
        }
        if (!kwargs.mode) {
            kwargs.mode = 'copy';
        }

        var mode = kwargs.mode;
        if ( !(mode in {'copy':'', 'move':'', 'preallocate':'', 'manual':''}) ) {
            throw("Mode must be in [copy, move, preallocate, manual]");
        }

        var use_handoff_dir;
        var handoff_dir;

        if (mode in {'copy':'', 'move':''}) {
            var applet = spt.Applet.get();

            handoff_dir = this.get_handoff_dir()

            // make sure that handoff dir is empty
            applet.rmtree(handoff_dir);
            applet.makedirs(handoff_dir);

            // remove trailing / or \
            dir = dir.replace(/[\/\\]+$/, '');

            // copy or move the tree
            var parts = dir.split(/[\/\\]/);
            var basename = parts[parts.length-1];

            if (mode == 'move') {
                applet.move(dir, handoff_dir + "/" + basename);
            }
            else if (mode == 'copy') {
                applet.copytree(dir, handoff_dir + "/" + basename);
            }
            use_handoff_dir = true;
        }
        else if (mode in {'manual':''}) {
            // files are already in handoff
            use_handoff_dir = true;
        }
        else {
            use_handoff_dir = false;
        }

        kwargs.use_handoff_dir = use_handoff_dir;
        return this._delegate("add_file", arguments, kwargs )
    }


    this.add_file = function(snapshot_code, file, kwargs) {
        // If no mode is specified, set the default mode to 'copy'.
        if (!kwargs) {
            kwargs = {__empty__:true};
        }
        if (!kwargs.mode) {
            kwargs.mode = 'copy';
        }
        var mode = kwargs.mode;
        if ( !(mode in {'copy':'', 'move':'', 'preallocate':'', 'manual': '', 'upload': '', 'uploaded': ''}) ) {
            throw("Mode '" + mode + "' must be in [copy, move, preallocate, manual, upload, uploaded]");
        }
        
        file = spt.path.get_filesystem_path(file); 
        var use_handoff_dir;
        var handoff_dir;

        if (mode in {'copy':'', 'move':''}) {
            var applet = spt.Applet.get();

            handoff_dir = this.get_handoff_dir()

            // make sure that handoff dir is empty
            applet.rmtree(handoff_dir);
            applet.makedirs(handoff_dir);

            // copy or move the file
            var basename = spt.path.get_basename(file);
             
            if (mode == 'move') {
                applet.move(file, handoff_dir + "/" + basename);
            }
            else if (mode == 'copy') {
                applet.copy_file(file, handoff_dir + "/" + basename);
            }
            use_handoff_dir = true;
        }
        else if (mode in {'manual':''}) {
            // files are already in handoff
            use_handoff_dir = true;
        }
        else if (mode == 'upload') {
            var ticket = this.transaction_ticket;
            this.upload_file(file, ticket);
            use_handoff_dir = false;
        }
        else {
            use_handoff_dir = false;
        }

        kwargs.use_handoff_dir = use_handoff_dir;
        return this._delegate("add_file", arguments, kwargs )
    }

    this.checkout = function(search_key, context, kwargs) {
    
        // get the files for this search_key, defaults to latest version and checkout to current directory
        if (!kwargs) {
            kwargs = {version: -1, file_type: 'main', to_dir: null, to_sandbox_dir: true, mode: 'download'};
        }
        else if (!kwargs.to_dir && kwargs.to_sandbox_dir==null) {
            kwargs.to_sandbox_dir = true;
        }


     
        if (kwargs.mode in {'download':'', 'copy':''} == false) {
            throw("Mode '" + kwargs.mode + "' must be in [download, copy]");
        }
        // get the server paths and the client paths to copy
        //var paths = this.get_all_paths_from_snapshot(search_key, {'mode': kwargs.mode});
        //var sand_paths = this.get_all_paths_from_snapshot(search_key, {'mode':'sandbox', filename_mode:'source'});
        var mode = kwargs.mode;
        var to_sandbox_dir = kwargs.to_sandbox_dir;
        var to_dir = kwargs.to_dir;

        delete kwargs.mode;
        delete kwargs.to_sandbox_dir;
        delete kwargs.to_dir;
        paths = this._delegate("checkout", arguments, kwargs); 

        var client_lib_paths = paths['client_lib_paths'];
        var sandbox_paths = paths['sandbox_paths'];
        var web_paths = paths['web_paths'];
        var to_paths = [];

        var applet = spt.Applet.get();
        var env = spt.Environment.get();
        try {
            for (var i=0; i < client_lib_paths.length; i++){
                var client_lib_path = client_lib_paths[i];
                if (to_sandbox_dir){
                    var to_path = sandbox_paths[i];
                    var filename = spt.path.get_basename(to_path);
                }
                else {
                    var filename = spt.path.get_basename(client_lib_path);
                    if (!to_dir)
                        throw("If to_sandbox_dir is set to false, you have to provide a directory for to_dir");

                    var to_path = to_dir + '/' + filename;
                }
                to_paths.push(to_path);

                // copy the file from the repo
                var to_dir = spt.path.get_dirname(to_path);
                if (applet.exists(to_dir) == false)
                    applet.makedirs(to_dir);

                if (mode == 'copy') {
                    if (applet.exists(client_lib_path)) {
                        if (applet.is_dir(client_lib_path))
                            applet.copytree(client_lib_path, to_path);
                        else
                            applet.copy_file(client_lib_path, to_path);
                    }
                    else {
                        throw("Path [" + client_lib_path + "] does not exist");  
                    }
                }
                else if (mode == 'download'){
                    web_path = web_paths[i];
                    applet.download_file(web_path, to_path);
                }


            }
        }
        catch(e) {
           alert(spt.exception.handler(e));
        }
   
    }

    this.checkout_snapshot = function(search_key, sandbox_dir, kwargs) {
        // get the files for this snapshot
        if (!kwargs) {
            kwargs = {};
        }

        if (! kwargs.mode ) {
            transfer_mode = spt.Environment.get().get_transfer_mode();
            kwargs.mode = transfer_mode;
        }

        if (kwargs.mode in {'client_repo':'', 'web':''} == false) {
            throw("Mode '" + kwargs.mode + "' must be in [client_repo, web]");
        }

        var file_types
        if (! kwargs.file_types ) {
            file_types = [];
        }
        else {
            file_types = kwargs.file_types;
        }


        // get the server paths and the client paths to copy
        var paths = this.get_all_paths_from_snapshot(search_key, {'mode': kwargs.mode, file_types:file_types});
        var sand_paths = this.get_all_paths_from_snapshot(search_key, {'mode':'sandbox', filename_mode: kwargs.filename_mode, file_types:file_types});

        var dst_paths = [];
        var applet = spt.Applet.get();
        var env = spt.Environment.get();
        var server_root = env.get_server_url();

        var filename_mode;
        if (!kwargs.filename_mode) {
            filename_mode = 'repo';
        }
        else {
            filename_mode = kwargs.filename_mode;
        }

        try {
        for (var i = 0; i < paths.length; i++ ) {
            var path = paths[i];
	    var dst = sand_paths[i];
            var basename;
            if (filename_mode == 'repo') {
                basename = spt.path.get_basename(dst);
            }
            else if (filename_mode == 'versionless') {
               
                basename = spt.path.get_basename(dst);
                var dir_name = spt.path.get_dirname(dst);
                basename = basename.replace(/_v\d+/i, '');
                dst = dir_name + '/' + basename;
             
            }
            else if (filename_mode == 'source') {
                basename = spt.path.get_basename(dst);
            }


            // FIXME: this doesn't work for directory checkins.  It flattens
            // the directories
            // remap sandbox paths if one is explicitly supplied
            if (sandbox_dir){
                dst = sandbox_dir + "/" + basename;
            }
          
            dst_paths.push(dst)

            if (kwargs.mode == 'client_repo'){
                applet.copytree(path, dst);
            }
            else if (kwargs.mode =='web'){
                var url = server_root + path;
                if (spt.url.exists(url)){
                    applet.download_file(url, dst);
                }
                else {
                    alert(url + ' does not exist on the server. It may have been backed up.');
                }
            }
        }
        }
        catch(e){
           alert(spt.exception.handler(e));
        }
        return dst_paths;
    }




    this.query_snapshots = function(kwargs) {
        return this._delegate("query_snapshots", arguments, kwargs);
    }

    this.get_snapshot = function(search_key, kwargs) {
        return this._delegate("get_snapshot", arguments, kwargs);
    }

    this.get_client_dir = function(snapshot_code, kwargs) {
        return this._delegate("get_client_dir", arguments, kwargs);
    }



    this.get_preallocated_path = function(snapshot_code, kwargs) {
        return this._delegate("get_preallocated_path", arguments, kwargs);
    }

    this.get_virtual_snapshot_path = function(search_key, context, kwargs) {
        return this._delegate("get_virtual_snapshot_path", arguments, kwargs);
    }
    
    this.get_all_dependencies = function(snapshot_code, kwargs) {
        return this._delegate("get_all_dependencies", arguments, kwargs);
    }
    
    /*
     * Low Level Database methods
     */
    this.get_related_types = function(search_type) {
        return this._delegate("get_related_types", arguments);
    }

    this.query = function(search_type, kwargs) {
        var value = this._delegate("query", arguments, kwargs, "string");
        //return this._delegate("query", arguments, kwargs);
        value = JSON.parse(value);
        return value
    }

    this.get_by_search_key = function(search_key) {
        return this._delegate("get_by_search_key", arguments);
    }


    this.get_by_code = function(search_type, code) {
        return this._delegate("get_by_code", arguments);
    }



    this.insert = function(search_type, data, kwargs) {
        // server.insert(search_type, data, kwargs);
        return this._delegate("insert", arguments, kwargs);
        
    }


    this.update = function(search_type, data, kwargs) {
        return this._delegate("update", arguments, kwargs);
    }



    this.update_multiple = function(data, kwargs) {
        data = JSON.stringify(data);
        return this._delegate("update_multiple", arguments, kwargs);
        
    }



    //
    // Expression methods
    //
    this.eval = function(expression, kwargs) {
        return this._delegate("eval", arguments, kwargs);
    }

    //
    // SObject methods
    //

    this.create_search_type = function(search_key, search_type, title, kwargs) {
        return this._delegate("create_search_type", arguments, kwargs);
    }

    this.add_column_to_search_type = function(search_type, column_name, column_type) {
        return this._delegate("add_column_to_search_type", arguments);
    }

    this.insert_update = function(search_key, data, kwargs) {
        return this._delegate("insert_update", arguments);
    }


    this.get_unique_sobject = function(search_type, data) {
        return this._delegate("get_unique_sobject", arguments);
    }


    this.retire_sobject = function(search_key) {
        return this._delegate("retire_sobject", arguments);
    }

    this.reactivate_sobject = function(search_key) {
        return this._delegate("reactivate_sobject", arguments);
    }

    this.delete_sobject = function(search_key) {
        return this._delegate("delete_sobject", arguments);
    }

    this.clone_sobject = function(search_key, data) {
        return this._delegate("clone_sobject", arguments);
    }

    this.set_widget_setting = function(key, value) {
        return this._delegate("set_widget_setting", arguments);
    }

    this.get_widget_setting = function(key) {
        return this._delegate("get_widget_setting", arguments);
    }

    /*
     * sType Hierarchy Functions
     */

    this.get_parent = function(search_key, kwargs) {
        return this._delegate("get_parent", arguments)
    }


    this.get_all_children = function(search_key, child_type, kwargs) {
        return this._delegate("get_all_children", arguments)
    }


    this.get_parent_type = function(search_key) {
        return this._delegate("get_parent_type", arguments);
    }


    this.get_child_types = function(search_type) {
        return this._delegate("get_child_types", arguments);
    }


    this.connect_sobjects = function(src_sobject, dst_sobject, kwargs) {
        return this._delegate("connect_sobjects", arguments, kwargs);
    }


    this.get_connected_sobjects = function(src_sobject, kwargs) {
        return this._delegate("get_connected_sobjects", arguments, kwargs);
    }

    this.get_connected_sobject = function(src_sobject, kwargs) {
        return this._delegate("get_connected_sobject", arguments, kwargs);
    }


    /* 
     * Task methods
     */ 
    this.create_task = function(search_key, kwargs) {
        return this._delegate("create_task", arguments, kwargs);
    }
 


    /* 
     * Note methods
     */ 
    this.create_note = function(search_key, note, kwargs) {
        return this._delegate("create_note", arguments, kwargs);
    }

    /*
     * Pipeline methods
     */
    this.get_pipeline_xml = function(search_key, kwargs) {
        return this._delegate("get_pipeline_xml", arguments, kwargs);
    }

    this.get_pipeline_processes = function(search_key, kwargs) {
        return this._delegate("get_pipeline_processes", arguments, kwargs);
    }

    this.get_pipeline_xml_info = function(search_key, kwargs) {
        return this._delegate("get_pipeline_xml_info", arguments, kwargs);
    }

    this.get_pipeline_processes_info = function(search_key, kwargs) {
        return this._delegate("get_pipeline_processes_info", arguments, kwargs);
    }

    /*
     * Widget methods
     */
    this.get_widget = function(class_name, kwargs) {
        var ret_val = this._delegate("get_widget", arguments, kwargs, "string");
        return ret_val;
    }

    this.class_exists = function(class_path) {
        return this._delegate("class_exists", arguments);
    }


    this.execute_cmd = function(class_name, args, values, kwargs) {
        var ret_val = this._delegate("execute_cmd", arguments, kwargs);
        if (ret_val.status == "ERROR") {
            // FIXME: put in a propert error here
            //alert("ERROR: " + ret_val.msg);
            throw ret_val;
        }
        return ret_val;
    }

    this.execute_python_script = function(script_path, script_kwargs, kwargs) {
        if (kwargs) callback = kwargs.on_complete;
        else callback = null;
        return this._delegate("execute_python_script", arguments, kwargs, null, callback);
    }

    this.execute = function(code) {
        return this._delegate("execute", arguments, null);
    }

    this.get_column_names = function(search_type) {
        return this._delegate("get_column_names", arguments, null);
    }

    this.get_column_info = function(search_type) {
        return this._delegate("get_column_info", arguments, null);
    }

    this.get_column_widgets = function() {
        var value = ''
        try {
            value = this._delegate("get_column_widgets", arguments, null, "string");
            value = JSON.parse(value);
        }
        catch (e) {
            alert("Error adding the column: " + spt.exception.handler(e));
        }
        return value;
    }


    this.update_config = function(search_type, view, element_names, kwargs) {
        return this._delegate("update_config", arguments, kwargs);
    }


    this.get_config_definition = function(search_type, view, element_name, kwargs) {
        return this._delegate("get_config_definition", arguments, kwargs);
    }

    this.set_config_definition = function(search_type, element_name, kwargs) {
        return this._delegate("set_config_definition", arguments, kwargs);
    }

    this.add_config_element = function(search_type, view, name, kwargs) {
        return this._delegate("add_config_element", arguments, kwargs);
    }

    this.set_application_state = function() {
        return this._delegate("set_application_state", arguments, null, null, function() {});
    }


    //
    // Directory methods
    //
    this.get_paths = function(search_key, kwargs) {
        return this._delegate("get_paths", arguments, kwargs);
    }


    this.get_base_dirs = function() {
        return this._delegate("get_base_dirs", arguments);
    }
    
    this.get_handoff_dir = function() {
        return this._delegate("get_handoff_dir", arguments);
    }

    this.get_plugin_dir = function() {
        return this._delegate("get_plugin_dir", arguments);
    }

    this.clear_upload_dir = function() {
        return this._delegate("clear_upload_dir", arguments);
    }



    // Doc methods
    this.get_doc_link = function(alias) {
        return this._delegate("get_doc_link", arguments, null);
    }



    // Misc
    this.get_path_from_snapshot = function(snapshot_code, kwargs) {
        return this._delegate("get_path_from_snapshot", arguments, kwargs);
    }


    this.get_all_paths_from_snapshot = function(snapshot_code, kwargs) {
        return this._delegate("get_all_paths_from_snapshot", arguments, kwargs);
    }


    // async functions

    this.async_get_widget = function(class_name, kwargs) {
        var callback = kwargs['cbjs_action'];
        this._delegate("get_widget", arguments, kwargs, "string", callback);
        return;
    }

    this.async_eval = function(class_name, kwargs) {
        var callback = kwargs['cbjs_action'];
        this._delegate("eval", arguments, kwargs, null, callback);
        return;
    }


    // method that delegates which function in xmlrpc to call
    //
    // @params:
    //   func_name: the name of the function to execute
    //   passed_args: the required arguments passed into the function
    //   kwargs: the optional arguments passed into the function
    //   ret_type: the type of value returned by the function.  Functions that
    //      return lots of data will often return strings back
    //   callback: a function that is run after the data has been returned.
    //      This is used be get_async_widget() and others
    this._delegate = function(func_name, passed_args, kwargs, ret_type, callback) {

        var client = new AjaxService( this.url, '' );

        var args = [];

        // build the transaction bundle
        if (this.transaction_ticket == null) {
            this.transaction_ticket = this.login_ticket;
        }


        if (! this.transaction_ticket ) {
            alert("Login or transaction ticket is empty. Cannot proceed");
            return;
        }


        var ticket = {
            'ticket': this.transaction_ticket,
            'project': this.project,
            'palette': this.get_palette(),
            'language': 'javascript'
        };
        args.push(ticket);


        if (typeof(passed_args) == 'undefined') {
            passed_args = [];
        }

        // determine if there was a kwargs passed in
        var num_args;
        var has_kwargs;
        if (typeof(kwargs) == 'undefined' || kwargs == null) {
            num_args = passed_args.length;
            has_kwargs = false;
        }
        else if (kwargs.__empty__) {
            num_args = passed_args.length;
            has_kwargs = true;
        }
        else {
            num_args = passed_args.length - 1;
            has_kwargs = true;
        }

        if (passed_args != undefined) {
            for (var i=0; i < num_args; i++) {
                args.push(passed_args[i]);
            }
        }

        // Always pass in a kwargs as the last argument.  If kwargs is not
        // present, we send an empty one through
        if (!has_kwargs) {
            args.push({});
        }
        else {
            delete kwargs.__empty__;
            args.push(kwargs);
        }
   
        //console.log(args);

        // handle asyncrhonous mode
        if (typeof(callback) != 'undefined' && callback != null) {
            var self = this;
            client.set_callback( function(request) {
                self.async_callback(request);
            } );
            client.invoke( func_name, args );

            // remember this
            this.func_name = func_name;
            this.ret_type = ret_type;
            this.callback = callback;
            return;
        }

        // just do it synchronously
        else {
            ret_val = client.invoke( func_name, args );
            return this._handle_ret_val(func_name, ret_val, ret_type);
        }

    }

    this.async_callback = function(request) {
        if (request.readyState == 4) {
            if (request.status == 200) {
                var data = this._handle_ret_val(this.func_name, request, this.ret_type);
                this.callback(data);
            } else {
                alert("status is " + request.status);
            }
        }
    }


        
    this._handle_ret_val = function(func_name, ret_val, ret_type) {
        if (ret_type == "raw") {
            return ret_val.responseText;
        }
        if (ret_type == "string") {
            // manually extract the value returned
           
            // FIXME: is this slow??
            var value = ret_val.responseText;
            value = value.replace(/^<\?xml version='1.0'\?>\n<methodResponse>\n<params>\n<param>\n<value><string>/, '');
            value = value.replace(/<\/string><\/value>\n<\/param>\n<\/params>\n<\/methodResponse>/, '');

            value = value.replace(/&amp;/g, "&");
            value = value.replace(/&lt;/g, "<");
            value = value.replace(/&gt;/g, ">");

            // fix inline < > that are not part of the html structure
            value = value.replace(/&spt_lt;/g, "&lt;");
            value = value.replace(/&spt_gt;/g, "&gt;");

            //return ret_val.responseText;
            return value;
        }
        else {
            var value = this._parse_result(ret_val, func_name);
            return value;
        }
    }


    // parse the return value from XMLRPC request.  This is assumed to be
    // a single return value in JSON format which can be parsed.  However,
    // if this produces an exception, then return a string
    //
    this._parse_result = function(ret_val, func_name) {

        var result = ret_val.responseXML;
        if (result == null) {
            ret_val = ret_val.responseText;
            spt.exception.handle_fault_response( ret_val );
            return ""
        }
        // join, normalize the data if the browser supports it, mostly for FF
        if (ret_val.responseXML.normalize)
            ret_val.responseXML.normalize();

        var nodeList = result.getElementsByTagName("string");
        if (nodeList.length == 0) {
            // in IE a fault response has a non-null result, but also has no string nodes, and so goes into this
            // block of code ... so handle it here the same as fault response above
            ret_val = ret_val.responseText;
            if( ret_val.contains("faultCode") ) {
                spt.exception.handle_fault_response( ret_val );
            }
            return "";
        }

        var child = nodeList[0].firstChild;
        if (child == null) {
            alert("Return format not a string or JSON text");
            alert(ret_val.responseText);
            return {};
        }

        var jsontext;
        // FIXME: you can just use child.nodeValue (it is supported by all browsers) instead of .text or .textContent
        if (spt.browser.is_IE()) {
            jsontext = child.text;
        }
        else {
            jsontext = child.textContent;
        }

        var value;
        try {
            value = JSON.parse(jsontext);
        } catch(e) {
            // assume it is just a string
            value = jsontext;
            if (func_name != 'start') {

                ret_val = ret_val.responseText;
                if( ret_val.contains("faultCode") ) {
                    spt.exception.handle_fault_response( ret_val );
                }
                else{
                    alert("Error parsing [" + value + "]");
                }
                return {};
            }
        }

        if (typeof(value) == "undefined") {
            alert("Value returned from server is undefined");
            return {};
        }
        if (value && value.status == "ERROR") {
            throw value;
        }

        return value;
    }

} 

/*
 * Treats the server stub as a singleton and allows you to retrieve the
 * same reference from various parts of the code.
 */
TacticServerStub.server = null;
TacticServerStub.get = function() {
    if (this.server == null) {
        this.server = new TacticServerStub();

        var env = spt.Environment.get();
        var login_ticket = env.get_ticket();
        var url = env.get_api_url();
        var project_code = env.get_project();

        this.server.set_url(url);
        this.server.set_ticket(login_ticket);
        this.server.set_project(project_code);
    }
    return this.server;
}



