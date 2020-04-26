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

__all__ = ['GeneralAppletWdg', 'PerforceAppletWdg']

from pyasm.common import TacticException
from pyasm.web import WebContainer, Widget, HtmlElement

class GeneralAppletWdg(Widget):
    APPLET_ID = "general_applet"
    APPLET_JAR = "Upload-latest.jar"
    APPLET_CLASS = "upload.GeneralApplet"

    def get_applet_id(cls):
        return cls.APPLET_ID
    get_applet_id = classmethod(get_applet_id)



    def init(self):
        #print "DEPRECATED"
        #raise TacticException("Use of GeneralAppletWdg is Deprecated")

        # it's generated thru JS in IE
        if WebContainer.get_web().is_IE():
            return
        
        context_url = WebContainer.get_web().get_context_url()
        
        print "-"*20
        print self.APPLET_CLASS


        # create applet
        applet = HtmlElement("applet")
        applet.set_attr("code", self.APPLET_CLASS)
        applet.set_attr("codebase", "%s/java" % context_url.get_url() )
        applet.set_attr("archive", self.APPLET_JAR)
        applet.set_attr("width", "1")
        applet.set_attr("height", "1")
        applet.set_attr("id", self.APPLET_ID)
    
        # create param for applet
        param = HtmlElement("param")
        param.set_attr("name","scriptable")
        param.set_attr("value","true")

        applet.add(param)
        
        self.add(applet)
        #ticket = WebContainer.get_security().get_ticket_key()
        #self.add(HtmlElement.script("document.%s.set_ticket('%s')" \
        #    %(self.APPLET_ID, ticket)) )



class PerforceAppletWdg(GeneralAppletWdg):
    APPLET_ID = "perforce_applet"
    APPLET_JAR = "Perforce-latest.jar"
    APPLET_CLASS = "perforce.PerforceApplet"


