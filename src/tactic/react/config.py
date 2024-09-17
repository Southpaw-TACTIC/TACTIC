
__all__ = ["ConfigCmd", "BaseElementWdg", "BaseEditElementWdg"]

import os
import json

from pyasm.common import Common
from pyasm.command import Command
from pyasm.search import Search


class ConfigCmd(Command):

    # override this method
    def get_config(self):
        return {}

    def get_renderer_params(self):
        return None



    def get_full_config(self):
        self.execute()
        return self.info.get("config")




    def execute(self):
        config = self.get_config().copy()
        config = self.process_config(config)

        edit_handlers = {}
        for item in config:
            name = item.get("name")

            edit = item.get("edit")
            if not edit:
                edit = "tactic.react.BaseEditElementWdg"
            kwargs = {
                "config": item,
            }
            handler = Common.create_from_class_path(edit, [], kwargs)
            handler.preprocess()

            edit_handlers[name] = handler



        # preprocess all of the handlers
        """
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
        """

        params = self.get_renderer_params()

        self.info["config"] = config
        self.info["renderer_params"] = params


    def process_config(self, config):

        for item in config:

            item_type = item.get("type")
            if item_type == "select":

                values = item.get("values")
                labels = item.get("labels")

                values_expr = item.get("values_expr")
                if values_expr:
                    values = Search.eval(values_expr)

                item["values"] = values

                labels_expr = item.get("labels_expr")
                if labels_expr:
                    labels = Search.eval(labels_expr)

                item["labels"] = labels

        return config



    def preprocess_commit(self, sobject):
        '''Called before an sobject is committed'''
        return



class BaseElementWdg():

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.sobjects = kwargs.get("sobjects")
        self.config = kwargs.get("config")
        self.sobject = None


    def set_current_sobject(self, sobject):
        self.sobject = sobject

    def get_current_sobject(self):
        return self.sobject

    def get_sobjects(self):
        return self.sobjects

    def preprocess(self):
        return

    def execute(self, data):

        sobject = self.get_current_sobject()

        column = self.config.get("column")

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



class BaseEditElementWdg():

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.config = kwargs.get("config")
        self.sobject = None


    def preprocess(self):
        pass



    def update(self, sobject, update):
        pass


