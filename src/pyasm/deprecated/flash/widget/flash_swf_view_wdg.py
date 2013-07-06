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
__all__ = ['FlashSwfViewWdg']

from pyasm.web import *
from pyasm.widget import *
from pyasm.search import Search
from pyasm.flash.widget import *


class FlashSwfViewWdg(Widget):

    ICON_DIV_ID = "icon_div"
    MAIN_SWF_ID = "join"

    def init(my):
        body = WebContainer.get_body()
        body.add_style("background-color: #000")
        body.add_style("color: #eee")
        my.init_map()

        WebContainer.add_js('PyFlash.js')

    def init_map(my):
        my.info_map = {FlashAsset.SEARCH_TYPE: FlashAssetCheckboxWdg.CB_NAME, \
                FlashShot.SEARCH_TYPE: FlashShotCheckboxWdg.CB_NAME,\
                FlashLayer.SEARCH_TYPE: FlashLayerCheckboxWdg.CB_NAME}
                
    def get_display(my):
    
        div = DivWdg()
        div.add_style("float: right")
        div.add_style("width: 100%")

        icon = IconWdg('tactic flash viewer',\
            icon='/context/icons/logo/flash_viewer.png')
        title = DivWdg(icon, css='left_content')
        title.add_style('margin-left', '6px') 
        title.add_style('font-size', '1.4em')
        div.add(title)

        select = FilterSelectWdg("fs_size_select")
        
        labels = '1080p|1/2 1080p|720p|1/2 720p|NTSC|3/4 NTSC|1/2 NTSC'
        values = '1920,1080|960,540|1280,720|640,360|720,480|540,360|360,240'
        select.set_option('labels', labels)
        select.set_option('values', values)
        select.set_option('default', '960,540')

        
        select.add_event('onchange',"player.resize_win('%s')" %select.get_name())

        span = SpanWdg('player size: ', css='med smaller')
        span.add(select)
        span.add_style('padding','0 0 10px 24px')
        
        title.add(span)
        
        source_span = SpanWdg('source size: ', css='med smaller')
        source_select = FilterSelectWdg("src_size_select")
        source_select.set_option('labels', labels)
        source_select.set_option('values', values)
        source_select.set_option('default', '960,540')
        
        source_span.add(source_select)
        source_span.add_style('padding','0 0 10px 24px')
        title.add(source_span)
        
        div.add(HtmlElement.br())

        setup_script = HtmlElement.script('''var fs_player = null; 
        var player=new FlashPlayer('%s'); 
        player.icon_div_id='%s'; 
        ''' %( my.MAIN_SWF_ID, my.ICON_DIV_ID ))
        div.add(setup_script)
        icon = HtmlElement.img(IconWdg.CLIP_PLAY)
        icon.set_attr('width', '16px')
        icon.set_attr('height', '16px')

        playing_icon = DivWdg(icon)
        playing_icon.add_style('display','none')
        playing_icon.add_style('position','absolute')
        playing_icon.add_style('z-index','5')
        
        playing_icon.set_id("playing")
        div.add(playing_icon)

        search_type = WebContainer.get_web().get_form_value('search_type')
        cb_name = my.info_map.get(search_type)
        assets = WebContainer.get_web().get_form_value(cb_name).split('|V|')

        swf_list = []
        search_ids = []
        search_type = ''
        for asset in assets:
            if asset:
                search_type, search_id = asset.split('|')
                search_ids.append(search_id)
        
        if not search_ids:
            warning = DivWdg("Please select one or more flash assets before opening the viewer.") 
            warning.add_style('font-size', '1.2em')
            div.add(warning)
            return div

        sobjects = Search.get_by_id(search_type, search_ids)
        thumb = ThumbWdg()
        thumb.set_has_img_link(False)
        thumb.set_sobjects(sobjects)
        thumb.set_icon_size(80)
        thumb.preprocess()

        left_div = FloatDivWdg(id=my.ICON_DIV_ID)
        left_div.add_style('height', '500px')
        left_div.add_style('margin-left','26px')
        left_div.add_style('margin-right','20px')
        left_div.add_style('overflow', 'auto')
        
        play_control = SwapDisplayWdg()
        play_control.add_class('hand')
        
        for idx, sobject in enumerate(sobjects):
            thumb.set_current_index(idx)
            icon = DivWdg()
            icon.add(thumb.get_display())
            icon_id = '%s_icon' %sobject.get_id()
            icon.set_id(icon_id)
            icon.add_class('hand')
           
            info = thumb.get_info()
            script = ["player.load_movie('%s', %d)" % (thumb.get_link_path(info), idx)]
            script.append(play_control.get_swap_script(bias=SwapDisplayWdg.ON))
            
            icon.add_event('onclick', ';'.join(script))
            
            div.add(HtmlElement.script("player.add_movie('%s','%s')" \
                    % (thumb.get_link_path(info), icon_id)))
            
            left_div.add(icon)
            left_div.add(HtmlElement.br(clear="all"))
            divider = DivWdg('&nbsp;')
            divider.add_style('height','3px')
            left_div.add(divider)
            
             
        BaseAppServer.add_onload_script("player.auto_start()" )  
        div.add(left_div)

        right_div = FloatDivWdg()
        div.add(right_div)
        right_div.add(my.get_flash_player(select))
        

        pause = IconWdg('pause', icon=IconWdg.CLIP_PAUSE)
        play = IconWdg('play', icon=IconWdg.CLIP_PLAY)
        play_control.set_display_widgets(pause, play) 
        play_control.add_action_script("player.pause_movie()", "player.play_movie()")
        right_div.add(HtmlElement.br())

        fs_info = FloatDivWdg("&nbsp;", id="fs_info")
        fs_info.add_style('left','10px')
        
        right_div.add(fs_info)
        right_div.add(HtmlElement.br())
        
        right_div.add(play_control)
      
        return div

    def get_flash_player(my, select):
        ''' get the flash player instance html code '''
        web = WebContainer.get_web()
        dir = web.get_context_url()
        player_swf = "%s/template/join.swf" %dir.to_string()
        
        size = select.get_value()
        width, height = size.split(',')
        player = '''
        <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0" width="%s" height="%s" id="join"  >
    <param name="allowScriptAccess" value="sameDomain" />

    <param name="movie" value="%s" />
    <param name="quality" value="medium" />
    <param name="bgcolor" value="#ffffff" />
    <param name="loop" value="false"/>
    <embed src="%s" quality="medium" bgcolor="#ffffff" width="%s" height="%s" name="join"  allowScriptAccess="sameDomain" swLiveConnect="true" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />
</object>
        ''' %(width, height, player_swf, player_swf, width, height)
        
        return player
