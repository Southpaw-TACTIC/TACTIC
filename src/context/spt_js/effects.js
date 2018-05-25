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



Effects = new function()
{

    this.tip= function() 
    {
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
        if (time == null)
            time = 1000;
         // fading out from 0.8 to 0

        hide = new Fx.Tween(id,  {
        property: 'opacity', 
        duration: time, 
        onComplete: function()
            {
              // by using document.id(id).setStyle('display','none'), 
              // the reference to this object is guaranteed
              if (typeof(on_complete_script) =='string') {
                  eval(on_complete_script); 
              } else {
                  on_complete_script(id);
              }
            }
            });
        hide.start(document.id(id).getStyle('opacity'), 0);
        // hide it completely
        
    }

    this.fade_in = function(id, time)
    {
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
        var dur = 100
        if (time)
            dur = time
        var my_morph = new Fx.Morph(id, {duration: dur});
        my_morph.start(css1);
        
    }        

    /* a simplified css_morph, changing just one property of the css*/ 
    this.css_simple_morph = function(id, class1, style_name, time)
    {
        var morph = new Fx.Morph(id)
        var dict = morph.search('.'+class1)
        var fx = new Fx.Tween(id,  {duration: time, wait: false, property: style_name})
        var value = dict[style_name]
        fx.start(value)
       
    }
   
    this.bg_color = function(id, class1)
    {
        this.css_simple_morph(id, class1, 'backgroundColor', 60)
    }

    this.color = function(id, class1)
    {
        this.css_simple_morph(id, class1, 'color', 100)
    }

    this.blink = function(obj_id, clear_id)
    // add blinking effect to an object
    {
        
        var elem = document.id(obj_id)
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
        var obj = document.id(obj_id)
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
                            document.id(obj_id + "_inner").setStyle('opacity', 0);
                        },
                    'complete': function()
                        {   
                            //Effects.fade_out(obj_id, 300)
                            set_display_off(obj_id);
                            document.id(obj_id + "_inner").setStyle('opacity', 1);
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
        var elem = document.id(obj_id);
        var body = document.id(obj_id + '_body');
        if (!body)
            return ;
        body.innerHTML= msg;
        [obj_id, obj_id+'_overflow'].each(function(el) {
            if (!document.id(el))
                return;
            var slide = new Fx.Slide(el, {mode: 'horizontal'});
            slide.slideIn();
        });
    }
    this.slide_out = function(obj_id)
    {
        var elem = document.id(obj_id);
        [obj_id, obj_id+'_overflow'].each(function(el) {
            if (!document.id(el))
                return;
            var slide = new Fx.Slide(el, {mode: 'horizontal'});
            slide.slideOut();
        });


    }
    
    this.slide_hide = function(obj_id)
    {
        var elem = document.id(obj_id);
        var slide = new Fx.Slide(obj_id, obj_id + '_overflow', {mode: 'horizontal'});
        slide.hide('horizontal');
        set_display_on(obj_id);
    }

}
    



