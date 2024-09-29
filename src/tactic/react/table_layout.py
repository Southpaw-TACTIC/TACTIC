
__all__ = [
    'BaseTableSearchCmd',
    'TableCreatePropertyCmd',
    'TableSaveCmd',
    'EditSaveCmd',
    'DeleteCmd',
]

from pyasm.common import Common
from pyasm.search import SearchType

from pyasm.command import Command
from pyasm.search import Search




class BaseTableSearchCmd(Command):

    def get_sobjects(self):
        return None


    def get_config(self):
        config_handler = self.kwargs.get("config_handler")
        if config_handler:
            handler = Common.create_from_class_path(config_handler, [])
            config = handler.get_full_config()
        else:
            config = []

        return config


    """
    def alter_search(self, search):
        return
    """


    def execute(self):
        # get the sobjects
        sobjects = self.get_sobjects() or []


        config = self.get_config()

        # preprocess all of the handlers
        display_handlers = {}
        for item in config:
            name = item.get("name")

            display = item.get("display")
            if not display:
                display = "tactic.react.BaseElementWdg"
            kwargs = {
                "config": item,
                "sobjects": sobjects
            }
            handler = Common.create_from_class_path(display, [], kwargs)
            handler.preprocess()
            display_handlers[name] = handler


        columns = []

        sobjects_list = []
        for sobject in sobjects:

            sobject_dict = sobject.get_sobject_dict(columns, mode="fast")

            for item in config:
                name = item.get("name")
                item_type = item.get("type")

                # if there is a display handler
                display = item.get("display")
                if display:
                    handler = display_handlers.get(name)
                    handler.set_current_sobject(sobject)
                    handler.execute(sobject_dict)

                elif item_type == "null":
                    value = ""

                elif item_type == "expression":
                    # FIXME: this is slow
                    expression = item.get("expression")
                    if not expression:
                        raise Exception("No expession for [%s] in expession type" % name)
                    value = Search.eval(expression, sobject)

                else:
                    column = item.get("column")

                    if name.find("->") != -1:
                        if not column:
                            column = name
                        parts = name.split("->")
                        name = parts[1]


                    if not column:
                        column = name

                    try:
                        value = sobject.get_value(column)
                    except:
                        value = ""

                    sobject_dict[name] = value



            sobjects_list.append(sobject_dict)

        return sobjects_list





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
        if not config_class:
            return []

        handler = Common.create_from_class_path(config_class)
        config = handler.get_full_config()


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
        sobjects = []


        for update in updates:

            search_key = update.get("search_key")
            if search_key:
                sobject = Search.get_by_search_key(search_key)
                if not sobject:
                    raise Exception("SObject [%s] does not exist" % search_key)

                column = update.get("column")
                value = update.get("value")

                data = update.get("data")
                if column:
                    item = {
                        column: value
                    }
                elif data:
                    item = data
                else:
                    raise Exception("Nothing to update")

            else:
                search_type = update.get("search_type")
                sobject = SearchType.create(search_type)
                item = update.get("item")

                code = item.get("code")
                sobject.set_value("code", code)


            for column, value in item.items():

                update_column = column

                config = configs.get(column) or {"name": column}
                edit = config.get("edit")

                if edit:
                    edit_handler = Common.create_from_class_path(edit)
                    edit_handler.update(sobject, update)


                else:
                    update_column = config.get("column") or config.get("name")
                    if value == "":
                        if update_column.find("->") != -1:
                            parts = update_column.split("->")
                            data = sobject.get_json_value(parts[0]) or {}
                            if data.get(parts[1]) != None:
                                del data[parts[1]]
                                sobject.set_json_value(parts[0], data)
                        else:
                            sobject.set_value(update_column, "NULL", quoted=False)
                    else:
                        sobject.set_value(update_column, value)

            extra_data = self.kwargs.get("extra_data") or {}

            for column, value in extra_data.items():

                config = configs.get(column)
                if config:
                    update_column = config.get("column") or config.get("name")
                    if value == "":
                        if update_column.find("->") != -1:
                            parts = update_column.split("->")
                            data = sobject.get_json_value(parts[0]) or {}
                            if data.get(parts[1]) != None:
                                del data[parts[1]]
                                sobject.set_json_value(parts[0], data)
                        else:
                            sobject.set_value(update_column, "NULL", quoted=False)
                    else:
                        sobject.set_value(update_column, value)
                else:
                    sobject.set_value(column, value)

            sobject.commit()

            sobject_dict = sobject.get_sobject_dict()

            sobjects.append(sobject_dict)

        self.info["sobjects"] = sobjects
        self.info["new_sobjects"] = new_sobjects
        self.info["updated_sobjects"] = updated_sobjects


class EditSaveCmd(Command):

    def execute(self):

        updates = self.kwargs.get("updates")
        extra_data = self.kwargs.get("extra_data") or {}

        config_handler = self.kwargs.get("config_handler")
        config = Common.create_from_class_path(config_handler)
        config_list = config.get_full_config() or []

        config_dict = {}
        for config_item in config_list:
            config_dict[config_item.get("name")] = config_item


        new_sobjects = []

        for update in updates:

            search_type = update.get("search_type")

            item = update.get("item")

            sobject = SearchType.create(search_type)
            for name, value in item.items():

                config_item = config_dict.get(name) or {}
                column = config_item.get("column")
                if not column:
                    column = name
                sobject.set_value(column, value)

            item_data = {};


            for name, value in extra_data.items():
                try:
                    sobject.set_value(name, value)
                except:
                    item_data[name] = value

            if item_data:
                sobject.set_value("data", item_data)

            config.preprocess_commit(sobject)
            sobject.commit()

            sobject_dict = sobject.get_sobject_dict()
            new_sobjects.append(sobject_dict)

        self.info["sobjects"] = new_sobjects



class DeleteCmd(Command):

    def execute(self):

        search_keys = self.kwargs.get("search_keys")
        print("sss: ", search_keys);

        sobjects = Search.get_by_search_keys(search_keys)

        for sobject in sobjects:
            sobject.delete()





