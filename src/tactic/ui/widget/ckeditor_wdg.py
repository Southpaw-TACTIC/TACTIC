###########################################################
#
# Copyright (c) 2012, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['CKEditorWdg']

from tactic.ui.common import BaseRefreshWdg
from pyasm.widget import TextWdg, TextAreaWdg


class CKEditorWdg(BaseRefreshWdg):

    def init(self):
        name = self.kwargs.get("name")
        assert(name)
        self.text = TextAreaWdg(name)
        self.text_id = self.kwargs.get("text_id")
        if not self.text_id:
            self.text_id = self.text.set_unique_id()
    def get_display(self):

        top = self.top
        top.add_style("min-width: 600px")

        top.add_class("spt_ckeditor_top")
        top.add_attr("text_id", self.text_id)

        top.add(self.text)

        value = self.kwargs.get("value")
        if value:
            self.text.set_value(value)

        self.text.add_style("width: 100%")
        self.text.add_style("height: 100%")
        self.text.add_style("min-height: 500px")
        self.text.add_style("display: none")
        self.text.set_id(self.text_id)

        self.text.add_behavior( {
        'type': 'load',
        'color': self.text.get_color("background", -10),
        'text_id': self.text_id,
        'cbjs_action': '''

        /*
        var js_file = "ckeditor/ckeditor.js";
        var url = "/context/spt_js/" + js_file;
        var js_el = document.createElement("script");
        js_el.setAttribute("type", "text/javascript");
        js_el.setAttribute("src", url);
        var head = document.getElementsByTagName("head")[0];
        head.appendChild(js_el);
        */
        var init =  function() {

CKEDITOR.on( 'instanceReady', function( ev )
{
    ev.editor.dataProcessor.writer.indentationChars = ' ';
});


var config = {
  toolbar: 'Full',
  uiColor: bvr.color,
  height: '800px'
};

/*
config.toolbar_Full =
[
    ['Source'],
    //['Cut','Copy','Paste'],
    ['Undo','Redo','-','Find','Replace'],
    ['Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
    ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
    '/',
    ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote','CreateDiv'],
    ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
    ['HorizontalRule','SpecialChar'],
    ['Styles','Format','FontSize'],
    ['TextColor','BGColor'],
    ['Maximize', 'ShowBlocks']
];


*/

config.toolbar_Full =
[
    { name: 'document', items : [ 'Source','-','Save','NewPage','DocProps','Preview','Print','-','Templates' ] },
    { name: 'clipboard', items : [ 'Cut','Copy','Paste','PasteText','PasteFromWord','-','Undo','Redo' ] },
    { name: 'editing', items : [ 'Find','Replace','-','SelectAll','-','SpellChecker', 'Scayt' ] },
    { name: 'forms', items : [ 'Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 
        'HiddenField' ] },
    '/',
    { name: 'basicstyles', items : [ 'Bold','Italic','Underline','Strike','Subscript','Superscript','-','RemoveFormat' ] },
    { name: 'paragraph', items : [ 'NumberedList','BulletedList','-','Outdent','Indent','-','Blockquote','CreateDiv',
    '-','JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock','-','BidiLtr','BidiRtl' ] },
    { name: 'links', items : [ 'Link','Unlink','Anchor' ] },
    { name: 'insert', items : [ 'Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak','Iframe' ] },
    '/',
    { name: 'styles', items : [ 'Styles','Format','Font','FontSize' ] },
    { name: 'colors', items : [ 'TextColor','BGColor' ] },
    { name: 'tools', items : [ 'Maximize', 'ShowBlocks','-','About' ] }
];


config.entities = false;
config.basicEntities = false;
config.extraAllowedContent = 'iframe[*]';
config.allowedContent = true;
config.enterMode = CKEDITOR.ENTER_BR;

var instance = CKEDITOR.instances[ bvr.text_id ];
if (instance) instance.destroy();
    
CKEDITOR.replace(bvr.text_id, config );

//var html = '';
//editor = CKEDITOR.appendTo( bvr.text_id, config, html );

bvr.src_el.setStyle("display", "none");




spt.ckeditor = {};


spt.ckeditor.get_value = function(text_id) {
    var text_value =  CKEDITOR.instances[ text_id ].getData();
    return text_value;
}

spt.ckeditor.set_value = function(text_id, data) {
    CKEDITOR.instances[ text_id ].setData(data);
}

}
spt.dom.load_js(['ckeditor/ckeditor.js'], init);
        '''
        } )


        return top



