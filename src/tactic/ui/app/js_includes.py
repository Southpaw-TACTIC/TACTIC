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

from pyasm.common import Environment


# currently in spt_js_url (tactic/src/context/spt_js) ... should be in own separate location
third_party = [
    # add mootools
    "mootools/mootools-core-1.4.1-full-nocompat-yc.js",
    "mootools/mootools-more-1.4.0.1-yc.js",

    #"mooDialog/Overlay.js",
    #"mooDialog/MooDialog.js",
    #"mooDialog/MooDialog.Extra.js",

    #"mooRainbow/Source/mooRainbow.js",
    # -- Compatibility library to temporarily house functions to make
    # -- things work from the old js stuff
    #"compat.js",           # DEPRECATED: if this functionality is needed
                            # is should be put in the api

    "json2.js",


    # DEPRECATED
    #"ofc/js/swfobject.js",   # NOTE: this *cannot* be made to work inline
                             # Not sure why this needs to be in the <head> tag,
                             # but need to remove this dependency
    #"edit_area/edit_area_full.js", # similar ro swfobject.js, it is required
                                   # that this is initialized at page
                                   # initialization and not afterwards
    #"ckeditor/ckeditor.js"

]





# DEPRECATED
# in js_url ... tactic/src/context/javascript
legacy_core = [
    #"Common.js",
    #"Overlay.js",
    #"PopupWindow.js",
    #"DynamicLoader.js",
    #"EventContainer.js",
]


# in spt_js_url ... all non-3rd-party scripts in tactic/src/context/spt_js
#
# Add each specific javascript file in the new src/context/spt_js/ area
# NOTE that spt_init.js MUST be the first of these includes and
# spt_onload_startup.js MUST be the last include (of the files in the
# "spt_js" area) ...
#
spt_js = [
    "spt_init.js",     # MUST be FIRST of these includes
    #"require.js",
    "effects.js",
    "utility.js",
    #"file.js",         # moved to utility.js
    "dynamic_css.js",
    "xmlrpc.js",       # add the xmlrpc libraries
    "api/utility.js",  # only basic form ganther is used here.
    #"upload.js",       # DEPRECATED: this is all done through java applet now
    "environment.js",
    "applet.js",
    #"command.js",      # moved to dg_table.js which still requires this
    "client_api.js",   # Add the client api
    "mouse.js",
    "keyboard.js",
    "events.js",
    "behavior.js",
    #"ctx_menu.js",
    #"smart_menu.js",
    #"smart_select_wdg.js", # DEPRECATED: moved to widget/smart_select_wdg.py
    "panel.js",
    #"side_bar.js",
    #"action_bar.js", # DEPRECATED

    #"dg_table.js",
    #"dg_table_action.js",
    #"dg_table_editors.js",


    #"sobject_planner.js",  # DEPRECATED - delete
    #"gantt.js",        # This has been moved to be dynamically loaded
    #"fx_anim.js",      # If this needs to be used, it should be loaded
                        # dynamically
    #"popup.js",        # DEPRECATED: moved to container/popup_wdg.js
    "js_logger.js",
    "page_utility_widgets.js",
    "validation.js",
    #"touch_ui.js",     # DEPRECATED: this code has been disabled in
                        # layout_wdg.py
    "custom_project.js",
    "spt_onload_startup.js",
    "api/api.js",       # add in the new api
]


# in js_url ... tactic/src/context/javascript
legacy_app = [
    #"PyMaya.js",
    #"PyHoudini.js",
    #"PyXSI.js",
    #"PyPerforce.js",
    #"PyFlash.js",
]


all_lists = [
    ("javascript", legacy_core),
    ("spt_js", spt_js),
    ("javascript", legacy_app),
]


def get_compact_js_context_path_suffix():
    context_path_suffix = "spt_js/_compact_spt_all_r%s.js" % Environment.get_release_version().replace(".","_")
    return context_path_suffix


def get_compact_js_filepath():
    all_js_path = "%s/src/context/%s" % \
                        ( Environment.get_install_dir(), get_compact_js_context_path_suffix() )
    return all_js_path


