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



Overlay = new function()
{
    //For Firefox to draw shadow patches
    this.makeCanvasCorner = function(shadow_on)
    {

        alert("Overlay.js is deprecated");

        // $$ or document.getElementsByClass does not return the divs properly
        // weirdness in Mootools 1.1
        var aModule = document.getElements('.module', true);
    
        var makeCorner = function(dModule, shadow_on)
        {
            
            //var dContainer = YUD.getElementsByClassName('container','div', dModule)[0];
            var dContainer = dModule.getElement('.container');
            var sBgColor = dContainer.getStyle('backgroundColor');
            dModule.addClass('module-has-canvas-shadow');
          
            // this enables the transparency effect
            dContainer.style.background='transparent';
            
            var nOpac = 0.1;
            
            var patch_num = 4;
            if (!shadow_on)
                patch_num = 1 

            // draw 3 shadow patches
            for(var s=1; s < patch_num; s++)
            {
                var oShadow = document.createElement('div');
                oShadow.className = 'shadow-patch';
                var oShadowStyle= oShadow.style;
                oShadowStyle.position = 'absolute';
                oShadowStyle.zIndex = -s;
                oShadowStyle.top = s*2 - 6  + 'px';
                oShadowStyle.left = s*2  - 2 + 'px';
                oShadowStyle.background = sBgColor ;
                
                oShadowStyle.opacity = nOpac ;            
                dModule.appendChild(oShadow);  
                
            } 
            
        }
       
        // call makeCorner
        for (var i=0;i<aModule.length;i++)
        {
             makeCorner(aModule[i], shadow_on);
        }
       
    }



    /* For Firefox to add shadow and round corner effect */
    this.init = function(shadow_on)
    {
        if (isIE())
             return
        var canvas =  document.createElement('canvas');
        if( canvas /*&& canvas.getContext && (document.getBoxObjectFor )*/)
        {
             this.makeCanvasCorner(shadow_on)
        }
    }    
    
    this.taller = function(iframe_name, shad_name)
    {
        var elem = document.getElementById(iframe_name);
        var h = parseFloat(document.getBoxObjectFor(elem).height) + 100;  
        
        elem.style.height = h+ 'px'; 
      
    }
   
    this.shorter = function(iframe_name, shad_name)
    {
        
        var elem = document.getElementById(iframe_name);
        h = parseFloat(document.getBoxObjectFor(elem).height) - 100;  
        
        if (h < 100)
            return
        elem.style.height = h+ 'px'; 
    
    }
    
    this.pause = function(millis)
    {
        date = new Date();
        var curDate = null;

        do { var curDate = new Date(); }
        while (curDate-date < millis);
        
    }

    // display a progress indicator as an overlay
    this.display_progress = function(message, show_meter)
    {
        if (message != '')
        {
            var text = document.getElementById('tactic_busy_msg')
            text.innerHTML = message
        }
        var busy = $('tactic_busy')
        if (busy.getStyle('display') != 'none')
            return

        set_display_on('tactic_busy')
        busy.setStyle('visibility','visible') 
        busy.setOpacity(0.8) 
       
        if (show_meter)
        {
            this.display_meter(true)
            this.display_icon(false)
        }
        else
        {
            
            this.display_meter(false)
            this.display_icon(true)
        }
        
    }

    // hide the progress indicator
    this.hide_progress = function(on_complete_script)
    {
        Effects.fade_out('tactic_busy', null, on_complete_script)
      
    }

    this.display_icon= function(show)
    {
        if (show)
            set_display_on('tactic_progress_icon')
        else
            set_display_off('tactic_progress_icon')
    }

    this.display_meter = function(show)
    {
        if (show)
            set_display_on('tactic_progress_meter')
        else
            set_display_off('tactic_progress_meter')
            
    }
    // update the progress meter 
    this.update_progress = function(percent, file_size)
    {
        if (file_size == null)
             file_size = 0

        var element = document.getElementById('tactic_progress_value')
        var percent_value = Common.validate_int(percent) ? percent + " %" : percent
        var file_size_label = 'n/a'
        if (file_size)
            file_size_label = file_size.toFixed(1)
        element.innerHTML = percent_value + " <span style='padding-left: 40px'> " 
            + file_size_label + " Mb </span>"

        element = document.getElementById('tactic_progress_bar')
        var ref_elem = document.getElementById('tactic_progress_ref_bar')
        var ref_width = ref_elem.style.width
        
        ref_width = parseInt(ref_width.replace(/px|em/,''))
        if (percent >= 0)
            element.style.width = parseInt(ref_width * percent/100) + 'px'   
        
    }

}   

Move = new function()
{
    this.drag = function(obj_id, resize_obj_id)
    {
        var dragged = $(obj_id)
        var resized = $(resize_obj_id)
        var height = 0
        if (resized)
            height = resized.getStyle('height')
        
        // designate an element to be the dragging handle
        var handle_id = obj_id + "_handle"
        /*
        new Drag(dragged, {
        handle: handle_id,
        onStart: function(){ if (resized) resized.setStyle('height','40px')},
        onComplete: function(){ if (resized) resized.setStyle('height', height)}
        })*/
    }
}
    
/* A download progress class. Call .show() and .hide() to display 
    and hide the overlay*/ 
function DownloadProgress(applet, url, custom_msg)
{
    this.applet = applet
    this.url = url

    this.show = function()
    {
        // applet is an instance of the General Applet
  
        var percent = this.applet.get_download_progress(this.url)

        var file_size = parseFloat(applet.get_file_size(this.url)) / 1048576
        Overlay.update_progress(percent, file_size) 

        var msg = 'Loading'
        if (custom_msg)
            msg = custom_msg
        Overlay.display_progress(msg, true)
        
        var is_error_free = true
        while (percent < 100)
        {
            if (percent < 0)
            {
                // -10 means exception occured in the applet 
                if (percent == -10)
                {
                    Overlay.update_progress('Exception occured.')
                    is_error_free = false
                    var error = applet.get_download_error(this.url)
                    alert(error)
                    break
                }
                Overlay.update_progress('N/A')
                break
            }
            if (is_error_free)
            {
                if (!file_size)
                    file_size = parseFloat(applet.get_file_size(this.url)) / 1048576

                percent = this.applet.get_download_progress(this.url)
                // update progress bar
                Overlay.update_progress(percent, file_size)
                Common.pause(500)
            }
            
        }

        return is_error_free
    }
   

    /* on_complete_script is optional */
    this.hide = function(on_complete_script)
    {
        Overlay.hide_progress(on_complete_script)
    }

}

Effects = new function()
{

    this.tip= function() 
    {
        alert("Overlay.js is deprecated");
        // stop using addEvent domready until memory leak issue is resolved
        //window.addEvent('domready', function(){
        return 
        var tip = new Tips($$('.tactic_tip'), {
            onShow: function(toolTip) {
                    if (!toolTip.id)
                        toolTip.id = 'tooltip'
                    var fx = new Fx.Tween(toolTip.id, {property: 'opacity', duration: 400, wait: false}).set(0);
                    fx.start(0.9);
            },
            onHide: function(toolTip) {
                    if (!toolTip.id)
                        toolTip.id = 'tooltip'
                    var fx = new Fx.Tween(toolTip.id, {property: 'opacity', duration: 400, wait: false}).set(0);
                    fx.start(0);
            },
            //className: ['main-tip', 'main-text','main-title'],
            offsets: {'x':30 , 'y': -45}
        });
 
        //});
    }

    this.fade_out = function(id, time, on_complete_script)
    {
        alert("Overlay.js is deprecated");
        if (time == null)
            time = 1000;
         // fading out from 0.8 to 0

        hide = new Fx.Tween(id,  {
        property: 'opacity', 
        duration: time, 
        onComplete: function()
            {
              // by using $(id).setStyle('display','none'), 
              // the reference to this object is guaranteed
              if (typeof(on_complete_script) =='string') {
                  eval(on_complete_script); 
              } else {
                  on_complete_script();
              }
            }
            });
        hide.start($(id).getStyle('opacity'), 0);
        // hide it completely
        
    }

    this.fade_in = function(id, time)
    {
        alert("Overlay.js is deprecated");
        if (time == null)
            time = 2000;
         // fading out from 0.8 to 0
        var hide = new Fx.Tween(id, {duration: time, 
                property: 'opacity',
                onComplete: function()
            { set_display_on(id) }});
        hide.start(0.1, 1);
        // show it completely
        
    }

    this.css_morph = function(id, css1, time)
    {
        alert("Overlay.js is deprecated");
        var dur = 100
        if (time)
            dur = time
        var my_morph = new Fx.Morph(id, {duration: dur});
        my_morph.start(css1);
        
    }        

    /* a simplified css_morph, changing just one property of the css*/ 
    this.css_simple_morph = function(id, class1, style_name, time)
    {
        alert("Overlay.js is deprecated");
        var morph = new Fx.Morph(id)
        var dict = morph.search('.'+class1)
        var fx = new Fx.Tween(id,  {duration: time, wait: false, property: style_name})
        var value = dict[style_name]
        fx.start(value)
       
    }
   
    this.bg_color = function(id, class1)
    {
        alert("Overlay.js is deprecated");
        this.css_simple_morph(id, class1, 'backgroundColor', 60)
    }

    this.color = function(id, class1)
    {
        alert("Overlay.js is deprecated");
        this.css_simple_morph(id, class1, 'color', 100)
    }

    this.blink = function(obj_id, clear_id)
    // add blinking effect to an object
    {
        alert("Overlay.js is deprecated");
        
        var elem = $(obj_id)
        // it returns false if it is not available
        if (!elem)
            return 
       
        if (isIE())
        {
            elem.setStyle('visibility','visible')
            return
        }
        var visible = elem.getStyle('visibility')
        if (clear_id != null)
        {
            clearInterval(clear_id)
            if (visible == 'hidden')
                new Fx.Tween(obj_id, 
                    {property: 'opacity', duration: 300 }).start(0, 0.8);
            return  
        }

        if (visible == 'visible')
        {
            new Fx.Tween(obj_id,
                {property: 'opacity', duration: 300, 
                    onComplete: function(){}}).start(0.8, 0);
            visible = 'hidden'
        }
        else
        {
            new Fx.Tween(obj_id,
                {property: 'opacity', duration: 300, 
                    onComplete: function(){}}).start(0, 0.8);
            
        }
        
        
    }  

    this.roll = function (obj_id, direction, obj_height)
    /* arg: direction = up | down */
    {
        alert("Overlay.js is deprecated");
        var obj = $(obj_id)
        //var effect = obj.effects({transition:Fx.Transitions.sineInOut})
        
        if (direction == 'up') // close
        {
            var tween = new Fx.Tween(obj_id,
                    {duration: 400, 
                    property: 'height',
                    transition: Fx.Transitions.Bounce.easeOut //moo1.11 fx
                    //transition: Fx.Transitions.sineInOut
                    
                    });
                    
            tween.addEvents({
                    'start': function() 
                        {   // hide inner div first if applicable
                            $(obj_id + "_inner").setStyle('opacity', 0);
                        },
                    'complete': function()
                        {   
                            //Effects.fade_out(obj_id, 300)
                            set_display_off(obj_id);
                            $(obj_id + "_inner").setStyle('opacity', 1);
                        }
                        });
            tween.start(obj.getStyle('height'), 0);
        }
        else // open
        {
            set_display_on(obj_id);
            var tween = new Fx.Tween(obj_id, 
                    {duration: 400, 
                    //transition: Fx.Transitions.Bounce.easeOut, //moo1.11 fx
                    transition: Fx.Transitions.sineInOut,
                    property: 'height' 
                    });
                    
            tween.addEvent('start', function()
                        { 
                            // show inner div first if applicable
                            //set_display_on(obj_id + "_inner");
                            Effects.fade_in(obj_id, 300);
                        });
                     
            tween.start(0, obj_height);
        }

    }
    /* slide in, out and hide functions */
    this.slide_in = function(obj_id, msg)
    {
        alert("Overlay.js is deprecated");
        var elem = $(obj_id);
        var body = $(obj_id + '_body');
        if (!body)
            return ;
        body.innerHTML= msg;
        [obj_id, obj_id+'_overflow'].each(function(el) {
            if (!$(el))
                return;
            var slide = new Fx.Slide(el, {mode: 'horizontal'});
            slide.slideIn();
        });
    }
    this.slide_out = function(obj_id)
    {
        alert("Overlay.js is deprecated");
        var elem = $(obj_id);
        [obj_id, obj_id+'_overflow'].each(function(el) {
            if (!$(el))
                return;
            var slide = new Fx.Slide(el, {mode: 'horizontal'});
            slide.slideOut();
        });


    }
    
    this.slide_hide = function(obj_id)
    {
        alert("Overlay.js is deprecated");
        var elem = $(obj_id);
        var slide = new Fx.Slide(obj_id, obj_id + '_overflow', {mode: 'horizontal'});
        slide.hide('horizontal');
        set_display_on(obj_id);
    }

}
    



