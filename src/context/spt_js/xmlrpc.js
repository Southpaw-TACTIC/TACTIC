/*
    Copyright (c) 2005 Redstone Handelsbolag

    This library is free software; you can redistribute it and/or modify it under the terms
    of the GNU Lesser General Public License as published by the Free Software Foundation;
    either version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License along with this
    library; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330,
    Boston, MA  02111-1307  USA


    Note from Southpaw Technology:
        This library was taken from http://xmlrpc.sourceforge.net/
    It was distributed as ajax.js which we have renamed to xmlrpc.js.  There
    was no license under the original file, so we have added the same
    GNU Lesser General Public License that came with the rest of the
    distribution (which was all in Java).

    We have made a number of enhancements including reworking the serialization
    so that it does not affect change the prototype of base types
*/



/**
 *  Creates a connection object that may be used to post messages
 *  to a server. 
 */
function Connection()
{
    var self = this;
    this.callback = null;

    this.set_callback = function(callback) {
        this.callback = callback;
    }


    /**
     *  Returns an XmlHttpRequest object for the current browser.
     */
    this.getXmlHttpRequest = function()
    {
        var result = null;

        try
        {
            result = new XMLHttpRequest();
        }
        catch ( e )
        {
            try
            {
                result = new ActiveXObject( 'Msxml2.XMLHTTP' )
            }
            catch( e )
            {
                var success = false;
                
                var MSXML_XMLHTTP_PROGIDS = new Array(
                    'Microsoft.XMLHTTP',
                    'MSXML2.XMLHTTP',
                    'MSXML2.XMLHTTP.5.0',
                    'MSXML2.XMLHTTP.4.0',
                    'MSXML2.XMLHTTP.3.0' );
                
                for ( var i = 0; i < MSXML_XMLHTTP_PROGIDS.length && !success; i++ )
                {
                    try
                    {
                        result = new ActiveXObject( MSXML_XMLHTTP_PROGIDS[ i ] );
                        success = true;
                    }
                    catch ( e )
                    {
                        result = null;
                    }
                }
            }
        }
        
        self.xmlHttpRequest = result;
        return result;
    }
    
    /**
     *  Posts a message to a server.
     */
    this.post = function( url, content, contentType )
    {
        if ( typeof self.xmlHttpRequest.abort == 'function' && self.xmlHttpRequest.readyState != 0 )
        {
            self.xmlHttpRequest.abort();
        }

        // by default, async is false
        var async = false;

        // handle asynchronous mode
        if (this.callback != null) {
            async = true;
            var callback = this.callback;
            var request = self.xmlHttpRequest;
            self.xmlHttpRequest.onreadystatechange = function() {
                callback(request);
            }
        }


        self.xmlHttpRequest.open( 'POST', url, async );
        
        if ( typeof self.xmlHttpRequest.setRequestHeader == 'function' )
        {
            self.xmlHttpRequest.setRequestHeader(
                'Content-Type',
                contentType );
        }

        try {
            self.xmlHttpRequest.send( content );
        }
        catch(e) {
            msg = "Error connecting to TACTIC server.  Please contact the Administrator of this server.";
            spt.error(msg)
            spt.app_busy.hide();
            spt.notify.show_message(msg);
            throw(e);
        }
        
        //return self.xmlHttpRequest.responseText;
        //return self.xmlHttpRequest.responseXML;
        // only send the request back now
        return self.xmlHttpRequest
    }


    
    if ( !this.getXmlHttpRequest() )
    {
        throw new Error( "Could not load XMLHttpRequest object" );
    }
}



/**
 *  Client object constructor.
 */
function AjaxService( url, handlerName )
{
    this.url = url;
    this.handlerName = handlerName;
    this.connection = new Connection();
}

AjaxService.prototype.set_callback = function(callback) {
    this.connection.set_callback(callback);
}


/**
 *  Posts an XML-RPC message to the supplied method using the
 *  given arguments.
 */
AjaxService.prototype.invoke = function( method, arguments )
{
    return this.connection.post( this.url, this.getMessage( method, arguments ), 'text/xml' );
}

/**
 *  Generates an XML-RPC message based on the supplied method name
 *  and argument array.
 */
AjaxService.prototype.getMessage = function( method, arguments )
{
    if ( arguments == null )
    {
        arguments = new Array();
    }

/*
    var message =
        '<?xml version="1.0"?><methodCall><methodName>' +
        this.handlerName + '.' + method +
        '</methodName>';
*/
    var message =
        '<?xml version="1.0"?><methodCall><methodName>' +
        method +
        '</methodName>';
                
    if ( arguments.length > 0 )
    {
        message += '<params>';
        
        for ( var i = 0; i < arguments.length; i++ )
        {
            var argument = arguments[ i ];
            if (argument == undefined) {
                spt.js_log.debug("WARNING: argument index ["+i+"] of method ["+method+"] is undefined");
            }
            var serialized = '<param><value>' + spt.xmlrpc.serialize(argument) + '</value></param>';
            message += serialized;

        }
        
        message += '</params>';
    }

    message += '</methodCall>';
    //alert(message);
    return message;
}


spt.xmlrpc = {};

//
// Main serialization function
//
spt.xmlrpc.serialize = function(element) {
    //var type = $type(element);
    // Avoid using Mootools type to handle their base types as well
    //var type = typeOf(element)
    var type = typeof element
    /*
    if (type == 'element') {
        spt.alert('Illegal attempt to serialize an html element. Please use a hash as arguments of a JS Client API call.'); 
        return;
    }
    */
    
    if (type == 'array') {
        return spt.xmlrpc.array(element);
    }
    else if (type == 'hash') {
        return spt.xmlrpc.hash(element);
    }
    else if (type == 'string') {
        return spt.xmlrpc.string(element);
    }
    else if (type == 'number') {
        return spt.xmlrpc.number(element);
    }
    else if (type == 'boolean') {
        return spt.xmlrpc.boolean(element);
    }
    else if (type == 'date') {
        return spt.xmlrpc.boolean(element);
    }
    else {
        if (type == 'object') {
            // TODO, when js 1.8 is more common, use Array.isArray()
            if (Object.prototype.toString.call( element ) === '[object Array]') {
                return spt.xmlrpc.array(element);
            }
        }
        return spt.xmlrpc.object(element);
    }

}


//
// Serialization functions for the complex datatypes.
//
spt.xmlrpc.object = function(element)
{
    var result = '<struct>';
    for ( var member in element )
    {
        var sub_element = element[member];
        if ( sub_element == undefined ) {
            continue;
        }
        if ( typeof( sub_element ) != 'function' )
        {
            result += '<member>';
            result += '<name>' + member + '</name>';
            result += '<value>' + spt.xmlrpc.serialize(sub_element) + '</value>';
            result += '</member>';
        }
    }

    result += '</struct>';
    return result;
}


spt.xmlrpc.array = function(element)
{
    var result = '<array><data>';

    for ( var i = 0; i < element.length; i++ )
    {
        var sub_element = element[i];
        result += '<value>' + spt.xmlrpc.serialize(sub_element) + '</value>';
    }

    result += '</data></array>';
    return result;
}



spt.xmlrpc.hash = function(element)
{
    var result = '<struct>';
    for ( var member in element )
    {
        var sub_element = element[member];
        if ( sub_element == undefined ) {
            continue;
        }
        if ( typeof( sub_element ) != 'function' )
        {
            result += '<member>';
            result += '<name>' + member + '</name>';
            result += '<value>' + spt.xmlrpc.serialize(sub_element) + '</value>';
            result += '</member>';
        }
    }

    result += '</struct>';
    return result;
}



//
// Serialization functions for the String datatype.
//
spt.xmlrpc.string = function(element)
{
    var expression = '' + element;

    // process unicode
    /*
    var value = expression;
    var new_value = "";
    for ( var i = 0; i < value.length; i++ ) {
        var char = value.substr(i,1);
        var ord = String.charCodeAt(char);
        if (ord > 127) {
            char = "&#" + ord + ";";
        }
        new_value += char;
    }
    expression = new_value;
    */

    expression = expression.replace(/&/g, "&amp;");
    expression = expression.replace(/</g, "&lt;");
    expression = expression.replace(/>/g, "&gt;");



    expression = '<string>' + expression + '</string>';
    return expression
}

/**
 *  Serialization functions for the Number datatype.
 */
spt.xmlrpc.number = function(element)
{
    if ( element % 1 != 0 ) // Very crude way of determining type. May be mismatch at server.
    {
        return '<double>' + element + '</double>';
    }
    else
    {
        return '<i4>' + element + '</i4>';
    }
}

/**
 *  Serialization function for the Boolean datatype.
 */
spt.xmlrpc.boolean = function(element)
{
    if (element == true)
        element = 1;
    else
        element = 0;
    return '<boolean>' + element + '</boolean>';
}


/**
 *  Serialization function for Date datatype.
 */
spt.xmlrpc.date = function(element)
{
    return '<dateTime.iso8601>' +
       element.getFullYear() +
       ( element.getMonth() < 10 ? '0' : '' ) + element.getMonth() +
       ( element.getDay() < 10 ? '0' : '' ) + element.getDay() + 'T' +
       ( element.getHours() < 10 ? '0' : '' ) + element.getHours() + ':' +
       ( element.getMinutes() < 10 ? '0' : '' ) + element.getMinutes() + ':' +
       ( element.getMinutes() < 10 ? '0' : '' ) + element.getSeconds() + 
       '</dateTime.iso8601>'; // Phew :-)
}


