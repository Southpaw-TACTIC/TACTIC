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
String.prototype.trim = function()
{
    return this.replace(/^\s*|\s*$/g,'')
}

function isIE()
{
    var bname = navigator.appName
    if (bname == "Microsoft Internet Explorer")
        return true
    else
        return false
}

    


function submit_icon_button(name, value) 
{
    //var element = document.form.elements[name]
    var element = spt.api.Utility.get_input(document, name)
    if (element.length != undefined) {
        for (var i=0; i < element.length;i++) {
            element[i].value = value
        }
    }
    else
        element.value = value
    //document.form.submit()
}




// function to execute a command on the server
function delete_sobject( search_key, name )
{
    // get row and turn its color
    var table_row_id = "table_row_"+search_key
  
    var agree = confirm("Are you sure you want to DELETE ["  
        + name + "]?")
    if (agree) {

        //set_display_off(table_row_id)
        Effects.fade_out(table_row_id)
        return true
    }
    else
        return false
}




// function to execute a command on the server
function retire_sobject( sobject_key, name )
{
    var table_row_id = "table_row_"+sobject_key
    //var row = document.getElementById(table_row_id)

    var agree = confirm("Are you sure you want to RETIRE ["  
        + name + "]?")
    if (agree) {

        //set_display_off(table_row_id)
        Effects.fade_out(table_row_id)
        return true
    }
    else
        return false
}










/* get the absolute position of a relative element */
function get_pos(el)
{
    for ( var lx=0, ly=0; el!=null;
        lx+=el.offsetLeft, ly+=el.offsetTop, el=el.offsetParent);
    return {x:lx,y:ly}
}


/* align the absolute position of a relative element */
function align_element(source_element_name, dest_element_name)
{
     var dest_element = document.getElementById(dest_element_name)
     var source_element = document.getElementById(source_element_name)

     var pos = get_pos(source_element)

     dest_element.style.top = pos.y
     dest_element.style.left = pos.x
}


/* align an element to the current top of the page */
function align_to_top(source_element_name)
{
     var source_element = document.getElementById(source_element_name)
     var yoffset = window.pageYOffset
     if ( yoffset == undefined ) yoffset = 0
     source_element.style.top = yoffset
}


/* function to include a src script file dynamically */
function Script()
{

    this.included_files = new Array();
    
    
    this.include_dom = function(script_file)
    {
        var html_doc = document.getElementsByTagName('body').item(0)
        var js = document.createElement('script')
        js.setAttribute('language', 'javascript')
        //js.setAttribute('type', 'text/javascript')
        js.setAttribute('src', script_file)
        html_doc.appendChild(js)
        return false
    }

    this.include_once = function(script_file)
    {
        if (!this.in_array(script_file, this.included_files))
        {
            this.included_files[this.included_files.length] = script_file
            this.include_dom(script_file)
        }
    }
    
    this.in_array = function(needle, haystack)
    {
        for (var i=0; i<haystack.length; i++)
        {
            if (haystack[i] == needle)
                return true
        }
        return false
    }

}



function Annotate()
{
}



Annotate.prototype.add_new = function(event)
{
    var x = event.pageX
    var y = event.pageY
    // handle explorer
    if (x == undefined)
    {
        x = event.x
        y = event.y
    }

    // get the image that is being annotated
    var element = document.getElementById("annotate_image")
    var image_pos = get_pos(element)

    document.form.mouse_xpos.value = x-image_pos.x
    document.form.mouse_ypos.value = y-image_pos.y


    // place a new annotate ui on the image
    var msg = document.getElementById("annotate_msg")
    msg.style.top = y + "px"
    msg.style.left = x + "px"
    msg.style.display = "block"
}


Annotate.prototype._align_to_image = function(element_name)
{
    var element = document.getElementById(element_name)
    if (element.aligned == true)
        return


    // get the image that is being annotated
    var image = document.getElementById("annotate_image")
    var image_pos = get_pos(image)

    // store the offsets on the element
    var top = element.style.top
    top = parseInt(top)
    var left = parseInt(element.style.left)

    var y = parseInt(element.style.top) + image_pos.y
    var x = parseInt(element.style.left) + image_pos.x
    element.style.top = y + "px"
    element.style.left = x + "px"

    element.aligned = true
}





Annotate.prototype.show_marks = function(key, num)
{
    // get all of the elements
    for ( var i = 0; i <= num; i++ )
    {
        var name = "annotate_div_" + key + "_" + i
        toggle_display(name)

        name = "annotate_mark_" + key + "_" + i
        this._align_to_image(name)

        name = "annotate_back_" + key + "_" + i
        this._align_to_image(name)

        name = "annotate_msg_" + key + "_" + i
        this._align_to_image(name)
    }

}




Annotate.prototype.set_opacity = function()
{
    var element = document.getElementById("annotate_image")
    var element2 = document.getElementById("annotate_image_alt")

    // if either of them have opacity, then turn it off
    if ( element.style.opacity != 1.0 || element2.style.opacity != 1.0 ) {
        element.style.opacity = 1.0
        element2.style.opacity = 1.0
    }
    else {

        if ( element.style.zIndex > element2.style.zIndex ) {
            element.style.opacity = 0.8
            element2.style.opacity = 1.0
        }
        else {
            element.style.opacity = 1.0
            element2.style.opacity = 0.8
        }
    }
}


Annotate.prototype.switch_alt = function()
{
    var element = document.getElementById("annotate_image")
    /*
    if (element.style.opacity == 1.0)
        element.style.opacity = 0.8
    else
        element.style.opacity = 1.0
    */

    var element2 = document.getElementById("annotate_image_alt")
    /*
    if (element2.style.opacity == 1.0)
        element2.style.opacity = 0.8
    else
        element2.style.opacity = 1.0
    */

    if (element2.style.zIndex == 0)
        element2.style.zIndex = 2
    else
        element2.style.zIndex = 0


}

function WdgStyle(img, state)
{
    this.img = img;
    this.state = state;
}

WdgStyle.prototype.OVER = 'over';
WdgStyle.prototype.OUT = 'out';
function wdg_opacity(img, state)
{
    var a = new WdgStyle(img, state);
    a.flip();
}

WdgStyle.prototype.flip = function() 
{
    var img_obj = document.getElementById(this.img);
    // change style on mouse over or out
    if (this.state == this.OVER)
        img_obj.className = 'icon_over';
    else if (this.state = this.OUT)
        img_obj.className = 'icon_out';
}

function get_element(id)
{
    return new Element(id)
}


function get_elements(name)
{
    var elems = document.getElementsByName(name)
    if ( elems == null || elems.length == 0)
        return null
    else
        return new TElements(name)
}

/* A group of elements with the same name */
function TElements(name)
{
    this.objs = document.getElementsByName(name)
}

/* Toggle all the checkboxes with the same name 
    with optional attr_name, value matching */
TElements.prototype.toggle_all = function(me, attr_name, attr_value)
{
    var objs = this.objs
    for (k=0; k<objs.length; k++)
    {
        if (attr_name && attr_value)
        {
            if ( objs[k].getAttribute(attr_name) != attr_value )
                continue
        }    
        if (me.checked)
            objs[k].checked = true
        else
            objs[k].checked = false
    }
}

TElements.prototype.toggle_me = function(id)
{
    var me = document.getElementById(id)
    if (me.checked)
        me.checked = false
    else
        me.checked = true
}  

TElements.prototype.check_all = function()
{
    var objs = this.objs
    for (k=0; k<objs.length; k++)
        objs[k].checked = true
}  

TElements.prototype.check_me = function(id)
{
    var me = document.getElementById(id)
    if (me.checked)
    {
        var objs = this.objs
        for (k=0; k<objs.length; k++)
            objs[k].checked = false
        me.checked = true    
    }
}  

/* used for mini-tabs and menu items in PopupMenuWdg */
TElements.prototype.tab_me = function(tab_name, on_class, off_class)
{
   
    var objs = this.objs
    for (k=0; k<objs.length; k++)
    {
        if (objs[k].getAttribute('tab') == tab_name)
            objs[k].className = on_class
        else
            objs[k].className = off_class 
    } 
   
}

TElements.prototype.get_values = function(attr_name)
{
    var objs = this.objs
    var values = new Array()
    for (k=0; k<objs.length; k++)
    {
        var obj = objs[k]
        var value = ''
        if (!attr_name)
            value = obj.value
        else
            value = obj.getAttribute(attr_name)
        // depending on the element type, push the value to the array
        if (obj.type =='checkbox')
        {
            if (obj.checked)
                values.push(value)
        }
        else if (obj.type =='select-multiple')
        {
            var selected = new Array()
            // this works faster than cycling thru the whole select
            while (obj.selectedIndex != -1) 
            {   if (obj.selectedIndex != 0)
                    values.push(obj.options[obj.selectedIndex].value); 
                selected.push(obj.selectedIndex) 
                obj.options[obj.selectedIndex].selected = false;
            }
            for (k=0; k < selected.length; k++)
                obj.options[selected[k]].selected = true
            
        }
        else if (obj.type =='hidden')
        {
            values.push(value)
        }
        else 
        {
            values.push(value)
        }
    }
    return values
}
/* Get the "|V|" joined values from elements */
TElements.prototype.get_value = function()
{
    var values = this.get_values()
    return values.join("|V|")
}
        
TElements.prototype.set_value = function(value)
{
    if (this.objs[0])
        this.objs[0].value = value
}

/* define the commonly used (pseudo)static functions */
Common = new function()
{ 
    this.pause = function(millis)
    {
        // TODO: java object doesn't exist in IE ... what is the equivalent?
        if (!isIE() && navigator.javaEnabled()) {
            java.lang.Thread.sleep(millis)
        }
        else  // Maybe we can run this in an applet instead of this dumb way
        {  
            var date = new Date();
            var curDate = null;

            do { var curDate = new Date(); }
            while (curDate-date < millis);
        }
    } 

    /* Form Validation functions */
    this.validate_int = function( strValue ) 
    {
        var objRegExp  = /(^-?\d\d*$)/
        //check for integer characters
        return objRegExp.test(strValue)
    }

    /* find position of an element in the DOM */
    this.find_pos_x = function(obj)
    {
        var curleft = 0;
        if(obj.offsetParent)
            while(1) 
            {
              curleft += obj.offsetLeft;
              if(!obj.offsetParent)
                break;
              obj = obj.offsetParent;
            }
        else if(obj.x)
            curleft += obj.x;
        return curleft;
    }

    this.find_pos_y = function(obj)
    {
        var curtop = 0;
        if(obj.offsetParent)
            while(1)
            {
              curtop += obj.offsetTop;
              if(!obj.offsetParent)
                break;
              obj = obj.offsetParent;
            }
        else if(obj.y)
            curtop += obj.y;
        return curtop;
    }
    /* scroll vertically to a pixel value stored in window.name*/
    this.scroll_y = function(y){

       if (y != null)
            window.name = y
       if (window.name) window.scrollTo(0, window.name)
    }

    /* move the div where the user clicks */
    this.follow_click = function(event, id, x_offset, y_offset)
    {
        var obj = document.getElementById(id)
        var dy = event.clientY + document.body.scrollTop 
        if (y_offset)
            dy += parseInt(y_offset)
        if (! obj)
        {
            alert(id + " not found. Reload ")
            return
        }
        obj.style.top = dy
           
        
        var dx =  event.clientX + document.body.scrollLeft
        if (x_offset)
            dx += parseInt(x_offset)
        obj.style.left = dx

    }

    this.add_upload_input = function(parent_id, input_name, counter_name)
    {
       var counter = get_elements(counter_name)
       var counter_val = parseInt(counter.get_value()) + 1
       counter.set_value(counter_val) 

       var file = new Element('input').setProperties(
                { 'type': 'file',
                   'name': input_name + counter.get_value(),
                   'size': '40',
                   'value': ''
                });
       var span = new Element('div').setStyle('margin', '6px 0 0 80px')
       var br = new Element('br')
       
       file.injectInside(span)  
       var parent_elem = $(parent_id)
       span.injectAfter(parent_elem)
    }

    this.overlay_setup = function(ev, func)
    {
        document.addEvent( ev, func )
    }

}   

Note = new function()
{
    this.focus_note = function(id, y_offset, container_id, status_id)
    {
        var obj = document.getElementById(id)
        obj.focus()
        //var ty = $(id).getTop()
        var ty = Common.find_pos_y(obj)
        ty = ty + parseInt(y_offset)
        Common.scroll_y(ty)
        //var scroller = new Fx.ScrollWindow( {duration: 300, 
        //    onComplete: function()  {}});
           
        //scroller.scrollTo(false, ty);
        //var scroller = new Fx.Scroll(document.body);
        //scroller.custom(document.body.scrollTop, $(id).getTop());

        //display reply to info
        var note = document.getElementById(container_id)

        var sign  = document.getElementById(status_id)
        if (note && sign)
        {
            sign.innerHTML = "Reply to: <i>" + note.innerHTML.substring(0, 40) 
                + ". . .</i>"
            // this should be passed in, but it should be the same as my_id in 
            // this.new_note()
            set_display_on(id + "_new")

            // set parent_id
            var parent_id = note.getAttribute('parent_id')
            var parent_var = document.getElementsByName(id + "_parent")[0]
            parent_var.value = parent_id
        }
        var textarea = $(id)
        textarea.addClass('reply_note') 
    }

    this.new_note = function(my_id, status_id, textarea_id)
    {
        set_display_off(my_id)
        //display reply to info
        var sign  = document.getElementById(status_id)
        if (sign)
            sign.innerHTML = "New note: "

        var textarea = $(textarea_id)
        textarea.removeClass('reply_note') 
        var parent_var = document.getElementsByName(textarea_id + "_parent")[0]
        
        parent_var.value = ''

        var select = document.getElementsByName(textarea_id + "_context")[0]
        select.removeAttribute('disabled')
        
    }
       
    this.child_display = function(child_id, long_id, short_id)
    {
        if ($(long_id).getStyle('display') != 'none')
            set_display_on(child_id)
        else
            set_display_off(child_id)
    }

    this.lock_context = function(select_name, context)
    {
        var select = document.getElementsByName(select_name)[0]
        
        var matched = false
        for (var i=0; i < select.options.length; i++)
        {
            if (context == select.options[i].value)
            {
                matched = true
                break
            }
        }
        if (matched)
        {
            select.value = context
            select.setAttribute('disabled','true')
        }
        else
        {
            alert('Context [' + context + '] is not available here.\n'  + 
                'This ' + context + ' note is probably not meant to be replied to here!')
            select.removeAttribute('disabled')
        }
    }

 
  
    this.refresh = function(cmd_holder)
    /* refresh the note area */
    {
        var elems = get_elements(cmd_holder)
        var values = elems.get_values()
        for (var k=0; k < values.length; k++)
        {
            var value = values[k]
            if (value != '')
                eval(value)
        }
    }

    this.setup_util = function(skey, skey_parent, base_name)
    {
        get_elements('skey_note').set_value(skey)
        get_elements('skey_note_parent').set_value(skey_parent)
        var elems = $('NoteMenuWdg_content').getElements('input[name=base_name]')
        elems[0].value =base_name
        
    }


}

Timecard = new function()
{
    this.update_date = function(week_name, year_name, direction)
    {
        if (direction=='forward')
        {
            var week = get_elements(week_name)
            var new_week = parseInt(week.get_value()) + 1
            if (new_week > 52)
            {
                new_week = 1
                var year = get_elements(year_name)
                var new_year = parseInt(year.get_value()) + 1
                year.set_value(new_year)
            }
            week.set_value(new_week)
            
        }
        else
        {
            var week = get_elements(week_name)
            var new_week = parseInt(week.get_value()) - 1
            if (new_week < 1) 
            {
                new_week = 52
                var year = get_elements(year_name)
                
                var new_year = parseInt(year.get_value()) - 1
                if (new_year < 1)
                    alert("Year has to start at 1")
                else
                    year.set_value(new_year)
            }
            week.set_value(new_week)
            
            
        }

    }

    /* updating the calendar of the Work Hours Summary tab thru
      clicking on 'next' or 'prev' icon */
    this.summary_cal_update = function(cal_name, direction)
    {
        var cur_date = new Date()
        var a= get_elements(cal_name)
        if (a.get_value())
        {
            dates = a.get_value().split('-')
            cur_date.setFullYear(dates[0])
            // specify base 10
            cur_date.setMonth(parseInt(dates[1], 10) - 1)
            cur_date.setDate(dates[2])
        }
        if (direction == 'forward')
        {
            cur_date.setDate(cur_date.getDate() + 7)
        }
        else
            cur_date.setDate(cur_date.getDate() - 7)

        var new_date = cur_date.getFullYear() + "-" + (parseInt(cur_date.getMonth()) + 1) + "-" + cur_date.getDate()
        
        a.set_value(new_date)
    }
}

Submission = new function()
{
    //dynamically inject a hidden input in the page for redirection to the right bin
    this.set_bin = function(bin_sel_name, bin_id, is_child)
    {
        var hidden_in_page = null;
        if (is_child)
        {
            hidden_in_page = window.parent.document.getElementsByName(bin_sel_name)
        }
        else
        {
            hidden_in_page = document.getElementsByName(bin_sel_name)
        }
        if (hidden_in_page && hidden_in_page.length > 0)
        {
            hidden_in_page[0].value = bin_id;
        }
    }
}

Table = new function()
{
    this.locate_elem = function(id, attr, mode)
    {
        get_elements('skey_DynamicTableElementWdg').set_value(id)
        get_elements('attr_DynamicTableElementWdg').set_value(attr)
        get_elements('update_DynamicTableElementWdg').set_value(mode)
    }
}




/*
 * Wrapper around the general applet
 */
Applet = new function()
{
    this.open_explorer = function(path)
    {
        var applet = document.general_applet
        //applet.makedirs(path)
        applet.open_folder(path)
        return
    } 

    this.makedirs = function(path)
    {
        var applet = document.general_applet
        applet.makedirs(path)
    }

    this.command_port = function(url, port, cmd)
    {
        var applet = document.general_applet
        // strip http:// or https://
        host = url.replace(/^http:\/\/|^https:\/\//g,'')
        return applet.command_port(host, port, cmd)
    }

    this.get_connect_error = function()
    {
        applet = document.general_applet
        return applet.get_connect_error()
    }
    this.copy_file = function(from_path, to_path)
    {
        var applet = document.general_applet
        return applet.copy_file(from_path, to_path)
    }

    this.move_file = function(from_path, to_path)
    {
        var applet = document.general_applet
        return applet.copy_file(from_path, to_path)
    }

}
