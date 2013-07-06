import sys, os, shutil, getopt

from tactic_client_lib import TacticServerStub

SEARCH_TYPE = "prod/plate"


    

def main(args, login=None):
    # USAGE: checkin_plates.py   
    code = args[0]
    file_range = args[1]
    pattern = args[2]
    # hard-coded for now
    context = 'publish'
    server = TacticServerStub(login)

    # do the actual work
    server.start("Checked in file group [%s]" % pattern)
    try:
        

        # checkin the uploaded file  
        filters = []
        filters.append(('code', code))
        results = server.query(SEARCH_TYPE, filters)
        # take the first one
        if results:
            id = results[0].get('id')
        else:
            print "Plate with code [%s] not found. Please insert an entry in the Plates tab first." %code
            return
        search_key = server.build_search_key(SEARCH_TYPE, id, column='id')


        # move the file
        dir = server.get_handoff_dir()
        print "Copied files to handoff dir\n"
        new_pattern = pattern
        file_type = 'main'
        
        # run group checkin
        server.group_checkin(search_key, context, file_path=new_pattern, file_type=file_type, \
                file_range=file_range, mode='copy', info={'type':'2d_plates'})
        
    except:
        server.abort()
        raise
    else:
        server.finish()

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
            print "python checkin_plates.py [-l <tactic_login>] <code> <file_range> <file_pattern>"
            print "python checkin_plates.py S0001 1-20 D:/file_dir/plates.####.png"
    if len(args) != 3:
        print "python checkin_plates.py <code> <file_range> <file_pattern>"
        print "python checkin_plates.py S0001 1-20 D:/file_dir/plates.####.png"
        sys.exit(2)
    main(args, login=login)

