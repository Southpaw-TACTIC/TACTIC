###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = [ 'TacticCopyrightNoticeWdg' ]


from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.common import Environment, TacticException

from tactic.ui.common import BaseRefreshWdg


# --------------------------------------------------------------------------------------------------------------------
#
#   All widgets related to the TACTIC logo or name should be placed in this file
#
# --------------------------------------------------------------------------------------------------------------------

class TacticCopyrightNoticeWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            'show_license_info': 'Boolean indicating whether or not to show the license information along with ' \
                                 'the Copyright notice'
        }


    def get_display(my):
        top_div = DivWdg()
        top_div.add_styles("text-align: center")
        top_div.add_style("margin-top: 10px")
        top_div.add_style("opacity: 0.5")
        top_div.add_style("font-size: 10px")

        tactic_span = SpanWdg()
        tactic_span.add( "TACTIC&reg;" )
        rel_span = SpanWdg()
        rel_span.add( "&nbsp;&nbsp;Release %s" % Environment.get_release_version() )
        top_div.add( tactic_span )
        top_div.add( rel_span )

        top_div.add( "&nbsp;&nbsp; &copy; 2005-2015, Southpaw Technology Inc. &nbsp; All Rights Reserved.&nbsp; " )

        show_license_info = my.kwargs.get("show_license_info")
        if show_license_info:
            security = Environment.get_security()
            if security:
                license = Environment.get_security().get_license()
                company = license.get_data("company")
                if company.startswith('ALL'):
                    lic_type = ''
                    tmps = company.split('-')
                    if tmps:
                        lic_type = tmps[-1]
                        lic_type = lic_type.strip()
                    license_text = "Open Source License - %s" %lic_type
                else:
                    license_text = "Licensed to %s" % company
            else:
                license_text = "No License"
            top_div.add( license_text )

        top_div.add("<br/>"*2)
        return top_div


