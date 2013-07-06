// *********************************************************
//
// Copyright (c) 2005-2008, Southpaw Technology
//                     All Rights Reserved
//
// PROPRIETARY INFORMATION.  This software is proprietary to
// Southpaw Technolog, and is not to be reproduced, transmitted,
// or disclosed in any way without written permission.
//
//


// DEPRECATED: moved to dg_table.js
//
// BUT: keep around because this may be used for reference if we put
// a real command system in the interface

Command = new Class({

    initialize: function(){
        return;
    },
    execute: function() {
        spt.js_log.debug("execute");
    },

    get_description: function() { return ''; },

    undo: function() {
        spt.js_log.debug("undo");
    },

    redo: function() {
        spt.js_log.debug("redo");
    }
});


// store a list of commands that have been executed
Command.commands = [];
Command.command_index = -1;
Command.execute_cmd = function(cmd) {
    cmd.execute();

    try {
        var description = cmd.get_description();
        spt.js_log.debug( "CMD: " + description);
    } catch(e) {
        spt.js_log.debug( "No description" );
    }
    // FIXME: do not add to undo just yet
    //this.add_to_undo(cmd);
}


Command.add_to_undo = function(cmd) {

    // remove old commands
    for (var i=Command.commands.length;i>Command.command_index+1;i--) {
        Command.commands.pop();
    }

    Command.commands.push(cmd);
    Command.command_index += 1;
}





Command.undo_last = function() {
    if (Command.command_index == -1) {
        alert("Nothing to undo");
        return;
    }

    var cmd = Command.commands[Command.command_index];
    cmd.undo();
    Command.command_index -= 1;
    
}



Command.redo_last = function() {

    if (Command.command_index == Command.commands.length-1) {
        alert("Nothing to redo");
        return;
    }

    var cmd = Command.commands[Command.command_index+1];
    cmd.redo();
    Command.command_index += 1;
    
}





Command.undo_all = function() {
    for (var i = Command.commands.length-1; i >= 0; i--) {
        var cmd = Command.commands[i];
        cmd.undo();
    }
}


Command.test = function() {
    for (var i=0; i < 5; i++) {
        var cmd = new Command();
        Command.execute_cmd(cmd);
    }

    // undo all of the commands
    Command.undo_all()

}


