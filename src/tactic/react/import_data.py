__all__ = ["ImportDataCmd"]

import tacticenv

from pyasm.common import Common
from pyasm.biz import Project, ProjectSetting
from pyasm.security import Batch
from pyasm.command import Command
from pyasm.search import Search, SearchType

from dateutil import parser
from datetime import datetime, timedelta
import csv

from dateutil import rrule, parser


class ImportDataCmd(Command):


    def get_mapping(self):
        column_map = {
            "name": "name",
            "description": "description",
        }
        return column_map




    def check_headers(self, headers_dict):
        # Check for required headers
        pass




    def execute(self):

        dry_run = self.kwargs.get("dry_run") or False

        header = self.kwargs.get("header") or ""
        headers = header.split("\t")
        headers_dict = {}
        for i, header in enumerate(headers):
            header = header.strip()
            header = header.lower()
            header = header.replace(" ", "_")
            header = header.replace("(", "")
            header = header.replace(")", "")
            if not header:
                continue

            # give preference over the left most dates
            if headers_dict.get(header) == None:
                headers_dict[header] = i


        self.check_headers(headers_dict)

        input_data = self.kwargs.get("data") or ""
        data = []

        delimiter = "\t"

        lines = input_data.split("\n")


        for line in lines:
            line = line.strip()
            if not line:
                continue
            values = line.split(delimiter)

            # handle line
            row = {}
            for index, header in enumerate(headers):
                if not header:
                    continue

                orig_header = header
                header = header.strip()
                header = header.lower()

                clean_header = header.replace(" ", "_")
                clean_header = clean_header.replace("(", "")
                clean_header = clean_header.replace(")", "")
                if not clean_header:
                    continue
                #index = headers_dict.get(clean_header)

                try:
                    value = values[index]
                except:
                    continue

                mapping = self.get_mapping()
                column = mapping.get(header)
                if not column:
                    column = mapping.get(clean_header)
                if not column:
                    column = mapping.get(orig_header) # Backwards compatibilty

                if not column:

                    # check if this column is a date
                    try:
                        #check if header is a integer
                        if header.isnumeric() == False:
                            date = parser.parse(header)
                            # set to the closest monday
                            date = date - timedelta(days=(date.weekday()))# this subtracts the days to get the Monday of the week

                            dates = row.get("__dates__")
                            if dates == None:
                                dates = {}
                                row["__dates__"] = dates

                            column = date.strftime("%Y-%m-%d 12:00:00")

                            dates[column] = value

                            continue

                    except Exception as e:
                        #print("ERROR: ", e)
                        pass


                if not column:
                    #print("Header [%s] has no mapping" % orig_header)
                    column = "data->%s" % clean_header

                row[column] = value


            data.append(row)

        self.handle_data(data, dry_run)



    def handle_data(self, data, dry_run):

        line_errors = {}
        data = []


        search_type = self.kwargs.get("search_type")
        print("sss: ", search_type)

        # insert the data
        for item in data:
            print("item: ", item)

        self.info["data"] = data
        self.info["line_errors"] = line_errors



