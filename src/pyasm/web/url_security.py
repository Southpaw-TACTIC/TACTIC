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

__all__ = ['RedirectSecurity', 'UrlSecurity']

from pyasm.common import *

from web_container import WebContainer
from widget import Html


class RedirectSecurity(Base):
    '''class that manages the security for the url'''

    def get_display(my):

        web = WebContainer.get_web()

        # get the request uri
        request_uri = web.get_env("REQUEST_URI")

        security = WebContainer.get_security()
        groups = security.get_groups()

        # go through each group and find a redirect.  Take the first one
        for group in groups:

            # find out if the person user has a redirect which confines them
            # to a particular address
            redirect = group.get_value("redirect_url")
            # prevent mistaken infinte loops
            redirect = redirect.strip()
            if not redirect:
                continue
            
            if request_uri.find(redirect) == -1:
                # draw the actual page
                html = Html()
                html.writeln('<HEAD>')
                html.writeln('<META HTTP-EQUIV="Refresh" CONTENT="0; URL=%s"' % redirect)
                html.writeln('</HEAD>')
                return html


        return None



class UrlSecurity(Base):

    def get_display(my):

        html = None

        url = WebContainer.get_web().get_request_url().to_string()

        # check the url security
        security = WebContainer.get_security()
        if not security.check_access("url", url, "view"):
            html = Html()

            # should probably just use this widget instead of redirecting
            redirect = "/tactic/Error403"
            html.writeln("<script>document.location = '%s'</script>" % redirect)

        return html







