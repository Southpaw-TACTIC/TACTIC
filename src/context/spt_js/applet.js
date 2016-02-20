/* *********************************************************
 *
 * Copyright (c) 2005-2010, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 



/*
 * Javascript wrapper around the General Applet.  The gernal Applet is a thin
 * wrapper on top of an applet that has access to the client machine.  This
 * applet enables the application developer to have access to the operations
 * on the client machine which would otherwise be blocked.
 *
 * It provides numerous system level commands that are essential for checkin
 * files in and out of TACTIC.
 *
 */

spt.Applet = function()
{

    this.server_api_version = null;

    // Method to arbitrarily run system commands on the client
    //
    // @param:
    //  cmd - string that will executed as a system command
    //  wait_for - (true|false) determines whether or not the method will wait
    //      for the completion of the command
    //
    // @return:
    //  ret_val - the return code of the system command
    //
    // @examples:
    //
    //  Execute "notepad" in the background
    //
    //      var applet = spt.Applet.get();
    //      var cmd = "notepad";
    //      var wait_for = false;
    //      var ret_val = applet.exec(cmd, wait_for);
    //
    //
    this.exec = function(cmd, wait_for)
    {
        var applet = document.general_applet;
        if (wait_for == null)
            wait_for = true;

        var ret_val;
        if (this.client_lang == 'python') {
            ret_val = applet.execute(cmd, wait_for)
        }
        else {
            ret_val = applet.exec(cmd, wait_for)
        }
        return ret_val;
    } 


    this.exec_shell = function(cmd, wait_for)
    {
        var applet = document.general_applet;
        if (wait_for == null)
            wait_for = true;

        var ret_val;
        if (this.client_lang == 'python') {
            ret_val = applet.execute_shell(cmd, wait_for)
        }
        else {
            ret_val = applet.exec_shell(cmd, wait_for)
        }

        return ret_val;
    } 

 

    // Method to open up file explorer to a specific directory.  This will
    // open up Windows Explorer (Windows) for the File Chooser (OSX)
    //
    // @param:
    //  dir - the starting directory
    //
    // @return:
    //  null
    //
    // @examples:
    //
    //  Open a directory to C:/Temp
    //
    //      var applet = spt.Applet.get();
    //      var dir = "C:/Temp:;
    //      applet.open_explorer(dir);
    //
    this.open_explorer = function(dir)
    {
        var applet = document.general_applet;
        applet.open_folder(dir);
        return;
    } 


    // Method to create a file from a string
    //
    // @param:
    //  path - the path of the file to be created
    //  doc - the string that will be put in the file
    //
    // @param:
    //  null
    //
    // @examples:
    //
    //  Example to create a simple bat file that puts a command in a bat file
    //  and executes
    //
    //      var my_cmd = 'notepad "C:/Temp/whatever.txt"';
    //      var applet = spt.Applet.get();
    //      var path = "C:/Temp/whatever.bat";
    //      applet.create_file(path, my_cmd);
    //      applet.exec(path);
    //
    this.create_file = function(path, doc)
    {
        var applet = document.general_applet;
        applet.create_file(path, doc);
    }


    // Method to generate the MD5 Checksum of a file
    this.get_md5 = function(path)
    {
        var applet = document.general_applet;
        return applet.get_md5(path);
    }



    // Method to determine if a path exists
    //
    // @param:
    //   path - the path of the file or directory that is to be checked
    //
    // @return:
    //   true is path exists
    //
    // @examples:
    //
    //  Test whether "C:/Program Files" is a directory and if so, list the
    //  contents.
    //
    //      var applet = spt.Applet.get();
    //      var path = "C:/Program Files";
    //      var exts = applet.exits(path);
    //
    this.exists = function(path)
    {
        var applet = document.general_applet;
        return applet.exists(path);
    }



    // Get dictionary of data about a file
    //
    // @param:
    //   path - the path of the file or directory that is to be checked
    //
    // @return:
    //   dict of infoabout a file
    //
    // @examples:
    //
    //      var applet = spt.Applet.get();
    //      var path = "C:/Program Files";
    //      var exts = applet.get_path_info(path);
    //
    this.get_path_info = function(path)
    {
        var applet = document.general_applet;
        var json_info = applet.get_path_info(path);
        return JSON.parse(json_info);
    }






    // Method to determine if a path is a directory or a file
    //
    // @param:
    //   path - the path of the file or directory that is to be checked
    //
    // @return:
    //   true is path is a directory, false if path is a file
    //
    // @examples:
    //
    //  Test whether "C:/Program Files" is a directory and if so, list the
    //  contents.
    //
    //      var applet = spt.Applet.get();
    //      var path = "C:/Program Files";
    //      var is_dir = applet.is_dir(path);
    //      if (is_dir == true) {
    //          var contents = applet.list_dir(path);
    //      }
    //
    this.is_dir = function(path)
    {
        var applet = document.general_applet;
        return applet.is_dir(path);
    }


    // Method to recursively create directories.
    //
    // @param:
    //  dir - the directory that is to be created
    //
    // @return:
    //  null
    //
    // @examples:
    // 
    //  Create a directory "C:/Temp/assets/chr/chr001/model"
    // 
    //      var applet = spt.Applet.get();
    //      var dir = "C:/Temp/assets/chr/chr001/model";
    //      applet.makedirs(dir)
    //
    //
    this.makedirs = function(dir)
    {
        if (this.exists(dir)) {
            return;
        }
        var applet = document.general_applet;
        applet.makedirs(dir);
    }


    // Method to list all of the files/directories under give path
    //
    // @param:
    //  dir - the directory under which the list will be built
    //
    // @return:
    //  a list of paths under the given path
    //
    // @examples:
    //
    //  Get a list of all the paths underneath "C:/Temp/assets/chr".
    //
    //      var applet = spt.Applet.get();
    //      var dir = "C:/Temp/assets/chr";
    //      var paths = applet.list_dir(dir);
    //      for (var i = 0; i < paths.length; i++) {
    //          var path = paths[i];
    //          alert(path);
    //      }
    //
    //
    this.list_dir = function(dir, depth)
    {
        if (typeof(depth) == 'undefined') {
            depth = 0
        }
        var applet = document.general_applet;
        var paths = applet.list_recursive_dir(dir, depth);
        if (this.client_lang == 'python') {
            return JSON.parse(paths);
        }
        else {
            return paths;
        }
    }


    // Method to list all of the files/directories under give path
    //
    // @param:
    //  dir - the directory under which the list will be built
    //
    // @return:
    //  a list of paths under the given path
    //
    this.list_recursive_dir = function(dir)
    {
        var depth = -1
        var applet = document.general_applet;
        var paths = applet.list_recursive_dir(dir, depth);
        if (this.client_lang == 'python') {
            return JSON.parse(paths);
        }
        else {
            return paths;
        }


    }


    // Method to get the size of a path
    //
    // @param:
    //  path - the path from which the size will be calculated
    //
    // @return:
    //  an integer representing the size of the path in bytes
    //
    this.get_size = function(path)
    {
        var applet = document.general_applet;
        return applet.get_size(path);
    }




    // Method to send commands through a given port
    //
    this.command_port = function(url, port, cmd)
    {
        var applet = document.general_applet;
        // strip http:// or https://
        host = url.replace(/^http:\/\/|^https:\/\//g,'');
        return applet.command_port(host, port, cmd);
    }

    this.get_connect_error = function()
    {
        applet = document.general_applet;
        return applet.get_connect_error();
    }



    this.copy_file = function(from_path, to_path)
    {
        var applet = document.general_applet;
        return applet.copy_file(from_path, to_path);
    }

    this.copytree = function(from_path, to_path)
    {
        var applet = document.general_applet;
        return applet.copytree(from_path, to_path);
    }

    this.rmtree = function(path)
    {
        var applet = document.general_applet;
        return applet.rmtree(path);
    }


    this.move = function(from_path, to_path)
    {
        var applet = document.general_applet;
        return applet.move_file(from_path, to_path);
    }
    this.move_file = function(from_path, to_path)
    {
        var applet = document.general_applet;
        return applet.move_file(from_path, to_path);
    }



    // Get the contents of a file and return them
    this.read_file = function(path)
    {
        var applet = document.general_applet;
        return applet.read_file(path);
    }


    // upload a file to the server
    //
    this.upload_file = function(path, ticket, subdir)
    {
        var applet = document.general_applet;
        var server_url = spt.Environment.get().get_server_url();
        if (!ticket)
            ticket = spt.Environment.get().get_ticket();
        server_url = server_url + "/tactic/default/UploadServer/";
        applet.set_ticket(ticket);
        try {
            if (typeof subdir =='undefined')
            {
                applet.do_upload(server_url, path, '');
            }
            else
                applet.do_upload(server_url, path, subdir);
        } catch(e) {
            spt.alert(spt.exception.handler(e));
        }
    }


    this.upload_directory = function(dir_path, ticket, subdir)
    {
        var applet = document.general_applet;
        var files = applet.list_recursive_dir(dir_path, -1);
        if (!ticket)
            ticket = spt.Environment.get().get_ticket();
        if (!subdir)
            subdir = null;

        var parts = dir_path.split(/[\/\\]/);
        var root = parts.pop();
        dir_path = dir_path.replace(/\\/g, "/");    
        
        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            file = file.replace(/\\/g, "/");
            var relpath = file.replace(dir_path + "/", "");
            var parts = relpath.split("/");
            var filename = parts.pop();
            var subdir;
            if (parts.length) {
                subdir = root + "/" + parts.join("/");
            }
            else {
                subdir = root;
            }
            // no need to upload directory
            if (applet.is_dir(file)) continue;
                
            this.upload_file(file, ticket, subdir);
        }
        return files;
    }


    // Method to a download the file from the provide url to a given path
    //
    this.download_file = function(url, to_path)
    {
        var applet = document.general_applet;

        if (to_path.substr(to_path.length-1) === "/") {
            var parts = url.split("/");
            var basename = parts[parts.length-1];
            to_path = to_path + basename;
        }

        url = url.replace(/ /g, "%20");

        if (this.client_lang == 'python') 
            applet.download_file(url, to_path);
        else
            applet.download(url, to_path);
    }





    this.current_dir = null;
    this.reset_current_dir = function() {
        this.current_dir = null;
    }

    // Method to open a file browser and select files
    //
    // @param:
    //  current_dir - the starting directory that will be displayed
    //
    // @return:
    //  paths - a list of absolute paths that were selected
    //
    // @example:
    //
    //  Open a file browser to the C:/Temp directory
    //
    //    var applet = spt.Applet.get();
    //    var dir = "C:/Temp";
    //    var paths = applet.open_file_browser(dir);
    //
    this.open_file_browser = function(current_dir, select_dir)
    {
        if (this.current_dir != null) {
            // if it already set, then do nothing
            current_dir = this.current_dir;
        }
        else if (typeof(current_dir) == 'undefined') {
            current_dir = this.current_dir;
        }

        var applet = document.general_applet;
       
        if (typeof(select_dir) == 'undefined')
            select_dir = false;

        var file_paths;
        if (this.client_lang == 'python') {
            
            file_paths = applet.open_file_browser(current_dir, select_dir);
            if (file_paths) 
                file_paths = JSON.parse(file_paths);
            
            else 
                file_paths = [];
        } else {
            file_paths = applet.open_file_browser(current_dir);
        }

        // convert to a js array ... much more friendly to use
        var js_paths = [];
        for (var i = 0; i < file_paths.length; i++) {
            js_paths[i] = file_paths[i];
        }

        if (js_paths.length >= 0) {
            if (js_paths[0] ) {
                var path = js_paths[0];
                path = path.replace(/\\/g, '/');
                if (this.is_dir(path) ) {
                    var parts = path.split("/");
                    parts.pop();
                    path = parts.join("/");
                }

                this.current_dir = path;
            }
        }

        return js_paths;
    }

    this.get_current_dir = function() {
        return this.current_dir;
    }


    // environment variables
    //
    this.getenv = function(key)
    {
        var applet = document.general_applet;
        var value = (this.client_lang == 'python')? applet.get_env(key) : applet.getenv(key);
        return value;
    }

    this.getenvp = function(key)
    {
        var applet = document.general_applet;
        return applet.getenvp(key);
    }


    this.setenvp = function(key, value)
    {
        var applet = document.general_applet;
        return applet.setenvp(key, value);
    }


    // Read infile that is in base 64 notation and create the outfile of it decoded.
    //
    // @param:
    //  infile  - path to the input file that has been encoded in base 64 notation
    //  outfile - path to where the output file will be created, decoded
    //
    // @return:
    //  none
    //
    // @examples:
    //
    //  Decode the infile named "encoded.txt" from base 64 notation to "decoded.jpg":
    //
    //      var applet = spt.Applet.get();
    //      applet.decodeFileToFile("C:/temp/encoded.txt", "C:/temp/decoded.jpg");
    //
    this.decodeFileToFile = function(infile, outfile)
    {
        var applet = document.general_applet;
        applet.decodeFileToFile(infile, outfile);
    }


    // Read the input string and return the string decoded from base 64 notation.
    //
    // @param:
    //  input_str  - the input string to be decoded
    //
    // @return:
    //  the decoded string
    //
    // @examples:
    //
    //  Decode the input string from base 64 notation:
    //
    //      var applet = spt.Applet.get();
    //      var my_decoded_str = applet.decodeString(my_encoded_str);
    //
    this.decodeString = function(input_str)
    {
        var applet = document.general_applet;
        return applet.decodeString(input_str);
    }


    // Read infile and create the outfile of it encoded in base 64 notation.
    //
    // @param:
    //  infile  - path to the input file that we wish to be encoded
    //  outfile - path to where the output file will be created, encoded
    //
    // @return:
    //  none
    //
    // @examples:
    //
    //  Encode the infile named "original.jpg" to base 64 notation to "output.txt":
    //
    //      var applet = spt.Applet.get();
    //      applet.encodeFileToFile("C:/temp/original.jpg", "C:/temp/encoded.txt");
    //
    this.encodeFileToFile = function(infile, outfile)
    {
        var applet = document.general_applet;
        applet.encodeFileToFile(infile, outfile);
    }


    // Read the input string and return the string encoded in base64 notation.
    //
    // @param:
    //  input_str  - the input string to be encoded
    //
    // @return:
    //  the encoded string
    //
    // @examples:
    //
    //  Encode the input string from "Hello World!" to base 64 notation:
    //
    //      var applet = spt.Applet.get();
    //      var my_encoded_str = applet.encodeString("Hello World!");
    //
    this.encodeString = function(input_str)
    {
        var applet = document.general_applet;
        return applet.encodeString(input_str);
    }


    // Open a file with it's associated application
    //
    // @param:
    //  path - the path of the file to open
    //
    // @return:
    //  null
    //
    // @examples:
    //
    //  Encode the input string from "Hello World!" to base 64 notation:
    //
    //      var applet = spt.Applet.get();
    //      applet.open_file("C:/test.psd");
    //
    this.open_file = function(path)
    {
        var applet = document.general_applet;
        return applet.open_file(path);
    }


    // Open a url with it's associated browser application
    //
    // @param:
    //  url - the url of the file to open
    //
    // @return:
    //  null
    //
    // @examples:
    //
    //      var applet = spt.Applet.get();
    //      applet.open_url("http://www.yahoo.com");
    //
    this.open_url = function(url)
    {
        var applet = document.general_applet;
        return applet.open_url(url);
    }


    this.open_browser_url = function(url)
    {
        if (this.client_lang == 'python') {
            applet.open_browser_url(url);
        }
        else {
            // don't use applet for this in the browser
            window.open(url);
        }
    }


    this.open_tactic_url = function(url)
    {
        if (this.client_lang == 'python') {
            var env = spt.Environment.get();
            var ticket = env.get_ticket();

            if (url.indexOf("?") != -1) {
                url = "&login_ticket=" + ticket
            }
            else {
                url = "?login_ticket=" + ticket
            }
            applet.open_browser_url(url);
        }
        else {
            // don't use applet for this in the browser
            window.open(url);
        }
    }



    // Method to unzip files on the client
    //
    this.unzip_file = function(from_path, to_dir)
    {
        var applet = document.general_applet;
        applet.unzip_file(from_path, to_dir);
    }




    this.install_python = function() {
        spt.app_busy.show("Installing client libraries ...")

        // Windows only for now
        //
        var server = TacticServerStub.get();
        api_version = this.server_api_version;
        api_version = "tactic-api-python-" + api_version;


        var file_name = api_version + ".zip";

        var base = 'C:/ProgramData/Tactic';


        var output_base = base + "/temp/output";
        var to_path = base + "/api/" + file_name;

        var python = base + "/api/" + api_version + "/python.exe";

        var env = spt.Environment.get();
        var server_url = env.get_server_url();
        var download_url = server_url + "/context/client/" + file_name;

        this.download_file(download_url, to_path);
        this.unzip_file(to_path, base +"/api");
        spt.app_busy.hide();

    }


    this.exec_local_cmd = function(class_name, kwargs)
    {
        // If the client language is ptyhon, then call the functions
        // directly from python
        if (this.client_lang == 'python') {
            return this.exec_python_cmd(class_name, kwargs);
        }


        var server = TacticServerStub.get();
        if (this.server_api_version == null) {
            this.server_api_version = server.get_server_api_version();
        }
        api_version = this.server_api_version;
        api_version = "tactic-api-python-" + api_version;

        // NOTE: this assumes an installed directory (and assumes windows)
        var base = 'C:/ProgramData/Tactic';

        var output_base = base + "/temp/output";
        var python = base + "/api/" + api_version + "/python.exe";
        var executable = base + "/api/"+api_version+"/Lib/site-packages/tactic_client_lib/scm/delegate.py";


        // detect if there is a python version available
        if (! this.exists(python)) {
            if (confirm("TACTIC client side libraries not installed in ["+base+"] ... do you wish to install?")) {
                this.install_python();
            }
            else {
                throw("No TACTIC Libraries installed");
            }
        }



        var applet = document.general_applet;
        var env = spt.Environment.get();

        // add the class name to the kwargs
        kwargs.class_name = class_name;
        var kwargs_json = JSON.stringify(kwargs);

        applet.create_file(output_base + "/kwargs.json", kwargs_json);

        var cmd = python + " " + executable;
        this.exec_shell(cmd);


        var ret_val_json = applet.read_file(output_base + "/output.json");;
        var ret_val = JSON.parse(ret_val_json);
        if (ret_val.status == 'error') {
            throw(ret_val);
        } 

        return ret_val;
    }



    this.exec_python_cmd = function(class_name, kwargs) {
        // This only works on Qt Team version of TACTIC
        var kwargs = JSON.stringify(kwargs)
        var applet = document.general_applet;
        var ret_val_json = applet.execute_python_cmd(class_name, kwargs);
        ret_val = JSON.parse(ret_val_json);
        return ret_val;
    }

}






// Treats the Applet as a singleton and allows you to retrieve the
// same reference from various parts of the code.
//
spt.Applet.applet = null;
spt.Applet.get = function() {

    if (this.applet != null) {
        return this.applet;
    }

    // use python applet if it exists
    qt_browser = spt.browser.is_Qt();
    if (qt_browser) {
        if (typeof(pyApplet) != 'undefined') {
            document.general_applet = pyApplet;
            this.applet = new spt.Applet();
            this.applet.client_lang = 'python';
            return this.applet;
        }
        else {
            alert("No connector to Python (pyApplet) found");
            this.applet = null;
            return null;
        }
    }


    var applet;
    if (spt.browser.is_IE()) {
       
        // Need to add the applet when the dom is finished loading for IE
        window.addEvent('domready', function() {
            applet = document.createElement("OBJECT");
            applet.setAttribute("classid", "clsid:8AD9C840-044E-11D1-B3E9-00805F499D93");
            applet.setAttribute("width", "1");
            applet.setAttribute("height", "1");
            applet.setAttribute("id", "general_applet");

            var param = document.createElement("param");
            param.setAttribute("name", "archive");
            param.setAttribute("value", "/context/java/Upload-latest.jar");
            applet.appendChild(param);

            var param = document.createElement("param");
            param.setAttribute("name", "code");
            param.setAttribute("value", "upload.GeneralApplet");
            applet.appendChild(param);

            var param = document.createElement("param");
            param.setAttribute("name", "codebase");
            param.setAttribute("value", "/context/java");
            applet.appendChild(param);

            var param = document.createElement("param");
            param.setAttribute("name", "id");
            param.setAttribute("value", "general_applet");
            applet.appendChild(param);

            var div = document.createElement("div");
            div.appendChild(applet);
            var html = div.innerHTML;

            var span = document.createElement("span");
            $("side_bar").appendChild(span);
            span.innerHTML = html;
        });
    }
    else {
        applet = document.createElement("object");
        applet.setAttribute("code", "upload.GeneralApplet");
        applet.setAttribute("archive", "/context/java/Upload-latest.jar");
        applet.setAttribute("type","application/x-java-applet");
        applet.setAttribute("codebase", "/context/java");
        applet.setAttribute("width", "1");
        applet.setAttribute("height", "1");
        applet.setAttribute("id", "general_applet");

      
        var param = document.createElement("param");
        param.setAttribute("name", "archive");
        param.setAttribute("value", '/context/java/Upload-latest.jar');
        applet.appendChild(param);

        var param = document.createElement("param");
        param.setAttribute("name", "scriptable");
        param.setAttribute("value", "true");
        applet.appendChild(param);
        var param = document.createElement("param");
        param.setAttribute("name", "mayscript");
        param.setAttribute("value", "yes");
        applet.appendChild(param);
        document.body.appendChild(applet);
    }


   

    this.applet = new spt.Applet();
    this.applet.client_lang = 'java';

    //check if JRE is installed    
    try {
        applet.onload = function() { spt.notify.show_message("Initializing Java"); 
            document.general_applet.init(); document.general_applet.exists();}
        
    } catch(e) {
        spt.alert('Java plug-in has not been installed for your web browser!');
       
        this.applet = null;
        return this.applet;
    }

   
    //init transfer mode
    try {
        var env = spt.Environment.get();
        var handoff_state = document.general_applet.exists(env.get_client_handoff_dir());
        var asset_state = document.general_applet.exists(env.get_client_repo_dir());
        if (asset_state == false) {
            env.set_transfer_mode("web");
        }
        else if (handoff_state == false) {
            env.set_transfer_mode("web");
        }
        else {
            env.set_transfer_mode("copy");
        }
    } catch(e) {
        if (e.message.test(/has no method/)) {
            this.applet = null;

            spt.alert('Java applet has not been properly initialized.');
        }
        else if (e.message.test(/is not a function/)) {
            this.applet = null;
            log.critical("Java applet is not enabled or updated: "  + e.message);
        }
        else
            spt.alert(spt.exception.handler(e));
    }

    return this.applet;
    
}



