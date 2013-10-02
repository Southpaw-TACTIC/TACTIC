#!/usr/bin/python
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


import unittest

from widget import *
from web_state import *

class WidgetTest(unittest.TestCase):


    def test_url(my):

        base = "http://www.yahoo.com"
        url = Url( base )
        url.set_option("widget","EditWdg")
        url.set_option("args","person")
        
        url_str = url.get_url()

        my.assertEquals("%s?widget=EditWdg&args=person" % base, url_str)


    def test_state(my):

        # set the state
        state = WebState.get()
        state.add_state("episode_code", "TF01A")
        state.add_state("scene", "TF01A-003")

        base = "http://www.yahoo.com"
        url = Url(base)
        state.add_state_to_url(url)

        url_str = url.to_string()

        my.assertEquals("%s?episode=TF01A&scene=TF01A-003" % base, url_str)



        


if __name__ == '__main__':
    unittest.main()



