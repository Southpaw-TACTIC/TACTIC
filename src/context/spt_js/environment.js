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
    this.site = null;
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
    this.libraries = {};
    this.kiosk_mode = false;
    this.master_enabled = false;
    this.master_url = null;
    this.master_login_ticket = null;
    this.master_project_code = null;
    this.master_site = null;

    // by default, look at the browser
    if (typeof(document) != 'undefined') {
        var location = document.location;
        var port = location.port;
        this.server_url = location.protocol + "//" + location.hostname;
        if (port)
            this.server_url = this.server_url + ':' + port
    }



    this.set_site = function(site) {
        if (site) {
            this.site = site;
        }
    }
    this.get_site = function() {
        return this.site;
    }


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


    this.add_library = function(library) {
        this.libraries[library] = true;
    }
    this.get_libraries = function() {
        return this.libraries;
    }
    this.has_library = function(library) {
        var state = this.libraries[library];
        if (!state) {
            return false;
        }
        else {
            return true;
        }
    }
   
    this.set_kiosk_mode = function(mode) {
        if (mode == 'true' || mode == true) 
            this.kiosk_mode = true;
    }
    this.get_kiosk_mode = function() {
        return this.kiosk_mode;
    }

    this.set_master_enabled = function(mode) {
        if (mode == 'true' || mode == true) {
            this.master_enabled = true;
        }
    }
    this.get_master_enabled = function() {
        return this.master_enabled;
    }

    this.set_master_url = function(url) {
        this.master_url = url;
    }
    this.get_master_url = function() {
        return this.master_url;
    }

    this.set_master_login_ticket = function(ticket) {
        this.master_login_ticket = ticket;
    }
    this.get_master_login_ticket = function() {
        return this.master_login_ticket;
    }

    this.set_master_project_code = function(code) {
        this.master_project_code = code;
    }
    this.get_master_project_code = function() {
        return this.master_project_code;
    }

    this.set_master_site = function(site) {
        if (site) {
            this.master_site = site;
        }
    }
    this.get_master_site = function() {
        return this.master_site;
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
        if (typeof(document) != 'undefined') {
            var value = document.cookie.match('(?:^|;)\\s*' + key.replace(/([-.*+?^${}()|[\]\/\\])/g, '\\$1') + '=([^;]*)');
                    return (value) ? decodeURIComponent(value[1]) : null;
        }
        else return null;
    }

    this.get_widget_server_url = function(param_dict) {

        var location = window.location;
        var base = location.protocol + "//" + location.host;

        var url = base + '/tactic/default/WidgetServer/?project=' + this.project_code +'&';

        if (this.site != "default" && this.site != null)
        {
            url = base + '/tactic/' + this.site + '/default/WidgetServer/?project=' + this.project_code +'&';
        }

        for (param in param_dict)
            url += param + '=' + param_dict[param] + '&';
            
        return url
    }



}



spt.Environment._environment = null;
spt.Environment.get = function() {
    if (this._environment == null) {
        this._environment = new spt.Environment();
    }
    return this._environment;
}

