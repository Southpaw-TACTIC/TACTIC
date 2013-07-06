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


function PyXSI()
{
    this.xsi = new ActiveXObject( "XSI.Application" )
    this.utils = new ActiveXObject( "XSI.Utils" )
    // Verify a connection was made
    if ( this.xsi == undefined ) {
        Window.alert( "Connection to XSI failed" )
        return
    }

    this.app = this.xsi.Application

    // Call XSI's LogMessage Command
    // (Must prefix command with the XSI application object)
    this.xsi.LogMessage( "Connection to XSI established" )

    this.name           = "xsi"
    this.user           = null
    this.local_dir      = null
    this.context_url    = null
    this.base_url       = null
    this.upload_url     = null
    this.sandbox_dir    = null
    this.project_code   = null
}


PyXSI.prototype.init = function(cmd)
{
    // before every download, add the ticket and set the server
    var ticket = spt.Environment.get().get_ticket();
    this.app.SetGlobal("tactic_ticket", ticket)

    xmlrpc_server = this.base_url + "/tactic/default/XMLRPC"
    this.app.SetGlobal("tactic_xmlrpc", xmlrpc_server)

    // and set the upload server
    this.app.SetGlobal("tactic_upload", this.upload_url)

    // and set the user
    this.app.SetGlobal("tactic_user", this.user)

    // and set the tmpdir server
    tmp_dir = this.local_dir+"/temp"
    this.app.SetGlobal("tactic_tmpdir", tmp_dir)

    sandbox_dir = this.local_dir+"/temp"
    this.app.SetGlobal("tactic_sandbox_dir", sandbox_dir)
    this.app.SetGlobal("tactic_project_code", this.project_code)
    this.app.SetGlobal("tactic_base_url", this.base_url)


}

PyXSI.prototype.get_init_script = function()
{
    var list = new Array();
    
    var ticket = spt.Environment.get().get_ticket();
    list.push('Application.SetGlobal("tactic_ticket","' + ticket + '")');
    //xmlrpc_server = this.base_url + this.context_url+"/XMLRPC"
    var xmlrpc_server = this.base_url + "/tactic/default/XMLRPC";
    list.push('Application.SetGlobal("tactic_xmlrpc","' + xmlrpc_server + '")');
    list.push('Application.SetGlobal("tactic_upload","' + this.upload_url + '")');
    list.push('Application.SetGlobal("tactic_user","' + this.user + '")');
    tmp_dir = this.local_dir+"/temp"
    list.push('Application.SetGlobal("tactic_tmpdir","' + tmp_dir + '")');

    sandbox_dir = this.local_dir+"/temp"
    list.push('Application.SetGlobal("tactic_sandbox_dir","' + sandbox_dir + '")');
    list.push('Application.SetGlobal("tactic_project_code","' + this.project_code + '")');
    list.push('Application.SetGlobal("tactic_base_url","' + this.base_url + '")');
    str = list.join('\\n') + '\\n';
    return str;

}

PyXSI.prototype.get_open_script = function(file_path)
{
    str = 'Application.OpenScene("' + file_path + '", False, False)\\n';
    return str;
}

PyXSI.prototype.run_batch = function(file_path)
{
    var batch_exe = this.app.GetInstallationPath2(3) + "/Application/bin/xsibatch.exe"; 
    cmd =   batch_exe + ' -script \"' +  file_path +  '\" -lang  python';
    startDir = this.app.GetInstallationPath2(1);
    bBlocking = false; 
    this.utils.LaunchProcess('cmd  /C start cmd /K "' + cmd + '" ', bBlocking 
        , startDir);  
           
}




PyXSI.prototype.py = function(cmd)
{
    this.app.ExecuteScriptCode( cmd, "Python" )
}



/* Call a python file */
PyXSI.prototype.py_file = function()
{
    var cmd = arguments[0]
    var args = new Array()
    args.push(cmd)
    args.push("xsi")
    for (var i = 1; i < arguments.length; i++) {
        args.push(arguments[i])
    }
    //var cmd = cmd + args
    this.app.ExecuteScript(cmd, "python", "start", args)
}

PyXSI.prototype.batch_write_py_file = function()
{
    var gen_path = arguments[0];
    var cmd = arguments[1];
    
    var args = new Array()
    args.push(cmd)
    args.push("xsi")
    for (var i = 2; i < arguments.length; i++) {
        args.push(arguments[i]);
    }
    //var cmd = cmd + args
    var arg_str = "args = ['" + args.join("','") + "']\\n";
    var cmd_str =  'Application.ExecuteScript("' + cmd + '", "python", "start", args)\\n';
    cmd_str =  cmd_str.replace(/"/g, '\\"')

    this.py('file = open("' + gen_path + '", "a"); file.write("' + arg_str +'"); file.write("' + cmd_str + '"); file.close();');
}



/**
  * Download an arbitrary file to the client
  */
PyXSI.prototype.py_download = function(url, to_path)
{
    var b=to_path.match(/^(.*)[\/|\\]([^\\\/]+)$/);
    to_dir = b[1]

    cmd = "import os\nif not os.path.exists('"+to_dir+"'): os.makedirs('"+to_dir+"');"
    this.py(cmd)
    cmd = "import os, urllib, sys\nf = urllib.urlopen('"+url+"');   file = open('"+to_path+"', 'wb');    file.write(f.read());    file.close();"
    this.py(cmd)

}
PyXSI.prototype.get_temp_path = function(prefix)
{
    var dir =  this.app.ActiveProject.Path;
    dir = dir.replace(/\\/g, '/');
    var path = dir + '/TacticTemp/' + prefix ;
    var ext = '.scn';
    var tmp = new Array();
    tmp.push(path);
    tmp.push(ext);
    return tmp;

}

PyXSI.prototype.batch_write_cbk = function(bvr, values, kwargs)
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
        "{'search_type': '" + bvr.search_type + "'}, values=" + values_str  + ")");
    cmd_list.push('if rtn:');
    cmd_list.push('    print');
    cmd_list.push("    print '%s' %rtn.get('description')");
    cmd_str = cmd_list.join(app.linesep); 
    this.batch_write(bvr.batch_path, cmd_str, {write_mode: 'a'});
}

PyXSI.prototype.linesep = '\\n';
// write a string to a batch file
PyXSI.prototype.batch_write = function(batch_path, cmd, kwargs)
{
    var cmd_str = cmd;
    cmd_str =  cmd_str.replace(/"/g, '\\"')

    var write_mode = kwargs.write_mode;
    this.py('file = open("' + batch_path + '", "' + write_mode + '"); file.write("' 
        + cmd_str + '\\n"); file.close();');
}

