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


from pyasm.web import AppServer


# DEPRECATED


class Error404(AppServer):
    ''' this should be displaying the error status and message, not necessarily 404'''

    def __init__(my):
        my.status = 404
        my.message = ''

    def get_page_widget(my):

        return("""
<html>
<head><title>Error %s</title>
<body style="color:black;background-color:white;font-size:12pt;font-family:sans-serif;padding:16pt">

<div style="text-align: left">
<img src="/context/icons/logo/sthpw_logo_120.png"/>

<h1 style="color:#008">Error 404</h1>
<h2 style="color:#C00">Page Not Available</h2>
<p style="padding:2ex 0pt; border-style:solid none;border-width:thin;border-color:black">The page you requested was not found on this server. %s</p>
<p style="color:#008;font-size:smaller;font-weight:bold">Tactic Application Server</p>
</div>
</body>
</html>

        """ %(my.status, my.message))

