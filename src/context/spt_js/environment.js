// -----------------------------------------------------------------------------
//
//  Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//  PROPRIETARY INFORMATION.  This software is proprietary to
//  Southpaw Technology Inc., and is not to be reproduced, transmitted,
//  or disclosed in any way without written permission.
//   
// 

// ---------------------------------------------------------------------
// Global environment
// ---------------------------------------------------------------------


/* *****************************************************************************

    SPT Environment
    ---------------

********************************************************************************
*/


spt.Environment = function() {
    this.project_code = null;
    //this.url = null;
    this.user = null;
    this.user_id = null;
    this.login_groups = [];
    this.ticket = null;
    this.palette = null;
    this.transfer_mode = null;
    this.client_handoff_dir = null;
    this.client_repo_dir = null;
    this.colors = {};

    // by default, look at the browser
    var location = document.location;
    var port = location.port;
    this.server_url = location.protocol + "//" + location.hostname;
    if (port)
        this.server_url = this.server_url + ':' + port


    this.set_project = function(project_code) {
        this.project_code = project_code;
    }
    this.get_project = function(project_code) {
        return this.project_code;
    }

    this.set_user = function(user) {
        this.user = user;
    }
    this.get_user = function() {
        return this.user;
    }

    this.set_user_id = function(user_id) {
        this.user_id = user_id;
    }
    this.get_user_id = function() {
        return this.user_id;
    }
    this.set_login_groups = function(login_groups) {
        this.login_groups = login_groups;
    }
    this.get_login_groups = function() {
        return this.login_groups;
    }

    this.set_client_handoff_dir = function(dir) {
        this.client_handoff_dir = dir;
    }
    this.get_client_handoff_dir = function(dir) {
        return this.client_handoff_dir;
    }

    this.set_client_repo_dir = function(dir) {
        this.client_repo_dir = dir;
    }
    this.get_client_repo_dir = function(dir) {
        return this.client_repo_dir;
    }

    this.set_transfer_mode = function(transfer_mode) {
        this.transfer_mode = transfer_mode;
    }
    this.get_transfer_mode = function() {
        return this.transfer_mode;
    }


    this.set_palette = function(palette) {
        this.palette = palette;
    }
    this.get_palette = function() {
        return this.palette;
    }


    this.set_colors = function(colors) {
        this.colors = colors;
    }
    this.get_colors = function() {
        return this.colors;
    }





    /*
     * Url methods
     */
    this.set_server_url = function(server_url) {
        if (! server_url.match(/^http(s?):/)) {
            server_url = "http://" + server_url;
        }
        this.server_url = server_url;
    }
    this.get_server_url = function() {
        return this.server_url;
    }

    this.get_api_url = function(server_name) {
        if (typeof(server_name) == 'undefined') {
            return this.server_url + "/tactic/default/Api/"
        }
        else if (server_name.substr(0, 4) == "http") {
            return server_name + "/tactic/default/Api/"
        }
        else {
            return "http://" + server_name + "/tactic/default/Api/"
        }
    }


    this.is_local_url = function() {
        if (this.server_url.test(/\/\/localhost/) ||
                this.server_url.test(/\/\/127\.0\.0\.1/) ) {
            return true;
        }
        return false;
    }


    this.set_ticket = function(ticket) {
        this.ticket = ticket;
    }

    this.get_ticket = function() {
        if (this.ticket != null) {
            return this.ticket;
        }

        var ticket = this.read_cookie('login_ticket');
        return ticket;
    }

    this.read_cookie = function(key) {
        var value = document.cookie.match('(?:^|;)\\s*' + key.escapeRegExp() + '=([^;]*)');
		return (value) ? decodeURIComponent(value[1]) : null;
    }

}



spt.Environment._environment = null;
spt.Environment.get = function() {
    if (this._environment == null) {
        this._environment = new spt.Environment();
    }
    return this._environment;
}

spt.Environment.get_widget_server_url = function(project_code, param_dict) {
    var location = window.location;
    var base = location.protocol + "//" + location.host;
    
    var url = base + '/tactic/default/WidgetServer/?project=' + project_code +'&';
    for (param in param_dict)
        url += param + '=' + param_dict[param] + '&';
        
    return url
}

