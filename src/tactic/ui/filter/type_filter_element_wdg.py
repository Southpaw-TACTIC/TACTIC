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

__all__ = ['TypeFilterElementWdg']

from pyasm.web import DivWdg, SpanWdg, Table, WebContainer
from pyasm.search import Search
from pyasm.widget import CheckboxWdg, SelectWdg, TextWdg

from tactic.ui.common import BaseRefreshWdg

from filter_data import FilterData
from filter_element_wdg import BaseFilterElementWdg



# FIXME: this has duplicate code FilterWdg ... need to reconcile this two
# because they are slowly drifting apart!!!

class TypeFilterElementWdg(BaseFilterElementWdg):

    def set_filter_value(my, filter):
        # templates do not have values
        #if filter_index == -1:
        #    return

        # set the value
        filter_id = filter.get_name()
        value = my.values.get(filter_id)
        if value:
            filter.set_value(value, set_form_value=False)


    def init(my):
        my.prefix = 'custom'


    def get_display(my):
        type = my.kwargs.get("type")

        if type not in ['string', 'varchar', 'float', 'integer', 'timestamp', 'login']:
            print("WARNING: FilterWdg: type [%s] not supported, using 'string'" % type)
            type = 'string'

        filter_span = SpanWdg()

        web = WebContainer.get_web()

        if type in ["string", "varchar"]:

            relations = ["is", "is not", "contains", "does not contain", "is empty", "starts with", "ends with"]
            relation_select = SelectWdg("%s_relation" % my.prefix)
            relation_select.set_option("values", relations)
            relation_select.set_persist_on_submit()
            my.set_filter_value(relation_select)

            filter_span.add(relation_select)
            value_text = TextWdg("%s_value" % my.prefix)
            value_text.set_persist_on_submit()
            my.set_filter_value(value_text)
            filter_span.add(value_text)

        elif type in ['integer', 'float', 'currency']:
            relations = ["is equal to", "is greater than", "is less than"]
            relation_select = SelectWdg("%s_relation" % my.prefix)
            relation_select.set_option("values", relations)
            relation_select.set_persist_on_submit()
            my.set_filter_value(relation_select)
            filter_span.add(relation_select)

            value_text = TextWdg("%s_value" % my.prefix)
            value_text.set_persist_on_submit()
            my.set_filter_value(value_text)
            filter_span.add(value_text)

        elif type == 'timestamp':
            relations = ["is newer than", "is older than"]
            relation_select = SelectWdg("%s_relation" % my.prefix)
            relation_select.set_option("values", relations)
            relation_select.set_persist_on_submit()
            my.set_filter_value(relation_select)
            filter_span.add(relation_select)

            options = ["1 day", '2 days', '1 week', '1 month']
            another_select = SelectWdg("%s_select" % my.prefix)
            another_select.add_empty_option("-- Select --")
            another_select.set_option("values", options)
            another_select.set_persist_on_submit()
            my.set_filter_value(another_select)
            filter_span.add(another_select)

            filter_span.add(" or ")

            value_text = TextWdg("%s_value" % my.prefix)
            value_text.set_persist_on_submit()
            my.set_filter_value(value_text)
            filter_span.add(value_text)

        elif type in ['login']:

            relations = ["is", "is not", "contains", "does not contain", "is empty", "starts with", "ends with"]
            relation_select = SelectWdg("%s_relation" % my.prefix)
            relation_select.set_option("values", relations)
            relation_select.set_persist_on_submit()
            my.set_filter_value(relation_select)
            filter_span.add(relation_select)

            value_text = CheckboxWdg("%s_user" % my.prefix)
            value_text.set_persist_on_submit()
            my.set_filter_value(value_text)
            filter_span.add(value_text)
            filter_span.add("{user}")

            filter_span.add(" or ")

            value_text = TextWdg("%s_value" % my.prefix)
            value_text.set_persist_on_submit()
            my.set_filter_value(value_text)
            filter_span.add(value_text)


        return filter_span




    def alter_search(my, search):

        expression = my.kwargs.get("column")
        if not expression:
            expression = my.values.get("%s_column" % my.prefix)
        if not expression:
            return
        parts = expression.split(".")
        search_types = parts[:-1]
        column = parts[-1]

        # go through the hierarchy
        sobjects = None
        search2 = None
        if len(search_types) > 1:
            search_types.reverse()
            for search_type in search_types:
                if sobjects == None:
                    my._alter_search(search, column)
                else:
                    search2 = Search(search_type)
                    search2.add_relationship_filters(sobjects)
                    sobjects = search2.get_sobjects()

                if not sobjects:
                    # if the trail ends, then set the null filter and exit
                    search.set_null_filter()
                    return


        elif not search_types:
            my._alter_search(search, column)
            return
        else:
            search_type = search_types[0]

            # get all the sobjects at the appropriate hierarchy
            search2 = Search(search_type)
            my._alter_search(search2, column)
            sobjects = search2.get_sobjects()

        if search2:
            search.add_relationship_search_filter(search2)
        elif sobjects:
            search.add_relationship_filters(sobjects)
        else:
            search.set_null_filter()





    def _alter_search(my, search, column=None):

        search_type_obj = search.get_search_type_obj()
        values = my.values

        enabled = values.get("%s_enabled" % my.prefix)
        if not column:
            column = values.get("%s_column" % my.prefix)
        relation = values.get("%s_relation" % my.prefix)
        value = values.get("%s_value" % my.prefix)
        if not value:
            value = values.get("%s_select" % my.prefix)

        column_type = search_type_obj.get_tactic_type(column)

        # check if this filter is enabled
        if enabled == None:
            # by default, the filter is enabled
            is_enabled = True
        else:
            is_enabled = (str(enabled) in ['on','true'])
        if not is_enabled:
            return


        # handle all of the types

        if relation == "is empty":
            search.add_where('''("%s" = '' or "%s" is NULL)''' % (column, column) )
            return

        user = values.get("%s_user" % my.prefix)
        if user:
            search.add_user_filter()
            return

        if not value or not column or not relation:
            return

        if relation == "is":
            search.add_filter(column, value)
        elif relation == "is not":
            search.add_where("\"%s\" != '%s'" % (column, value) )
        elif relation == "contains":
            search.add_regex_filter(column, value, op="EQI")
        elif relation == "does not contain":
            search.add_regex_filter(column, value, op="NEQI")
        elif relation == "is empty":
            search.add_where("(\"%s\" = '' or \"%s\" is NULL)" % (column, column) )
        elif relation == "starts with":
            search.add_where("(\"%s\" like '%s%%')" % (column, value) )
        elif relation == "ends with":
            search.add_where("(\"%s\" like '%%%s')" % (column, value) )

        # integer / float comparisons
        elif relation == "is equal to":
            search.add_where("(\"%s\" = %s)" % (column, value) )
        elif relation == "is greater than":
            search.add_where("(\"%s\" > %s)" % (column, value) )
        elif relation == "is less than":
            search.add_where("(\"%s\" < %s)" % (column, value) )

        # date comparisons
        elif relation == "is older than":
            import re
            p = re.compile("\d+-\d+-\d")
            if re.match(p, value):
                search.add_where("\"%s\" <= '%s'" % (column, value) )
            else:
                search.add_where("(now() - \"%s\" >= '%s')" % (column, value) )
        elif relation == "is newer than":
            import re
            p = re.compile("\d+-\d+-\d")
            if re.match(p, value):
                search.add_where("\"%s\" >= '%s'" % (column, value) )
            else:
                search.add_where("(now() - \"%s\" <= '%s')" % (column, value) )
        else:
            print "WARNING: relation [%s] not implemented" % relation
            return


