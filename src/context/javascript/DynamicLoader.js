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

/* IframeLoader convenience display function */
IframeLoader_display = function(img_span_name, name, src, dynamic_element_str)
{
    var iframe = new IframeLoader(img_span_name, name, src)
    iframe.add_element_names(dynamic_element_str)
    iframe.display()
    
}
/* IframeLoader Object */
function IframeLoader(img_span_name, name, src)
{

    this.img_span_name = img_span_name
    this.iframe_name = name
    this.src = src

    this.element_names = new Array()

    this.add_element_names = function(element_names)
    {
        if (element_names != null && element_names != '') 
        {
            element_names = element_names.split("||")
            for (var i=0; i<element_names.length; i++) 
                this.add_element_name(element_names[i])
        }
    }

    this.add_element_name = function(element_name)
    {
        this.element_names.push(element_name)
    }

    this.display = function()
    {
        var a= document.getElementById(this.img_span_name);
        window.frames[this.iframe_name].document.body.innerHTML=a.innerHTML;
        var x=document.getElementById(this.iframe_name);
       
        // build the element string
        var elements_expr = new Array()

        for (var i=0; i<this.element_names.length; i++) {
            var element_name = this.element_names[i]
            
            var element = get_elements(element_name)
            if ( element != null ) {
                var value = element.get_value()
                if (value != null ) {
                    // escape the values
                    element_name = encodeURIComponent(element_name)
                    value = encodeURIComponent(value)
                    var element_str = element_name + "=" + value
                    elements_expr.push(element_str)
                } 
            }
        }
        if (elements_expr.length > 0)
            this.src += "&" + elements_expr.join("&")
        x.src = this.src
    }
}

/* AjaxLoader Object */ 
function AjaxLoader(display_id)
{
    this.element_names = []

    this.add_element_names = function(element_names)
    {
        if (element_names != null && element_names != '') 
        {
            element_names = element_names.split("||")
            for ( var i=0; i<element_names.length; i++ ) {
                element_name = element_names[i]
                this.add_element_name(element_name)
            }
        }
    }
}


AjaxLoader.prototype.add_element_name = function(element_name)
{
    this.element_names.push(element_name)
}


AjaxLoader.prototype.load_content = function(url, display_id, mode, show_progress)
{
    var http_request = false

    // build the element string
    var elements_expr = new Array()

    //for (i in document.elements ) {
    for (var i=0; i<this.element_names.length; i++) {
        var element_name = this.element_names[i]
        
        var element = get_elements(element_name)
        if ( element != null ) {
            var values = element.get_value().split('|V|')
            if (values != null)
            {
                for (var k=0; k < values.length; k++)
                {
                    // escape the values
                    element_name = encodeURIComponent(element_name)
                    value = encodeURIComponent(values[k])
                    var element_str = element_name + "=" + value
                    //alert(element_str)
                    elements_expr.push(element_str)
                }
            } 
        }
    }

    // display the loading message
    display = document.getElementById( display_id )
    if ( display != null && show_progress != 'false')
    {
        display.innerHTML = '<img src="/context/icons/common/indicator_snake.gif" border="0">'
        
        set_display_on(display_id)
    }
    if (display)
        display.setAttribute('loaded', 'true')

    if (window.XMLHttpRequest) {
        http_request = new XMLHttpRequest()
        if (! isIE() ) { // this does not work in IE
            http_request.overrideMimeType('text/xml; charset=utf-8')
        }
    } else if (window.ActiveXObject) {
        http_request = new ActiveXObject("Microsoft.XMLHTTP")
    }

    if ( !http_request) {
        alert('Cannot create and XMLHTTP instance')
        return false
    }

    object = this
    http_request.onreadystatechange = function() {
        if (http_request.readyState == 4) {
            if (http_request.status && http_request.status == 200) {
                
                object.handle_request(http_request, display_id, mode)
            }
            else {
                alert('Error with request')
                return false
            }
        }

    }

    http_request.open('POST', url, true)
    // Multipart does not work.  Probably need to format the request
    // accordingly.
    //http_request.setRequestHeader('Content-Type','multipart/form-data')
    //http_request.setRequestHeader('Content-Type','application/x-www-form-urlencoded;charset=utf-8')
    http_request.setRequestHeader('Content-Type','application/x-www-form-urlencoded')
    
    http_request.send(elements_expr.join("&"))
}


/* static functions */
/* on success handling request */
AjaxLoader.prototype.handle_request = function(http_request, display_id, mode)
{
    if (mode == 'cmd')
    {
        var response = http_request.responseText;
        set_display_off(display_id);
        var cmd_report_bubble = new PopupDiv('cmd_report','report');
        cmd_report_bubble.show(null, response, null);

        // run response script if available
        this._run_response_script(response) ;
       
    }
    else
    {
        var display = document.getElementById( display_id )
        // get the parent if the replace flag is on
        replace_flag = false;
        if (replace_flag == true)
            display = display.parentNode;
        if (display)
        {
            //display.innerHTML = http_request.responseText;
            spt.behavior.replace_inner_html(display, http_request.responseText);
            //this.dynamic_content(display_id, http_request.responseText);
        }
     
    }
    // run post-ajax script for command or wdg
    var display = document.getElementById( display_id )
    if (display)
    {
        
        var script = display.getAttribute('post_ajax')
        if (script)
            eval(script)
    }
    this.parse_script()
    
}

AjaxLoader.prototype._run_response_script = function(response)
{
    var cmd_response = ''
    // case-insensitive, multi-line
    var re = /^<!-- commands response([\s\S]*)-->$/im
    var match = response.match(re)

    // match[1] is like match.group(1)
    if (match)
        cmd_response = match[1]
    
    var cmd_list = cmd_response.split('<br/>')
    for (var i=0; i<cmd_list.length; i++)
    {
        var cmd_name = cmd_list[i].split('||')[0]
        var msg = cmd_list[i].split('||')[1]
        if (!msg)
            continue
        var msgs = msg.split('\n')

        // run the script if there is any in the command's response
        for (var k=0; k < msgs.length; k++)
        {
            msg = msgs[k]
            if (msg != null && msg.trim() != '')
            {
                re = /<script>(.*)\<\/script>/im
                match = msg.match(re)
                if (match)
                    eval(match[1])
            }
        }
    }
}

// test using DOM to insert content
AjaxLoader.prototype.dynamic_content = function(elementid, content)
{
    if (document.getElementById && !document.all) {
        var rng = document.createRange();
        var el = document.getElementById(elementid);
        rng.setStartBefore(el);
        var htmlFrag = rng.createContextualFragment(content);
        while (el.hasChildNodes())
            el.removeChild(el.lastChild);
        el.appendChild(htmlFrag);
    }
}



// parse scripts definition defined in the page source
AjaxLoader.prototype.parse_script = function()
{
    //EventContainer.reset()
    var head = document.getElementsByTagName('form').item(0)
    var elems = document.getElementsByTagName('SCRIPT')
   
    for (var k=0; k < elems.length; k++)
    {
        // we are only interested in the scripts of type 'dynamic'
        if (elems[k].getAttribute('mode') == 'dynamic')
        {
            var script = ''
            if (isIE())
                script = elems[k].text
            else
                script = elems[k].textContent
            if (script != '')
            {
                eval(script)
            }
            elems[k].setAttribute('mode','loaded')         
        }
    }
    
}


/* convenience static function to load a url */
AjaxLoader_load_cbk = function(display_id, url, element_names, show_progress)
{
    var ajax = new AjaxLoader(display_id)
    ajax.add_element_names(element_names)

    ajax.load_content(url, display_id, 'load', show_progress)
}


/* covenience function to execute a command on the server and passing a value */
/* from the element that submitted it */
AjaxLoader_execute_cmd = function(display_id, command_url, element, element_names, show_progress)
{
    if ( element != null )
    {
        var value = element.value
        command_url += "&value="+value
    }
    ajax = new AjaxLoader(display_id)
    ajax.add_element_names(element_names)
    ajax.load_content(command_url, display_id, 'cmd', show_progress)
}





/* some other dynamic functions that probably shouldn't be in this file */


/* if bias_id is specified, its display will take precedence */
function swap_display(element1_id, element2_id, bias_id)
{
    var element1 = document.getElementById( element1_id )
    var element2 = document.getElementById( element2_id )
    if (element1 == null || element2 == null)
        return

    if ( element1.style.display == "none" || bias_id == element1_id )
    {
        element1.style.display = "inline"
        element2.style.display = "none"
    }
    else
    {
        element1.style.display = "none"
        element2.style.display = "inline"
    }

}


function toggle_display(element_id)
{

    var element = document.getElementById( element_id )
    if (element == null) {
        // Commenting this out until Event container can remove listeners
        //alert("Element ["+element_id+"] is null")
        return
    }

    if ( element.style.display == "none" )
        set_display_on(element_id)
    else
        set_display_off(element_id)
   
}



// explicitly set the display
function set_display_on(element_id)
{
    for (var i=0; i < arguments.length; i++)
    {
        var element_id = arguments[i]
        var element = document.getElementById( element_id )
        if (!element)
        {
            // Commenting this out until Event container can remove listeners
            //alert("Element id: " + element_id)
            continue
        }
        
        // check that the element has a display defined
        if ( element && element.style.display == "" )
            alert( "Element ["+element_id+"] has undefined display" )

        
        if ( isIE() == true ) {
            element.style.display = "block"
        }
        else {
            if ( element instanceof HTMLDivElement )
                element.style.display = "block"
            else if ( element instanceof HTMLTableSectionElement )
                element.style.display = "table-row-group"
            else if ( element instanceof HTMLTableRowElement )
                element.style.display = "table-row"
            else if ( element instanceof HTMLTableCellElement )
                element.style.display = "table-cell"
            else if (element instanceof HTMLSpanElement )
                element.style.display = "inline"
            else 
                element.style.display = "block"
            $( element_id ).setOpacity(1) 
        }
        //element.style.visibility = 'visible'
        //element.style.opacity = 1
        
    }
}



// explicitly set the display
function set_display_off(element_id)
{
    for (var i=0; i < arguments.length; i++)
    {
        var element_id = arguments[i]
        var element = document.getElementById( element_id )
        if (!element)
            continue
        // check that the element has a display defined, don't bother with IE
        if ( element.style.display == "" && !isIE())
            alert( "Element ["+element_id+"] has undefined display" )

        element.style.display = "none"
    }
    
}


/* LOTS OF DUPLICATE CODE HERE!!!! */

function toggle_element_display(element)
{
    if ( element.style.display == "none" )
        set_element_display_on(element)
    else
        set_element_display_off(element)
}




// explicitly set the display
function set_element_display_on(element)
{
    // check that the element has a display defined
    if ( element.style.display == "" )
        alert( "Element ["+element.id+"] has undefined display" )

    if ( isIE() == true ) {
        element.style.display = "block"
    }
    else {
        if ( element instanceof HTMLTableRowElement )
            element.style.display = "table-row"
        else if ( element instanceof HTMLTableCellElement )
            element.style.display = "table-cell"
        else if ( element instanceof HTMLTableSectionElement )
            element.style.display = "table-row-group"
        else
            element.style.display = "block"
    }
}

// explicitly set the display
function set_element_display_off(element)
{
    // check that the element has a display defined
    if ( element.style.display == "" )
        alert( "Element ["+element+"] has undefined display" )

    element.style.display = "none"
}

// Show the elements with attr_name == value, collected thru the elem_name

function filter_elements(elem_name, attr_name, value)
{
    
    var elems = document.getElementsByName(elem_name)
    for (var k=0; k < elems.length; k++) 
    {
        var elem = elems[k]
        if (value == null || value == '')
        {
            set_element_display_on(elem)
            continue
        }
        if (elem.getAttribute(attr_name) == value)
            set_element_display_on(elem)
        else
            set_element_display_off(elem)
    }
}


// to handle buttons in Internet Explorer.
function button_down(element)
{
    element.style.borderWidth='2px 0px 0px 2px'
}

function button_up(element)
{
    element.style.borderWidth='0px 2px 2px 0px'
}


/* Toggles the display of a specific column in a table */
function toggle_column_display(table_id, column, do_show)
{
    var display;
    if (do_show)
        display = 'table-cell'
    else
        display = 'none';

    var table = document.getElementById(table_id);
    for (var j=0; j<table.rows.length; j++)
    {
        try {
            var cell = table.rows[j].cells[column]
            cell.style.display = display
            /*
            if (display == "none")
                Effects.fade_out(cell, 200)
            else
                Effects.fade_in(cell, 200)
            */
           
        }
        catch (e) {
            // do nothing
        }
    }
}


