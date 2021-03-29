


upload_files = (kwargs) => {
    if (!kwargs) {
        kwargs = {};
    }

    let files = kwargs.files;
    if (!files || !files.length) {
        return;
    }
    // callbacks
    let upload_start = kwargs.upload_start;
    let upload_complete = kwargs.upload_complete;
    let upload_progress = kwargs.upload_progress;
    let upload_failed = kwargs.upload_failed;

    let server = kwargs.server;
    if (!server) {
        //server = TACTIC.get();
        alert("No server defined");
        return;
    }

    let login_ticket = server.ticket;
    if (!login_ticket) {
        login_ticket = server.login_ticket;
    }
    let site = server.site;
    let server_url = server.server_url;
    if (!server_url) {
        server_url = server.server_name;
    }


    if (!login_ticket) {
        alert("No ticket for upload");
    }
    let upload_dir = kwargs.upload_dir;
    if(!upload_dir){
        upload_dir = "";
    }


    // build the form data structure
    let fd = new FormData();
    for (let i = 0; i < files.length; i++) {
        fd.append("file"+i, files[i]);
        var name = files[i].name;
        var path = files[i].path;
        fd.append("file_name"+i, name);
        if (path) {
            fd.append("file_path"+i, path);
        }
    }
    fd.append("num_files", files.length);
    fd.append('login_ticket', login_ticket);
    fd.append('upload_dir',upload_dir)


    // event listeners

    let xhr = new XMLHttpRequest();
    if (upload_start) {
        xhr.upload.addEventListener("loadstart", upload_start, false);
    }
    if (upload_progress) {
        xhr.upload.addEventListener("progress", upload_progress, false);
    }
    if (upload_complete) {
        xhr.addEventListener("load", upload_complete, false);
    }
    if (upload_failed) {
        xhr.addEventListener("error", upload_failed, false);
        xhr.addEventListener("abort", upload_failed, false);
    }

    xhr.addEventListener('readystatechange', function(evt) {
    } )


    xhr.addEventListener("abort", function() {alert("abort")}, false);

    //xhr.withCredentials = true;
    //alert("/tactic/"+site+"/default/UploadServer/");
    let full_url;
    if (!server_url) {
        server_url = "";
    }
    if (site && site !== "default") {
        full_url = server_url+"/tactic/"+site+"/default/UploadServer/";
    }
    else {
        full_url = server_url+"/tactic/default/UploadServer/";
    }

    xhr.open("POST", full_url, true);
    xhr.send(fd);
}


