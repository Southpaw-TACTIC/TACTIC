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

import tacticenv

from pyasm.common import Environment, SPTDate
from pyasm.security import Batch, Security
Batch()

from tactic_client_lib import TacticServerStub

import os, sys, xmlrpclib, datetime
from mod_python import apache, Cookie



# This will ensure that any asset requires a valid ticket


def accesshandler(request):

    cookies = Cookie.get_cookies(request)

    # if login ticket cookie does not exist, then deny
    if not cookies.has_key('login_ticket'):
        # just refuse access
        return apache.HTTP_FORBIDDEN

    ticket = cookies['login_ticket'].value
    if not ticket:
        return apache.HTTP_FORBIDDEN

    server = TacticServerStub.get(protocol='local')
    expr = "@SOBJECT(sthpw/ticket['ticket','%s'])" % ticket
    sobject = server.eval(expr, single=True)
    now = SPTDate.now()
    expiry = sobject.get("expiry")
    if expiry and expiry < str(now):
        return apache.HTTP_FORBIDDEN

    request.add_common_vars()
    path = str(request.subprocess_env['REQUEST_URI'])
    if path == None:
        return apache.HTTP_FORBIDDEN


    # FIXME: find some mechanism which is more acceptable ... like /icons
    #if path.find("_icon_") != -1:
    #    return apache.OK

    return apache.OK



def outputfilter_example(filter):
    s = filter.read()
    while s:
        filter.write(s.upper())
        s = filter.read()
    if s is None:
        filter.close()


from PIL import Image, ImageChops, ImageFont, ImageDraw
from cStringIO import StringIO

from pyasm.security import Ticket
from pyasm.security.watermark import Watermark
from datetime import datetime

def outputfilter_watermark(filter):

    s_in = None
    s_out = None
    try:
        s_in = StringIO(filter.read())
        im_in = Image.open(s_in)
        if im_in.size[0] <= 240 and im_in.size[1] <= 120:
            filter.write(s_in.getvalue())
            return

        # if this is a sub request, then don't process again
        req = filter.req
        if req.main:
            filter.write(s_in.getvalue())
            return

        cookies = Cookie.get_cookies(req)
        ticket = cookies['login_ticket'].value
        query = req.parsed_uri[apache.URI_QUERY]


        if query == "watermark=false":
            filter.write(s_in.getvalue())
            ticket_sobj = Ticket.get_by_valid_key(ticket)

            # if this is not a valid ticket, then just exit with no image
            if not ticket_sobj:
                return

            # TODO: need fancier algorithm here
            if ticket_sobj.get_value("login") == 'admin':
                filter.write(s_in.getvalue())
                return

        sizex = im_in.size[0]
        sizey = im_in.size[1]
        max_res = 240
        max_width = 640
        im_in = im_in.resize( (max_res, int(sizey/(sizex/float(max_res)))) )
        im_in = im_in.resize( (max_width, int(sizey/(sizex/float(max_width)))) )

        # add the watermark
        watermark = Watermark()
        now = datetime.today().strftime("%Y/%m/%d, %H:%M")
        texts = ['Do Not Copy', ticket, now]
        sizes = [20, 10, 10, 20, 20]

        mark = watermark.generate(texts, sizes)
        im_out = watermark.execute(im_in, mark, 'tile', 0.5)


        s_out = StringIO()
        im_out.save(s_out, format='jpeg')
        filter.write(s_out.getvalue())

    finally:
        if s_in:
            s_in.close()
        if s_out:
            s_out.close()

    

    
