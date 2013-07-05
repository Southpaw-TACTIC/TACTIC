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

'''query.py: simple script to query for set information
'''


# import the client api library
from tactic_client_lib import TacticServerStub

def main():
    # get an instance of the stub
    server = TacticServerStub()

    # start the transaction
    server.start("Set query")
    try:

        # define the search type we are searching for
        search_type = "prod/asset"
          
        # define a filter
        filters = [] 
        filters.append( ("asset_library", "chr") )
          
        # do the query
        assets = server.query(search_type, filters)

        # show number found
        print("found [%s] assets" % len(assets) )
          
        # go through the asset and print the code
        for asset in assets:
            code = asset.get("code")  
            print(code)


    except:
        # in the case of an exception, abort all of the interactions
        server.abort()
        raise
    else:
        # otherwise, finish the transaction
        server.finish()


if __name__ == '__main__':
    main() 


