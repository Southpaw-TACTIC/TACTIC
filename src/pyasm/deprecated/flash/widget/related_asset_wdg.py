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

__all__ = ['RelatedAssetInsertElement', 'RelatedAssetInputWdg', 'RelatedAssetAction',
        'RelatedAssetDescriptionWdg']

from pyasm.web import WebContainer, WebState, Widget
from pyasm.widget import BaseInputWdg, SelectWdg, FilterSelectWdg
from pyasm.search import Search
from pyasm.command import DatabaseAction
from pyasm.common import UserException
from pyasm.prod.biz import Asset
from pyasm.widget import BaseTableElementWdg, InsertLinkWdg, TextAreaWdg, FunctionalTableElement

class RelatedAssetInsertElement(FunctionalTableElement):

    def get_title(my):
        return "Related"

    def get_display(my):

        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()

        web_state = WebState.get()
        web_state.add_state("edit|related", sobject.get_code() )

        link = InsertLinkWdg(search_type, \
            text="Insert Related", long=False, config_base='insert_related')
        return link



class RelatedAssetInputWdg(BaseInputWdg):

    def get_title(my):
        return "Related Asset"

    
    def get_display(my):

        search_type = "prod/asset"
    
        web = WebContainer.get_web()
        related_asset = web.get_form_value("edit|related")
        search = Search(search_type)
        search.add_filter("code", related_asset)
        sobjects = search.get_sobjects()

        labels = "|".join( ["%s - %s" % (x.get_code(), x.get_value("name") ) for x in sobjects ] )
        values = "|".join( [x.get_code() for x in sobjects ] )

        select = SelectWdg( my.get_input_name() )
        select.set_persist_on_submit()
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.set_option("web_state","true")

        return select

class RelatedAssetAction(DatabaseAction):

    
    def execute(my):
        my.search_type = my.sobject.get_base_search_type()
        sobject = my.sobject

        related_code = my.get_value()
        if related_code == "":
            return

        # get the related asset selected
        search = Search("prod/asset")
        search.add_filter("code", related_code)
        related_asset = search.get_sobject()
        my.related_asset = related_asset


        # copy the parameters from the related asset
        asset_library = related_asset.get_value("asset_library")
        asset_type = related_asset.get_value("asset_type")

        if related_asset.has_value("episode_code"):
            episode_code = related_asset.get_value("episode_code")
            sobject.set_value("episode_code", episode_code)

        sobject.set_value("asset_library", asset_library )
        sobject.set_value("asset_type", asset_type )

        new_code = my.get_new_code(related_asset)
        sobject.set_value("code", new_code)




    def get_new_code(my, related_asset):

        related_code = related_asset.get_value("code")
        related_type = my.get_value("type")
        if not related_type:
            raise UserException("Suffix (define the list by clicking on the edit icon) cannot be empty")
        # find all of the other related assets that match
        search = Search("prod/asset")
        search.add_where("code like '%s_%s%%'" % (related_code,related_type))
        search.add_order_by("code desc" )
        last_asset = search.get_sobject()
        if last_asset:
            last_code = last_asset.get_code()
            # get the related index
            if my.search_type == 'flash/asset':
                from pyasm.flash import FlashCodeNaming 
                naming = FlashCodeNaming(last_asset, last_code)
            elif my.search_type == 'prod/asset':
                from pyasm.prod.biz import ProdAssetCodeNaming 
                naming = ProdAssetCodeNaming(last_asset, last_code)
            related_index = naming.get_related_index()
        else:
            related_index = 0

        # build up the code
        new_code = '%s_%s%02d' % \
            (related_code, related_type, related_index+1)
        return new_code




    def postprocess(my):
        ''' call the post process '''
        if my.search_type == 'flash/asset':
            from pyasm.flash import FlashAssetCodeUpdate
            update = FlashAssetCodeUpdate()
            update.set_sobject( my.sobject )
            update.postprocess()
        elif my.search_type == 'flash/asset':
            from pyasm.prod.command import AssetCodeUpdate
            update = AssetCodeUpdate()
            update.set_sobject( my.sobject )
            update.execute()


class RelatedAssetDescriptionWdg(BaseInputWdg):

    def get_title(my):
        return "Description"

    
    def get_display(my):

        wdg = TextAreaWdg(my.get_input_name())
        wdg.set_attr("rows", "8")
        parent_asset_code = WebContainer.get_web().get_form_value("edit|related")
        asset = Asset.get_by_code(parent_asset_code)
        if asset:
            wdg.set_value(asset.get_description())
        return wdg







