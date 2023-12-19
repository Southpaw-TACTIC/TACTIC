
__all__ = [
    'TableCreatePropertyCmd',
    'TableSaveCmd',
    'EditSaveCmd',
]

from pyasm.common import Common
from pyasm.search import SearchType

from pyasm.command import Command
from pyasm.search import Search

class TableCreatePropertyCmd(Command):

    def execute(self):

        sheet_code = "breakdown_custom_property"

        item = self.kwargs.get("item")

        name = item.get("name")
        type = item.get("type")
        title = item.get("title")
        editable = item.get("editable")


        sheet = Search.get_by_code("workflow/sheet", sheet_code)
        if not sheet:
            sheet = SearchType.create("workflow/sheet")
            sheet.set_value("category_code", "custom_property")
            sheet.commit()


        # create a new property
        property_item = SearchType.create("workflow/sheet_data")
        property_item.set_value("sheet_code", sheet_code)

        property_data = {
                "title": title,
                "name": name,
                "type": type,
                "editable": editable
        }
        property_item.set_value("data", property_data)

        property_item.commit()




class TableSaveCmd(Command):


    def get_config(self):

        config_class = self.kwargs.get("config_handler")

        handler = Common.create_from_class_path(config_class)
        config = handler.get_config()

        return config
       



    def execute(self):

        updates = self.kwargs.get("updates")

        config = self.get_config()

        configs = {}
        for item in config:
            name = item.get("name")
            configs[name] = item;


        new_sobjects = []
        updated_sobjects = []

        for update in updates:

            search_key = update.get("search_key")
            sobject = Search.get_by_search_key(search_key)

            column = update.get("column")
            value = update.get("value")

            update_column = column

            config = configs.get(column)
            if config:
                update_column = config.get("column") or config.get("name")


            if value == "":
                sobject.set_value(update_column, "NULL", op="is", quoted=False)

            sobject.set_value(update_column, value)
            sobject.commit()

            sobject_dict = sobject.get_sobject_dict()
            updated_sobjects.append(sobject_dict)

        self.info["new_sobjects"] = new_sobjects
        self.info["updated_sobjects"] = updated_sobjects




        

class EditSaveCmd(Command):

    def execute(self):

        updates = self.kwargs.get("updates")
        extra_data = self.kwargs.get("extra_data") or {}

        new_sobjects = []

        for update in updates:

            search_type = update.get("search_type")

            item = update.get("item")

            sobject = SearchType.create(search_type)
            for name, value in item.items():
                sobject.set_value(name, value)

            item_data = {};


            for name, value in extra_data.items():
                try:
                    sobject.set_value(name, value)
                except:
                    item_data[name] = value

            if item_data:
                sobject.set_value("data", item_data)


            sobject.commit()

            sobject_dict = sobject.get_sobject_dict()
            new_sobjects.append(sobject_dict)

        self.info["sobjects"] = new_sobjects




