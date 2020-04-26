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
#
__all__ = ["DevSandbox03Wdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg

from tactic.ui.widget import TextBtnWdg, TextBtnSetWdg
from tactic.ui.container import PopWindowWdg, ResizeScrollWdg



class DevSandbox03Wdg(BaseExampleWdg):

    def get_example_title(self):
        # UI prototype sandbox for Mike
        return "::: Developer UI Sandbox 03 - Mike :::"


    def get_example_description(self):
        return "This is a prototyping and testing sandbox widget container (#3) for Mike."


    def get_simple_div(self, text, bg_color):
        div = DivWdg()
        if bg_color:
            div.add_styles("background-color: %s; color: black; padding: 10px; border: solid 1px black;" % bg_color)
        else:
            div.add_styles("color: black; padding: 10px; border: solid 1px black;")
        div.add( text )
        return div


    def get_example_display(self):

        div = DivWdg()
        div.add_styles("background: grey; padding: 10px; width: 450px;")
        div.add( "<br/><br/>" )

        from tactic.ui.container import RoundedCornerDivWdg
        rc_wdg = RoundedCornerDivWdg(corner_size=10)
        # rc_wdg.set_dimensions(width_str="100%", content_height_str='100%', height_str="100%")
        rs0_wdg = ResizeScrollWdg( width=300, height=200, scroll_bar_size_str='thin', scroll_expansion='inside',
                                   # max_content_w=500, max_content_h=400,
                                   set_max_to_content_size=True,
                                   min_content_w=100, min_content_h=50 )
        rs0_wdg.add( self.get_popwin_oversize_content() )

        rc_wdg.add( rs0_wdg )
        div.add( rc_wdg )

        div.add( "<br/><br/>" )

        div.add( "<p style='color: black;'>Resize/Scroll Widget example ...</p>" )
        rs_wdg = ResizeScrollWdg( width=300, height=200, scroll_bar_size_str='thin', scroll_expansion='inside' )
        rs_wdg.add( self.get_popwin_oversize_content() )
        div.add( rs_wdg )

        div.add( "<br/><br/>" )

        div.add( "<p style='color: black;'>Resize/Scroll Widget example WITH NO RESIZE CAPABILITY" \
                 " (just scroll bars) ...</p>" )
        rs2_wdg = ResizeScrollWdg( width=300, height=200, scroll_bar_size_str='thin', scroll_expansion='inside',
                                  no_resize=True )
        rs2_wdg.add( self.get_popwin_oversize_content() )
        div.add( rs2_wdg )

        div.add( "<br/><br/>" )

        popwin_id = "NewPopupWindowTest"
        popwin_title = "New Popup Window Widget Test"
        popwin = PopWindowWdg(top_id=popwin_id, title=popwin_title, width=150, height=150)
        popwin.add( self.get_popwin_oversize_content() )
        div.add( popwin )
        pwin_launch = DivWdg()

        pwin_launch.add_styles("cursor: pointer; background-color: red; color: black; border: 1px solid black; width: 100px; height: 50px;")
        pwin_launch.add_behavior( {'type': 'click_up', 'cbjs_action': 'spt.popup.open("' + popwin_id + '");'} )
        pwin_launch.add("Click to launch New Popup Window")
        div.add( pwin_launch )



        div.add( "<br/><br/>" )

        test_div = DivWdg()
        test_div.add_styles("background: black; padding: 10px; width: 350px; text-align: center;")

        test_div.add( SpanWdg("This black DIV has<br/>text-align set to center") )

        my_table = Table()
        my_table.add_row()
        my_table.add_cell("This").add_styles("border: 1px solid white; padding: 4px;")
        my_table.add_cell("that").add_styles("border: 1px solid white; padding: 4px;")
        my_table.add_cell("and").add_styles("border: 1px solid white; padding: 4px;")
        my_table.add_cell("The").add_styles("border: 1px solid white; padding: 4px;")
        my_table.add_cell("other").add_styles("border: 1px solid white; padding: 4px;")

        test_div.add( "<br/><br/>" )
        test_div.add( my_table )

        test_div.add( "<br/><br/>" )
        tmp_div = DivWdg()
        tmp_div.add_styles("width: 200px; background-color: green; color: black; padding: 10px;")
        tmp_div.add("I am a DIV without self margins set")
        test_div.add(tmp_div)

        test_div.add( "<br/><br/>" )
        tmp_div = DivWdg()
        tmp_div.add_styles("width: 200px; background-color: green; color: black; padding: 10px;")
        tmp_div.center()
        tmp_div.add("I am a DIV with self margins<br/>set using HtmlElement.center()")
        test_div.add(tmp_div)

        test_div.add( "<br/><br/>" )
        buttons_list = [
            {
                'label': "Insert",
                'tip': "This is an insert",
                'bvr': {'cbjs_action': 'alert("Insert!");'}
            },
            {
                'label': 'Cancel',
                'tip': 'Cancel',
                'bvr': {'cbjs_action': 'alert("Cancel!");'}
            }
        ]
        buttons = TextBtnSetWdg( float="", align="center", buttons=buttons_list, spacing=6,
                                 size='medium', side_padding=4 )
        test_div.add( buttons )

        div.add(test_div)



        div.add( "<br/><br/>" )
        div.add( "<br/><br/>" )

        buttons_list = [
                {'label': 'One', 'tip': 'Button One', 'bvr': {'cbjs_action': 'alert("First button!");'} },
                {'label': 'Two', 'tip': 'Button Two', 'bvr': {'cbjs_action': 'alert("Second button!");'} },
                {'label': 'Three', 'tip': 'Button Three', 'bvr': {'cbjs_action': 'alert("Third button!");'} },
                {'label': 'Four', 'tip': 'Button Four', 'bvr': {'cbjs_action': 'alert("Fourth button!");'} },
        ]

        txt_btn_set = TextBtnSetWdg( float='right', buttons=buttons_list, spacing=6, size='large', side_padding=4 )
        txt_btn_set.get_btn_by_label('Three').add_behavior( {'type': 'click_up', 'modkeys': 'SHIFT',
                                                             'cbjs_action': 'alert("SHIFT happened!");'} )
        div.add( txt_btn_set )


        div.add( "<br/><br/>" )
        div.add( "<br/><br/>" )

        d1 = self.get_simple_div( "Drop Zone (runs cbjs_action of drag-drop element on drop)", None )
        d1.set_attr("SPT_ACCEPT_DROP","Qweejibo")
        d1.add_behavior( { 'type': 'hover', 'mod_styles': 'background-color: green;' } )


        table1 = Table()
        tr = table1.add_row()
        tr.add_behavior( { 'type': 'hover', 'mod_styles': 'background-color: #f11; color: green' } )

        td = table1.add_cell('what')
        #td.add_behavior( { 'type': 'hover', 'mod_styles': 'background-color: orange;' } )
        td = table1.add_cell('is')
        #td.add_behavior( { 'type': 'hover', 'mod_styles': 'background-color: green;' } )
        div.add(table1)

        # d2 = self.get_simple_div( "Pick Up!", "white" )
        d2 = self.get_simple_div( "Override with 'accept_drop' behavior!", None )
        d2.add_looks("menu");

        # NOTE: with 'accept_drop' behavior you do not need to set the "SPT_ACCEPT_DROP" attribute on the
        #       given drop-on element, just need to add the same value to a 'drop_code' attribute in the
        #       'accept_drop' bvr spec (doing this will automatically add it to the SPT_ACCEPT_DROP at
        #       behavior construction time
        # so we do not need this here --> d2.set_attr("SPT_ACCEPT_DROP","Qweejibo")
        d2.add_behavior( { 'type': 'accept_drop', 'cbjs_action': 'log.debug("Override #1 on Qweejibo");',
                            'drop_code': 'Qweejibo' } )
        d2.add_behavior( { 'type': 'accept_drop',
            'cbjs_action': '''
                log.debug("Override #2 on Qweejibo");
                var el = bvr._drop_source_bvr.src_el;
                el.setStyle("background-color", "white");
            ''',
            'drop_code': 'Qweejibo' } )

        d2.add_behavior( { 'type': 'hover', 'add_looks': 'menu_hover' } )
        d2.add_behavior( { 'type': 'hover', 'mod_styles': 'border: 1px solid red;',
                            'drag_drop_codes': 'Qweejibo',
                            } )

        div.add( d1 )
        div.add( "<br/>" )
        div.add( d2 )


        div.add( "<br/><br/>" )
        div.add( "<br/><br/>" )

        btn = DivWdg()
        btn.add("TEST JS LOG TIME")
        btn.add_styles("padding: 4px; width: 150px; cursor: pointer; background: red; color: white; " + 
                        "border: 1px solid white;")
        btn.add_behavior( { 'type': 'click', 'cbjs_action': 'spt.js_log.test_perf();' } )

        div.add( btn )
        div.add( "<br/><br/>" )

        dragme = DivWdg()
        dragme.add_styles( "background: blue; padding: 10px; width: 200px; border: 1px solid black; " \
                           "position: absolute; top: 200px; left: 400px; cursor: default;" )
        dragme.add( "Click me OR Drag me!" )


        # dragme.add_behavior( { 'type': 'drag', 'drag_el': '@', 'use_default_cbs': 'true',
        #                        'cbjs_action_onnomotion': 'alert("I\'ve been clicked!");' } )

        dragme.add_behavior( { 'type': 'smart_drag', 'drag_el': '@',
                               'use_copy': 'true',
                               'use_delta': 'true', 'dx': 1, 'dy': 1,
                               'drop_code': 'Qweejibo',
                               'copy_styles': 'background: red; opacity: .3;',
                               'cbjs_action': 'alert("Got Qweejibo");',
                               'cbjs_action_onnomotion': 'alert("I\'ve been clicked!");' } )


        div.add( dragme )
        div.add( "<br/><br/>" )

        select = SelectWdg("OnChangeTestSelectWidget")
        select.add_behavior( {'type': 'change',
            'cbjs_preaction': '''
                alert("Click OK then see Web Client Output Log for 'change' behavior activity");
                log.debug("[preaction] My value is now: "+bvr.src_el.value);
                ''',
            'cbjs_action': 'log.debug("[action] My value is now: "+bvr.src_el.value);',
            'cbjs_postaction': 'log.debug("[postaction] My value is now: "+bvr.src_el.value);'
        } );
        select.add_behavior( {'type': 'change', 'cbjs_action': 'log.debug("ORIG - stacked change behavior #2!");'} );
        select.add_behavior( {'type': 'change', 'cbjs_action': 'log.debug("ORIG - stacked change behavior #3!");'} );
        select.add_behavior( {'type': 'change', 'cbjs_action': 'log.debug("ORIG - stacked change behavior #4!");'} );
        select.set_option("values", "One|Day|In|Your|Life")
        select.set_value("Life")

        # Test for set_behavior override with stacked onchange behaviors ...
        '''
        select.set_behavior( {'type': 'change', 'cbjs_action': 'alert("This is what me gots: "+bvr.src_el.value);'} );
        select.add_behavior( {'type': 'change', 'cbjs_action': 'log.debug("OVERRIDE - stacked change behavior #5!");'} );
        select.add_behavior( {'type': 'change', 'cbjs_action': 'log.debug("OVERRIDE - stacked change behavior #6!");'} );
        '''

        div.add(select)

        div.add( "<br/><br/>" )

        click_core_div = DivWdg()
        click_core_div.add_styles( "background-color: blue; color: white; border: 1px solid black; padding: 10px" )
        click_core_div.add_styles( "cursor: pointer;" )
        click_core_div.add( "Click me for preaction, action, postaction test" )
        click_core_div.add_behavior( {'type': 'click',
            'cbjs_preaction': '''
                alert("Click OK then see Web output log for 'click' behavior activity");
                log.debug("Click pre-action");
            ''',
            'cbjs_action': 'log.debug("Click action");',
            'cbjs_postaction': 'log.debug("Click post-action");'
        } )

        div.add( click_core_div )


        div.add( "<br/><br/>" )
        override = DivWdg()
        override.add_styles( "padding: 4px; background: white; color: black; border: 1px solid black; cursor: pointer;" )
        override.add( "Set Behavior Override Test" )

        bvr = { 'type': 'click', 'modkeys': 'SHIFT', 'cbjs_action': 'alert("Load ONE");' }
        override.add_behavior( bvr )

        bvr = { 'type': 'click', 'modkeys': 'SHIFT', 'cbjs_action': 'alert("Load ONE OVERRIDDEN!");' }
        override.set_behavior( bvr )

        div.add(override)

        div.add( "<br/><br/>" )

        div1 = DivWdg()
        div1.add_styles("background: #444477; border: solid 1px black; padding: 10px;")
        div1.add("Div1")
        div1.set_id("Div_1")

        div2 = DivWdg()
        div2.add_styles("background: #4444BB; border: solid 1px black; padding: 10px; cursor: pointer;")
        div2.add("Div2")
        div2.set_id("Div_2")

        # div2.add_behavior( { 'type': 'click_up', 'cbjs_action': '$("Div_3").inject("Div_2","after");' } )
        div2.add_behavior( { 'type': 'click_up', 'cbjs_action': '$("Div_3").inject("Div_1","bottom");' } )

        div1.add( div2 )

        div.add(div1)
        div.add("<br/><br/>")

        div3 = DivWdg()
        div3.add_styles("background: #4444FF; border: solid 1px black; padding: 10px;")
        div3.add("Div3")
        div3.set_id("Div_3")

        div.add(div3)

        return div


    def get_popwin_oversize_content(self):

        div = DivWdg()
        div.add_styles("background-color: orange; color: black; padding: 20px; width: 600px;")
        div.add('''
<p>SCENE I. DUKE ORSINO's palace.</p>

<p>Enter DUKE ORSINO, CURIO, and other Lords; Musicians attending</p>

<h2>DUKE ORSINO</h2>

<p>If music be the food of love, play on;
Give me excess of it, that, surfeiting,
The appetite may sicken, and so die.
That strain again! it had a dying fall:
O, it came o'er self ear like the sweet sound,
That breathes upon a bank of violets,
Stealing and giving odour! Enough; no more:
'Tis not so sweet now as it was before.
O spirit of love! how quick and fresh art thou,
That, notwithstanding thy capacity
Receiveth as the sea, nought enters there,
Of what validity and pitch soe'er,
But falls into abatement and low price,
Even in a minute: so full of shapes is fancy
That it alone is high fantastical.</p>

<h2>CURIO</h2>

<p>Will you go hunt, self lord?</p>

<h2>DUKE ORSINO</h2>

<p>What, Curio?</p>

<h2>CURIO</h2>

<p>The hart.</p>

<h2>DUKE ORSINO</h2>

<p>Why, so I do, the noblest that I have:
O, when mine eyes did see Olivia first,
Methought she purged the air of pestilence!
That instant was I turn'd into a hart;
And self desires, like fell and cruel hounds,
E'er since pursue me.</p>

<p><i>Enter VALENTINE</i><p>

<p>How now! what news from her?</p>

<h2>VALENTINE</h2>

<p>So please self lord, I might not be admitted;
But from her handmaid do return this answer:
The element itself, till seven years' heat,
Shall not behold her face at ample view;
But, like a cloistress, she will veiled walk
And water once a day her chamber round
With eye-offending brine: all this to season
A brother's dead love, which she would keep fresh
And lasting in her sad remembrance.</p>

<h2>DUKE ORSINO</h2>

<p>O, she that hath a heart of that fine frame
To pay this debt of love but to a brother,
How will she love, when the rich golden shaft
Hath kill'd the flock of all affections else
That live in her; when liver, brain and heart,
These sovereign thrones, are all supplied, and fill'd
Her sweet perfections with one self king!
Away before me to sweet beds of flowers:
Love-thoughts lie rich when canopied with bowers.</p>

<p><i>Exeunt</i></p>

        ''')

        return div


