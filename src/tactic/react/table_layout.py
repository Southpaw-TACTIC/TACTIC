
__all__ = ['TableCreatePropertyCmd']

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





