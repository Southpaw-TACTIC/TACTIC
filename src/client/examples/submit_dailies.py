###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import sys, getopt

from tactic_client_lib import TacticServerStub, TacticApiException



def main(args, src_snapshot_code=None, src_search_type=None, src_search_code=None, src_context=None, src_version=None,\
        tgt_context=None, tgt_version=None, file_path=None):

    if len(args) == 3:
        # assume code and file path are equivalent
        search_type = args[0]
        code = args[1]
        bin_info = args[2]
    elif len(args) == 4:
        search_type = args[0]
        code = args[1]
        bin_info = args[2]
        file_path = args[3]
    server = TacticServerStub()

    if file_path:
        description = "Dailies Submission [%s] to [%s] - [%s]" % (file_path, search_type, code)
    elif src_snapshot_code:
        description = "Dailies Submission internal reference [%s] to [%s] - [%s]" \
            % (src_snapshot_code, search_type, code)
    else:
        description = "Dailies Submission internal reference [%s|%s] to [%s] - [%s]" \
            % (src_search_type, src_search_code, search_type, code)
    server.start(title='Dailies Submission', description=description )
    try:
        parts = bin_info.split('|')
        if len(parts) == 3:
            bin_code, type, label = parts[0], parts[1], parts[2]
            bins = server.query('prod/bin', [('code', bin_code), ('label', label), ('type', type)])
        elif len(parts) == 2:
            bin_code, type = parts[0], parts[1]
            bins = server.query('prod/bin', [('code', bin_code), ('type', type)])
        if not bins:
            raise TacticApiException("Bin code [%s], type [%s], label [%s] not found in system " % (bin_code, type, label))
    
        
        search_key = server.build_search_key(search_type, code)
        sobject = server.query(search_type, [("code", code)])
        if not sobject:
            raise TacticApiException("SObject [%s] with code [%s] not found" %(search_type, code))

        sobject_id = sobject[0].get('id')
        # add a new submission
        full_search_type = server.build_search_type(search_type)
        submit_data = {'search_type': full_search_type,\
                        'search_id': sobject_id,\
                        'description': "Client Api Submission: [%s]" %code\
                        }
        if tgt_context and tgt_version != None:
            submit_data['context'] = tgt_context
            if tgt_version in ['0', 0 ,'-1', -1]:
                tgt_snapshot = server.get_snapshot(search_key, tgt_context, version=tgt_version)
                if not tgt_snapshot:
                    print "tgt_context [%s] and tgt_version [%s] for this sobject cannot be found" %(tgt_context, tgt_version)
                else: 
                    tgt_version = tgt_snapshot.get('version')
            submit_data['version'] = tgt_version

        src_snapshot = None
        if src_snapshot_code:
            src_snapshot = server.query('sthpw/snapshot',filters=[('code', src_snapshot_code)], single=True)
            submit_data['context'] = src_snapshot.get('context')
            submit_data['version'] = src_snapshot.get('version')

        submission = server.insert('prod/submission', submit_data)
        # add to bin
        submit_in_bin_data = { 'bin_id': bins[0].get('id'), \
                                'submission_id': submission.get('id')\
                                }
        server.insert('prod/submission_in_bin', submit_in_bin_data)
        
        print "New submission [%s] created for [%s].\n" %(submission.get('__search_key__'), full_search_type)
         
        if file_path:
            #NOTE: use the upload method instead of copy or move 
            server.simple_checkin(submission.get('__search_key__'), 'publish', file_path, \
                    snapshot_type='submission', description='Client API dailies submission', mode='upload')
        else:
            if src_snapshot:
               
                pass 
            elif src_search_type:
                src_search_key = server.build_search_key(src_search_type, src_search_code)
            else:
                src_search_key = search_key

            if not src_snapshot:
                src_snapshot = server.get_snapshot(src_search_key, context=src_context, version=src_version)
        
            if src_snapshot:
                snapshot_code = src_snapshot.get('code')
                
                # build a new snapshot
                
                submit_snapshot = server.create_snapshot(submission.get('__search_key__'), \
                        "publish", description='Client API dailies submission', \
                        snapshot_type='submission')

                # add dependency
                server.add_dependency_by_code(submit_snapshot.get('code'), snapshot_code)
            else:
                raise TacticApiException("No snapshot found for [%s] with context [%s] and version [%s]."\
                        %(src_search_key, src_context, src_version))
                return
        
        

    except Exception, e:
        server.abort()
        print "ERROR: ", e.__str__()
    else:
        server.finish()


if __name__ == '__main__':
    
    executable = sys.argv[0]
    src_search_type = None
    src_search_code = None
    src_context = None
    src_version = None
    tgt_context = None
    tgt_version = None
    file_path = None
    try:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("--ssn", help="Source snapshot code")
        parser.add_option("--sst", help="Source search type")
        parser.add_option("--ssc", help="Source search code")
        parser.add_option("--sc", help="Source context")
        parser.add_option("--sv", help="Source version")
        parser.add_option("--tc", help="Target context")
        parser.add_option("--tv", help="Target version")
      
        opts, args = parser.parse_args()
    except getopt.error, msg:
        print msg
        sys.exit(2)
    # process options
    
    src_search_type = opts.sst
    src_search_code = opts.ssc
    src_snapshot_code = opts.ssn
    src_context  = opts.sc
    src_version  = opts.sv
    tgt_context = opts.tc
    tgt_version = opts.tv

    usage = "USAGE: submit_dailies.py <search_type> <code> <bin_info> [path] [--sst search_type] [--ssc search_code] [--sc context] [--sv version] [--tc context] [--tv version]\n"
    usage += "example1: python submit_dailies.py prod/shot HT001_010 \"2008-10-10|dailies|review\" --tc anim --tv -1 \"C:/test/berry.jpg\"\n"
    usage += "example2: python submit_dailies.py prod/shot HT001_010 \"2008-10-10|dailies\" --sst prod/asset --ssc char001 --sc rig --sv 5\n'"
    usage += "example2: python submit_dailies.py prod/shot HT001_010 \"2008-10-10|dailies\"--ssn 101BAR\n'"

    # TODO: lots of assumptions here

    if len(args) == 3:
        # assume code and file path are equivalent
        search_type = args[0]
        code = args[1]
        bin_info = args[2]
        if (not src_context or not src_version) and not src_snapshot_code:
            print "source context --sc and source version --sv required if no <file_path> is provided."
            sys.exit(2)

    elif len(args) == 4:
        search_type = args[0]
        code = args[1]
        bin_info = args[2]
        file_path = args[3]
    
    else:
        print usage
        sys.exit(2)

    parts = bin_info.split('|')
    if len(parts) not in [2, 3]:
        print "The format for bin info is either <bin_code>|<type> or <bin_code>|<type>|<label>."
        print "e.g. 2008-10-20|dailies or 2008-10-20|dailies|review."
        sys.exit(2)

    main(args, src_snapshot_code=src_snapshot_code, src_search_type=src_search_type, src_search_code=src_search_code, \
            src_context=src_context, src_version=src_version,\
            tgt_context=tgt_context, tgt_version=tgt_version, file_path=file_path)

