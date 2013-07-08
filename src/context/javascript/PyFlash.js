/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 */ 


function PyFlash() 
{
    this.server_url     = null
    this.upload_url     = null
    this.context_url    = null
    this.user           = null
    this.local_dir      = null
    // not used for now, let it upload forever
    // it will be disabled in the applet
    this.max_publish_time  = 6000000
    this.stage_mode = false
    this.cmd = ''

    /* executes flash */
    this.run_flash = function()
    {
        var exec_path = this.local_dir + "/temp/run.jsfl"
        
        spt.Applet.get()
        var applet = document.general_applet
        var content = 'x=1'
        applet.create_file(exec_path, content)
        if (applet.is_windows())
            applet.exec(exec_path, false)
        else
            // for Mac OS X
            applet.exec("/usr/bin/open " + exec_path , false)
        // wait for 1 second
        Common.pause(1000)
       
    }

    this.close_docs = function()
    {
        this.run_flash()
        var exec_path = this.local_dir+"/temp/exec.jsfl"
        spt.Applet.get()
        applet = document.general_applet

        cmd = "var docs = fl.documents; for (var k=0; k < docs.length; k++ ) \n"
        cmd += "{ docs[k].close(false) }"
        applet.create_file(exec_path, cmd)
        
        applet.exec(exec_path)
    }   

   
    /* open a folder in the current OS */
    this.open_exp = function(sandbox_path) 
    {
        spt.Applet.get()
        applet = document.general_applet
        applet.makedirs(sandbox_path)
        applet.open_folder(sandbox_path)
        return
    }

     /* copy a list of comma-separated filenames delimited by '='*/
    this.copy = function(filenames) 
    {
        spt.Applet.get()
        applet = document.general_applet
        for (var i=0; i < arguments.length; i++)
        {
            var groups = arguments[i].split('=')
            var src_path = this._get_publish_path() + "/" + groups[0]
               
            var dest_path = groups[1]
            applet.copy_file(src_path, dest_path)
        } 
    }
    /* function to load an asset into flash */
    this.load = function(url, to_path, asset_code, sandbox_path, tmpl_url, tmpl_to_path, progress_id, load_mode_id, prefix_mode_id)
    {

        spt.Applet.get()
        applet = document.general_applet
        if (applet == null)
        {
            alert("Please reload the page!")
            return
        }

        // set the message to the browser 
        var elem = document.getElementById(progress_id)
        if (elem)
            elem.innerHTML = "loading. . ."

        // dynamically get the load mode and prefix mode from the interface

        // HACK: if load_mode_id is either merge or simple, then use that as
        // the load mode instead of looking and a form element
        var load_mode = null
        if (load_mode_id == "merge" || load_mode_id == "simple" )
            load_mode = load_mode_id
        else
            load_mode = document.form.elements[load_mode_id].value

        var prefix_mode = document.form.elements[prefix_mode_id].checked

        // download the necessary jsfl files
        load_jsfl = "load2.jsfl"
        this.download_jsfl(load_jsfl)
        this.download_jsfl("common.jsfl")

        // post loading script
        // FIXME: disable this for now
        //this.download_jsfl("post_load_asset.jsfl", true)


        var log_file = this.local_dir + "/temp/actionLog.txt"
     
        // download the asset file and the template
        // lazy download is set to true
        var lazy_download = true
        applet.download_thread(url, to_path, lazy_download)
        progress = new DownloadProgress(applet, url)
        progress.show()

        applet.download(tmpl_url, tmpl_to_path)

        // prerun flash
        this.run_flash()

        // include the common.jsfl
        this.add_jsfl(load_jsfl, 'include', 'common.jsfl', this.local_dir + '/JSFL')
        // initialize the session for this asset
        this.add_jsfl(load_jsfl, 'init_session', load_mode, prefix_mode, log_file, sandbox_path)

        this.add_jsfl(load_jsfl, 'load_asset', to_path, tmpl_to_path, asset_code)


        // test
        //this.run_jsfl(load_jsfl, 'import_leica', '', tmpl_to_path, 1, 10)
        /*
        this.download_jsfl("render.jsfl")
        this.add_jsfl("render.jsfl", 'include', 'common.jsfl', this.local_dir + '/JSFL')
        this.add_jsfl("render.jsfl", 'render_layer', "BG", "png", "C:/sthpw/render/", log_file)
        */

        this.run_jsfl()
        if (applet.find_in_file(log_file, '[' + asset_code + ']'))
        {
            // post hiding script
            progress.hide('$(' + progress_id + ').innerHTML = ""');
        }
        applet.remove_file(log_file);
        
        
    }


    // FIXME: calling function "import" breaks IE
    this.ximport = function(url, to_path, asset_code, sandbox_path, tmpl_url, tmpl_to_path, progress_id)
    {
        
        spt.Applet.get()
        applet = document.general_applet
        if (applet == null)
        {
            alert("Please reload the page!")
            return
        }

        // set the message to the browser 
        var elem = document.getElementById(progress_id)
        if (elem)
            elem.innerHTML = "importing. . ."

        // download the necessary jsfl files
        load_jsfl = "load2.jsfl"
        this.download_jsfl(load_jsfl)
        this.download_jsfl("common.jsfl")


        var log_file = this.local_dir + "/temp/actionLog.txt"
     
        // download the asset file and the template
        // lazy download is set to true
        var lazy_download = true
        applet.download_thread(url, to_path, lazy_download)
        progress = new DownloadProgress(applet, url, 'Downloading')
        progress.show()

        applet.download(tmpl_url, tmpl_to_path)

        // prerun flash
        this.run_flash()

        // include the common.jsfl
        this.add_jsfl(load_jsfl, 'include', 'common.jsfl', this.local_dir + '/JSFL')
        // initialize the session for this asset
        this.add_jsfl(load_jsfl, 'init_session', '','', log_file, sandbox_path)

        this.add_jsfl(load_jsfl, "import_asset", to_path, tmpl_to_path, asset_code)

        this.run_jsfl()

        if (applet.find_in_file(log_file, '[' + asset_code + ']'))
        {
            // post hiding script
            progress.hide('$(' + progress_id + ').innerHTML = ""')
        }
        applet.remove_file(log_file)
        
    }
   
     /* function to download an asset into the local repo */
    this.download = function(url, to_path, asset_code, progress_id)
    {

        spt.Applet.get()
        applet = document.general_applet
        if (applet == null)
        {
            alert("Please reload the page!")
            return
        }
        var log_file = this.local_dir + "/temp/actionLog.txt"
    

        // set the message to the browser 
        var elem = $(progress_id)
        if (elem)
            elem.innerHTML = "downloading. . ."

        // download the asset file
        // lazy download is set to true
        var lazy_download = true

        // this has to be called before DownloadProgres
        applet.download_thread(url, to_path, lazy_download)
        progress = new DownloadProgress(applet, url, "Downloading " + asset_code)
        progress.show()

        // post hiding script
        progress.hide('$(' + progress_id + ').innerHTML = ""')
        // a slight pause is inserted so that if a file has been downloaded 
        // before, the progress will stay on screen for half a second
        Common.pause(600)
    }

    /* get the publish path with user name */
    this._get_publish_path = function()
    {
        return this.local_dir + "/publish/" + this.user
    }

    this.publish = function(asset_code, progress_id)
    {
        ret_val = true

        publish_path = this._get_publish_path()
        spt.Applet.get()
        applet = document.general_applet
        
        Overlay.display_progress('Publishing', false)
        var elem = document.getElementById(progress_id)
        if (elem)
            elem.innerHTML = "publishing. . ."


        // download the necessary jsfl files
        jsfl = "publish2.jsfl"
        this.download_jsfl(jsfl)
        this.download_jsfl("common.jsfl")

        var log_file = this.local_dir + "/temp/actionLog.txt"
      
        // include the common.jsfl
        this.add_jsfl(jsfl, 'include', 'common.jsfl', this.local_dir + '/JSFL')
        this.add_jsfl(jsfl, "publish_asset", asset_code, publish_path,
            log_file)


        this.run_jsfl()
      
        // pause for the publish to finish
        if (applet.find_in_file(log_file, '[' + asset_code + ']'))
        {
            applet.do_upload(this.upload_url, publish_path 
                + "/" + asset_code + ".fla")
            applet.do_upload(this.upload_url, publish_path 
                + "/" + asset_code + ".swf")
            applet.do_upload(this.upload_url, publish_path 
                + "/" + asset_code + ".png")
            applet.do_upload(this.upload_url, publish_path 
                + "/" + asset_code + ".xml")


            // DEPRECATED: requests are done 1 at a time now
            // if this is stage mode, then all the files are assembled together
            // in one shot
            /*
            var values = null
            if (this.stage_mode == true) {
                values = document.form.upload_files.value
                if (values != "")
                    values = values + "|"
            }
            else {
                values = ""
            }
            */
            var values = ""
            
            document.form.upload_files.value = values + asset_code+".fla|" + asset_code+".swf|" + asset_code+".png"
        }
        else
        {
            alert("Publish of [" + asset_code + "] failed. " 
                    + applet.get_file_content()) 
            ret_val = false
        }

        // reset the display
        if (elem)
            elem.innerHTML = ""

        // use a nice big fat global variable
        Overlay.hide_progress()
        comment_bubble.close()
        applet.remove_file(log_file)

        return ret_val
    }



    this.post_stage_script = function()
    {
        // download the necessary jsfl files
        jsfl = "load2.jsfl"
        this.download_jsfl(jsfl)
        this.download_jsfl("common.jsfl")

        // include the common.jsfl
        this.add_jsfl(jsfl, 'include', 'common.jsfl', this.local_dir + '/JSFL')
        this.add_jsfl(jsfl, "post_stage")
        
        this.run_jsfl()
    }



    // trigger multiple actions based on checked checkboxes.
    // action is either "load", "download", or "publish" 
    this.multi_action = function(action, checkbox_name)
    {
        if (action =='load')
        {       
            this.run_flash()
        }
        var cbs = document.getElementsByName(checkbox_name) 
        var count = 0   
        for (var i=0; i < cbs.length; i++)
        {
            var cb = cbs[i]
            
            if (cb.checked)
            {
                count++
                EventContainer.get().call_event(cb.value + '_' + action)
                
            }
        }
        if (count==0)
            alert("To " + action + " mulitple layers, " 
                + "please first check the corresponding checkboxes on the left.")
        else if ( action == 'publish' )
        {
            document.form.submit()
        }
    }
    
    /*
     * if set to true, prefix will be prepended to layers and file will
     * close after publish
     */
    this.set_stage_mode = function(mode)
    {
        this.stage_mode = mode
    }

 
    /*
     * downloads a jsfl file through the applet to the client
     */
    this.download_jsfl = function(file_name, from_context)
    {
        spt.Applet.get()
        var applet = document.general_applet
        var jsfl_url = this.server_url + "/context/JSFL/" + file_name
        if (from_context == true)
            jsfl_url = this.context_url + "/JSFL/" + file_name
        var jsfl_to_path = this.local_dir + "/JSFL/" + file_name
        applet.download(jsfl_url, jsfl_to_path);
        return jsfl_to_path
    } 

  
    /*
     * arg0 = jsfl_file_name
     * arg1 = function_name
     * args[2..] = arguments to the fucntions
     */
    this.add_jsfl = function()
    {
        var file_name = arguments[0]
        var file_path = this.local_dir + "/JSFL/" + file_name

        var cmd = "fl.runScript("

        var args = new Array()
        args.push("'file:///" + file_path + "'")

        for (var i = 1; i < arguments.length; i++)
        {
            argument = arguments[i]
            if (typeof(argument)=="number" || typeof(argument)=="boolean")
            {
                args.push(argument + "")
            }
            else
                args.push(" \"" + arguments[i] + "\"")
        }

        cmd += args.join(", ") + ");\n"
        this.cmd += cmd
    }

    this.run_jsfl = function()
    {
        // actually run the script
        spt.Applet.get()
        var applet = document.general_applet
        var exec_path = this.local_dir+"/temp/exec.jsfl"
        applet.create_file(exec_path, this.cmd)
        if (applet.is_windows())
            applet.exec(exec_path)
        else
            // for Mac OS X
            applet.exec("/usr/bin/open " + exec_path)
        this.cmd = ''
    }
    
    
    //client code
    this.build = function(project_code, shot_input_name, audio_input_name)
    {
        shot_codes = get_elements(shot_input_name).get_values('code')
        audio = get_elements(audio_input_name).get_value()
        with_audio = 'false'
        if (audio)
            with_audio = 'true'
        if (shot_codes.length == 0)
        {
            alert('Please select a shot')
            return
        }
        spt.Applet.get()
        var applet = document.general_applet
        py_url = this.server_url + "/context/client/delegator.py.xx"
        zip_url = this.server_url + "/context/client/tactic.zip"
        var py_url_to_path = this.local_dir + "/temp/delegator.py.xx"
        var zip_url_to_path = this.local_dir + "/temp/tactic.zip"
        applet.download(py_url, py_url_to_path)
        applet.download(zip_url, zip_url_to_path)

        var exec_path = 'python ' + py_url_to_path + ' ' + project_code +  
            " flash_test2.build " + with_audio + ' ' + shot_codes.join(' ')
        applet.exec(exec_path, false)
    }
}



/* FlashPlayer related object and functions */
// fs_player is a global var

function auto_start()
{
    if (fs_player)
        fs_player._auto_start()
}


function FlashPlayer(main_swf)  
{
    this.main_swf = main_swf
    this.icon_div_id = "icon_div"
    this.movies = new Array()
    this.icons = new Array()
    this.current_idx = 0
    this.is_auto_start = true
    this.is_started = false
    this.auto_start_id = 0

    this.add_movie = function(movie_name, icon_id)
    {
        this.movies.push(movie_name)
        this.icons.push(icon_id)
    }

    this.get_flash_movie_obj = function(movieName) 
    {
        if (window.document[movieName]) 
        {
            return window.document[movieName];
        }
        if (navigator.appName.indexOf("Microsoft Internet")==-1)
        {
            if (document.embeds && document.embeds[movieName])
                 return document.embeds[movieName]; 
        }
        else 
        {
            return document.getElementById(movieName);
        }
    }

    this.auto_start = function()
    {
        this.auto_start_id = setInterval('auto_start()', 1000)
    }
    
    this._auto_start = function()
    {
        if (this.is_auto_start && this.is_started == true)
        {
            this.set_player_width()
            this.set_source_width()
            this.load_movie(this.movies[0], 0)
            this.is_started = false
            // clear the setInterval
            clearInterval(this.auto_start_id)
        }
    }

    this.set_ready = function()
    {
        this.is_started = true
        fs_player = this
        
    }
        
    this.load_movie = function(clip_name, idx)
    {
        if (idx != null)
            this.current_idx = idx
        var flash_movie = this.get_flash_movie_obj(this.main_swf)
        flash_movie.load_movie(clip_name, idx + 1)
    
        this._position_pointer(idx)
        
              
    }

    this._position_pointer = function(idx)
    {
        var thumb = document.getElementById(this.icons[idx])
        var y_pos = Common.find_pos_y(thumb)
        var icon = document.getElementById('playing')  

        var icon_div = document.getElementById(this.icon_div_id)
        var scroll_top = icon_div.scrollTop
             
        icon.style.top = y_pos - scroll_top
        icon.style.left = 15
        set_display_on('playing')

    }
    
    
    this.pause_movie = function()
    {
        var flash_movie = this.get_flash_movie_obj(this.main_swf)
        flash_movie.pause_movie()
   
    }
    this.play_movie = function()
    {
        var flash_movie = this.get_flash_movie_obj(this.main_swf)
        flash_movie.play_movie()
   
    }

    this.set_player_width = function(width)
    {
        var flash_movie = this.get_flash_movie_obj(this.main_swf)
        if (width == null)
             width = get_elements('fs_size_select').get_value().split(',')[0]

        flash_movie.set_player_width(parseInt(width))
   
    }

    this.set_source_width = function(width)
    {
        var flash_movie = this.get_flash_movie_obj(this.main_swf)
        if (width == null)
            width = get_elements('src_size_select').get_value().split(',')[0]
        
        flash_movie.set_source_width(parseInt(width))
   
    }

    // this is called by ActionScript
    this.switch_movie = function()
    {
        this.current_idx  += 1
        // increment the index
        if (this.current_idx >= this.movies.length)
            this.current_idx = 0
        if (this.movies.length > 0)
            this.load_movie(this.movies[this.current_idx], this.current_idx)
    }

        
    this.write_info = function(str)
    {
        document.getElementById('fs_info').innerHTML = str
    }

    /* resize the window only if bigger res for the player is chosen */
    this.resize_win = function(select_name)
    {
        var value = get_elements(select_name).get_value() 
        values = value.split(',')
        width = parseInt(values[0]) + 230
        height = parseInt(values[1]) + 180
        if (width > 950)
            window.moveTo(0,0)
        
        window.resizeTo(Math.max(950, width), Math.max(640, height))
    }  


}



