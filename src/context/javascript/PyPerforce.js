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



function PyPerforce() 
{
    this.applet_id = "repo_applet"
    this.open_explorer = function(dir) 
    {
        var applet = document.getElementById(this.applet_id)
        dir = applet.get_root() + "/" +  dir
        applet.makedirs(dir)
        applet.exec("explorer file://" + dir )
        return
    }

    // open exporer with path given
    this.open_explorer2 = function(dir) 
    {
        var applet = document.getElementById(this.applet_id)
        applet.makedirs(dir)
        applet.exec("explorer file://" + dir )
        return
    }


   
    this.perforce_submit =  function(name, code) 
    {
        comment = document.form.elements["comment_" + code].value
        applet = document.getElementById(this.applet_id)
        applet.commit(name, comment)
        return true
    }
 

    this.set_info = function(name, path) 
    {
        spt.RepoApplet.get();
        var applet = document.getElementById(this.applet_id)

        var path = applet.get_root() + "/" + path

        var workspaces = applet.perforce("workspaces")
        var workspaces_hidden = document.form.elements["workspaces_" + name]
        workspaces_hidden.value = workspaces

        // test getting a bunch of data marshalled to python
        var have = applet.perforce("have")
        have_hidden = document.form.elements["have_" + name]
        have_hidden.value = have


        // get the local files
        var local = applet.get_files(path) + ""
        local = local.replace(/\\/g, "/")
        local = local.replace(/\"/g, "")
        local_hidden = document.form.elements["local_" + name]
        local_hidden.value = local.toLowerCase()


        var sync = applet.get_repo(path + "/", true) + ""
        sync = sync.replace(/\\/g, "/")
        sync_hidden = document.form.elements["sync_" + name]
        sync_hidden.value = sync.toLowerCase()
        
        var repo = applet.get_repo(path + "/", false) + ""
        repo  = repo.replace(/\\/g, "/")
        repo_hidden = document.form.elements["repo_" + name]
        repo_hidden.value = repo.toLowerCase()

        var checkout = applet.get_checkout(path + "/")+ ""
        checkout = checkout.replace(/\\/g, "/")
        checkout_hidden = document.form.elements["checkout_" + name]
        checkout_hidden.value = checkout.toLowerCase()

        return true
    }
 


    this.checkin_file = function(cb_name, text_name, asset_name) 
    {
        var cbs = get_elements(cb_name)
        var desc = document.getElementsByName(text_name)[0].value
        var applet = document.getElementById(this.applet_id)
        var output_hidden = document.form.elements['output_' + asset_name]
        var paths = new Array()
        
        var cbs_values = cbs.get_value().split('||')
        output_hidden.value = cbs_values.length + " file(s) selected for Publish"
             + "<br/><br/> " 
        for (var k=0; k < cbs_values.length; k++)
        {
            var cbs_value = cbs_values[k]
            var output = applet.add_checkin_path(cbs.value)
            output_hidden.value  += output  + '<br/>'
            paths.push(cbs_value) 
            
        }
        
        var root = applet.get_root()
        output = applet.commit(paths, desc, root)
        output_hidden.value  += output  + '<br/>'
    }

    
    this.file_action = function (cb_name, asset_name, func_name, action) 
    {
        var cbs = get_elements(cb_name)
        var applet = document.getElementById(this.applet_id)
        var output_hidden = document.form.elements['output_' + asset_name]

        var cbs_values = cbs.get_value().split('||')
        output_hidden.value = cbs_values.length + " file(s) selected for "
            + action + "<br/><br/> " 
        for (var k=0; k < cbs_values.length; k++)
        {
            var cbs_value = cbs_values[k]
            var output =  eval(eval("applet." + func_name + "('" 
                + cbs_value + "')"))
            output_hidden.value += output + '<br/>'
            
        }
        
    }

 
}



function TacticRepo()
{
    
    this.applet_id = "repo_applet";
    this.general_applet_id = "general_applet";
    this.upload_url = '';

    this.open_explorer = function(dir) 
    {
        spt.RepoApplet.get();
        var applet = document.getElementById(this.applet_id);

        applet.makedirs(dir);
        //applet.exec("explorer file://" + dir );
        var gen_applet = document.getElementById(this.general_applet_id);
        gen_applet.open_folder(dir);
        return;
    }


    /* tactic repo commands */
    this.set_info = function(name, path) 
    {
        spt.RepoApplet.get();
        var applet = document.getElementById(this.applet_id)

        //workspace_hidden = document.form.elements["workspaces_" + name]
        var workspace_hidden = spt.api.Utility.get_input(document, "workspaces_"+name)
        workspace_hidden.value = path

        var local = applet.get_files(path) + ""
        local = local.replace(/\\/g, "/")
        local = local.replace(/\"/g, "")
        //local_hidden = document.form.elements["local_" + name]
        var local_hidden = spt.api.Utility.get_input(document, "local_"+name)
        local_hidden.value = local

/*
        var sync = applet.get_file(path + "/", true) + ""
        sync = sync.replace(/\\/g, "/")
        sync_hidden = document.form.elements["sync_" + name]
        sync_hidden.value = sync.toLowerCase()


        var repo = applet.get_repo(path + "/", false) + ""
        repo  = repo.replace(/\\/g, "/")
        repo_hidden = document.form.elements["repo_" + name]
        repo_hidden.value = repo.toLowerCase()
*/


        // clear out the hidden values for uploading
        var upload_files = spt.api.Utility.get_input(document, "upload_files");
        if (upload_files != null)
            upload_files.value = "";
    }



    this.checkout_file = function(cb_name, asset_name)
    {
        var cbs = get_elements(cb_name)
        //var output_hidden = document.form.elements['output_' + asset_name]
        var output_hidden = spt.api.Utility.get_input(document, "output_"+asset_name)


        var cbs_values = cbs.get_values()
        output_hidden.value = cbs_values.length + " file(s) selected for checkout<br/><br/> " 
        for (var k=0; k < cbs_values.length; k++)
        {
            var cbs_value = cbs_values[k]
            
            paths = cbs_value.split('|')

            remote_path = paths[0]
            local_repo_path = paths[1]
            sandbox_path = paths[2]
            // download the file to the local repo
            applet = document.getElementById(this.general_applet_id)
            applet.download(remote_path, local_repo_path)
            applet.copy_file(local_repo_path, sandbox_path)
            

            output = "downloaded and copied to " + sandbox_path;
            output_hidden.value  += output  + '<br/>';
            
        }
    }

    this.checkin_file = function(cb_name, text_name, asset_name) 
    {
        var desc = document.getElementsByName(text_name)[0].value
        //var applet = document.getElementById(this.applet_id)
        var applet = spt.Applet.get();
        //var output_hidden = document.form.elements['output_' + asset_name]
        var output_hidden = spt.api.Utility.get_input(document, "output_"+asset_name)
        var paths = new Array()

        applet = document.getElementById(this.general_applet_id)
            
        var cbs = get_elements(cb_name)
        var cbs_values = cbs.get_values()
        for (k=0; k < cbs_values.length; k++) {
            path = cbs_values[k]
            applet.do_upload(this.upload_url, path)
            paths.push(path)
           
        }
        var upload_files = spt.api.Utility.get_input(document, "upload_files");
        upload_files.value = paths.join('|')
        output_hidden.value = "Published files (" + paths.length + "): <br/> " 
            + paths.join('<br/>')

    }

}


// Treats the server stub as a singleton and allows you to retrieve the
// same reference from various parts of the code.
//
spt.RepoApplet = function()
{
    // method to arbitrarily run system commands on the client
    //
    this.exec = function(cmd)
    {
        var applet = document.repo_applet
        applet.exec(cmd)
        return
    } 


    // method to open up file explorer to a specific directory
    //
    this.open_explorer = function(dir)
    {
        var applet = document.repo_applet
        //applet.makedirs(dir)
        applet.open_folder(dir)
        return
    } 

}



spt.RepoApplet.applet = null;
spt.RepoApplet.get = function() {
    if (this.applet == null) {
        var applet = document.createElement("applet");
        applet.setAttribute("code", "perforce.PerforceApplet");
        applet.setAttribute("archive", "Perforce-latest.jar");
        applet.setAttribute("codebase", "/context/java");
        applet.setAttribute("width", "1");
        applet.setAttribute("height", "1");
        applet.setAttribute("id", "repo_applet");

        var param = document.createElement("param");
        param.setAttribute("name", "scriptable");
        param.setAttribute("value", "true");
        applet.appendChild(param);

        document.body.appendChild(applet);
        

        this.applet = new spt.RepoApplet();

    }
    return this.applet;
}



