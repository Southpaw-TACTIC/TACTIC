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
    this.site = null;
    this.project = null;

    this.get_promise = function() {
        promise = new Promise( function(resolve, reject) {
           resolve();
        })
        return promise;
    }

    this.set_transaction_ticket = function(ticket) {
        this.transaction_ticket = ticket;
    }


    this.set_ticket = function(login_ticket) {
        this.login_ticket = login_ticket;
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



    this.set_site = function(site) {
        if (site) {
            this.site = site;
        }
    }
    this.get_site = function() {
        return this.site;
    }

    this.set_api_key = function(api_key) {
        if (api_key) {
            this.api_key = api_key;
        }
    }
    this.get_api_key = function() {
        return this.api_key
    }
    this.clear_api_key = function() {
        this.api_key = null
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


    this.get_server = function() {
        return this.server_name;
    }




    this.get_transaction_ticket = function() {
        return this.transaction_ticket;
    }


    // a key is an encoded
    this.set_key = function(key) {

        var str = '';
        if (key.indexOf("http") == 0) {
            str = key;
        }
        else {
            var hex = key.toString();
            for (var i = 0; i < hex.length; i += 2)
                str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
        }

        
        // The format of key is as follows
        // https://portal.southpawtech.com/tegna/tank/key/ABCDEFG
        var parts = str.split("/");
        if (parts.length == 7) {
            var login_ticket = parts[6];
            var hash = parts[5];
            var project = parts[4];
            var site = parts[3];
        }
        else {
            var login_ticket = parts[5];
            var hash = parts[4];
            var project = parts[3];
        }

        if (hash != "ticket" && hash != "login_ticket") {
            throw("Malformed key [http<s>://<server>/<site>/<project>/ticket/<ticket>]");
        }

        var server = parts[0] + "/" + parts[1] + "/" + parts[2];

        var env = spt.Environment.get();
        var url = env.get_api_url(server);


        console.log(str);
        console.log("server: " + server);
        console.log("site: " + site);
        console.log("project: " + project);
        console.log("ticket: " + login_ticket);

        /*
        env.set_server_url(server);
        env.set_site(site)
        env.set_project(project);
        env.set_ticket(login_ticket);
        */

        this.set_url(url);
        this.set_ticket(login_ticket);
        if (site)
            this.set_site(site);
        this.set_project(project);

    }

    this.get_key = function(key) {

        var env = spt.Environment.get();

        var server = env.get_server_url();
        var site = this.get_site();
        var project = this.get_project();
        var ticket = this.get_login_ticket();
        var api_key = this.get_api_key();

        var str = [];
        str.push(server);
        if (site)
            str.push(site)
        str.push(project)
        str.push(ticket)
        str.push(api_key)

        str = str.join("/");

        var hex = '';
        for(var i=0;i<str.length;i++) {
            hex += ''+str.charCodeAt(i).toString(16);
        }

        return hex;
    }


    this.build_search_key = function(search_type, code, project_code, column) {
        if (project_code == null) {
            project_code = this.project;
        }
        if (column == null) {
            column = 'code';
        }
        var temps = search_type.split("?project=");
        search_type = temps[0];
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


    this.get_ticket = function(login, password, kwargs) {
        var func_name = "get_ticket";
        var client = new AjaxService( this.url, '' );

        var args = [login, password];
        if (kwargs && kwargs.site)
            args.push(kwargs.site);

     
        var ret_val = client.invoke( func_name, args );
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
            'site': this.site,
            'project': this.project,
            'palette': this.get_palette(),
            'language': 'javascript',
            'api_key': this.get_api_key()
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

    this.async_ping = function(kwargs={}) {
    
        var callback = kwargs['cbjs_action'];
        if (!callback) {
            callback = kwargs['callback'];
        }
        var on_error = function(e) {
            callback(e);
        };

        this._delegate("ping", arguments, kwargs, null, callback, on_error);
        return;
    }




    this.get_connection_info = function() {
        return this._delegate("get_connection_info");
    }



    /*
     * Preferences
     */
    this.get_preference = function(key) {
        return this._delegate("get_preference", arguments);
    }



    this.set_preference = function(key, value) {
        return this._delegate("set_preference", arguments);
    }



    /*
     * Logging facilities
     */
    this.log = function(level, message, kwargs) {
        return this._delegate("log", arguments);
    }


    /*
     * Messaging facilities
     */

    this.get_message = function(key, kwargs, on_complete, on_error) {
        //return this._delegate("get_message", arguments);
        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
        passed_args = [key, kwargs];
        var ret_val = this._delegate("get_message", passed_args, kwargs, null, on_complete, on_error);
        // asynchronouse
        if (on_complete) {
            return;
        }
        // synchronouse
        if (ret_val && ret_val.status == "ERROR") {
            throw ret_val;
        }
        return ret_val;
    }




    this.p_get_message = function(key, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.get_message(key, kwargs);
        }.bind(this) )
    }




    this.get_messages = function(keys, kwargs) {
        return this._delegate("get_messages", arguments);
    }


    this.log_message = function(key, message, kwargs) {
        return this._delegate("log_message", arguments, kwargs);
    }

    this.subscribe = function(key, kwargs) {
        return this._delegate("subscribe", arguments, kwargs);
    }

    this.unsubscribe = function(key, kwargs) {
        return this._delegate("unsubscribe", arguments, kwargs);
    }

    /*
     * interaction logging
     */
    this.add_interaction = function(key, data, kwargs) {
        callback = function() {console.log("done")};
        return this._delegate("add_interaction", arguments, kwargs, null, callback);
    }

    this.get_interaction_count = function(key, kwargs) {
        return this._delegate("get_interaction_count", arguments, kwargs);
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

        // mode is no uploaded by default
        var mode = kwargs['mode'];
        if (mode == undefined) mode = "uploaded";
        if (typeof(file_path) != 'string') {
            spt.alert("file_path should be a string instead of an array.");
            return;
        }


        // already uploaded
        if (mode == 'uploaded') {
            kwargs.use_handoff_dir = false;
            //file_path = spt.path.get_filesystem_path(file_path); 
        }



        // NOTE: the modes upload, copy, move and local require local access
        // either by a java applet or some other applet like pyApplet.
        // Otherwise, these modes should not be used
        else {
            var applet = spt.Applet.get();
            if (!applet) {
                spt.alert("Mode ["+mode+"] requires a valid applet (either Java or Python or equivalent).  None found")
            }


            if (mode == 'upload') {
                var ticket = this.transaction_ticket;
                
                this.upload_file(file_path, ticket);
                kwargs.use_handoff_dir = false;
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
                    // it moves from handoff to repo during check-in
                }
                mode = 'create';
            }

        }



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
                var repo_path = client_repo_dir + "/" + rel_path;
                var tmp_path = repo_path + ".temp";
                applet.copy_file(file_path, tmp_path);
                applet.move_file(tmp_path, repo_path);
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
                mode = 'create';
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
                mode = 'create';
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
            mode = 'create';
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
            mode = 'create';
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
            kwargs.mode = 'preallocate';
        }
        var mode = kwargs.mode;
        if ( !(mode in {'copy':'', 'move':'', 'preallocate':'', 'manual': '', 'upload': '', 'uploaded': ''}) ) {
            throw("Mode '" + mode + "' must be in [copy, move, preallocate, manual, upload, uploaded]");
        }
        
        //file = spt.path.get_filesystem_path(file); 
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
            mode = 'create';
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


    this.add_sequence = function(snapshot_code, file, file_type, file_range, kwargs) {
        return this.add_group(snapshot_code, file, file_type, file_range, kwargs);
    }

    this.add_group = function(snapshot_code, file_pattern, file_type, file_range, kwargs) {
        // If no mode is specified, set the default mode to 'copy'.
        if (!kwargs) {
            kwargs = {__empty__:true};
        }
        if (!kwargs.mode) {
            kwargs.mode = 'preallocate';
        }
        var mode = kwargs.mode;
        if ( !(mode in {'copy':'', 'move':'', 'preallocate':'', 'manual': '', 'upload': '', 'uploaded': ''}) ) {
            throw("Mode '" + mode + "' must be in [copy, move, preallocate, manual, upload, uploaded]");
        }
        
        //file = spt.path.get_filesystem_path(file); 
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
            mode = 'create';
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
        else { // preallocate
            use_handoff_dir = false;
        }



        kwargs.use_handoff_dir = use_handoff_dir;
        return this._delegate("add_group", arguments, kwargs )
    }





    // DEPRECATED: use checkout_snapshot
    /*
    this.checkout = function(search_key, context, kwargs) {
    
        // get the files for this search_key, defaults to latest version and checkout to current directory
        if (!kwargs) {
            kwargs = {version: -1, file_type: 'main', to_dir: null, to_sandbox_dir: true, mode: 'download', __empty__:true};
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
        return to_paths
   
    }
    */



    this.checkout_snapshot = function(search_key, sandbox_dir, kwargs) {
        // get the files for this snapshot
        if (!kwargs) {
            kwargs = {};
        }
        if (! kwargs.mode ) {
            transfer_mode = spt.Environment.get().get_transfer_mode();
            kwargs.mode = transfer_mode;
        }
        if (! kwargs.mode ) {
            kwargs.mode = 'web';
        }


        if (kwargs.mode in {'client_repo':'', 'web':'', 'browser':''} == false) {
            throw("Mode '" + kwargs.mode + "' must be in [client_repo, web, browser]");
        }

        var file_types;
        if (! kwargs.file_types ) {
            file_types = [];
        }
        else {
            file_types = kwargs.file_types;
        }

        var expand_paths;
        if (! kwargs.expand_paths ) {
            expand_paths = true;
        }
        else {
            expand_paths = kwargs.expand_paths;
        }

        // get the server paths and the client paths to copy
        var paths = this.get_all_paths_from_snapshot(search_key, {'mode': kwargs.mode, file_types:file_types, expand_paths: expand_paths});
        var sand_paths = this.get_all_paths_from_snapshot(search_key, {'mode':'sandbox', filename_mode: kwargs.filename_mode, file_types:file_types, expand_paths: expand_paths});

        var applet;
        var dst_paths = [];
        if (kwargs.mode in {'client_repo':'', 'web':''}) {
            applet = spt.Applet.get();
        } 
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

            dst_paths.push(dst);

            if (kwargs.mode == 'client_repo'){
                applet.copytree(path, dst);
            }
            else if (kwargs.mode =='webX'){
                // NOTE: this is no long supported due to lack of Java support on
                // the browser.  Web mode is now the same as browser mode.
                var url = server_root + path;
                if (spt.url.exists(url)){
                    applet.download_file(url, dst);
                }
                else {
                    alert(url + ' does not exist on the server. It may have been backed up.');
                }
            }
            else if (kwargs.mode == 'browser' || kwargs.mode == 'web'){
                var download_el = document.createElement("a");
                download_el.setAttribute("href",path);
                download_el.setAttribute("download",basename);
                document.body.appendChild(download_el);
                download_el.click();
                document.body.removeChild(download_el);
            }
        }
        }
        catch(e){
           alert(spt.exception.handler(e));
        }
        return dst_paths;
    }



    this.set_current_snapshot = function(snapshot_code) {
        return this._delegate("set_current_snapshot", arguments, null);
    }

    this.query_snapshots = function(kwargs) {
        return this._delegate("query_snapshots", arguments, kwargs);
    }

    this.get_snapshot = function(search_key, kwargs) {
        return this._delegate("get_snapshot", arguments, kwargs);
    }


    this.get_snapshots_by_relative_dir = function(relative_dir, kwargs) {
        return this._delegate("get_snapshots_by_relative_dir", arguments, kwargs);
    }

    this.get_sobjects_by_relative_dir = function(relative_dir, kwargs) {
        return this._delegate("get_sobjects_by_relative_dir", arguments, kwargs);
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
     * Task methods
     */ 
    this.create_task = function(search_key, kwargs) {
        return this._delegate("create_task", arguments, kwargs);
    } 

    this.get_tasks = function(search_key, kwargs) {
        return this._delegate("get_tasks", arguments, kwargs);
    }

    this.get_task_status_colors = function() {
        return this._delegate("get_task_status_colors", arguments);
    }


    this.add_initial_tasks = function(search_key, kwargs) {
        return this._delegate("add_initial_tasks", arguments, kwargs);
    }


    this.get_input_tasks = function(search_key, kwargs) {
        return this._delegate("get_input_tasks", arguments, kwargs);
    }

    this.get_output_tasks = function(search_key, kwargs) {
        return this._delegate("get_output_tasks", arguments, kwargs);
    }


    
    /*
     * Low Level Database methods
     */
    this.get_related_types = function(search_type) {
        return this._delegate("get_related_types", arguments);
    }



    this.query = function(search_type, kwargs, on_complete, on_error) {
        var newArgs = Array.prototype.slice.call(arguments).slice(0,2);
        if(on_complete){
          if(!on_error){
            on_error = function(err){
                console.log(err);
            };
          }
          return this._delegate("query", newArgs, kwargs, "string", on_complete, on_error);
        }

        var value = this._delegate("query", newArgs, kwargs, "string");
        //return this._delegate("query", arguments, kwargs);
        value = JSON.parse(value);
        return value
    }



    /* TEST Promises */
    this.query2 = function(search_type, kwargs, on_complete, on_error) {

        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
        on_complete2 = function(value) {
            value = JSON.parse(value);
            on_complete(value);
        }
       
        passed_args = [search_type, kwargs];
        var value = this._delegate("query", passed_args, kwargs, "string", on_complete2, on_error);
        // asynchronouse
        if (on_complete) {
            return;
        }
        value = JSON.parse(value);
        return value
    }


    this.p_query = function(search_type, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {};
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            return this.query2(search_type, kwargs);
        }.bind(this) )
    }




    this.get_by_search_key = function(search_key, kwargs, on_complete, on_error) {
        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
        passed_args = [search_key, kwargs];
        var value = this._delegate("get_by_search_key", passed_args, kwargs, null, on_complete, on_error);
        // asynchronouse
        if (on_complete) {
            return;
        }
        return value

    }

    this.p_get_by_search_key = function(search_key, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.get_by_search_key(search_key, kwargs);
        }.bind(this) )
    }




    this.get_by_code = function(search_type, code) {
        return this._delegate("get_by_code", arguments);
    }

    this.p_get_by_code = function(search_type, code, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.get_by_code(search_type, code, kwargs);
        }.bind(this) )
    }






    this.insert = function(search_type, data, kwargs) {
        // server.insert(search_type, data, kwargs);
        return this._delegate("insert", arguments, kwargs);
        
    }

    this.insert_multiple = function(search_type, data, kwargs) {
        // server.insert(search_type, data, kwargs);
        return this._delegate("insert_multiple", arguments, kwargs);
        
    }



    this.update = function(search_key, data, kwargs, on_complete, on_error) {

        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);

        passed_args = [search_key, data, kwargs];
        var ret_val = this._delegate("update", passed_args, kwargs, null, on_complete, on_error);
        if (on_complete) {
            return;
        }
        if (ret_val && ret_val.status == "ERROR") {
            throw ret_val;
        }
        return ret_val;
    }



    /*
    this.update = function(search_key, data, kwargs, on_complete, on_error) {
        var newArgs = Array.prototype.slice.call(arguments).slice(0,3);
        if(on_complete){
          if(!on_error){
            on_error = function(err){
              console.log(err);
            };
          }
          return this._delegate("update", newArgs, kwargs, undefined, on_complete, on_error);
        }

        return this._delegate("update", newArgs, kwargs);
    }
    */





    this.p_update = function(search_type, data, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {};
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            return this.update(search_type, data, kwargs);
        }.bind(this) )
    }





    this.update_multiple = function(data, kwargs, on_complete, on_error) {
        var newArgs = Array.prototype.slice.call(arguments).slice(0,2);
        data = JSON.stringify(data);
        if(on_complete){
          if(!on_error){
            on_error = function(err){
              console.log(err);
            };
          }
          return this._delegate("update_multiple", arguments, kwargs, undefined, on_complete, on_error);
        }

        return this._delegate("update_multiple", arguments, kwargs);
    }



    //
    // Expression methods
    //
    this.eval = function(expression, kwargs, on_complete, on_error) {

        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
       
        passed_args = [expression, kwargs];
        var ret_val = this._delegate("eval", passed_args, kwargs, null, on_complete, on_error);
        // asynchronouse
        if (on_complete) {
            return;
        }
        // synchronouse
        if (ret_val && ret_val.status == "ERROR") {
            throw ret_val;
        }
        return ret_val;
    }


    /* Test promises */
    this.p_eval = function(expression, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.eval(expression, kwargs);
        }.bind(this) )
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

    this.delete_sobject = function(search_key, kwargs) {
        return this._delegate("delete_sobject", arguments, kwargs);
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
     * Instance methods
     */
    this.add_instance = function(search_key1, search_key2) {
        return this._delegate("add_instance", arguments);
    }
 
    this.get_instances = function(search_key, search_type) {
        return this._delegate("get_instances", arguments);
    }
 
    this.remove_instance = function(search_key1, search_key2) {
        return this._delegate("remove_instance", arguments);
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
    this.get_widget = function(class_name, kwargs, on_complete, on_error) {
        var libraries = spt.Environment.get().get_libraries();
        kwargs.libraries = libraries;

        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);

        passed_args = [class_name, kwargs];
        try {
            var ret_val = this._delegate("get_widget", passed_args, kwargs, "string", on_complete, on_error);
            return ret_val;
        }
        catch(e) {
            var e_msg = spt.exception.handler(e);
            if (/Cannot login with key/.test(e_msg)) 
                this._redirect_login();
            else
                alert(e_msg);
            return;
        }
    }



    // Test load view
    this.load_view = function(el, view, kwargs, on_complete, on_error) {

        if (!kwargs) kwargs = {};
        kwargs['view'] = view;

        var class_name = 'tactic.ui.panel.CustomLayoutWdg';
        var wdg_kwargs = {
            args: kwargs,
            cbjs_action: function(widget) {
                var node = document.createElement("div");

                node.innerHTML = widget;

                el.appendChild(node);

                var scripts = node.getElementsByTagName("script");
                for (var i = 0; i < scripts.length; i++) {
                    var func = function() {
                        eval(scripts[i].innerHTML);

                    };
                    func();
                    scripts[i].remove();
                }

                if (on_complete)
                    on_complete(node);
            }


        };
        this.async_get_widget(class_name, wdg_kwargs);
    }






    this.class_exists = function(class_path) {
        return this._delegate("class_exists", arguments);
    }


    this.execute_cmd = function(class_name, args, values, kwargs, on_complete, on_error) {

        if (typeof(values) == 'undefined') {
            values = {};
        }
        if (typeof(kwargs) == 'undefined') {
            kwargs = {};
        }

        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
        passed_args = [class_name, args, values, kwargs];
        var ret_val = this._delegate("execute_cmd", passed_args, kwargs, null, on_complete, on_error);
        if (on_complete) {
            return;
        }
        if (ret_val && ret_val.status == "ERROR") {
            throw ret_val;
        }
        return ret_val;
    }


    this.p_execute_cmd = function(class_name, args, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.execute_cmd(class_name, args, {}, kwargs);
        }.bind(this) )
    }





    this.execute_class_method = function(class_name, method, kwargs) {
        return this._delegate("execute_class_method", arguments);
    }


    
    this.execute_transaction = function(transaction_xml, kwargs) {
        return this._delegate("execute_transaction", arguments, kwargs);
    }




    this.execute_python_script = function(script_path, script_kwargs, kwargs) {
        if (kwargs) callback = kwargs.on_complete;
        else callback = null;
        return this._delegate("execute_python_script", arguments, kwargs, null, callback);
    }


    this.execute_js_script = function(script_path, script_kwargs, kwargs) {
        if (kwargs) callback = kwargs.on_complete;
        else callback = null;
        return this._delegate("execute_js_script", arguments, kwargs, null, callback);
    }


    this.execute_cbk = function(bvr, callback, args, kwargs) {
        var cbk = "tactic.ui.panel.CustomLayoutCbk";
        var top = bvr.src_el.getParent(".spt_custom_top");
        var view = top.getAttribute("spt_view");

        var cbk_kwargs = {
            view: view,
            callback: callback,
            kwargs: args,
        }

        return this.execute_cmd(cbk, cbk_kwargs)
    }


    this.p_execute_cbk = function(bvr, callback, args, kwargs) {
        var cbk = "tactic.ui.panel.CustomLayoutCbk";
        var top = bvr.src_el.getParent(".spt_custom_top");
        var view = top.getAttribute("spt_view");

        var cbk_kwargs = {
            view: view,
            callback: callback,
            kwargs: args
        }

        return this.p_execute_cmd(cbk, cbk_kwargs)
    }
 


    

    this.execute = function(code) {
        return this._delegate("execute", arguments, null);
    }



    this.check_access = function(access_group, key, access, kwargs) {
        return this._delegate("check_access", arguments, kwargs);
    }


    //
    // Queue Manager
    //
    this.add_queue_item = function(class_name, args, kwargs) {
        return this._delegate("add_queue_item", arguments, kwargs);
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
    // Trigger methods
    //
    this.call_trigger = function(search_key, event, kwargs, on_complete, on_error) {
        [on_complete, on_error] = this._handle_callbacks(kwargs, on_complete, on_error);
        passed_args = [search_key, event, kwargs];
        var ret_val = this._delegate("call_trigger", passed_args, kwargs, null, on_complete, on_error);
        return ret_val
    }

    this.p_call_trigger = function(search_key, event, kwargs) {
        return new Promise( function(resolve, reject) {
            if (!kwargs) kwargs = {}
            kwargs.on_complete = function(x) { resolve(x); }
            kwargs.on_error = function(x) { reject(x); }
            this.call_trigger(search_key, event, kwargs);
        }.bind(this) )
    }


    this.call_pipeline_event = function(search_key, process, event, data) {
        return this._delegate("call_pipeline_event", arguments)
    }

    this.get_pipeline_status = function(search_key, process) {
        return this._delegate("get_pipeline_status", argumnets);
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


    // Access to some useful external functions
    this.send_rest_request = function(method, url, kwargs) {
        return this._delegate("send_rest_request", arguments, null);
    }



    // Misc
    this.get_path_from_snapshot = function(snapshot_code, kwargs) {
        return this._delegate("get_path_from_snapshot", arguments, kwargs);
    }


    this.get_all_paths_from_snapshot = function(snapshot_code, kwargs) {
        return this._delegate("get_all_paths_from_snapshot", arguments, kwargs);
    }


    // async functions

    this.async_get_widget = function(class_name, kwargs, on_complete, on_error) {

        var api = this;
        var api_kwargs = {};
        Object.assign(api_kwargs, kwargs);

        var libraries = spt.Environment.get().get_libraries();
        kwargs.libraries = libraries;
        
        var callback = kwargs['cbjs_action'];
        if (!callback) {
            callback = kwargs['callback'];
        }
        if (!callback) {
            callback = kwargs['on_complete'];
        }
        if (!callback) {
            callback = on_complete;
        }


        var err_callback = function(e) {
            // try handling the ERROMETHOD error
            /*
            if (e.contains("XERRORMETHOD")) {
                //alert("ERRORMETHOD!!!!!");
                //api.async_get_widget(class_name, api_kwargs, on_complete, on_error);
                return;
            }
            */
            if (e == 0) {
                e = 'Received an error (Error 0)';
                var error = new Error();
                console.log(error.stack);
            }
            else if (e == 502)
                e = 'Timeout Error (Error 502)';
            else if (e == 503)
                e = 'Service is unavailable (Error 503)';
            else if (e == 504)
                e = 'Gateway Timeout error (Error 504)';

            if (!on_error) {
                on_error = kwargs['on_error'];
            }

            if (on_error) {
                on_error(e);
            }
            else {
                spt.alert("async_get_widget: " + e);
            }
        };
        passed_args = [class_name, kwargs];
        this._delegate("get_widget", passed_args, kwargs, "string", callback, err_callback);
        return;
    }

    //DEPRECATED use eval
    this.async_eval = function(class_name, kwargs) {
        alert("Client API function async_eval is deprecated. Use eval")
        var callback = kwargs['cbjs_action'];
        if (!callback) {
            callback = kwargs['callback'];
        }
        this._delegate("eval", arguments, kwargs, null, callback);
        return;
    }


    // methed that handles asynchronous callbacks.
    // It allows for on_complete to be called in the kwargs as well.
    // It also handles a flag "promise" which can be used with promises which
    // defines an oncomplete that is passed to the "then" function of the
    // promise
    //
    this._handle_callbacks = function(kwargs, on_complete, on_error) {
        if (typeof(kwargs) != 'undefined' && kwargs != null) {

            if (!on_complete) {
                on_complete = kwargs.on_complete;
            }
            if (!on_error) {
                on_error = kwargs.on_error;
            }

            delete kwargs.on_error;
            delete kwargs.on_complete;
        }
        else {
            on_complete = null;
            on_error = null;
        }

        if (on_complete) {
            if (!on_error) {
                on_error = function(err){
                    throw(err);
                };
            }
        }

        return [on_complete, on_error];
            
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
    //   on_error: A function that is run when a request throws an error.
    //      This is used be get_async_widget() and others
    this._delegate = function(func_name, passed_args, kwargs, ret_type, callback, on_error) {

        
        if (spt._delegate) {
            return spt._delegate(func_name, passed_args, kwargs);
        }


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
            'site': this.site,
            'project': this.project,
            'palette': this.get_palette(),
            'api_key': this.get_api_key() || "",
            'language': 'javascript'
        };
        args.push(ticket);

        // Trims off undefined kwargs
        if (typeof(passed_args) == "undefined") {
            passed_args = [];
        } else {
            if (typeof(passed_args) == "arguments") {
                passed_args = Array.from(passed_args);
            } 
            if (passed_args.length > 0) {
                if (passed_args[passed_args.length-1] == undefined) {
                    passed_args = passed_args.splice(0, passed_args.length-1);
                }
            }
        }

        // determine if there was a kwargs passed in
        var num_args;
        var has_kwargs;

        if (typeof(kwargs) == undefined || kwargs == null) {
            num_args = passed_args.length;
            has_kwargs = false;
        }
        else if (kwargs.__empty__) {
            num_args = passed_args.length;
            has_kwargs = true;
        } else {
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


        // handle asynchronous mode
        if (typeof(callback) != 'undefined' && callback != null) {
            var self = this;
            client.set_callback( function(request) {
                self.async_callback(client, request, on_error);
            } );
            client.invoke( func_name, args );

            // Store on the client
            client.func_name = func_name;
            client.ret_type = ret_type;
            client.callback = callback;
            return;
        }

        // just do it synchronously
        else {
            ret_val = client.invoke( func_name, args );
            return this._handle_ret_val(func_name, ret_val, ret_type);
        }

    }

    this._show_login = function() {
        
        var spinners = $$('.spt_spin');
        spinners.each(function(x) {spt.hide(x)});
        var login_scr = document.getElement('.spt_login_screen');
        login_scr.setStyle('z-index','1100');
        var custom_content = login_scr.getParent('.spt_custom_content');
        if (custom_content) {
            custom_content.setStyle('position','absolute');
            custom_content.setStyle('top','30%');
            custom_content.setStyle('left','50%');
        }
        spt.popup.show_background();
        spt.show(login_scr);

    }
    this._redirect_login = function() {
       
        var ok = function() {
            window.location.reload();
        };
        spt.info('Your session has expired.', {'click': ok});
    }
    this.async_callback = function(client, request, on_error) {
        if (request.readyState == 4) {
            if (request.status == 200) {
                try {
                    var data = this._handle_ret_val(client.func_name, request, client.ret_type);
                    client.callback(data);
                } catch(e) {
                    var e_msg = spt.exception.handler(e);
                    if (/Cannot login with key/.test(e_msg)) {
                        this._redirect_login();
                    }
                    else if (on_error)
                        on_error(e);
                    else
                        spt.alert("async_callback: " + e_msg);
                }
            } else {
                
                if (on_error)
                    on_error(request.status);
                else
                    throw("status is " + request.status);
            }
        }
    }


        
    this._handle_ret_val = function(func_name, ret_val, ret_type) {
        if (ret_val.status != 200) {
            throw(ret_val.status);
        }

        if (ret_type == "raw") {
            return ret_val.responseText;
        }
        if (ret_type == "string") {
            // manually extract the value returned
           
            var value = ret_val.responseText;
            value = value.replace(/^<\?xml version='1.0'\?>\n<methodResponse>\n<params>\n<param>\n<value><string>/, '');
            value = value.replace(/<\/string><\/value>\n<\/param>\n<\/params>\n<\/methodResponse>/, '');

            value = value.replace(/&amp;/g, "&");
            value = value.replace(/&lt;/g, "<");
            value = value.replace(/&gt;/g, ">");

            // fix inline < > that are not part of the html structure
            value = value.replace(/&spt_lt;/g, "&lt;");
            value = value.replace(/&spt_gt;/g, "&gt;");

            if (value.match("<name>faultCode</name>")) {
                var el = document.createElement("div");
                el.innerHTML = value;
                el = el.getElementsByTagName("value")[2];
                el = el.childNodes[0];
                value = el.innerHTML;
                throw("Server Error: " + value);
            }

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
            var patt = /faultCode/g;
            if (patt.test(ret_val)) {
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

        if (jsontext == "OK") {
            return ret_val;
        }
                
        var value;
        try {
            value = JSON.parse(jsontext);
        } catch(e) {
            // assume it is just a string
            value = jsontext;
            if (func_name != 'start') {

                ret_val = ret_val.responseText;
                var patt = /faultCode/g;
                if(patt.test(ret_val)) {
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
        var site = env.get_site();
        var project_code = env.get_project();

        this.server.set_url(url);
        this.server.set_ticket(login_ticket);
        this.server.set_site(site);
        this.server.set_project(project_code);
    }
    return this.server;
}

TacticServerStub.get_master = function() {
    var env = spt.Environment.get();
    var master_slave_setup = env.get_master_enabled();

    if (['true', true].indexOf(master_slave_setup) > -1) {
        this.server = new TacticServerStub();
        var master_slave_setup = env.get_master_enabled();
        var url = env.get_master_url();
        var login_ticket = env.get_master_login_ticket();
        var site = env.get_master_site();
        var project_code = env.get_master_project_code();

        this.server.set_url(url);
        this.server.set_ticket(login_ticket);
        this.server.set_site(site);
        this.server.set_project(project_code);
        this.server.set_transaction_ticket(login_ticket);
    } else {
        this.server = this.get(); 
    }
    return this.server;
}


TACTIC = TacticServerStub;



