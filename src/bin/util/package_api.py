###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

import tacticenv

import os, shutil

from pyasm.common import ZipUtil, Common, Environment


def main():

    install_dir = tacticenv.get_install_dir()
    version = Environment.get_release_version()
    api_version = Environment.get_release_api_version()

    client_api_dir = '%s/src/client' % install_dir
    context_client_dir = '%s/src/context/client' % install_dir

    print "install: ", install_dir
    print "version: ", version

    # copy scm directory in api
    scm_dir = "%s/src/tactic/scm" % install_dir
    client_dir = "%s/src/client" % install_dir
    to_scm_dir = "%s/src/client/tactic_client_lib/scm" % install_dir
    if os.path.exists(to_scm_dir):
        shutil.rmtree(to_scm_dir)
    shutil.copytree(scm_dir, to_scm_dir)


    # create the client api zip package into context/client dir
    path = "%s/src/context/client/tactic-api-%s.zip" % (install_dir, api_version)
    if os.path.exists(path):
        os.system('''rm "%s"''' % path)
    os.system('''cd "%s"; zip -r "%s" "tactic_client_lib"''' % (client_api_dir, path) )




    # copy the client api into the standalone minimal python
    from_dir = '%s/src/client/tactic_client_lib' % install_dir
    python = '%s/src/client/python-3.6.6-win32-minimal' % install_dir
    to_dir = '%s/Lib/site-packages/tactic_client_lib' % python
    if os.path.exists(to_dir):
        shutil.rmtree(to_dir)
    shutil.copytree(from_dir, to_dir)

    # copy and rename to the api version
    to_name = "tactic-api-python-%s" % api_version
    to_dir = os.path.dirname(python) + "/" + to_name;
    if os.path.exists(to_dir):
        shutil.rmtree(to_dir)
    shutil.copytree(python, to_dir)

    # zip this up
    to_dir = os.path.dirname(python)
    zip_path = "%s/%s.zip" % (to_dir, to_name)
    if os.path.exists(zip_path):
        os.unlink(zip_path)
    os.system('''cd "%s"; zip -r "%s.zip" "%s"''' % (to_dir, to_name, to_name) )
    shutil.rmtree("%s/%s" % (to_dir, to_name) )

    #
    final_path = "%s/%s.zip" % (context_client_dir, to_name)
    if os.path.exists(final_path):
        os.unlink(final_path)
    print(zip_path, final_path)
    shutil.move(zip_path, final_path)







if __name__ == '__main__':
    main()

    





