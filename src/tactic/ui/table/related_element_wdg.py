############################################################
#
#    Copyright (c) 2008, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['RelatedElementWdg']

from pyasm.web import DivWdg
from pyasm.search import Search

from tactic.ui.common import BaseTableElementWdg

class RelatedElementWdg(BaseTableElementWdg):

    ARGS_KEYS = {
    'column': 'the column to display',
    'expression': 'the expression to operate on the result sobject to display',
    'template': 'template for finding related data'
    }



    def preprocess(my):
        my.data = my.get_data()

    def get_display(my):

        sobject = my.get_current_sobject()
        sobject_id = sobject.get_id()
        result = my.data.get(sobject_id)

        top = DivWdg()
        if not result:
            return top


        expression = my.get_option("expression")
        if expression:
            value = Search.eval(expression, result)
        else:
            column = my.get_option("column")
            if not column:
                column = my.get_name()
            try:
                value = result.get_value(column)
            except:
                value = ""

        top.add(value)

        return top


    def is_editable(my):
        return True


    def get_data(my):
        """
        <element name='work_location' title='Originating Site'>
          <display class='tactic.ui.table.ExpressionElementWdg'>
            <expression>@GET(MMS/work_location.location)</expression>
            <alt_expression>@GET(MMS/work_location.id)</alt_expression>
            <order_by>work_location.location</order_by>
          </display>
        </element>
        """


        data = {}

        sobjects = my.sobjects
        if not sobjects:
            return data

        #template = "MMS/subtask.MMS/job.MMS/request.MMS/security_classification"
        template = my.get_option("template")
        keys = template.split(".")

        # get the sobjects (main search)
        search_type_obj = sobjects[0].get_search_type_obj()
        join_table = search_type_obj.get_table()
        search_type = search_type_obj.get_value("search_type")

        if keys[0] != search_type:
            keys.insert(0, search_type)

        search_ids = []
        for sobject in sobjects:
            search_id = sobject.get_id()
            search_ids.append(search_id)


        keys.reverse()

        # create main search
        search = Search(keys[0])
        table = search.get_table()

        # add the columns
        search.add_column("*", table=table)
        # add the id column from the joined table
        search.add_column("id", table=join_table, as_column='%s_id' % join_table)

        current_key = None
        for i in range(1, len(keys)):
            key = keys[i]
            namespace, table = key.split("/")
            search.add_join(key, current_key)

            current_key = key

        search.add_filters("id", search_ids, table=table)
        search.set_show_retired(True)

        results = search.get_sobjects()

        # make into a dictionary based on search id
        for result in results:
            id = result.get_value("%s_id" % join_table)
            data[id] = result
            print id, result.get_data()

        print "results: ", len(results)
        return data


__all__.append('RelatedInputWdg')
#from tactic.ui.input import BaseInputWdg
from pyasm.widget import BaseInputWdg, SelectWdg, TextWdg
class RelatedInputWdg(BaseInputWdg):

    ARGS_KEYS = {
    'path': 'path'
    }

    def get_display(my):
        top = DivWdg()
        top.add_style("width: 200px")
        top.add_style("height: 200px")
        top.add_color("background", "background")
        top.add_color("padding", "10px")
        top.add_border()

        template = my.get_option("template")
        template = "prod/sequence"

        select = SelectWdg("foo")
        top.add(select)
        select.set_option("values", "XG|FF|WOW")

        text = TextWdg("foo")
        top.add(text)



        top.add("!!!!!")


        return top





