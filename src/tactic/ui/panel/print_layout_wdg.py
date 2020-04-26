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
__all__ = ["TablePrintLayoutWdg","TablePrintLayoutTitleWdg"]


import types
import datetime

from pyasm.common import Environment, TacticException, Common, Container, Xml, Date, UserException, Config
from pyasm.command import Command
from pyasm.search import Search, SearchKey, SearchType, WidgetDbConfig, Sql
from pyasm.web import *
from pyasm.biz import *   # Project is part of pyasm.biz

from pyasm.widget import BaseConfigWdg, TextWdg, TextAreaWdg, SelectWdg, \
                         WidgetConfigView, WidgetConfig, CheckboxWdg, SearchLimitWdg, IconWdg, \
                         EditLinkWdg, FilterSelectWdg, ProdIconButtonWdg, IconButtonWdg, HiddenWdg,\
                         SwapDisplayWdg

from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.container import PopupWdg, SmartMenu, HorizLayoutWdg
from tactic.ui.widget import DgTableGearMenuWdg, TextBtnSetWdg, CalendarInputWdg

from base_table_layout_wdg import BaseTableLayoutWdg


class TablePrintLayoutTitleWdg(BaseRefreshWdg):

    def get_args_keys(self):
        return {
            "search_type": "Search type of items listed for printing",
            "page_title": "HTML title for the page to be printed",
            "use_short_search_type_label": "Flag to indicate whether or not to shorten the search type name for " \
                                           "use in the page title (shortening involves removing the project prefix)"
        }


    def init(self):

        self.search_type = self.kwargs.get('search_type')
        self.page_title = self.kwargs.get('page_title')
        self.use_short_search_type_label = (self.kwargs.get('use_short_search_type_label') in ['true','True','TRUE',True])

        self.html_template_dir = "%s/src/context/html_templates" % Environment.get_install_dir()


    def get_display(self): 

        page_title = self.page_title
        if not page_title:
            st_label = self.search_type
            if self.use_short_search_type_label:
                bits = st_label.split('/')
                st_label = bits[ len(bits) - 1 ].capitalize()
            page_title = "Print %s listing" % st_label

        page_title = "%s %s" % ( page_title, datetime.datetime.now().strftime("(generated %b. %m, %Y at %H:%M:%S)") )

        # returns a straight text string for the title ...
        return page_title



class TablePrintLayoutWdg(BaseTableLayoutWdg):

    def __init__(self, **kwargs):
        # kwargs['specified_search_key_list'] = None
        super(TablePrintLayoutWdg, self).__init__(**kwargs)

        self.page_title = self.kwargs.get('page_title')
        self.use_short_search_type_label = (self.kwargs.get('use_short_search_type_label') in ['true','True','TRUE',True])


    def get_display(self):
        
        # get view attributes
        self.view_attributes = self.config.get_view_attributes()

        # Handle security ... get overall sobject security access ...
        #
        # Different security types
        #
        # group: search_type, 
        #
        security = Environment.get_security()

        # check edit permission
        default_access = self.view_attributes.get('access')

        if not default_access:
            default_access = 'view'
        key = {
            'search_type': self.search_type
        }
        self.view_permission = security.check_access("sobject", key, "view", default=default_access)


        # if a search key has been explicitly set, use that
        search_key = self.kwargs.get("search_key")
        if search_key:
            sobject = Search.get_by_search_key(search_key)
            self.sobjects = [sobject]

        elif self.kwargs.get("selected_search_keys"):
            # if this is provided then build the list of sobjects to show in table from the list
            # of search keys provided in this kwarg parameter value ...
            sel_skey_list = self.kwargs.get("selected_search_keys")
            for skey in sel_skey_list:
                sobj = Search.get_by_search_key( skey )
                self.sobjects.append( sobj )

        elif self.kwargs.get("do_search") == "true":
            self.handle_search()

        # Create top level Div to return ...
        top_wdg = DivWdg()

        # Add print instructions on page ...
        print_instructions_html = '''
        <div class="print_instructions hide_for_printing">
            <input type='button' onclick='javascript:window.print();' value='Print!'/>
            To preview go to 'File-&gt;Print Preview' ... to set-up print margins go to 'File-&gt;Page Setup'
        </div>

        <div class="hide_for_printing">
            <br/>
        </div>
        '''
        top_wdg.add( print_instructions_html )

        # Add a Title for the printed listing ...
        page_title = self.page_title
        if not page_title:
            st_label = self.search_type
            if self.use_short_search_type_label:
                bits = st_label.split('/')
                st_label = bits[ len(bits) - 1 ].capitalize()
            page_title = "%s listing" % st_label

        timestamp = datetime.datetime.now().strftime("(generated %b. %m, %Y at %H:%M:%S)")
        top_wdg.add( '<div><span class="page_title">%s</span> &nbsp;<span class="page_title_timestamp">%s</span></div>' % \
                     (page_title, timestamp) )


        # -- GROUP SPAN - this is to how hidden elements for ordering and
        # grouping
        group_span = SpanWdg()
        group_span.add_class("spt_table_search")
        group_span.add(self.get_group_wdg() )
        top_wdg.add(group_span)

        # allow generators to add widgets as needed
        new_widgets = []
        for i, widget in enumerate(self.widgets ):
            attrs = self.config.get_element_attributes(widget.get_name())
            gen_expr = attrs.get("generator")
            gen_list = attrs.get("generator_list")
            generator = widget.get_name()

            list = None
            if gen_expr:
                # TODO: this communication needs to be formalized.  Currently
                # this is used in MMS to generate employee columns for a
                # given supervisor
                vars = Container.get("Message:search_vars")
                parser = ExpressionParser()
                list = parser.eval(gen_expr, vars=vars)
            elif gen_list:
                list = gen_list.split("|")
                

            if list != None:
                import copy
                for result in list:
                    new_widget = copy.copy(widget)
                    new_widget.set_name(result)
                    new_widget.set_title( None )
                    new_widget.set_sobjects( self.sobjects )
                    new_widgets.append(new_widget)
                    new_widget.set_generator(generator)
                # FIXME: this should not be displayed???
                if not list:
                    new_widgets.append(widget)

            else:
                new_widgets.append(widget)
        self.widgets = new_widgets
        

        # set the state
        for i, widget in enumerate( self.widgets ):
            widget.set_state(self.state)

        table_width_set = False
        for i, widget in enumerate( self.widgets ):
            # set the type
            widget_type = self.config.get_type( widget.get_name() )
            widget.type = widget_type

            if not table_width_set and widget.width:
                table_width_set = True

        top_wdg.add( HtmlElement.br(clear="all") )


        # override the table created in the __init__ ... as we need to setup different CSS classes
        # for print layout and display ...
        #
        self.table = Table()
        self.table.add_styles( "width: 100%s;" % "%" )

        top_wdg.add( self.table )


        # get all the attributes
        for widget in self.widgets:
            name = widget.get_name()
            if name and name != "None":
                attrs = self.config.get_element_attributes(name)
                self.attributes.append(attrs)

            else:
                self.attributes.append({})


        # check the security for the elements in a config
        element_names = self.config.get_element_names()
        for i, widget in enumerate(self.widgets):
            element_name = widget.get_name()
            default_access = self.attributes[i].get('access')
            if not default_access:
                default_access = 'view'
            key = {
                'search_type': self.search_type,
                'key': str(element_name)
            }
            if not security.check_access('element',key,"view",default=default_access):
                self.widgets.remove(widget)

        # set the sobjects to all the widgets then preprocess
        for widget in self.widgets:
            widget.set_sobjects(self.sobjects)
            widget.set_parent_wdg(self)
            # preprocess the elements
            widget.preprocess()


        widgets_not_meant_for_print = [
                "HiddenRowToggleWdg",
                "ButtonElementWdg"
        ]
        valid_widget_idx_list = []

        # only output widgets that are specified in the view and that are "printable" ...
        for i, widget in enumerate(self.widgets):
            if not widget.is_in_column():
                continue
            full_class_name = Common.get_full_class_name( widget )
            bits = full_class_name.split('.')
            widget_class_name = bits[ len(bits) - 1 ]
            if widget_class_name in widgets_not_meant_for_print:
                continue
            valid_widget_idx_list.append(i)


        '''
        # add all of the headers
        num_wdg = len(self.widgets)
        for i, widget in enumerate(self.widgets):
            if not widget.is_in_column():
                continue
            th = self.add_header_wdg( self.table, widget, i, num_wdg )
        '''

        # get the color maps
        color_config = WidgetConfigView.get_by_search_type(self.search_type, "color")
        color_xml = color_config.configs[0].xml
        color_maps = {}
        for widget in self.widgets:
            name = widget.get_name()
            xpath = "config/color/element[@name='%s']/colors" % name
            color_node = color_xml.get_node(xpath)
            color_map = color_xml.get_node_values_of_children(color_node)


            # use old weird query language
            query = color_map.get("query")
            query2 = color_map.get("query2")
            if query:
                color_map = {}

                search_type, match_col, color_col = query.split("|")
                search = Search(search_type)
                sobjects = search.get_sobjects()

                # match to a second atble
                if query2:
                    search_type2, match_col2, color_col2 = query2.split("|")
                    search2 = Search(search_type2)
                    sobjects2 = search2.get_sobjects()
                else:
                    sobjects2 = []

                for sobject in sobjects:
                    match = sobject.get_value(match_col)
                    color_id = sobject.get_value(color_col)

                    for sobject2 in sobjects2:
                        if sobject2.get_value(match_col2) == color_id:
                            color = sobject2.get_value(color_col2)
                            break
                    else:
                        color = color_id


                    color_map[match] = color

            color_maps[name] = color_map


        # do the header row ...
        self.table.add_row()
        for j, widget in enumerate(self.widgets):

            if j not in valid_widget_idx_list:
                continue

            th = self.table.add_header()
            th.add( widget.get_title() )


        # Add the data rows
        #
        # Note: there are some special rows at the beginning.  These rows
        # correspond to special functionality of the table and are generally
        # hidden
        #
        # row #1: hidden row, which provides the template widgets to create
        #   newly inserted rows
        # row #2: contains all of the templates for editability of the cells
        #
        for row, sobject in enumerate(self.sobjects):

            if sobject.is_insert():
                continue

            # TODO: handle grouping?

            tbody = self.table.add_tbody()
            search_key = SearchKey.get_by_sobject(sobject)

            row_id = "%s|%s" % (self.table_id, search_key)
            tbody.set_id(row_id)

            self.row_ids[search_key] = row_id

            # add the main row
            tr = self.table.add_row()
            tr.add_class("spt_table_tr")

            tr.add_style('min-height: %spx' % self.min_cell_height)
            tr.add_style('height: %spx' % self.min_cell_height)
            tr.add_style('vertical-align: top')

            for j, widget in enumerate(self.widgets):

                widget.set_current_index(row)

                if j not in valid_widget_idx_list:
                    continue

                td = self.table.add_cell()

                name = widget.get_name()
                td.add_attr("spt_element_name", name)

                # actually draw the widget
                div = DivWdg()
                div.add_style('padding', '3px')
                div.add_style("width: 100%")
                div.add_style("height: 100%")
                if self.widgets[j-1].get_name() == widget.get_name():
                    widget.column_index = 1
                else:
                    widget.column_index = 0

                div.add( widget.get_buffer_display() )
                # div.add( widget.get_simple_display() )  # doesn't work for expressions and such, also dates aren't formatted

                td.add_styles( "border: 1px solid black; padding: 4px;" )
                td.add(div)

                # add a color based on the color map
                try:
                    widget_value = str(widget.get_value())
                    color_map = color_maps.get(name)
                    if color_map:
                        color = color_map.get(widget_value)
                        if color:
                            td.add_style("background-color", color)
                except Exception as e:
                    print('WARNING: problem when getting widget value for color mapping on widget [%s]: ' % widget, e.message)

            # close the surrounding tbody
            self.table.close_tbody()

        return top_wdg


    def get_print_action_js( cls, listing_type ):
        web = WebContainer.get_web()
        template_js = """
            var activator_el = spt.smenu.get_activator( bvr );
            var ok_to_print = true;

            // Now Run any print-setup script code here ...
            //
            %%s

            if( ok_to_print ) {
                var options_list = [
                    'width=850',
                    'height=600',
                    'location=no',
                    'directories=no',
                    'status=no',
                    'menubar=yes',
                    'scrollbars=yes',
                    'resizable=yes'
                ];

                if( window.navigator.userAgent.match( /Firefox/ ) ) {
                    options_list.push( 'toolbar=yes' );
                } else {
                    options_list.push( 'toolbar=no' );
                }

                //var base_url = '%(url)s';

                var location = document.location;
                var base_url = spt.Environment.get().get_server_url();



                var print_url = base_url + "/context/utility/print_table_items.html";

                var win = window.open( print_url,  // URL
                                       '',  // name of window
                                       options_list.join(',') );

                var server = TacticServerStub.get();

                // FIRST get window title for print page pop-up ...
                //
                var table_top = activator_el.getParent(".spt_table_top");
                var args_map = {
                    'search_type': table_top.getProperty("spt_search_type"),
                    'use_short_search_type_label': true
                };

                var title = server.get_widget( "tactic.ui.panel.TablePrintLayoutTitleWdg", {'args': args_map} );
                win.document.title = title;

                // Then set-up the call to generate the table listing HTML for the body content ...
                // spt.dg_table.search_cbk( {},
                var evt = {};
                var body_html = spt.dg_table.search_cbk(evt, 
                                    { 'src_el': activator_el,
                                      'override_class_name': 'tactic.ui.panel.TablePrintLayoutWdg',
                                      'use_short_search_type_label': true,
                                      'return_html': true,
                                      %%s
                                    } );

                if( spt.browser.is_IE() ) {
                    win.document._SptTablePrintHtml_ = body_html;
                    win.document._SptTablePrintLoaded_ = 'LOADED';
                } else {
                    win._SptTablePrintHtml_ = body_html;
                    win._SptTablePrintLoaded_ = 'LOADED';
                }
            }

        """% {'url': web.get_base_url().to_string()}

        if listing_type == "selected_items":
            # print_selected_items_js
            js = template_js % (
                """
                var table_top = activator_el.getParent(".spt_table_top");
                var table = table_top.getElement(".spt_table");

                var selected_skey_list = [];

                var layout = activator_el.getParent(".spt_layout");
                var version = layout.getAttribute("spt_version");
                var selected_tbodies = [];
                if (version == "2") {
                    selected_tbodies = spt.table.get_selected_rows();
                } else {
                    selected_tbodies = spt.dg_table.get_selected_tbodies( table );
                }
                for( var c=0; c < selected_tbodies.length; c++ ) {
                    var skey = selected_tbodies[c].getProperty("spt_search_key");
                    if( ! skey.contains("-1") ) {
                        selected_skey_list.push( skey );
                    }
                }

                if( ! selected_skey_list.length ) {
                    alert("Nothing selected to print. Please select items from the list first.");
                    ok_to_print = false;
                }
                """,
                "     'selected_search_keys': selected_skey_list"
                )

        elif listing_type == "page_matched_items":
            # print_page_matched_items_js
            js = template_js % (
                "",
                "     'show_search_limit': true"
                )

        elif listing_type == "all_matched_items":
            # print_all_matched_items_js
            js = template_js % (
                "",
                "     'show_search_limit': false,\
                       'search_limit': -1"
                )
        else:
            js = "alert('Print listing type [%s] is not valid');" % listing_type

        return js

    get_print_action_js = classmethod(get_print_action_js)


