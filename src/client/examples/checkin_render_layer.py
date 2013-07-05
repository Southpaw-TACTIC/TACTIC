import sys, os, shutil, getopt

from tactic_client_lib import TacticServerStub

SEARCH_TYPE = "prod/render"

def move_file(file_paths, new_dir):
    '''move file to the handoff dir'''
    new_file_paths = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        new_file_path = '%s/%s' %(new_dir, file_name)
        shutil.move(file_path, new_file_path)
        '''
        while not os.path.exists(new_file_path):
            sys.stdout.write('.')
        '''
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
    # USAGE: checkin_render_layer.py   
    shot_code = args[0]
    layer_name = args[1]
    version = args[2]
    context = args[3]
    file_range = args[4]
    pattern = args[5]

    server = TacticServerStub(login)

    # do the actual work
    server.start("Checked in file group [%s] to shot [%s] layer [%s]" % (pattern, shot_code, layer_name))
    try:
        # move the file
        dir = server.get_handoff_dir()
        paths = expand_paths(pattern, file_range)
        move_file(paths, dir)

        file_name = os.path.basename(pattern)
        new_pattern =  '%s/%s' %(dir, file_name)
        print "Files moved to handoff dir.\n"
        
        # checkin the moved files  
        filters = []
        filters.append(('shot_code', shot_code))
        filters.append(('name', layer_name))
        results = server.query('prod/layer', filters)
        
        # take the first one
        if results:
            id = results[0].get('id')

        search_type = server.build_search_type('prod/layer')
        # find the layer snapshot
        filters = []
        filters.append(('version', version))
        filters.append(('search_type', search_type))
        filters.append(('search_id', id))
        #TODO : may need a context to search for the proper layer
        results = server.query('sthpw/snapshot', filters)
        snap_code = ''
        if results:
            snap_code = results[0].get('code')
        
        # find the render
        render = None
        filters = []
        filters.append(('search_type', search_type))
        filters.append(('search_id', id))
        filters.append(('snapshot_code', snap_code))
        results = server.query(SEARCH_TYPE, filters)
        if results:
            render = results[0]

        if not render:
            render_data = {
                'search_type': search_type,
                'search_id': id,
                'snapshot_code': snap_code
            }

            render = server.insert("prod/render", render_data)
        '''
        results = server.query(SEARCH_TYPE, filters)
        render_id = 0
        if results:
            render_id = results[0].get('id')
        # find the render id    
        search_key = server.build_search_key(SEARCH_TYPE, render_id, column='id')
        '''
        file_type = 'main'
        
        # run group checkin
        server.group_checkin(render.get("__search_key__"), context=context, file_path=new_pattern, file_type=file_type, file_range=file_range)
        
    except:
        server.abort()
        raise
    else:
        server.finish()

if __name__ == '__main__':
    executable = sys.argv[0]
    #args = sys.argv[1:]
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
        if o in ("-h", "--help"):
            print "python checkin_render_layer.py <shot_code> <layer_name> <version> <context> <file_range> <file_pattern>"
            print "python checkin_render_layer.py S0001 layer1 1 lgt 1-20 D:/file_dir/plates.####.png"
            sys.exit(0)
    print args, len(args)
    if len(args) != 6:
        print "python checkin_render_layer.py <shot_code> <layer_name> <version> <context> <file_range> <file_pattern>"
        print "python checkin_render_layer.py S0001 layer1 1 lgt 1-20 D:/file_dir/plates.####.png"
        sys.exit(2)
    main(args, login=login)

