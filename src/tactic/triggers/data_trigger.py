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
__all__ = ["DataUpdateTrigger"]


from pyasm.command import Trigger
from tactic.command import PythonCmd


class DataValidationTrigger(Trigger):

    def execute(self):
        sobject = self.get_current_sobject()



class DataUpdateTrigger(Trigger):

    def get_args_keys(self):
        return {
        }

    def execute(self):
        input = self.get_input()

        if input.get("mode") == 'delete':
            return


        #print "input: ", input
        sobject = input.get("sobject")

        trigger_sobj = self.get_trigger_sobj()
        data = self.get_trigger_data()

        print "data: ", data

        op = data.get("op")
        assert op

        print "op: ", op


        if op == 'join':

            src_cols = data.get("src_cols")
            dst_col = data.get("dst_col")
            src_cols = src_cols.split("|")

            delimiter = "_"

            values = []
            for col in src_cols:
                value = sobject.get_value(col)
                values.append(value)

            value = delimiter.join(values)

            print "value: ", value

            sobject.set_value(dst_col, value)
            sobject.commit()


        elif op == 'part':
            src_col = data.get("src_col")
            dst_col = data.get("dst_col")

            index = data.get("index")
            if index:
                index = int(index)

            value = sobject.get_value(src_col)

            delimiter = "_"

            parts = value.split(delimiter)
            value = parts[index]

            sobject.set_value(dst_col, value)
            sobject.commit()

        elif op == 'expression':
            # use the full expression language
            dst_col = data.get("dst_col")

            # {@GET(.sequence_code)}_{@GET(.name)}
            # or
            # {@UPPER(.name)}
            expression = data.get("expression")
            value = Search.eval(expression, sobject)
            sobject.set_value(dst_col, value)
            sobject.commit()

        else:
            return




if __name__ == '__main__':

    trigger = DataUpdateTrigger()





