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
/* PopupWindow convenience display function */
PopupWindow_display = function(src, dynamic_element_str)
{
    popup = new PopupWindow(src)
    popup.add_element_names(dynamic_element_str)
    popup.display()
    
}
/* convenience class for opening up popup windows in the browser */

function PopupWindow(ref) {
    this.reference = ref;
    this.window_name = "";
    this.titlebar = "no";
    this.toolbar = "no";
    this.scrollbars = "yes";
    this.resizable = "yes";
    this.height	= 600;
    this.width = 950;
    this.dependent = "yes";
    this.element_names = new Array();

    this.add_element_names = function(element_names)
    {
        if (element_names != null && element_names != '') 
        {
            element_names = element_names.split("||")
            for (var i=0; i<element_names.length; i++) 
                this.element_names.push(element_names[i])
        }
    }

}

/* Build up window options and open up the window */
PopupWindow.prototype.display = function() {
    
    var options = 
        "titlebar="     + this.titlebar + "," +
        "toolbar="      + this.toolbar + "," +
        "scrollbars="   + this.scrollbars + "," +
        "resizable="    + this.resizable + "," +
        "width="        + this.width + "," +
        "height="       + this.height + "," +
        "dependent="    + this.dependent
    ;
    
     // build the element string
    elements_expr = new Array()

    for (var i=0; i<this.element_names.length; i++) {
        element_name = this.element_names[i]
        
        var element = get_elements(element_name)
        if ( element != null ) {
            value = element.get_value()
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
        this.reference += "&" + elements_expr.join("&")

    this.window = window.open( this.reference, this.window_name, options )
    this.window.focus()
}

/* close the popup window */
PopupWindow.prototype.close = function() {
    this.window.close();
}

PopupWindow.prototype.resize = function(width, height) 
{    
    this.window.resizeTo(width, height)
}

    

/* A Popup div element. After initialization, call the show() 
   and hide() functions. */
function PopupDiv(id, type) 
{
    // type : 'plain' (hint), 'action', 'comment', 'help', 'report', 'warning'
    this.id = id
    this.class_name = 'popup_hint'
    this.type = type
    this.title_id = this.id + '_title'
    this.button_id = this.id + '_button'
    this.content_id = this.id + '_content'

    this.__get_close_link = function()
    {
        var link = document.createElement("a")
        var link_span =  document.createElement('span')
        link_span.setAttribute('style','position: absolute; right: 0.5em; padding-left: 4px')
        link.setAttribute('style','outline: none;')
        link.setAttribute('href', "javascript:void(set_display_off('"
           + this.id  + "'))")
        link.innerHTML = "X"
        link_span.appendChild(link)
        return link_span
    }

    this.close = function()
    {
        set_display_off(this.id)
    }

    this.__create_div = function()
    {
        var div = document.createElement('div')
        div.id = this.id
        div.className = this.class_name
        div.style.display = 'none'
        var body = document.getElementsByTagName("BODY")[0]
        body.appendChild(div)
        return div
    }

    this.__create_plain_wdg = function()
    {
        var main_div = this.__create_div()
        var title_div =  document.createElement('div')
        var title_span =  document.createElement('span')
        title_span.setAttribute('id', this.title_id)
        title_span.setAttribute('style', 'padding: 0 2px 0 2px')
        title_div.appendChild(title_span)

        main_div.appendChild(this.__get_close_link())
        main_div.appendChild(title_div)
        main_div.setAttribute("active","true")
        return main_div
    }

    this.__create_report_wdg = function()
    {
        main_div = this.__create_action_wdg('command report')
        main_div.style.width = '500px'
        main_div.style.overflow = 'auto'
        return main_div
    }

    this.__create_help_wdg = function()
    {
        var main_div = this.__create_div()
        var title_div =  document.createElement('div')
        var content_div = document.createElement('div')
        main_div.appendChild(title_div)
        main_div.appendChild(content_div)
        title_div.setAttribute('style',
            'border-bottom: 1px dotted #bbb; font-size: smaller;') 
        var title_text = document.createTextNode('help items')
        title_div.appendChild(title_text)
        title_div.appendChild( this.__get_close_link() ) 
        return main_div
    }

    this.__create_warning_wdg = function()
    {
        var main_div = this.__create_div()
        var title_div =  document.createElement('div')
        var content_div = document.createElement('div')
        main_div.appendChild(title_div)
        main_div.appendChild(content_div)
        main_div.setAttribute('style', 'z-index: 500')
        title_div.setAttribute('style',
            'border-bottom: 1px dotted #bbb; font-size: smaller;') 
        var title_text = document.createTextNode('warnings')
        title_div.appendChild(title_text)
        title_div.appendChild( this.__get_close_link() ) 
        return main_div
    }

    this.__create_action_wdg = function(header)
    {
        if (header==null)
            header = 'actions'
        var main_div = this.__create_div()
        var title_div =  document.createElement('div')
        var header_div =  document.createElement('div')
        header_div.setAttribute('style','margin: 0 10px 6px 2px')       
        var header_text = document.createTextNode(header)
        var header_span = document.createElement('span')
        header_span.setAttribute('style','border-bottom: 1px dotted #888;')       
        header_span.appendChild(header_text)
       
        header_div.appendChild(header_span)
        header_div.appendChild( this.__get_close_link() )

        var title_span =  document.createElement('span')
        title_span.setAttribute('id', this.title_id)
        title_span.setAttribute('style', 'padding: 0 5px 0 5px')
        title_div.appendChild(title_span)
        
        main_div.appendChild(header_div)
        main_div.appendChild(title_div)
        return main_div
    }

    this.__create_comment_wdg = function()
    {
        var main_div = this.__create_div()
        var title_div =  document.createElement('div')
        
        var title_text = document.createTextNode('Comments:')
        title_div.appendChild(title_text)
        var title_span =  document.createElement('span')
        title_span.setAttribute('id', this.title_id)

        title_div.appendChild(title_span)
        title_div.appendChild( this.__get_close_link() )

        var text = document.createElement('textArea')
        text.setAttribute('id', this.content_id)
        text.setAttribute('rows', '4')
        text.setAttribute('cols', '30')  

        // TODO: made this smarter instead of hard-coded
        text.setAttribute('onblur',"a=document.getElementsByName("
         + "'upload_description')[0]; a.value= this.value;")
       
        var button_div =  document.createElement('div')
        button_div.setAttribute('align', 'right')
        var button = document.createElement('input')
        button.setAttribute('id', this.button_id)
        button.setAttribute('type', 'button')
        button.setAttribute('value', 'Publish')
        button.setAttribute('style', 'margin: 3px 0 3px 0;')
        button_div.appendChild(button)
        main_div.appendChild(title_div)
        main_div.appendChild(text)
        main_div.appendChild(button_div)
        var body = document.getElementsByTagName("BODY")[0]
        body.appendChild(main_div)
        return main_div
    }
    this.show = function(event, msg, js)
    {
        clearTimeout(this.timer)
        var div = document.getElementById(this.id)
        if (div == null)
            div = eval('this.__create_' + this.type + '_wdg()')
         
        if (this.type == 'comment')
        {
            this.__customize_comment(div, event, msg, js)
            div.style.display = "block"
        }
        else if (this.type == 'plain' || this.type =='action')
        {
            this.__customize_plain(div, event, msg)
            div.style.display = "block"
        }
        else if (this.type == 'report')
            this.__customize_report(div, msg)
        else if (this.type == 'help')
        {
            this.__customize_help(div, event)
            div.style.display = "block"
            return div
        }
        else if (this.type = 'warning')
        {
            this.__customize_warning(div, event)
            div.style.display = "block"
            return div
        }
            
    }

    this.__customize_plain = function(div, event, msg)
    {
        div.setAttribute('onmouseover', "var time=document.getElementById('" + this.id 
            + "').getAttribute('timer'); clearTimeout(time)")
        div.setAttribute('onmouseout', "var bubble = new PopupDiv('" 
            + this.id + "','plain'); bubble.hide(3500)")
        left_pos =  event.clientX + document.body.scrollLeft + 10
 
        div.style.left = Math.min(document.body.clientWidth - 180, left_pos)
        
        div.style.top = event.clientY + document.body.scrollTop - 80
        title_div = document.getElementById(this.title_id)
        if (title_div)
            title_div.innerHTML = msg + "&nbsp;&nbsp;"
    }

    this.__customize_help = function(div, event)
    {
        div.setAttribute('onmouseover', "var time=document.getElementById('" + this.id 
            + "').getAttribute('timer'); clearTimeout(time)")
        div.setAttribute('onmouseout', "var bubble = new PopupDiv('" 
            + this.id + "','help'); bubble.hide(3500)")
        div.style.left = event.clientX + document.body.scrollLeft - 75
        div.style.top = event.clientY + document.body.scrollTop + 15
    }

    this.__customize_warning = function(div, event)
    {
        div.setAttribute('onmouseover', "var time=document.getElementById('" + this.id 
            + "').getAttribute('timer'); clearTimeout(time)")
        div.setAttribute('onmouseout', "var bubble = new PopupDiv('" 
            + this.id + "','warning'); bubble.hide(3500)")
        div.style.left = event.clientX + document.body.scrollLeft - 140
        div.style.top = event.clientY + document.body.scrollTop - 60
    }

    this.__customize_comment = function(div, event, msg, js)
    {
        div.style.left = event.clientX + document.body.scrollLeft + 30
        div.style.top = event.clientY + document.body.scrollTop - 150
        title_div = document.getElementById(this.title_id)
        title_div.innerHTML = ' [' + msg + ']'
        button = document.getElementById(this.button_id)
        button.setAttribute('onclick', 'javascript:' + js) 
       
        // clear contents
        var text = document.getElementById(this.content_id)
        if (text != null)
            text.value = '' 
    } 

    this.__customize_report = function(div, msg)
    {
        // remove all commands response 
        msg = msg.replace(/^<!-- commands response[\s\S]*-->$/im, '')
        // remove any comments
        msg = msg.replace(/<!-- .* -->/gi, '')
        // replace line break and tabs
        msg = msg.replace(/(\n|\t|\r)/gi, '')
        msg = msg.trim()

        // ignore it if it is just the script tag
        
        if (msg.match(/^\<script.*script\>$/gim))  
        { 
            return
        }
        
        if (msg != '' && msg != null)
        {
            div.style.display = "block"
            div.style.left = document.body.scrollLeft + 50
            div.style.top = document.body.scrollTop + 10
            title_div = document.getElementById(this.title_id)
            title_div.innerHTML= msg
        }
            
    }

    this.hide = function(time)
    {
        var func_str= "var elem = document.getElementById('"  + this.id 
            + "'); if (elem) elem.style.display = 'none'" 
        var timer_id = setTimeout(func_str, time)
        document.getElementById( this.id ).setAttribute('timer', timer_id) 
        
    }
   
     
}

/* display a popup on clicking of the middle mouse button */
PopupDiv_middle_click = function (e, my_id, source_id, type)
{
    // do nothing for Mac
    if (navigator.appVersion.indexOf('Mac') > -1)
        return true
    if ((isIE() && e.button == 4) || (!isIE() && e.button == 1))
    {
        var div = new PopupDiv(source_id, type)
        //div.show(e, document.getElementById(source_id).innerHTML)  
        div.show(e, '')  
    }   
}

var HelpMenu = new Class(
{
    initialize: function()
    {
        this.help_labels = new Array()
        this.help_actions = new Array()
    },
    add: function(label, action)
    {
        this.help_labels.push(label)
        this.help_actions.push(action)
    },
   
    _get_menu: function()
    {
         return new PopupDiv("help_menu", "help")
    },
    show: function(event)
    {
        
        var pop = this._get_menu()
        var main_div = pop.show(event)
        
        content_div = main_div.childNodes[1]
        content_div.innerHTML = ''        

        
        for (var i=0; i< this.help_labels.length; i++)
        {
            var elem =  document.createElement('a')
            var br =  document.createElement('br')
            content_div.appendChild(elem)
            content_div.appendChild(br) 
            var label = document.createTextNode(this.help_labels[i]) 
            elem.appendChild(label)
            // this is FF specific
            elem.setAttribute('style','-moz-user-select: none')
            elem.setAttribute('href','#')
            // IE and FF are both compatible with this format
            elem.onmousedown = new Function(this.help_actions[i])
            
            
        }
        document.addEvent('mousedown', function() {pop.hide(100)})
    } 
});

var WarnMenu = HelpMenu.extend(
{
    _get_menu: function()
    {
         return new PopupDiv("warn_menu", "warning")
    } 
});

