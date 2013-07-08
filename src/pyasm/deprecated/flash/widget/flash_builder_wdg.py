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

__all__ = ['FlashBuilderWdg']

from pyasm.search import Search
from pyasm.web import *
from pyasm.widget import *
from pyasm.biz import *
from pyasm.flash import *
from pyasm.flash.widget import *


class FlashBuilderWdg(Widget):

    def get_display(my):

        widget = Widget()

        table = Table()
        table.add_row()

        # provide all of the shots
        div = DivWdg()
        div.add_style("width: 400px")
        search = Search("flash/shot")
        sobjects = search.get_sobjects()

        div.add( HtmlElement.h3("Scenes") )
        shot_table = TableWdg("flash/shot", 'layout')
        shot_table.set_sobjects(sobjects)
        div.add(shot_table)
        td = table.add_cell(div)
        td.add_style("vertical-align: top")

        # provide the interface to build
        div = DivWdg()
        div.add_style("width: 400px")
        div.add( HtmlElement.h3("Scene Build") )

        div.add("Include the following layers: ")


        # add the template
        checkbox = CheckboxWdg("build_option")
        checkbox.set_option("value", "template")
        template_div = DivWdg()
        template_div.add(checkbox)
        template_div.add("Template")
        div.add(template_div)

        # add the instances
        checkbox = CheckboxWdg("build_option")
        checkbox.set_option("value", "instances")
        instance_div = DivWdg()
        instance_div.add(checkbox)
        instance_div.add("Instances of Assets")
        div.add(instance_div)

        # add the audio layer
        checkbox = CheckboxWdg("audio_option")
        checkbox.set_option("value", "audio")
        audio_div = DivWdg()
        audio_div.add(checkbox)
        audio_div.add("Audio Layer")
        audio_div.add("shot code\n")
        audio_div.add("<pre>TF01C-001.wav\n")
        audio_div.add(     "^       ^</pre>")

        div.add(audio_div)

        # add the leica layer
        checkbox = CheckboxWdg("build_option")
        checkbox.set_option("value", "leica")
        leica_div = DivWdg()
        leica_div.add(checkbox)
        leica_div.add("Leica Layer")
        leica_div.add("<pre>C:\\test\\TF01C-001\\image0001.wav\n")
        leica_div.add(     "        ^       ^\n")
        leica_div.add(     "                       ^  ^</pre>")
        leica_div.add("<pre>C:\\test\\#########\\image####.wav</pre>")
        div.add(leica_div)


        button = IconButtonWdg("Submit Build", IconWdg.REFRESH, long=True)
        button.add_event('onclick', "pyflash.build('%s','prod_shot','audio_option')" \
            %(Project.get_project_code())) 
        div.add(button)


        td = table.add_cell(div)
        td.add_style("vertical-align: top")

        widget.add(table)

        return widget


        return table

