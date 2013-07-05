
import tacticenv

from pyasm.common import jsonloads

import os

install_dir = tacticenv.get_install_dir()

f = open("%s/doc/alias.json" % install_dir)
s = f.read()
f.close()

data = jsonloads(s)

exist_list = []
non_exist_list = []
non_exist_path = []
for alias, rel_path in data.items():

    path = "%s/doc/%s" % (install_dir, rel_path)
    if not os.path.exists(path):
        non_exist_list.append(alias)
        non_exist_path.append(path)
    else:
        exist_list.append(alias)

print "Existing list:"
for alias in exist_list:
    print "[%s]" %alias

print "-----"

print "Missing list:"
for idx, alias in enumerate(non_exist_list):
    print "[%s]" %alias
    print "path: %s" %non_exist_path[idx]

