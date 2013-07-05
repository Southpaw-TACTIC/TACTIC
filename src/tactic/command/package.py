###########################################################
#
# Copyright (c) 2010, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['Package']

import tacticenv

from pyasm.common import Xml
from pyasm.search import Search

from pyasm.command import Command


class Package(Command):

    def __init__(my, search_key, context, package):
        my.search_key = search_key
        my.context = context
        my.package = package

        my.package_xml = Xml()
        my.package_xml.read_string(package)

        super(Package, my).__init__()

        

    def execute(my):

        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get(protocol='local')

        # create a new snapshot
        snapshot = server.create_snapshot(my.search_key, my.context)

        # get all of the file_types

        file_nodes = my.package_xml.get_nodes("package/file_type")

        count = 0

        for file_node in file_nodes:
            name = my.package_xml.get_attribute(file_node, "name")

            values = my.package_xml.get_node_values_of_children(file_node)
            expression = values.get("expression")
            dir_naming = values.get("dir_naming")
            file_naming = values.get("file_naming")

            files =  Search.eval(expression)

            for file in files:
                file_type = "%s%s" % (name, count)
                try:
                    # FIXME: the assumed action is to checkin
                    server.add_file(snapshot, file, file_type=file_type, mode='copy', dir_naming=dir_naming, file_naming=file_naming)

                    # What if we just wished to copy?  Can we run the files
                    # through a naming convention filter?

                    count += 1
                except Exception, e:
                    print "WARNING: ", str(e)
                #server.add_xx(search_key, context)




class TestPackageCmd(Command):
    def execute(my):
        # simple packaging.  Take the latest chr001 and
        package = '''
<package>
  <!-- get files for vehicle002 -->
  <file_type name='vehicle002'>
    <expression>@LATEST(prod/asset['code','vehicle002'], 'model')</expression>
  </file_type>

  <!-- get files for vehicle003 -->
  <file_type name='vehicle003'>
    <expression>@LATEST(prod/asset['code','vehicle003'], 'model')</expression>
  </file_type>
</package>
        '''

        search_key = "prod/asset?project=sample3d&code=chr001"
        context = "main_vehicles"

        package = Package(search_key, context, package)
        package.execute()



        package = '''
        <package>
        <!-- get latest modelling files for all vehicle -->
        <file_type name='whatever'>
        <expression>@LATEST(prod/asset['asset_library','chr'], 'model')</expression>
        </file_type>
        </package>
        '''

        search_key = "prod/asset?project=sample3d&code=chr001"
        context = "character"

        package = Package(search_key, context, package)
        package.execute()

        package = '''
<package>
<!-- get files for vehicle002 -->
<file_type name='vehicle002'>
  <mode>copy</mode>
  <expression>@LATEST(prod/asset['code','vehicle002'], 'model')</expression>
  <dir_naming>delivery/vehicles/{@GET(date.today),%Y-%m-%d}</dir_naming>
  <file_naming>v{version}.{ext}</file_naming>
</file_type>
</package>
        '''

        package = Package(search_key, context, package)
        package.execute()


def main():
    cmd = TestPackageCmd()
    Command.execute_cmd(cmd)


if __name__ == '__main__':
    from pyasm.security import Batch
    Batch(project_code='sample3d')
    main()




