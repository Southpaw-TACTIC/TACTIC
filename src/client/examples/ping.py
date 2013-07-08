###########################################################
#
# Copyright (c) 2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

'''ping.py: simpe function to ping the server.  This scripts illustrates the
most basic interaction with the server'''


# import the client api library
from tactic_client_lib import TacticServerStub

def main():
    # get an instance of the stub
    server = TacticServerStub()

    # start the transaction
    server.start("Ping Test")
    try:
        # ping the server
        print server.ping()
    except:
        # in the case of an exception, abort all of the interactions
        server.abort()
        raise
    else:
        # otherwise, finish the transaction
        server.finish()


if __name__ == '__main__':
    main() 


