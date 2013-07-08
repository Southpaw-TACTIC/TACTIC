import sys, os, shutil, getopt

from tactic_client_lib import TacticServerStub

SEARCH_TYPE = "prod/shot"

def copy_file(file_paths, new_dir):
    '''copy file to the handoff dir'''
    new_file_paths = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        new_file_path = '%s/%s' %(new_dir, file_name)
        #shutil.move(file_path, new_file_path)
        shutil.copy(file_path, new_file_path)
        print new_file_path
        if not os.path.exists(new_file_path):
            print "[%s] does not exist!!!" % new_file_path
        new_file_paths.append(new_file_path)
    return new_file_paths

def expand_paths( file_path, file_range ):
    '''expands the file paths, replacing # as specified in the file_range'''
    file_paths = []
    
    # frame_by is not really used here yet
    frame_by = 1
    if file_range.find("/") != -1:
        file_range, frame_by = file_range.split("/")
    frame_start, frame_end = file_range.split("-")
    frame_start = int(frame_start)
    frame_end = int(frame_end)
    frame_by = int(frame_by)

    # find out the number of #'s in the path
    padding = len( file_path[file_path.index('#'):file_path.rindex('#')] )+1

    for i in range(frame_start, frame_end+1, frame_by):
        expanded = file_path.replace( '#'*padding, str(i).zfill(padding) )
        file_paths.append(expanded)

    return file_paths

    

def main(args, login=None):
    # USAGE: checkin_render.py   
    type = args[0]
    if type == "shot":
        parent_search_type = "prod/shot"
    elif type == "asset":
        parent_search_type = "prod/asset"
    

    else:
        parent_search_type = type

    code = args[1]
    file_range = args[2]
    pattern = args[3]
    layer_name = ''
    context = 'publish'

    if type == "layer":
        parent_search_type = "prod/layer"
        code, layer_name = args[1].split('|')
        
    server = TacticServerStub(login)

    # do the actual work
    server.start("Checked in file group [%s] to %s [%s]" % (pattern,type,code))

    try:
        # checkin the uploaded file  
        filters = []
        if type=='layer':
            filters.append(('shot_code', code))
            filters.append(('name', layer_name))
        else:
            filters.append(('code', code))
        results = server.query(parent_search_type, filters)
       
        # take the first one
        if results:
            id = results[0].get('id')
        else:
            if type =='layer':
                print "%s Code [%s] name [%s] not found. Please insert an entry in TACTIC first." %(type, code, layer_name)
            else:
                print "%s Code [%s] not found. Please insert an entry in TACTIC first." %(type, code)
        search_type = server.build_search_type(parent_search_type)
        file_type = 'main'
        render_type = '' # not used yet
        # move the file
        dir = server.get_handoff_dir()
        paths = expand_paths(pattern, file_range)
        copy_file(paths, dir)

        file_name = os.path.basename(pattern)
        new_pattern =  '%s/%s' %(dir, file_name)
        print "Copied files to handoff dir\n"
        render = find_render(server, search_type, id, login, render_type)
        if not render:
            render_data = {
                'search_type': search_type,
                'search_id': id,
                'login': login
                #'type': render_type
            }
            render = server.insert("prod/render", render_data)
        
        # run group checkin
        server.group_checkin(render.get("__search_key__"), context=context, file_path=new_pattern, file_type=file_type, file_range=file_range)
        
    except:
        server.abort()
        raise
    else:
        server.finish()


def find_render(server, search_type, id, login, type):
    render = None
    filters = []
    filters.append(('search_type', search_type))
    filters.append(('search_id', id))
    filters.append(('login', login))
    #filters.append(('type', type))
    results = server.query('prod/render', filters)
    if results:
        render = results[0]
    return render

if __name__ == '__main__':
    
    executable = sys.argv[0]
    login = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:h", ["login=","help"])
    except getopt.error, msg:
        print msg
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-l", "--login"):
            login = a
            print 
        if o in ("-h", "--help"):
            print "python checkin_render.py -l <tactic_login> <type> <code> <file_range> <file_pattern>"
            print "python checkin_render.py -l admin shot S0001 1-20 D:/file_dir/plates.####.png"
    if not login:
        print "-l <tactic_login> is required for this script"
        print "python checkin_render.py -l <tactic_login> <type> <code> <file_range> <file_pattern>"
        sys.exit(2)
    if len(args) != 4:
        print "python checkin_render.py -l <tactic_login> <type> <code> <file_range> <file_pattern>"
        print "python checkin_render.py -l admin shot S0001 1-20 D:/file_dir/render.####.png"
        print 'python checkin_render.py -l admin layer "S0001|diffuse_layer" 1-20 D:/file_dir/render.####.png'
        sys.exit(2)
    main(args, login=login)
