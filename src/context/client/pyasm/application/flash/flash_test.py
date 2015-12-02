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

    def setUp(my):
        pass


    def test_all(my):
        my.env = FlashEnvironment.get()

        my.app = Flash()
        my.env.set_app(my.app)

        tmp_dir = "C:/sthpw"
        my.env.set_tmpdir(tmp_dir)

        server_url = "http://saba"
        my.env.set_server_url(server_url)

        # run the tests

        my._test_run()
        my._test_jsfl()


    def _test_run(my):

        my.app.run_flash()


    def _test_jsfl(my):

        # download the jsfl file

        my.app.download_jsfl("common.jsfl")
        my.app.download_jsfl("load2.jsfl")
        my.app.download_jsfl("render.jsfl")

        sandbox_path = "C:/sthpw/sandbox"

        # download the file
        url = "http://saba/assets/flash/shot/TF01A/TF01A-004/TF01A-004_0099988FLA.fla"
        to_path = my.app.download(url)


        jsfl_list = []


        # load the appropriate jsfl files
        load_jsfl = "C:/sthpw/JSFL/load2.jsfl"
        jsfl = my.app.get_jsfl(load_jsfl, "include", "common.jsfl", "C:/sthpw/JSFL")
        jsfl_list.append(jsfl)

        # initialize the session
        load_mode="simple"
        prefix_mode = ""
        jsfl = my.app.get_jsfl(load_jsfl, "init_session", load_mode, prefix_mode, sandbox_path)
        jsfl_list.append(jsfl)

        # load file
        jsfl = my.app.get_jsfl(load_jsfl, "load_asset", to_path)
        jsfl_list.append(jsfl)

        # execute all of the jsfl commands
        jsfl_final = "\n".join(jsfl_list)
        my.app.run_jsfl(jsfl_final)


        # render
        jsfl_path = "C:/sthpw/JSFL/render.jsfl"
        file_format = "swf"
        render_dir = "C:/sthpw/render"
        log_path = "C:/sthpw/render/action_log.txt"

        jsfl = my.app.get_jsfl(jsfl_path, "render_layer", file_format, render_dir, log_path)
        print jsfl
        


def run():
    unittest.main()
    


#if __name__ == "__main__":
#    unittest.main()

