###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import sys
import os

import tacticenv
from pyasm.common import Environment

CLIENT_FILE_PATH_LIST = (\
        '/src/context',\
        '/src/client/tactic_client_lib',\
        '/src/pyasm/application/common/interpreter/tactic_client_lib'
    )

SERVER_FILE_PATH_LIST = (\
        '',
        '/src/client/tactic_client_lib',
        '/src/pyasm/application/common/interpreter/tactic_client_lib',
        '/src/context'
    )



def main(args):


    try:
        version_server_prev = get_file_contents('VERSION')
        version_server_new  = args[0]
        print ''
        print '                                                            VERSION'
        print '                                                            -------'
        print 'The VERSION file contains:                                 ', version_server_prev
        print 'The file will be changed to:                               ', version_server_new

        version_client_prev = get_file_contents('VERSION_API')
        version_client_prev = version_client_prev.strip()
        print ''
        print ''
        print '                                                            VERSION_API'
        print '                                                            -----------'
        print 'The VERSION_API file contains:                             ', version_client_prev

        prompt_str = 'The file will be changed to (%s): '%version_client_prev
        version_client_new = raw_input(prompt_str)
        print
        if version_client_new in [ version_client_prev, '']:
            print '--'
            print
            print 'VERSION_API remains unchanged.'
        else:
            print '--'
            print
            print 'Using the input string:', version_client_new
            set_string_in_version_file(CLIENT_FILE_PATH_LIST, 'VERSION_API', version_client_new)

        set_string_in_version_file(SERVER_FILE_PATH_LIST, 'VERSION', version_server_new)

    except Exception, e:
        print 'Error in set_version.py->update_version_file_server() or update_version_file_client(): ', e.__str__()
        print 'Updating version files failed.  Process terminated.'
        exit()
        
    try:
        run_create_zip()

    except Exception, e:
        print 'Error in set_version.py->run_create_zip(): ', e.__str__()
        print 'Creating zip file failed.  Process terminated.'
        exit()

    print '  ------------------------ set_version completed ------------------------'
    print_file_location_msg()

def set_string_in_version_file(pathList, version_filename, version_string):
    print '--'
    print
    print '  Updating string to "%s" in version file: %s ' % (version_string, version_filename)
    print
    env = Environment()
    install_dir = env.get_install_dir()
    pathCount = len(pathList)
    for index, path in enumerate(pathList):
        fullPath = install_dir + path + '/' + version_filename
        f = open(fullPath, 'w')
        print '  Output: %i of %i - Writing %s to:' % (index+1, pathCount, version_filename)
        print '                     %s' % fullPath
        # Write the give command line argument as the version string in the file.
        f.write(version_string)
        print '                 - Done.  Closing file.'
        f.close()
        print ''

# Get current contents from the specified file
def get_file_contents(version_filename):
    env = Environment()
    install_dir = env.get_install_dir()
    path = '/src/client/tactic_client_lib'
    fullPath = install_dir + path + '/' + version_filename
    f = open(fullPath, 'r')
    version_string = f.read()
    f.close()
    return version_string

# Execute the shell script: src/context/client/create_zip.sh
def run_create_zip():
    env = Environment()
    install_dir = env.get_install_dir()
    print install_dir
    os.system('cd ' + install_dir + '/src/context/client; ./create_zip.sh')

def print_file_location_msg():
    env = Environment()
    install_dir = env.get_install_dir()
    print '  The version files are located here:'
    print '    %s/VERSION' % install_dir
    print '    %s/src/context/VERSION' % install_dir
    print '    %s/src/client/tactic_client_lib/VERSION' % install_dir
    print '    %s/src/pyasm/application/common/interpreter/tactic_client_lib/VERSION' % install_dir
    print ''
    print '  The client tactic.zip is located here:'
    print '    %s/src/client/tactic_client_lib/tactic.zip' % install_dir


# Print the usage of the shell command to screen.
def print_usage():
    print 'NAME'
    print '  set_version <VERSION_STRING>'
    print ''
    print 'DESCRIPTION'
    print '  Sets the server version file (named "VERSION") to the first argument and'
    print '  prompts to the user to input the argument for the client version file (named "VERSION_API").'
    print '  If nothing is input for the client version file, then it is left unchanged.'
    print
    print '  Then, it executes create_zip.sh.'
    print '  The create_zip.sh copies everything in the pyasm/application directory,'
    print '  zips it up, and copies the zipped file to src/client/tactic_client_lib'
    print ''
    print_file_location_msg()
    print ''
    print '  For more details on what set_version.py is automating, please see:'
    print '    http://dev.southpawtech.com/trac/wiki/TACTIC_release_versioning'
    print ''
    print 'EXAMPLE'
    print '  python set_version.py 3.1.0.b01'
    print ''
    return
        

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(sys.argv) > 2:
        print_usage()
        print ''
        print 'error: Only 1 single argument is acceptable.  Please try again.'
        exit()
    if len(sys.argv) < 2:
        print_usage()
        print ''
        print 'error: No arguments found.  Please try again.'
        exit()
    main(args)

