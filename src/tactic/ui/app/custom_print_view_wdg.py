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
__all__ = ["CustomPrintViewWdg"]

# from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
# from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.common import BaseRefreshWdg
from pyasm.common import Environment
from pyasm.search import Search
from pyasm.biz import ExpressionParser

import types


class CustomPrintViewWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
            "search_key": "search_key for the item being printed?",
            "page_title": "Title for the title tag of the print view page",
            "content_type": "This is either 'title' or 'body' ... need to read both to get contents on web client",
            "custom_html_layout_file": "the html file name of the site_custom html template for the print layout"
        }


    def init(my):

        my.search_key = my.kwargs.get('search_key')
        my.page_title = my.kwargs.get('page_title')
        my.content_type = my.kwargs.get('content_type')
        my.html_file  = my.kwargs.get('custom_html_layout_file')


    def get_display(my): 

        if not my.html_file:
            return ""


        utility_path = "%s/src/context/utility" % Environment.get_install_dir()

        html_templates_path = "%s/templates" % utility_path
        custom_template_path = "%s/site_custom" % utility_path

        if my.content_type == 'title':
            return my.page_title

        elif my.content_type == 'body':
            body_template_fp = open( "%s/print_custom_page_TEMPLATE_body_contents.html" % html_templates_path, "r" )
            body_template = body_template_fp.read()
            body_template_fp.close()

            layout_html_fp = open( "%s/%s" % (custom_template_path, my.html_file), "r" )
            layout_html = layout_html_fp.read()
            layout_html_fp.close()

            layout_bits = layout_html.split("[[DATA_GATHER]]")
            layout_html = "%s%s" % (layout_bits[0], layout_bits[2])
            stmt = layout_bits[1].strip()

            stmt_bits = stmt.split("\n")
            stmt_arr = []
            for s in stmt_bits:
                stmt_arr.append( s.strip() )

            stmt = '\n'.join( stmt_arr )

            exec stmt  # assigns 'gather_specs' dictionary ...

            layout_html_filled = my.process_data_gather( my.search_key, gather_specs, layout_html )

            body_html = body_template.replace("[[PRINT_LAYOUT_PLACEHOLDER]]", layout_html_filled)
            return body_html

        return ""  # FIXME: should error or return some error message


    def process_data_gather( my, search_key, gather_specs, layout_html ):

        sobject = Search.get_by_search_key( search_key )
        for label,info in gather_specs.iteritems():

            if label == "@":
                subs_list = info.get("element_subs")
                for sub in subs_list:
                    value = sobject.get_value( sub )
                    if not value:
                        value = "&nbsp;"
                    substitution_tag = "${@.%s}" % sub
                    layout_html = layout_html.replace( substitution_tag, "%s" % value )

            elif info.get("type") == "sobject":
                expr = info.get("expr")
                expr_vars_list = info.get("expr_vars")
                if expr_vars_list:
                    for e_var in expr_vars_list:
                        bits = e_var.split("=")
                        var_name = bits[0]
                        value = sobject.get_value( bits[1].replace("@.","") )
                        expr = expr.replace( var_name, "%s" % value )
                parser = ExpressionParser()
                result = parser.eval( expr )
                if result:
                    if type(result) == types.ListType:
                        other_sobject = result[0]
                    else:
                        other_sobject = result
                    subs_list = info.get("element_subs")
                    for sub in subs_list:
                        src_col = sub
                        dst_col = sub
                        if "#" in sub:
                            sub_bits = sub.split("#")
                            src_col = sub_bits[0]
                            dst_col = sub_bits[1]
                        value = other_sobject.get_value( src_col )
                        if not value:
                            value = "&nbsp;"
                        if "_date" in dst_col:
                            value = value.split(" ")[0]
                        if "_time" in dst_col:
                            time_bits = value.split(" ")[1].split(":")
                            value = "%s:%s" % (time_bits[0], time_bits[1])
                        substitution_tag = "${%s.%s}" % (label, dst_col )
                        layout_html = layout_html.replace( substitution_tag, "%s" % value )

            elif info.get("type") == "gather_list_class":
                import_stmt = "%s as GatherClass" % info.get("import_stmt")
                exec import_stmt
                gc = GatherClass( sobject )
                item_list = gc.get_items()

                subs_list = info.get("element_subs")
                for c, item in enumerate(item_list):
                    for sub in subs_list:
                        substitution_tag = "${%s[%s].%s}" % (label, c, sub)
                        layout_html = layout_html.replace( substitution_tag, "%s" % item[ sub ] )

                max_id = info.get("max_id")
                if max_id > (len(item_list) - 1):
                    for c in range(len(item_list),max_id+1):
                        for sub in subs_list:
                            substitution_tag = "${%s[%s].%s}" % (label, c, sub)
                            layout_html = layout_html.replace( substitution_tag, "&nbsp;" )


            elif info.get("type") == "value":
                parser = ExpressionParser()
                value = parser.eval( info.get("expr"), sobject )
                if not value:
                    value = "&nbsp;"
                layout_html = layout_html.replace( "${%s}" % label, "%s" % value )

        return layout_html


