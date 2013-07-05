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


function EventContainer()
{
    this.events = []

    this.register_listener = function(event_name, callback, replace)
    {
        // if the event does not exist
        if (this.events[event_name] == null)
        {
            this.events[event_name] = []
        }

        var callbacks = this.events[event_name]
        var unique = true
        for ( var i =0; i <callbacks.length; i++ )
        {
            // this doesn't filter out callback that are dynamically created
            // thru ajax loading. TODO: compare the contents enclosed in { }
            if (callbacks[i] == callback.toString())
            {
                //alert("duplicated callback detected. Callback [" + callback
                //    + "] will not be registered.")
                unique = false   
                break
            }
        }
            
        if (unique)
        {
            // it's resetting the array first
            if (replace)
                this.events[event_name] = []
            this.events[event_name].push(callback)
        }
    }



    this.call_event = function(event_name)
    {
        var callbacks = this.events[event_name]
        if (callbacks == null)
        {
            //alert("Event ["+event_name+"] does not exist")
            return true;
        }

        for (var i = 0; i < callbacks.length; i++ )
        {
            var func = this.events[event_name][i]
            if (func != null)
                func()
                
        }

    }


}
// static functions

EventContainer.container = EventContainer()

// get the singleton
EventContainer.get = function()
{
    if (EventContainer.container == null)
    {
        EventContainer.container = new EventContainer()
    }
    return EventContainer.container
}

// reset the event container
EventContainer.reset = function()
{
    EventContainer.container = new EventContainer()
}






