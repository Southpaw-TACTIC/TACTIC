// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
//   Place all added functionality to existing Javascript Objects here ...
// -------------------------------------------------------------------------------------------------------------------

// Added String object functionality ...

String.prototype.strip = function()
{
    return this.replace( /\s+$/, "" ).replace( /^\s+/, "" );
}


String.prototype.lstrip = function()
{
    return this.replace( /^\s+/, "" );
}


String.prototype.rstrip = function()
{
    return this.replace( /\s+$/, "" );
}


String.prototype.contains_word = function( word_str )
{
    // find if word is in str_text but only if it is a full single word in that string
    var regex = new RegExp( "\\b" + word_str + "\\b" );
    var match = this.match( regex );
    if( match ) {
        return true;
    }
    return false;
}





// -------------------------------------------------------------------------------------------------------------------
//   Name space ("spt") for all Southpaw Tech functionality within JavaScript ...
// -------------------------------------------------------------------------------------------------------------------

var spt = {};  // establish name-space for all new Southpaw Tech TACTIC javascript


// -------------------------------------------------------------------------------------------------------------------
//  Browser Information tools ...
// -------------------------------------------------------------------------------------------------------------------

spt.browser = {};

spt.browser.is_IE = function() {
    return( spt.browser._info.specific_browser == 'IE' );
}
spt.browser.is_Firefox = function () {
    return( spt.browser._info.specific_browser == 'firefox' );
}
spt.browser.is_Safari = function () {
    return( spt.browser._info.specific_browser == 'safari' );
}
spt.browser.is_Chrome = function () {
    return( spt.browser._info.specific_browser == 'google_chrome' );
}
spt.browser.is_Seamonkey = function () {
    return( spt.browser._info.specific_browser == 'seamonkey' );
}
spt.browser.is_SeaMonkey = spt.browser.is_Seamonkey ;
spt.browser.is_Opera = function () {
    return( spt.browser._info.specific_browser == 'opera' );
}
spt.browser.is_Qt = function () {
    return( spt.browser._info.specific_browser == 'Qt' );
}

spt.browser.is_Mozilla_based = function () {
    return( spt.browser._info.browser == 'mozilla' );
}
spt.browser.is_Webkit_based = function () {
    return( spt.browser._info.browser == 'webkit' );
}

spt.browser.os_is_MacOsx = function() {
    return( spt.browser._info.client_os == 'mac_osx' );
}
spt.browser.os_is_Windows = function() {
    return( spt.browser._info.client_os == 'nt' );
}
spt.browser.os_is_Linux = function() {
    return( spt.browser._info.client_os == 'linux' );
}
spt.browser.os_is_iOS = function() {
    return( spt.browser._info.client_os == 'apple_ios' );
}


spt.browser._TOUCH_DEVICES = {
    'apple_ios': true,
    'android': true
};

spt.browser.is_touch_device = function() {
    if( spt.browser._info.client_os in spt.browser._TOUCH_DEVICES ) {
        return true;
    }
    return false;
}


spt.browser._info = {};

spt.browser._set_info = function()
{
    // Set BROWSER ...
    //
    var specific_browser = '-UNKNOWN-';
    var browser = '-UNKNOWN-';

    if( window.navigator.userAgent.match( /MSIE/ ) ) {
        specific_browser = 'IE';
        browser = 'IE';
    }
    else if( window.navigator.userAgent.match( /Qt/ ) ) {
        specific_browser = 'Qt';
        browser = 'webkit';
    }
    else if( window.navigator.userAgent.match( /Firefox/ ) ) {
        specific_browser = 'firefox';
        browser = 'mozilla';
    }
    else if( window.navigator.userAgent.match( /Chrome/ ) ) {
        specific_browser = 'google_chrome';
        browser = 'webkit';
    }
    else if( window.navigator.userAgent.match( /Safari/ ) ) {
        specific_browser = 'safari';
        browser = 'webkit';
    }
    else if( window.navigator.userAgent.match( /SeaMonkey/ ) ) {
        specific_browser = 'seamonkey';
        browser = 'mozilla';
    }
    else if( window.navigator.userAgent.match( /Opera/ ) ) {
        specific_browser = 'opera';
        browser = 'opera';
    }

    spt.browser._info[ 'specific_browser' ] = specific_browser;
    spt.browser._info[ 'browser' ] = browser;


    // Set Client OS ...
    //
    var client_os = 'linux';  // default to linux

    if( window.navigator.userAgent.match( /Windows/ ) ) {
        client_os = 'nt';
    }
    else if( window.navigator.userAgent.match( /Linux/ ) ) {
        client_os = 'linux';
    }
    else if( window.navigator.userAgent.match( /like Mac OS X/ ) ) {
        client_os = 'apple_ios';
    }
    else if( window.navigator.userAgent.match( /Mac OS X/ ) ) {
        client_os = 'mac_osx';
    }
    else if( window.navigator.userAgent.match( /Android/ ) ) {
        client_os = 'android';
    }

    spt.browser._info[ 'client_os' ] = client_os;
}


// RUN browser information setup!!! Need to run this here, before checks for IE below occur!
//
spt.browser._set_info();


spt.browser.show_info = function()
{
    var nav = window.navigator;

    spt.js_log.debug( " " );
    spt.js_log.debug( " " );
    spt.js_log.debug( ":::::::: window.navigator properties for this browser ..." );
    spt.js_log.debug( " " );

    for( var prop in nav ) {
        if( typeof nav[ prop ] == "string" || typeof nav[ prop ] == "boolean" ) {
            var value = "";
            if( typeof nav[ prop ] == "string" ) { value = '"' + nav[ prop ] + '"'; }
            else { value = nav[ prop ]; }
            spt.js_log.debug( ":: navigator." + prop + " = " + value );
        }
    }

    spt.js_log.debug( " " );
    spt.js_log.debug( " " );
}


// -------------------------------------------------------------------------------------------------------------------
//  Some low level tools ...
// -------------------------------------------------------------------------------------------------------------------


// --- On an element object (normal OR Mootified), you can add a new Javascript property to it
//     (e.g. moo_el.my_random_prop = "Hi";) ... HOWEVER, in IE you CANNOT delete it as you would normally
//     delete a Javascript object property ... e.g.
//
//         delete el.my_random_prop;  // this errors in IE
//
//         delete el["my_random_prop"];  // this errors in IE
//
//     ... so use this function below for any property deletions on any (to be safe) element object. If the
//     object is a straight Javascript object (e.g. my_obj = {};) then it is safe to use "delete" as above.
//

spt.delete_object_property = function() {};

if( spt.browser.is_IE() ) {
    spt.delete_object_property = function( obj, property_name ) {
        if( property_name in obj ) { obj[ property_name ] = null; }
    };
} else {
    spt.delete_object_property = function( obj, property_name ) {
        if( property_name in obj ) { delete obj[ property_name ]; }
    };
}


