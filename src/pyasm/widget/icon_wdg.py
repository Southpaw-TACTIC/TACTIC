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

__all__ = ['IconWdg', 'IconButtonWdg', 'IconSubmitWdg', 'IconRefreshWdg',
        'ProdIconButtonWdg','ProdIconSubmitWdg']

from pyasm.web import  DivWdg, HtmlElement, WebContainer



class IconWdg(DivWdg):

    icons = {
    # 16x16 icons		    
    'ADD'                  : "add.png",
    'ADD_GRAY'             : "add_GRAY.png",
    'ADVANCED'             : "/context/icons/common/advanced.png",
    'APPLICATION_TILE_VERTICAL' : "application_tile_vertical.png",
    'APP_TILE_VERTICAL'    : "application_tile_vertical.png",
    'APP_VIEW_TILE'        : "application_view_tile.png",
    'APPROVED'             : "/context/icons/common/approved.png",
    'ARROWHEAD_DARK_DOWN'  : "_spt_bullet_arrow_down_dark.png",  # silk MOD
    'ARROWHEAD_DARK_RIGHT' : "_spt_bullet_arrow_right_dark.png",  # silk MOD
    'ARROW_LEFT'           : "/context/icons/common/left-arrow.png",
    'ARROW_RIGHT'          : "/context/icons/common/right-arrow.png",
    'ARROW_UP'             : "/context/icons/common/up-arrow.png",
    'ARROW_UP_GREEN'       : "arrow_up.png",
    'ARROW_DOWN'           : "/context/icons/common/down-arrow.png",
    'ARROW_OUT'            : "arrow_out.png",
    'ARROW_OUT_GRAY'       : "arrow_out_GRAY.png",
    'ARROW_MORE_INFO'      : "/context/icons/custom/triangle_down.png",
    'ASSIGN'               : "_spt_user_assign.png",
    'ARROW_SWITCH'         : "arrow_switch.png",
    'ATTACHMENT'           : "attach.png",
    
    'CAMERA'               : "camera.png",
    'CALENDAR'             : "calendar.png",

    'CHART_BAR'            : "chart_bar.png",
    'CHECK'                : "tick.png",
    'CHECK_IN'             : "/context/icons/custom/checkin.png",
    'CHECK_IN_3D_LG'       : "/context/icons/custom/checkin_3d_lg.png",
    'CHECK_OUT_3D_LG'      : "/context/icons/custom/checkout_3d_lg.png",
    'CHECK_OUT_LG'         : "/context/icons/common/checkout_lg.png",
    #'CHECK_OUT_SM'        : "/context/icons/common/checkout_sm.png",
    #'CHECK_OUT'           : "/context/icons/common/checkout.png",
    'CHECK_OUT_SM'         : "/context/icons/custom/checkout_server.png",
    'CHECK_OUT'            : "/context/icons/custom/checkout_server.png",
    'CLEAR'                : "table_delete.png",
    'CLIP_PLAY'            : "/context/icons/common/clip_play.png",
    'CLIP_PAUSE'           : "/context/icons/common/clip_pause.png",
    'CLOCK'                : "clock.png",
    'CLOSE_ACTIVE'         : "/context/icons/custom/tab_close_active.png",
    'CLOSE_INACTIVE'       : "/context/icons/custom/tab_close_inactive.png",
    'COLUMNS'              : "text_columns.png",
    'COMMUNITY'            : "/context/icons/16x16/community.png",
    'CONNECT'              : "connect.png",
    'CONTENTS'             : "application_view_list.png",
    'CREATE'               : "lightbulb_off.png",
    'CROSS'                : "/context/icons/common/BtnKill.gif",
    'CURRENT'              : "_spt_bullet_radio.png",

    'DATE'                 : "date.png",
    'DATE_ADD'             : "date_add.png",
    'DATE_DELETE'          : "date_delete.png",
    'DATE_EDIT'            : "date_edit.png",
    'DATE_ERROR'           : "date_error.png",
    'DATE_GO'              : "date_go.png",
    'DATE_LINK'            : "date_link.png",
    'DATE_MAGNIFY'         : "date_magnify.png",
    'DATE_NEXT'            : "date_next.png",
    'DATE_PREVIOUS'        : "date_previous.png",

    # database icons
    'DB'                   : "database.png",
    'DB_CONNECT'           : "database_connect.png",
    'DB_EDIT'              : "database_edit.png",
    'DB_ERROR'             : "database_error.png",
    'DB_GEAR'              : "database_gear.png",

    "DOCUMENTATION"        : "/context/icons/16x16/documentation.png",

    'DOT_RED'              : "/context/icons/common/dot_red.png",
    'DOT_YELLOW'           : "/context/icons/common/dot_yellow.png",
    'DOT_GREEN'            : "/context/icons/common/dot_green.png",
    'DOT_GREY'             : "/context/icons/common/dot_grey.png",
    'DOWNLOAD'             : "_spt_download.png",

    'EDIT'                 : "page_white_edit.png",
    'EDIT_ALL'             : "_spt_page_white_stack_edit.png",
    'EDIT_SETTINGS'        : "cog_edit.png",
    'EMAIL'                : "email.png",
    'ERROR'                : "exclamation.png",

    'FILM'                 : "film.png",
    'FILM_SUBMIT'          : "film_go.png",
    'FLOAT'                : "/context/icons/oo_prev/stock_cell-align-top-16.png", # need to replace!
    'FOLDER'               : "folder.png",
    'FOLDER_GRAY'          : "folder_GRAY.png",
    'FOLDER_GO'            : "folder_go.png",
    'FOLDER_EDIT'          : "folder_edit.png",
    'FOLDER_EXPLORE'       : "folder_explore.png",

    'DELETE'               : "delete.png",
    'DEPENDENCY'           : "chart_organisation.png",
    'DETAILS'              : "page_white_text.png",
    'DIALOG_CLOSE'         : "/context/spt_js/mooDialog/css/dialog-close2.png",

    'GEAR'                 : "cog.png",
    'GOOD'                 : "accept.png",
    'GREEN_LIGHT'          : "/context/icons/custom/green_light.png",
    'GROUP'                : "group.png",
    'GROUP_LINK'           : "group_link.png",

    'HELP'                 : "help.png",
    'HELP_BUTTON'          : "/context/icons/custom/help_button.png",
    'HELP_MISSING'         : "/context/icons/32x32/help_01_32.png",
    'HISTORY'              : "/context/icons/custom/history.png",
    'HOME'                 : "house.png",

    'IMAGE'                : "image.png",
    'IMAGE_ADD'            : "image_add.png",
    'IMPORT'               : "application_get.png",
    'INFO'                 : "information.png",
    'INFO_CLOSED'          : "bullet_go.png",
    'INFO_CLOSED_SMALL'    : "_spt_bullet_arrow_right.png",
    'INFO_OPEN'            : "_spt_bullet_down_arrow.png",
    'INFO_OPEN_SMALL'      : "bullet_arrow_down.png",
    'INSERT'               : "page_white_add.png",
    'INSERT_MULTI'         : "_spt_page_white_stack_add.png",
    'INVALID'              : "cross.png",

    'JUMP'                 : "door_in.png",

    'KILL'                 : "/context/icons/common/kill_button.png",
    'LAYER'                : "_spt_page_white_stack_add.png",
    'LEFT'                 : "control_rewind.png",
    'LICENSE'              : "rosette.png",
    'LOAD'                 : "folder.png",
    'LINK'                 : "link.png",
    'LOCK'                 : "lock.png",

    'MAIL'                 : "email.png",
    'MOVIE_VIEW'           : "/context/icons/common/view_movie.png",

    'NAV'                  : "/context/icons/oo_prev/stock_navigator_purple.png", # need to replace!
    'NEW'                  : "new.png",
    'NOTE'                 : "note.png",
    'NOTE_ADD'             : "note_add.png",
    'NOTE_DELETE'          : "note_delete.png",
    'NOTE_EDIT'            : "note_edit.png",
    'NOTE_ERROR'           : "note_error.png",
    'NOTE_GO'              : "note_go.png",
    'NO_IMAGE'             : "/context/icons/common/no_image.png",

    'PAGE_WHITE_GO'        : "page_white_go.png",
    'PERFORCE'             : "/context/icons/16x16/p4_16.png",
    'PHOTOS'               : "photos.png",
    'PICLENS'              : "/context/icons/common/PicLensButton.png",
    'PICTURE_EDIT'         : "picture_edit.png",
    'PIPELINE'             : "arrow_divide.png",
    'PLUGIN'               : "plugin.png",
    'PLUGIN_32'            : "/context/icons/32x32/plugin_32.png",
    'PLUGIN_64'            : "/context/icons/32x32/plugin_64.png",
    'PLUGIN_ADD'           : "plugin_add.png",
    'PLUS'                 : "/context/icons/custom/tab_plus.png",
    'PLUS_ADD'             : "/context/icons/custom/plus_bw.png",
    'POPUP_ANCHOR'         : "/context/icons/custom/popup_anchor.png",
    'POPUP_WIN_CLOSE'      : "/context/icons/custom/popup_close.png",
    #'POPUP_WIN_CLOSE'      : "/context/icons/glyphs/test_close.png",
    'POPUP_WIN_MINIMIZE'   : "/context/icons/custom/popup_minimize.png",
    'POPUP_WIN_REFRESH'    : "_spt_popup_window_refresh.png",
    'PREF'                 : "brick.png",
    'PRINTER'              : "printer.png",
    'PROCESS'              : "application_view_tile.png",
    'PROGRESS'             : "/context/icons/common/indicator_medium.gif",
    'PROJECT'              : "/context/icons/custom/two_windows.png",
    'PROJECT_TYPE'         : "shape_group.png",

    #'PUBLISH'             : "_spt_disk_with_cog.png",
    'PUBLISH'              : "/context/icons/custom/checkin_disk.png",
    'PUBLISH_LG'           : "_spt_disk_with_cog_lg.png",
    'PUBLISH_MULTI'        : "_spt_disk_multiple_with_cog.png",

    'REDO'                 : "arrow_redo.png",
    'REF'                  : "/context/icons/common/reference.png",
    'REFRESH'              : "arrow_refresh.png",
    'REFRESH_GRAY'         : "arrow_refresh_GRAY.png",
    'REGISTER'             : "/context/icons/custom/register.png",
    'RENDER'               : "/context/icons/oo_prev/stock_flip-16.png",  # need to replace!
    'RESIZE_CORNER'        : "/context/icons/custom/resize.png",
    'RESIZE_HORIZ'         :    "/context/icons/custom/resize_horiz.png",
    'RESIZE_VERTICAL'      : "/context/icons/custom/resize_vertical.png",
    'REPLACE'              : "_spt_replace.png",
    'RETIRE'               : "/context/icons/common/retire.png",
    'RIGHT'                : "control_fastforward.png",

    'SAVE'                 : "disk.png",
    'SAVE_GRAY'            : "disk_GRAY.png",
    'SANDBOX'              : "/context/icons/custom/sandbox_16.png",
    'SELECT'               : "cursor.png",
    'SET_PROJECT'          : "folder_go.png",
    'SPECIAL'              : "medal_gold_3.png",
    'STAR'                 : "star.png",

    'TABLE_UPDATE_ENTRY'   : "_spt_table_update_entry.png",
    'TABLE_ROW_DELETE'     : "table_row_delete.png",
    'TABLE_ROW_INSERT'     : "table_row_insert.png",

    'TAG_ORANGE'           : "tag_orange.png",
    'TEST'                 : "/context/icons/common/test.png",
    'TIME'                 : "time.png",
    'TIMELINE_MARKER'      : "timeline_marker.png",
    'TODAY'                : "/context/icons/custom/today.png",
    'TOGGLE_ON'            : "_spt_option_toggle_on_darker.png",
    'TOGGLE_OFF'           : "_spt_option_toggle_off_darker.png",


    'TRANSPARENT'          : "/context/icons/common/transparent_pixel.gif",
    'TRASH'                : "basket_delete.png",


    'UNDO'                 : "_spt_arrow_undo_yellow.png",
    'UNKNOWN'              : "/context/icons/oo_prev/stock_unknown-16.png",  # need to replace!
    'UPDATE'               : "_spt_database_update.png",
    'UPLOAD'               : "_spt_upload.png",
    'HANDOFF'              : "/context/icons/common/connect.png",
    'UPLOAD2'              : "/context/icons/common/arrow_divide.png",
    
    'USER'                 : "user.png",
    'USER_ADD'             : "user_add.png",
    'USER_EDIT'            : "user_edit.png",
    'USER_DELETE'          : "user_delete.png",
    'UNITY'                : "/context/icons/custom/unity.png",

    'VIEW'                 : "vcard.png",
    'VIEW_EDIT'            : "vcard_edit.png",
    'WARNING'              : "/context/spt_js/mooDialog/css/dialog-warning.png",
    'WEBSITE'              : "/context/icons/16x16/website.png",
    'WRENCH'               : "wrench.png",

    'WIP'                  : "/context/icons/common/wip.png",
    'WRENCH'               : "/context/icons/custom/wrench.png",
    'WORK'                 : "/context/icons/custom/work.png",
    'ZOOM'                 : "zoom.png",
    'ZOOM_IN'              : "zoom_in.png",
    'ZOOM_OUT'             : "zoom_out.png",
    'MAYA'                 : "/context/icons/mime-types/maya.png",
    'XSI'                  : "/context/icons/mime-types/xsi_scn.jpg",
    'HOUDINI'              : "/context/icons/mime-types/houdini.png",

    # New 32x32 image icons
    'ADVANCED_32'             : "/context/icons/32x32/advanced_32.png",
    'ARROW_UP_LEFT_32'        : "/context/icons/32x32/arrow_up_left_32.png",
    'CALENDAR_01'             : '/context/icons/32x32/calendar_32_01.png',
    'CALENDAR_02'             : '/context/icons/32x32/calendar_32_02.png',
    'CALENDAR_04'             : '/context/icons/32x32/calendar_32_04.png',
    'CALENDAR_05'             : '/context/icons/32x32/calendar_32_05.png',
    'CLOCK_01'                : '/context/icons/32x32/clock_32_01.png',
    'CONFIGURE_01'            : '/context/icons/32x32/configure_32_01.png',
    'CONFIGURE_02'            : '/context/icons/32x32/configure_32_02.png',
    'CONFIGURE_03'            : '/context/icons/32x32/configure_32_03.png',
    'DASHBOARD_02'            : '/context/icons/32x32/dashboard_32_02.png',
    'FLOW_CHART_01'           : '/context/icons/32x32/flow_chart_32_01.png',
    'FLOW_CHART_02'           : '/context/icons/32x32/flow_chart_32_02.png',
    'FLOW_CHART_03'           : '/context/icons/32x32/flow_chart_32_03.png',
    'FOLDERS_01'              : '/context/icons/32x32/folders_32_01.png',
    'GRAPH_ARROW_01'          : '/context/icons/32x32/graph_arrow_32_01.png',
    'GRAPH_ARROW_02'          : '/context/icons/32x32/graph_arrow_32_02.png',
    'GRAPH_ARROW_03'          : '/context/icons/32x32/graph_arrow_32_03.png',
    'GRAPH_BAR_01'            : '/context/icons/32x32/graph_bar_32_01.png',
    'GRAPH_BAR_02'            : '/context/icons/32x32/graph_bar_32_02.png',
    'GRAPH_BAR_03'            : '/context/icons/32x32/graph_bar_32_03.png',
    'GRAPH_BAR_04'            : '/context/icons/32x32/graph_bar_32_04.png',
    'GRAPH_BAR_06'            : '/context/icons/32x32/graph_bar_32_06.png',
    'GRAPH_LINE_01'           : '/context/icons/32x32/graph_line_32_01.png',
    'GRAPH_LINE_02'           : '/context/icons/32x32/graph_line_32_02.png',
    'GRAPH_LINE_03'           : '/context/icons/32x32/graph_line_32_03.png',
    'GRAPH_LINE_04'           : '/context/icons/32x32/graph_line_32_04.png',
    'GRAPH_LINE_05'           : '/context/icons/32x32/graph_line_32_05.png',
    'GRAPH_LINE_06'           : '/context/icons/32x32/graph_line_32_06.png',
    'LIST_01'                 : '/context/icons/32x32/list_32_01.png',
    'LIST_02'                 : '/context/icons/32x32/list_32_01.png',
    'LOCK_32_01'              : '/context/icons/32x32/lock_32_01.png',
    'LOCK_32_02'              : '/context/icons/32x32/lock_32_02.png',
    'REPORT_01'               : '/context/icons/32x32/report_32_01.png',
    'REPORT_02'               : '/context/icons/32x32/report_32_02.png',
    'REPORT_03'               : '/context/icons/32x32/report_32_03.png',
    'SANDBOX_32'              : '/context/icons/32x32/sandbox_32.png',
    'SCHEMA_32'               : '/context/icons/32x32/schema_32.png',
    'SCRIPT_EDITOR_01'        : '/context/icons/32x32/script_editor_32_01.png',
    'SEARCH_32'               : '/context/icons/32x32/search_32.png',
    'SEARCH_TYPE_32'          : '/context/icons/32x32/search_type_32.png',
    'SECURITY_32_15'          : '/context/icons/32x32/security_32_15.png',
    'SECURITY_32_16'          : '/context/icons/32x32/security_32_16.png',
    'SECURITY_32_17'          : '/context/icons/32x32/security_32_17.png',
    'SECURITY_32_18'          : '/context/icons/32x32/security_32_18.png',
    'SECURITY_32_19'          : '/context/icons/32x32/security_32_19.png',
    'SECURITY_32_20'          : '/context/icons/32x32/security_32_20.png',
    'SECURITY_32_21'          : '/context/icons/32x32/security_32_21.png',
    'SHARE_32'                : '/context/icons/32x32/share_32.png',
    'TASK_01'                 : '/context/icons/32x32/task_32_01.png',
    'USER_32'                 : '/context/icons/32x32/end_user_32.png',
    'WIDGET_CONFIG_01'        : '/context/icons/32x32/widget_config_32_01.png',
    
    #black and white Icons
    
    'BW_COMMENT'          : "/context/icons/common/bw_comment.png",
    'BW_CREDIT_CARD'      : "/context/icons/common/bw_credit_card.png",
    'BW_DOCUMENT'         : "/context/icons/common/bw_document.png",
    'BW_PHOTO'            : "/context/icons/common/bw_photo.png",
    'BW_SHOPPING_BAG'     : "/context/icons/common/bw_shopping_bag.png",
    'BW_STORAGE'          : "/context/icons/common/bw_storage.png",
    'BW_DOCUMENTS'        : "/context/icons/common/bw_documents.png",
    
    #new sidebar icons
    'ADVANCED_PROJ_SETUP' : "/context/icons/common/advanced_project_setup_01.png",
    'PROJECT_STARTUP'     : "/context/icons/common/project_startup_01.png",
    'HOME_01'             : "/context/icons/common/home_01.png",
    'HOME_02'             : "/context/icons/common/home_02.png",


    'LAYOUT_64'           : "/context/icons/64x64/layout_64.png",



    # Glyphs
    'G_FOLDER'            : '/context/icons/glyphs/folder.png',
    'G_MAXIMIZE'          : '/context/icons/glyphs/maximize.png',
    'G_SETTINGS'          : '/context/icons/glyphs/settings.png',
    'G_SETTINGS_BLACK'    : '/context/icons/glyphs/settings_black.png',
    'G_SETTINGS_GRAY'     : '/context/icons/glyphs/settings_gray.png',
    'G_CALENDAR'          : '/context/icons/glyphs/calendar.png',
    'G_UP'                : '/context/icons/glyphs/chevron_up.png',
    'G_DOWN'              : '/context/icons/glyphs/chevron_down.png',
    'G_SEARCH'            : '/context/icons/glyphs/search.png',
    'G_SEARCH_BLACK'      : '/context/icons/glyphs/search_black.png',
    'G_LEFT'              : '/context/icons/glyphs/chevron_left.png',
    'G_RIGHT'             : '/context/icons/glyphs/chevron_right.png',
    'G_LEFT_BLACK'        : '/context/icons/glyphs/chevron_left_black.png',
    'G_RIGHT_BLACK'       : '/context/icons/glyphs/chevron_right_black.png',
    'G_CLOSE'             : '/context/icons/glyphs/close.png',
    'G_CLOSE_BLACK'       : '/context/icons/glyphs/close_black.png',
    'G_HOME_BLACK'        : '/context/icons/glyphs/home_black.png',


    
      


    # -- Constants:previously here, that are not referenced in any python code ... only add them back in as needed!
    #
    # ACTION      : "stock_form-pattern-field-16.png"   # not ref'd
    # DRAG        : "stock_navigator-drag-mode-16.png"  # not ref'd
    # INPUT       : "stock_alignment-right-16.png"      # not ref'd
    # OUTPUT      : "stock_alignment-left-16.png"       # not ref'd
    # ZOOM_IN     : "stock_zoom-in-16.png"              # not ref'd
    # ZOOM_OUT    : "stock_zoom-out-16.png"             # not ref'd
    }
    for key, value in icons.items():
        exec("%s = '%s'" % (key, value) )


    def get_icon_path( icon_name_key ):
        icon_path = IconWdg.icons.get( icon_name_key )
        if not icon_path:
            return ''
        if not icon_path.startswith("/"):
            return ("/context/icons/silk/%s" % icon_path)
        else:
            return icon_path
    get_icon_path = staticmethod(get_icon_path)


    def __init__(my, name=None, icon=None, long=False, css='', right_margin='3px', width='', opacity=None, **kwargs):
        try:
            my.icon_path = eval("IconWdg.%s" % icon.upper())
        except:
            my.icon_path = icon
        my.text = name
        my.long = long
        my.css = css
        my.right_margin = right_margin
        my.width = width
        my.kwargs = kwargs
        my.opacity = opacity
        super(IconWdg,my).__init__()


    def init(my):
        if my.icon_path.startswith("BS"):
            icon_path = my.icon_path
        elif not my.icon_path.startswith("/"):
            # icon_path = "/context/icons/oo/%s" % my.icon_path
            icon_path = "/context/icons/silk/%s" % my.icon_path
        else:
            icon_path = my.icon_path

        if icon_path.startswith("BS_"):
            icon = HtmlElement.span()
            icon.add_class("glyphicon")
            part = icon_path.replace("BS_", "")
            part = part.lower()
            part = part.replace("_","-")
            icon.add_class("glyphicon-%s" % part)
            icon.add_style("font-size: 16px")
            icon.add_style("opacity: 0.6")
            if not my.opacity:
                my.opacity = 0.6
        else:
            icon = HtmlElement.img(icon_path)

        if my.opacity:
            icon.add_style("opacity: %s" % my.opacity)


        if my.text and my.text != "":
            icon.set_attr("title", my.text)
        if my.right_margin:
            icon.add_style("margin-right: %s" % my.right_margin)
       
        my.icon = icon

        inline = my.kwargs.get("inline")
        if inline in [False, 'false']:
            my.add_style("float: left")
        else:
            my.add_style("display: inline")
        

        


    def get_display(my):

        my.add(my.icon)
        if my.css:
            my.add_class(my.css)

        if my.long:
            my.add(my.text)

        if my.width:
            if my.icon_path.startswith("BS_"):
                my.icon.add_style('font-size', my.width)
            else:
                my.icon.add_style('width', my.width)
        return super(IconWdg,my).get_display()

    def get_icon(my):
        return my.icon

    def get_icons_def():
        return IconWdg.icons
    get_icons_def = staticmethod(get_icons_def)

    def get_icons_keys():
        keys = IconWdg.icons.keys()
        keys.sort()
        return keys
    get_icons_keys = staticmethod(get_icons_keys)


class IconButtonWdg(HtmlElement):
    
    def __init__(my, name=None, icon=None, long=False, icon_pos="left", icon_styles='', opacity=None):
        my.text = name
        my.icon_path = icon
        my.long = long
        my.icon_pos = icon_pos
        super(IconButtonWdg,my).__init__("span")
        my.name = name
        my.icon_styles = icon_styles
    

    def set_icon(my, icon):
        my.icon_path = icon

    def set_text(my, text):
        my.text = text

    def get_display(my):

        if my.icon_pos == "left":
            my._add_icon()
            my._add_title()
        elif my.icon_pos == "right":
            my._add_title()
            my.add(" ")
            my._add_icon()

        return super(IconButtonWdg,my).get_display()


    def _add_icon(my):
        # icon is optional
        if not my.icon_path:
            return
        
        if not my.icon_path.startswith("/"):
            # icon_path = "/context/icons/oo/%s" % my.icon_path
            icon_path = "/context/icons/silk/%s" % my.icon_path
        else:
            icon_path = my.icon_path

        icon = HtmlElement.img(icon_path)
        icon.set_attr("title", my.name)
        icon.add_styles(my.icon_styles)   
        if my.long:
            img_id = my.generate_unique_id(my.name)
            icon.add_class("icon_out") 
            my.add_event("onmouseover","wdg_opacity('%s','over');" % (img_id))
            my.add_event("onmouseout","wdg_opacity('%s','out');" % (img_id))
            icon.set_id(img_id)
        else:
            icon.add_class("simple_button")


        if WebContainer.get_web().is_IE():
            icon.add_style("vertical-align: top")
        else:
            icon.add_style("vertical-align: middle")
       
        my.add(icon)





    def _add_title(my):
        if my.long:
            # This would be better on the whole span
            my.add(HtmlElement.href(my.text, "#"))
            # this is Mootools specific
            my.add_event('onclick', 'new Event(event).stop()')
            my.add_class("button")
          
            if WebContainer.get_web().is_IE():
                my.add_style("border-width: 0px 2px 2px 0px")
                my.add_style("border-style: solid")
                my.add_style("border-color: #303030")
                my.add_event("onmousedown", "button_down(this)")
                my.add_event("onmouseup", "button_up(this)")
                my.add_event("onmouseout", "button_up(this)")
       
            

class IconSubmitWdg(IconButtonWdg):
    def __init__(my, name=None, icon=None, long=False, icon_pos="left", \
            add_hidden=True, value=None):
        my.add_hidden = add_hidden
        my.hidden = None
        if not value:
            my.value = name
        else:
            my.value = value

        # for some reason, my.name gets reset to empty
        my.name = name
        my.submit_name = name
        
        super(IconSubmitWdg,my).__init__(name,icon,long,icon_pos)
    
    def init(my):
        from input_wdg import HiddenWdg
        if my.add_hidden:
            my.hidden = HiddenWdg(my.value,"")
            my.add( my.hidden )

        my.add_event("onclick", "submit_icon_button('%s','%s')" % \
                (my.submit_name,my.value) )

    def get_display(my):
        return super(IconSubmitWdg,my).get_display()

    def get_value(my):
        return my.hidden.get_value()
    


class IconRefreshWdg(IconSubmitWdg):
    def __init__(my, long=True):
        super(IconRefreshWdg,my).__init__("Refresh", IconWdg.REFRESH, long)



class ProdIconButtonWdg(IconButtonWdg):
    
    def __init__(my, name=None, icon=None, long=True, icon_pos="left", icon_styles=''):
        super(ProdIconButtonWdg,my).__init__(name, icon, long, icon_pos, icon_styles=icon_styles)
        #my.add_style("line-height: 14px")
        my.add_style("font-size: 1.0em")
        my.add_style("padding: 3px 10px 3px 10px")

class ProdIconSubmitWdg(IconSubmitWdg):
    
    def __init__(my, name=None, icon=None, long=True, icon_pos="left"):
        super(ProdIconSubmitWdg,my).__init__(name, icon, long, icon_pos)
        my.add_style("line-height: 14px")
        my.add_style("font-size: 1.0em")
        my.add_style("padding: 3px 10px 3px 10px")
