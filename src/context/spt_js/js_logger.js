// -------------------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// -------------------------------------------------------------------------------------------------------------------


// -------------------------------------------------------------------------------------------------------------------
// JavaScript Logger
//
//   Has log levels same as Python Logger. Simply call spt.js_log.info("blah blah blah") or spt.js_log.info("hello")
//   in your javascript code.
//
//   Output goes to a div with ID "spt_js_log_output_div", if one exists.
//
//   If console.log is defined then logging output will go to the defined console as well.
// -------------------------------------------------------------------------------------------------------------------

spt.js_log = {};

spt.js_log._log_level_map = { "CRITICAL" : 50,
                              "ERROR" : 40,
                              "WARNING" : 30,
                              "INFO" : 20,
                              "DEBUG" : 10,
                              "NOTSET" : 0 };

spt.js_log.output_div = null;
spt.js_log.popup_div = null;
spt.js_log.log_level = spt.js_log._log_level_map[ "NOTSET" ];
spt.js_log._buffer = [];


spt.js_log.setup = function()
{
    if( ! spt.js_log.hasOwnProperty("console_log_available") ) {
        try {
            console.log("Checking for 'console.log()' ...");
            spt.js_log.console_log_available = true;
            console.log("... 'console.log()' enabled!"); 
        }
        catch(e) {
            spt.js_log.console_log_available = false;
        }
    }

    var js_log_el = document.id("spt_js_log_output_div");
    if( js_log_el )
    {
        spt.js_log.output_div = js_log_el;
        spt.js_log.popup_div  = js_log_el.getParent("#WebClientOutputLogPopupWdg")

        var log_level = js_log_el.getAttribute( "spt_log_level" );
        if( log_level && log_level in spt.js_log._log_level_map ) {
            spt.js_log.log_level = spt.js_log._log_level_map[ log_level ];
        }
        else {
            spt.js_log.log_level = spt.js_log._log_level_map[ "NOTSET" ];
        }

        js_log_el.innerHTML = spt.js_log._buffer.join('<br/>') + '<br/>';
    }
}


spt.js_log.toggle_display = function( use_safe_position )
{
    if( ! spt.js_log.output_div ) {
        spt.js_log.setup();
    }
    spt.popup.toggle_display( spt.js_log.popup_div, use_safe_position );
}


spt.js_log.show = function( use_safe_position )
{
    if( ! spt.js_log.output_div ) {
        spt.js_log.setup();
    }
    spt.popup.open( spt.js_log.popup_div, use_safe_position );
}


spt.js_log.hide = function()
{
    if( spt.js_log.popup_div ) {
        spt.js_log.popup_div.setStyle("display","none");
    }
}

// SHORTCUT name-space for log message printing ...
var log = {};

spt.js_log.critical = function( msg )
{
    spt.js_log._print( spt.js_log._log_level_map[ "CRITICAL" ], msg );
}
log.critical = spt.js_log.critical;


spt.js_log.error = function( msg )
{
    spt.js_log._print( spt.js_log._log_level_map[ "ERROR" ], msg );
}
log.error = spt.js_log.error;


spt.js_log.warning = function( msg )
{
    spt.js_log._print( spt.js_log._log_level_map[ "WARNING" ], msg );
}
log.warning = spt.js_log.warning;


spt.js_log.info = function( msg )
{
    spt.js_log._print( spt.js_log._log_level_map[ "INFO" ], msg );
}
log.info = spt.js_log.info;


spt.js_log.debug = function( msg )
{
    spt.js_log._print( spt.js_log._log_level_map[ "DEBUG" ], msg );
}
log.debug = spt.js_log.debug;


spt.js_log._print = function( msg_log_level, msg )
{
    if( ! spt.js_log.output_div ) { spt.js_log.setup(); }

    if( spt.js_log.log_level > msg_log_level ) { return; }

    if( spt.js_log.console_log_available ) {
        console.log( msg );
    }

    // in case an object is passed in through parameter msg, we convert it to a string for
    // output to the Output Console ...
    msg = "" + msg;

    if( spt.js_log.output_div ) {
        // Create a <pre> element block to add the message text to and then append it as a
        // child to the log output div ...
        //
        var pre_el = document.createElement("pre");
        pre_el.innerHTML = msg;
        pre_el.style.marginTop = "0px";
        pre_el.style.marginBottom = "0px";
        spt.js_log.output_div.appendChild(pre_el);

        var h = spt.js_log.output_div.clientHeight;
        var sh = spt.js_log.output_div.scrollHeight;
        if( sh > h ) {
            spt.js_log.output_div.scrollTop = sh - h;
        }
    }
    else {
        spt.js_log._buffer.push( msg );
    }
}


spt.js_log.test_perf = function()
{
    spt.timer.start( "JS_LOG_TEST_PERF" );

    var num = 100;

    for( var c=0; c < num; c++ ) {
        spt.js_log.debug( "     Definitely Running like <span style='font-weight: bold; color: red;'>crazy</span> " +
                          " over this whole thing.\nif( x < 10 && x > 5 ) {};  &lt;TEST&gt; <tag> ...\n" );
    }

    spt.timer.stop( "JS_LOG_TEST_PERF" );
    spt.timer.print_timers();
}




