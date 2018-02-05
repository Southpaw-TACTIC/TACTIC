############################################################
#
#    Copyright (c) 2013, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

import tacticenv


from pyasm.common import Common, TacticException, Config

import os, subprocess, time, re, os



class RSyncConnectionException(Exception):
    pass



class RSync(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.paths = []
        self.data = {}

    def get_paths(self):
        return self.paths

    def get_data(self):
        return self.data


    def execute(self):
        base_dir = self.kwargs.get("base_dir")

        relative_dir = self.kwargs.get("relative_dir")

        # if not file_name is given, then the default is to recurse through
        # relative_dir
        file_name = self.kwargs.get("file_name")
        if not file_name:
            file_name = ""

        from_paths = []

        relative_paths = self.kwargs.get("relative_paths")
        from_path = self.kwargs.get("from_path")


        # support multiple relative paths
        if relative_paths:
            for relative_path in relative_paths:
                from_path = "%s/./%s" % (base_dir, relative_path)
                from_paths.append(from_path)

        elif from_path:
            from_paths.append(from_path)


        else:
            from_path = "%s/./%s/%s" % (base_dir, relative_dir, file_name)
            from_paths.append(from_path)



        # base to dir (should be to_dir, not to_path)
        to_path = self.kwargs.get("to_path")
        if not to_path:
            to_path = self.kwargs.get("to_dir")




        tries = 1
        success = False
        value = ""
        start = time.time()

        message_key = self.kwargs.get("message_key")

        while 1:
            try:
                value = self.sync_paths(from_paths, to_path)
                success = True
                break
            except RSyncConnectionException as e:
                time.sleep(60)

                from tactic_client_lib import TacticServerStub
                server = TacticServerStub.get()
                server.log_message(message_key, {"message": str(e)}, "error_retry")
                continue

            except Exception as e:
                print "Failed on try [%s]..." % tries
                raise

                # ping the server to see

                if message_key:
                    from tactic_client_lib import TacticServerStub
                    server = TacticServerStub.get()
                    server.log_message(message_key, {"message": str(e)}, "error_retry")

                time.sleep(tries)
                if tries == 3:
                    break

                tries += 1




        #print "success: ", success
        #print time.time() - start, " seconds"
        #print value



    def get_current_data(self):
        return self.current_data


    def get_data(self):
        return self.data


    def sync_paths(self, from_paths, to_path):

        server = self.kwargs.get("server")
        login = self.kwargs.get("login")
        paths = self.kwargs.get("paths")
        base_dir = self.kwargs.get("base_dir")

        paths_sizes = []
        if paths:
            for path in paths:
                full_path = "%s/%s" % (base_dir, path)
                print "full_path: ", full_path
                size = os.path.getsize(full_path)
                paths_sizes.append(size)


        if server:
            to_path = "%s@%s:%s" % (login, server, to_path)

        if os.name == "nt":
            # This assumes we are using the cygwin implementation of RSync
            if to_path[1] == ":":
                # then this is a drive letter
                drive_letter = to_path[0]
                to_path = "/cygdrive/%s/%s" % (drive_letter, to_path[3:])

            for i, from_path in enumerate(from_paths):
                if from_path[1] == ":":
                    # then this is a drive letter
                    drive_letter = from_path[0]
                    from_path = "/cygdrive/%s/%s" % (drive_letter, from_path[3:])
                from_paths[i] = from_path

            to_path = to_path.replace("\\", '/')
            from_path = from_path.replace("\\", '/')


        rsync = Config.get_value("services", "rsync")
        if not rsync:
            rsync = Common.which("rsync")

        if not rsync:
            raise Exception("RSync executable could not be found")


        cmd_list = []
        cmd_list.append(rsync)
        flags = "-az"
        cmd_list.append(flags)
        if server:
            cmd_list.append("-e ssh")
        cmd_list.append("-v")
        cmd_list.append("--progress")

        delete = False
        if delete:
            cmd_list.append("--delete")

        dry_run = self.kwargs.get("dry_run")
        if dry_run in [True, 'true']:
            cmd_list.append("--dry-run")

        relative = True
        if relative:
            cmd_list.append("--relative")

        partial = True
        if partial:
            cmd_list.append("--partial")


        for from_path in from_paths:
            cmd_list.append('%s' % from_path)

        cmd_list.append('%s' % to_path)

        print "exec: ", " ".join(cmd_list)

        program = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        #program.wait()

        message_key = self.kwargs.get("message_key")

        progress = RSyncProgress(
                message_key=message_key,
                paths=paths,
                paths_sizes=paths_sizes
        )

        on_update = self.kwargs.get("on_update")
        if not on_update:
            on_update = progress.on_update
        assert(on_update)

        on_complete = self.kwargs.get("on_complete")
        if not on_complete:
            on_complete = progress.on_complete
        assert(on_complete)

        on_error = self.kwargs.get("on_error")
        if not on_error:
            on_error = progress.on_error
        assert(on_error)



        data = []
        lines = []
        path = None
        self.paths = []
        error = []
        #while program.poll() is None:
        buffer = []
        line = ""
        while 1:
            char = program.stdout.read(1)
            if not char:
                break

            if char == "\n":
                line = "".join(buffer)

            else:
                buffer.append(char)
            

            if line:
                lines.append(line)
                if line.startswith(" "):

                    line = line.strip()
                    parts = re.split( re.compile("\ +"), line )

                    self.current_data = {
                        "bytes": int(parts[0]),
                        "percent": parts[1],
                        "rate": parts[2],
                        "time_left": parts[3]
                    }
                    #print self.current_data
                    #print "status: ", line

                    if on_update:
                        on_update(path, self.current_data)

                elif line.startswith("rsync "):
                    error.append(line)
                elif line.startswith("rsync: "):
                    error.append(line)
                elif line.startswith("deleting "):
                    self.handle_data_line(line)
                elif line.startswith("sent "):
                    self.handle_data_line(line)
                elif line.startswith("total "):
                    self.handle_data_line(line)
                elif line.startswith("sending incremental "):
                    self.handle_data_line(line)
                elif line.startswith("created directory "):
                    self.handle_data_line(line)
                else:
                    line = line.strip()
                    path = line
                    if not line.endswith("/"):
                        if line.find(" -> ") != -1:
                            parts = line.split(" -> ")
                            line = parts[0]

                        self.paths.append(line)
    
                # reset the line
                line = None
                buffer = []



        if error:
            error = "\n".join(error)
            if error.startswith("rsync: connection unexpectedly closed"):
                raise RSyncConnectionException(error) 

            if on_error:
                on_error(path, {"message": error})
            raise Exception("Sync Error\n%s" % error)


        if on_complete:
            on_complete(path, {"message": "All files synchronized"})


        return "success"



    def handle_data_line(self, line):

        if line.startswith("sent "):
            # sent 520 bytes  received 22 bytes  361.33 bytes/sec
            pass

        elif line.startswith("total "):
            #total size is 431666  speedup is 796.43 (DRY RUN)
            parts = line.split()
            total_size = parts[3]
            total_size = int(total_size)
            self.data['total_size'] = total_size




class RSyncProgress(object):
    def __init__(self, **kwargs):
        from tactic_client_lib import TacticServerStub
        self.server = TacticServerStub.get()
        self.message_key = kwargs.get("message_key")
        self.paths = kwargs.get("paths")
        self.paths_sizes = kwargs.get("paths_sizes")
        if not self.paths:
            self.paths = []

    def on_update(self, path, data):
        data['path'] = path

        bytes = data.get("bytes")

        try:
            index = self.paths.index(path)
        except:
            index = 0
        data["path_index"] = index+1
        data["paths_count"] = len(self.paths)
        data["paths_sizes"] = self.paths_sizes

        total_size = 0
        current_size = 0
        for i in range(0, len(self.paths)):
            if i < index:
                current_size += self.paths_sizes[i]
            elif i == index:
                current_size += bytes

            total_size += self.paths_sizes[i]

        #print "current_size: ", current_size
        #print "total_size: ", total_size
        #print "percent: ", (current_size*1000)/(total_size*10)
        if total_size:
            total_percent = (current_size*1000)/(total_size*10)
        else:
            total_percent = 0
        data['total_percent'] = total_percent


        if self.message_key:
            self.server.log_message(self.message_key, data, status="in_progress")


    def on_error(self, path, data):
        if self.message_key:
            self.server.log_message(self.message_key, data, status="error")

    def on_complete(self, path, data):
        if self.message_key:
            self.server.log_message(self.message_key, data, status="complete")



if __name__ == '__main__':

    import time

    from_path = "/home/tactic/svg"


    start = time.time()

    dir_info = Common.get_dir_info(from_path)
    print "dir_info: ", dir_info
    total_size = dir_info.get("size")


    from pyasm.security import Batch
    Batch()


    class Progress(object):
        def __init__(self):
            self.total_sent = 0

        def on_update(self, path, data):
            from tactic_client_lib import TacticServerStub
            server = TacticServerStub.get()
            data['path'] = path

            bytes = data.get("bytes")
            self.total_sent += bytes

            print "path: ", path
            print "total: ", self.total_sent

            server.log_message("wow", data)
    progress = Progress()



    kwargs = {
            "login": "root",
            "server": "sync1.southpawtech.com",
            "from_path": from_path,
            "to_path": "/spt/test/svg",
            "on_update": progress.on_update
    }
    cmd = RSync(**kwargs)

    cmd.execute()


