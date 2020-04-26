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
    def __init__(self):
        self.company = None
        super(TestHandler, self).__init__()

    def execute(self):
        # set the output for this process if it is model
        if self.get_process_name() == "model":
            self.set_output_value("file", "test.txt")

        self.company = self.get_package_value('company')
        self.set_status("complete")



class TestNextProcessHandler(TestHandler):

    def execute(self):
        self.add_next_process("extra1")
        self.add_next_process("extra2")

        self.set_status("complete")




