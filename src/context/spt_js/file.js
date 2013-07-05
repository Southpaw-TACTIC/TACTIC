// -----------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// ----------------------------------------------------------------------------


spt.file = {}

spt.file.expand_paths = function(path, file_range)
{
    //file_range = '1-100/3';
    //path = "/home/apache/frame####.png";

    parts = file_range.split(/[-\/]/);
    var start_frame = parts[0];
    start_frame = parseInt(start_frame);
    var end_frame = parts[1];
    end_frame = parseInt(end_frame);

    var by_frame;
    if (parts.length == 3) {
        by_frame = parts[2];
        by_frame = parseInt(by_frame);
    }
    else {
        by_frame = 1;
    }


    var start = path.indexOf("#");
    var end = path.lastIndexOf("#");
    var length = end - start + 1;

    var expanded_paths = [];

    for (var i = start_frame; i <= end_frame; i += by_frame) {

        var num = spt.zero_pad(i, length);

        expanded_path = path.replace(/#+/, num);
        expanded_paths.push(expanded_path);
    }

    return expanded_paths;

}

spt.url = {}

// check if a url file exists 
spt.url.exists = function(url){
    var request = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP"); 
    request.open("HEAD", url, false);
    request.send();
    return (request.status==404) ? false : true;
}    


