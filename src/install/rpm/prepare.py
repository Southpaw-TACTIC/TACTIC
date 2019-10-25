from __future__ import print_function

import tacticenv

from pyasm.common import Environment


import os, shutil




def main():

    # copy tactic
    install_dir = tacticenv.get_install_dir()
    base_dir = os.path.dirname(install_dir)

    branch = "4.7"
    basename = "tactic-%s.tar.gz" % branch

    # getting TACTIC source code
    print("TACTIC Source Code")
    from_dir = "%s/tactic" % (base_dir)
    print("FROM:", from_dir)
    to_dir = "SOURCES/tactic"
    if os.path.exists(to_dir):
        shutil.rmtree(to_dir)

    shutil.copytree(from_dir, to_dir)

    ################## Remove unnecessary stuff
    git_dir = "%s/.git" % to_dir
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)

    # Remove client directory
    context_client_dir = "%s/src/context/client" % to_dir
    if os.path.exists(context_client_dir):
        shutil.rmtree(context_client_dir)

    # remove doc directory
    doc_dir = "%s/doc" % to_dir
    if os.path.exists(doc_dir):
        shutil.rmtree(doc_dir)

    # remove deprecated directory
    deprecated_dir = "%s/src/deprecated" % to_dir
    if os.path.exists(deprecated_dir):
        shutil.rmtree(deprecated_dir)

    # remove java directory
    java_dir = "%s/src/java" % to_dir
    if os.path.exists(java_dir):
        shutil.rmtree(java_dir)

    # remove .pyc files
    cmd = '''find "SOURCES/tactic" | grep ".pyc" | xargs rm'''
    os.system(cmd)

    # remove __pycache__ directories
    cmd = '''find "SOURCES/tactic" | grep "__pycache__" | xargs rm -rf'''
    os.system(cmd)

    ################## Done removing unnecessary stuff

    cmd = '''cd "SOURCES"; tar zpcf %s tactic/*''' % (basename)
    os.system(cmd)
  
    ################## Prepare config folder

    # Create config folder
    config_dir = "SOURCES/config"
    install_config_dir = "%s/src/install" % install_dir

    install_files = [
        "apache/tactic.conf",
        "data/__init__.py",
        "data/tactic_paths.py",
        "postgresql/pg_hba.conf",
        "template/config/tactic_linux-conf_python3.xml",
        "template/config/tactic-license.xml",
        "service/tactic_python3"
    ]

    for path in install_files:

        dst = "%s/%s" % (config_dir, path)
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        src = "%s/%s" % (install_config_dir, path)
        shutil.copy(src, dst)

    # Set tacticenv paths
    tactic_paths = "%s/data/tactic_paths.py" % config_dir
    f = open(tactic_paths, "a")
    f.write("TACTIC_INSTALL_DIR='/opt/tactic/tactic'\n")
    f.write("TACTIC_SITE_DIR=''\n")
    f.write("TACTIC_DATA_DIR='/opt/tactic/tactic_data'\n")
    f.close()



    ################## Done preparing config folder
    
    version = "1.0.a01"
    tarname = "config-%s.tar.gz" % (version)

    cmd = '''cd "SOURCES"; tar zpcf %s config''' % tarname
    os.system(cmd)




if __name__ == "__main__":
    main()




