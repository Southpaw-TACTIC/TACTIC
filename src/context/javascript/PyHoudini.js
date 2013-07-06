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


function PyHoudini()
{
    /*this.hscript("openport 10389")*/
    this.name           = "houdini"
    this.user           = null
    this.local_dir      = null
    this.context_url    = null
    this.base_url       = null
    this.upload_url     = null
    this.sandbox_dir    = null
    this.project_code   = null
}


PyHoudini.prototype.init = function(cmd)
{
    // before every download, add the ticket and set the server
    ticket = spt.Environment.get().get_ticket();
    this.hscript('set -g tactic_ticket = "'+ticket+'"')

    this.has_connect_error = false
    
    // and set the xmlrpc serverfile:///C:/Documents%20and%20Settings/remko/Desktop/ttt.html
    var xmlrpc_server = this.base_url + "/tactic/default/XMLRPC"
    this.hscript('set -g tactic_xmlrpc = "'+xmlrpc_server+'"')

    // and set the upload server
    this.hscript('set -g tactic_upload = "'+this.upload_url+'"')

    // and set the user
    this.hscript('set -g tactic_user = "'+this.user+'"')

    // and set the tmpdir server
    tmp_dir = this.local_dir+"/temp"
    this.hscript('set -g tactic_tmpdir = "'+tmp_dir+'"')

    // TODO: this should be set externally
    sandbox_dir = this.local_dir+"/temp"
    this.hscript('set -g tactic_sandbox_dir = "'+sandbox_dir+'"')
    this.hscript('set -g tactic_project_code = "' + this.project_code +'"')
    this.hscript('set -g tactic_base_url = "' + this.base_url + '"')

}


PyHoudini.prototype.hscript = function(cmd)
{
    var port = 13000;
    if (this.has_connect_error)
        return;
    var result = spt.Applet.get().command_port('127.0.0.1', port, cmd)
    var error = result[1]
    if (error != '' && !this.has_connect_error)
    {
        //alert("Java connector chosen in TACITC Preferences. Connect Error: " + 
        this.has_connect_error = true;
        alert("Cannot connect to port 127.0.0.1:" + port + "\nRun hscript in Textport on start-up: openport " + port + "; You need to refresh this page.");
        
    }
    return result[0]
}



PyHoudini.prototype.py = function(cmd)
{
    cmd = 'python -c "'  + cmd + '"';
    this.hscript(cmd);
    //RunPythonStatements(cmd)

    // Houdini 8
    /*
    //var cmd = 'openport -a -p -r "pythonw -c \\"' + cmd + '\\""'
    var cmd = 'openport -a -p -r "$HFS/python/bin/python -c \\"' + cmd + '\\""'
    RunHCommand(cmd)
    */
}



/* Call a python file */
PyHoudini.prototype.py_file = function()
{
    var args = "'" + arguments[0] + "', 'houdini'"
    for (var i = 1; i < arguments.length; i++) {
        args = args + ", '" + arguments[i] + "'"
    }

    path = this.local_dir + "/download"
    var cmd = "python -c \"import sys; sys.path.insert(0,'"+path+"'); import delegator; delegator.start(" + args + ")\""
    //RunPythonStatements(cmd)
    this.hscript(cmd)

}







/**
  * Download an arbitrary file to the client
  */
PyHoudini.prototype.py_download = function(url, to_path)
{
    var b=to_path.match(/^(.*)[\/|\\]([^\\\/]+)$/);
    to_dir = b[1]

    cmd = "import os, urllib, sys;"
    this.py(cmd)
    cmd = "if not os.path.exists('"+to_dir+"'): os.makedirs('"+to_dir+"');"
    this.py(cmd)
    cmd = "f = urllib.urlopen('"+url+"');   file = open('"+to_path+"', 'wb');    file.write(f.read());    file.close();"
    this.py(cmd)

}

PyHoudini.prototype.get_init_script = function()
{
    return null;
}
