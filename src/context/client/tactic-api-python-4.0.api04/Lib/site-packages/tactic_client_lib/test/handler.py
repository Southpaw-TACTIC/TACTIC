###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['TestHandler', 'TestNextProcessHandler']

from tactic_client_lib.interpreter import Handler


class TestHandler(Handler):
    def __init__(my):
        my.company = None
        super(TestHandler, my).__init__()

    def execute(my):
        # set the output for this process if it is model
        if my.get_process_name() == "model":
            my.set_output_value("file", "test.txt")

        my.company = my.get_package_value('company')
        my.set_status("complete")



class TestNextProcessHandler(TestHandler):

    def execute(my):
        my.add_next_process("extra1")
        my.add_next_process("extra2")

        my.set_status("complete")




