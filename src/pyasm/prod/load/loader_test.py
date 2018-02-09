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



from pyasm.security import *
from pyasm.prod.biz import *

from loader import *

import unittest


class TestHandler:

    def handle_node(self, name, node):

        if name == "special":
            print "special"
            return True



class LoaderTest(unittest.TestCase):

    def setUp(self):
        batch = Batch()

    def test_all(self):
        #self._test_execute_parser()
        self._test_loader()


    def _test_execute_parser(self):

        xml = '''<execute>
          <file type="maya" path="./test.ma"/>
          <file type="anim"/>
          <mel>sphere</mel>
          <special>cow</special>
        </execute>'''

        handler = TestHandler()
        parser = ExecuteParser(xml)
        parser.add_handler(handler)
        parser.execute()


    def _test_loader(self):

        xml = '''
        <snapshot>
           <ref search_type="prod/texture" search_id="73"/>
        </snapshot>'''
        loader = LoaderCmd()
        loader.set_snapshot_xml(xml)
        Command.execute_cmd(loader)

        # test a real snapshot
        snapshot = Snapshot.get_latest("prod/asset", 37, "sht")
        loader = LoaderCmd()
        loader.set_snapshot(snapshot)

        Command.execute_cmd(loader)


    



    """
    def test_maya_load(self):
        # get the test sequence and shot
        sequence = Sequence.get_by_code("001SHO")
        shot = sequence.get_shot_by_code("0001")

        instance = "chr101_pig"
    
        # get the latest snapshot
        version = "-1"

        process = "anm"

        snapshot = shot.get_snapshot( "pig", process, version )
        #loader = MayaLoader()
    """



if __name__ == "__main__":
    unittest.main()

