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

__all__ = [ 'SqlPanelWdg' ]


# DEPRECATED: need to figure out if MMS is using this at all


from pyasm.search import DbContainer, SearchType

from tactic.ui.common import BaseRefreshWdg
from panel_wdg import ViewPanelWdg

class SqlPanelWdg(BaseRefreshWdg):

    def get_args_keys(my):
        return {
        "search_type": "search type to be used for editing",
        "view": "view of item to be edited",
        }



    def get_display(my):
        search_type = my.kwargs.get('search_type')
        view = my.kwargs.get('view')

        sobjects = my.get_sobjects()

        view_panel_wdg = ViewPanelWdg(search_type=search_type, view=view)
        view_panel_wdg.set_sobjects(sobjects)

        return view_panel_wdg

    '''
    select "product_type"."product_name", "discipline"."discipline_name",
    "labor_type"."labor_type", "subtask_labor"."total_hours", "personal_time_log"."login_id"

        FROM  "product_type"
        
        LEFT OUTER JOIN "discipline"
        ON "product_type"."discipline_id" = "discipline"."id"
        
        LEFT JOIN "labor_type"
        ON "labor_type"."discipline_id" = "discipline"."id"
        
        INNER JOIN "subtask_labor"
        ON "subtask_labor"."labor_type_id" = "labor_type"."id"

        LEFT OUTER JOIN "personal_time_log"
        ON "subtask_labor"."id" = "personal_time_log"."subtask_labor_id"
        
        ORDER BY "product_type"."product_name"
    ) X
    '''



    def get_sobjects(my):
        columns = ['product_name', 'login_id', 'sample_size', 'labor_average']

        sql = '''

    select "product_name", "login_id", count("total_hours") "sample_size", avg("total_hours") "labor_average"
    from (


    select "product_type"."id", "product_type"."product_name",
        "subtask_product"."product_quantity",
        "subtask"."subtask_letter",
        "subtask_labor"."total_hours",
        "personal_time_log"."login_id"

        FROM  "product_type"

        LEFT OUTER JOIN "subtask_product"
        ON "product_type"."id" = "subtask_product"."product_type_id"
        
        INNER JOIN "subtask"
        ON "subtask"."id" = "subtask_product"."subtask_id"
        
        INNER JOIN "subtask_labor"
        ON "subtask"."id" = "subtask_labor"."subtask_id"
        
        INNER JOIN "personal_time_log"
        ON "subtask_labor"."id" = "personal_time_log"."subtask_labor_id"

    ) X
    GROUP BY X."product_name", X."login_id"
        '''


        db = DbContainer.get("MMS")

        from pyasm.search import Select, Search
        search_type = my.kwargs.get('search_type')
        select = Select()
        select.set_statement(sql)
        statement =  select.get_statement()

        search = Search(search_type)
        search.select = select
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            sobject.set_value("id", -1)


        return sobjects




__all__.append("ProductEstimateReport")
class ProductEstimateReport(SqlPanelWdg):


    def get_sobjects(my):
        columns = ['product_name', 'sample_size', 'labor_average', 'material_average_cost', 'average_time_taken']


        sql = '''
SELECT 
"product_name",
"number_of_each_product_type" "sample_size",
"average_time_taken" "labor_average",
sum("material_cost_per_item") "material_average_cost",
sum("vendor_cost_per_item") "vender_average_cost"



FROM (

SELECT "product_name", "subtask"."id" "subtask_id", "number_of_each_product_type", "average_time_taken",
"product_quantity",
--"total_material_cost", "total_vendor_costs",
"total_material_cost" / "product_quantity" "material_cost_per_item",
"total_vendor_costs" / "product_quantity" "vendor_cost_per_item"


FROM "product_type"

LEFT OUTER JOIN "product_type_aggrgt"
ON "product_type"."id" = "product_type_aggrgt"."product_type_id"


LEFT OUTER JOIN "subtask_product"
ON "product_type"."id" = "subtask_product"."product_type_id"

LEFT OUTER JOIN "subtask"
ON "subtask"."id" = "subtask_product"."subtask_id"

LEFT OUTER JOIN "subtask_material_aggrgt"
ON "subtask"."id" = "subtask_material_aggrgt"."subtask_id"

LEFT OUTER JOIN "subtask_vndrcost_aggrgt"
ON "subtask"."id" = "subtask_vndrcost_aggrgt"."subtask_id"
) X


group by X."product_name", X."number_of_each_product_type", X."average_time_taken",
X."product_quantity", "subtask_id"

order by X."product_name"


        '''


        db = DbContainer.get("MMS")

        from pyasm.search import Select, Search
        search_type = my.kwargs.get('search_type')
        select = Select()
        select.set_statement(sql)
        statement =  select.get_statement()

        search = Search(search_type)
        search.select = select
        sobjects = search.get_sobjects()
        for sobject in sobjects:
            sobject.set_value("id", -1)


        return sobjects



