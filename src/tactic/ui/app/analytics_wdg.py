###########################################################
#
# Copyright (c) 2019, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#

__all__ = [ 'GoogleAnalyticsWdg']

from tactic.ui.common import BaseRefreshWdg
from pyasm.biz import ProjectSetting
from pyasm.web import Widget

class GoogleAnalyticsWdg(BaseRefreshWdg):

    def get_display(self):

        google_analytics_id = ProjectSetting.get_value_by_key("google_analytics_id") or ""
        widget = Widget()

        if google_analytics_id:
            widget.add('''<!-- Global Site Tag (gtag.js) - Google Analytics -->
                <script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
                <script>
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag('js', new Date());

                    gtag('config', '%s');
                </script>''' % (google_analytics_id, google_analytics_id))

        return widget