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

__all__ = ['UnityWdg']

from tactic_client_lib import TacticServerStub

from pyasm.common import Environment
from pyasm.web import DivWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg

class UnityWdg(BaseRefreshWdg):

    #    Container.append_seq("Page:js", "http://webplayer.unity3d.com/download_webplayer-3.x/3.0/uo/UnityObject.js")

    def get_display(my):

        top = my.top


        unity_wdg = DivWdg()
        top.add(unity_wdg)
        unique_id = unity_wdg.set_unique_id("unity")

        unity_wdg.add("Unity content can't be played. Make sure you are using compatible browser with JavaScript enabled.")
        #<input id="versionButton" type="button" value="Version" disabled="disabled" onclick="versionButtonClick();" />


        # TEST TEST TEST: dynamic loading of js
        env = Environment.get()
        install_dir = env.get_install_dir()
        js_path = "%s/src/context/spt_js/UnityObject.js" % install_dir
        f = open(js_path)
        init_js = f.read()
        f.close()
        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            %s;
            %s;
            ''' % (init_js, my.get_load_js(unique_id) )
        } )



        return top


    def get_load_js(my, unique_id):


        path = my.kwargs.get("path")
        if not path:
            path = "/context/Example.unity3d"

        return '''
        if (typeof unityObject != "undefined") {
            unityObject.embedUnity("%s", "Example.unity3d", "100%%", "600px", null, null, unityLoaded);

            //console.log(unityObject);
        }
        else {
            alert('got here');
        }
        function unityLoaded(result) {
            if (result.success) {
                var unity = result.ref;
                var version = unity.GetUnityVersion("3.x.x");
                //alert("Unity Web Player loaded!\\nId: " + result.id + "\\nVersion: " + version);

                unity.src = '%s';
            }
            else {
                alert("Please install Unity Web Player!");
            }
        }

        ''' % (unique_id, path)





