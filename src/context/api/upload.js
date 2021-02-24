


let upload_file = (kwargs) => {

    if (!kwargs) {
        kwargs = {};
    }
 
    let files = kwargs.files;
    if (!files || !files.length) {
        return;
    }

    let upload_start = kwargs.upload_start;
    let upload_complete = kwargs.upload_complete;
    let upload_progress = kwargs.upload_progress;
    let upload_failed = kwargs.upload_failed;

    let sandbox_data = kwargs.sandbox_data;

    let transaction_ticket = sandbox_data.ticket;
    let site = sandbox_data.site;
    let server_url = sandbox_data.server_url;

    //let transaction_ticket = kwargs.ticket;
    //let transaction_ticket = "XYZ123";
    //let site = null;
    //let server_url = "http://192.168.115.129";

    if (!transaction_ticket) {
        alert("No ticket for upload");
        //let server = TacticServerStub.get();
        //transaction_ticket = server.get_transaction_ticket();
    }
    let upload_dir = kwargs.upload_dir;
    if(!upload_dir){
        upload_dir = "";
    }

   
    // build the form data structure
    let fd = new FormData();
    for (let i = 0; i < files.length; i++) {
        //console.log(files[i]);
        fd.append("file"+i, files[i]);
        var name = files[i].name;
        var path = files[i].path;
        fd.append("file_name"+i, name);
        fd.append("file_path"+i, path);
    }
    fd.append("num_files", files.length);
    fd.append('login_ticket', transaction_ticket);
    fd.append('upload_dir',upload_dir)
   

    /* event listeners */

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
        //console.log(evt);
        //console.log(this.readyState);
        //console.log(this.status);
    } )


    //xhr.addEventListener("abort", uploadCanceled, false);
    xhr.addEventListener("abort", function() {alert("abort")}, false);

    //xhr.withCredentials = true;

    //alert("/tactic/"+site+"/default/UploadServer/");
    let full_url;
    if (site && site !== "default") {
        full_url = server_url+"/tactic/"+site+"/default/UploadServer/";
    }
    else {
        full_url = server_url+"/tactic/default/UploadServer/";
    }

    xhr.open("POST", full_url, true);
    xhr.send(fd);

}


export { upload_file };


