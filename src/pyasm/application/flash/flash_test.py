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

__all__ = ['FlashClientTest', 'run']

import unittest

from flash import *
from flash_environment import *

class FlashClientTest(unittest.TestCase):
    '''Client test for flash'''

    def setUp(self):
        pass


    def test_all(self):
        self.env = FlashEnvironment.get()

        self.app = Flash()
        self.env.set_app(self.app)

        tmp_dir = "C:/sthpw"
        self.env.set_tmpdir(tmp_dir)

        server_url = "http://saba"
        self.env.set_server_url(server_url)

        # run the tests

        self._test_run()
        self._test_jsfl()


    def _test_run(self):

        self.app.run_flash()


    def _test_jsfl(self):

        # download the jsfl file

        self.app.download_jsfl("common.jsfl")
        self.app.download_jsfl("load2.jsfl")
        self.app.download_jsfl("render.jsfl")

        sandbox_path = "C:/sthpw/sandbox"

        # download the file
        url = "http://saba/assets/flash/shot/TF01A/TF01A-004/TF01A-004_0099988FLA.fla"
        to_path = self.app.download(url)


        jsfl_list = []


        # load the appropriate jsfl files
        load_jsfl = "C:/sthpw/JSFL/load2.jsfl"
        jsfl = self.app.get_jsfl(load_jsfl, "include", "common.jsfl", "C:/sthpw/JSFL")
        jsfl_list.append(jsfl)

        # initialize the session
        load_mode="simple"
        prefix_mode = ""
        jsfl = self.app.get_jsfl(load_jsfl, "init_session", load_mode, prefix_mode, sandbox_path)
        jsfl_list.append(jsfl)

        # load file
        jsfl = self.app.get_jsfl(load_jsfl, "load_asset", to_path)
        jsfl_list.append(jsfl)

        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        self.app.run_jsfl(jsfl_final)


        # render
        jsfl_path = "C:/sthpw/JSFL/render.jsfl"
        file_format = "swf"
        render_dir = "C:/sthpw/render"
        log_path = "C:/sthpw/render/action_log.txt"

        jsfl = self.app.get_jsfl(jsfl_path, "render_layer", file_format, render_dir, log_path)
        print jsfl
        


def run():
    unittest.main()
    


#if __name__ == "__main__":
#    unittest.main()

